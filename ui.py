import os
import shutil
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog


try:
	from high_speed_detect import start_attendance
except Exception:
	
	start_attendance = None


def get_dataset_path():
	
	base = os.path.dirname(__file__)
	path = os.path.join(base, "dataset")
	if not os.path.exists(path):
		os.makedirs(path, exist_ok=True)
	return path


class CRUDUI(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Dataset CRUD Manager")
		self.geometry("700x420")

		self.dataset_dir = get_dataset_path()

		
		top_frame = tk.Frame(self)
		top_frame.pack(fill=tk.X, padx=8, pady=6)

		tk.Label(top_frame, text="Filter:").pack(side=tk.LEFT)
		self.filter_var = tk.StringVar()
		self.filter_var.trace_add("write", lambda *_: self._apply_filter())
		tk.Entry(top_frame, textvariable=self.filter_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

		
		middle = tk.Frame(self)
		middle.pack(fill=tk.BOTH, expand=True, padx=8)

		self.person_listbox = tk.Listbox(middle)
		self.person_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.person_listbox.bind("<<ListboxSelect>>", lambda e: self._update_status())

		sb = tk.Scrollbar(middle, command=self.person_listbox.yview)
		sb.pack(side=tk.LEFT, fill=tk.Y)
		self.person_listbox.config(yscrollcommand=sb.set)

		
		btn_frame = tk.Frame(self)
		btn_frame.pack(fill=tk.X, padx=8, pady=6)

		
		btn = tk.Button(btn_frame, text="Create", command=self.create_person)
		btn.pack(side=tk.LEFT)
		btn = tk.Button(btn_frame, text="Rename", command=self.rename_person)
		btn.pack(side=tk.LEFT, padx=(6, 0))
		btn = tk.Button(btn_frame, text="Delete", command=self.delete_person)
		btn.pack(side=tk.LEFT, padx=(6, 0))
		btn = tk.Button(btn_frame, text="Add Images", command=self.add_images)
		btn.pack(side=tk.LEFT, padx=(6, 0))
		btn = tk.Button(btn_frame, text="Open Folder", command=self.open_folder)
		btn.pack(side=tk.LEFT, padx=(6, 0))
		
		self.start_att_btn = tk.Button(btn_frame, text="Start Attendance", command=self.start_attendance_ui)
		self.start_att_btn.pack(side=tk.LEFT, padx=(6, 0))
		self.stop_att_btn = tk.Button(btn_frame, text="Stop Attendance", command=self.stop_attendance_ui, state=tk.DISABLED)
		self.stop_att_btn.pack(side=tk.LEFT, padx=(6, 0))
		
		btn = tk.Button(btn_frame, text="Refresh", command=self.refresh)
		btn.pack(side=tk.RIGHT)

		
		self.status_var = tk.StringVar()
		self.status_var.set("")
		tk.Label(self, textvariable=self.status_var, anchor="w").pack(fill=tk.X, padx=8, pady=(0, 6))

		self.refresh()

		
		self.attendance_thread = None
		self.attendance_stop_event = None

	def _list_persons(self):
		
		items = []
		try:
			for name in os.listdir(self.dataset_dir):
				p = os.path.join(self.dataset_dir, name)
				if os.path.isdir(p):
					items.append(name)
		except Exception:
			pass
		items.sort()
		return items

	def refresh(self):
		self._all_items = self._list_persons()
		self._apply_filter()
		self._update_status()

	def _apply_filter(self):
		term = self.filter_var.get().lower().strip()
		self.person_listbox.delete(0, tk.END)
		for name in self._all_items:
			if not term or term in name.lower():
				self.person_listbox.insert(tk.END, name)

	def _get_selected(self):
		sel = self.person_listbox.curselection()
		if not sel:
			return None
		return self.person_listbox.get(sel[0])

	def _update_status(self):
		sel = self._get_selected()
		total = len(self._all_items)
		if sel:
			count = len(os.listdir(os.path.join(self.dataset_dir, sel))) if os.path.exists(os.path.join(self.dataset_dir, sel)) else 0
			self.status_var.set(f"Selected: {sel} — images: {count} | total persons: {total}")
		else:
			self.status_var.set(f"Total persons: {total}")

	def create_person(self):
		name = simpledialog.askstring("Create", "Enter name for new person:")
		if not name:
			return
		name = name.strip()
		if not name:
			messagebox.showwarning("Invalid", "Name cannot be empty")
			return
		target = os.path.join(self.dataset_dir, name)
		if os.path.exists(target):
			messagebox.showerror("Exists", "A person with that name already exists")
			return
		try:
			os.makedirs(target)
			self.refresh()
			messagebox.showinfo("Created", f"Person '{name}' created")
		except Exception as e:
			messagebox.showerror("Error", f"Could not create: {e}")

	def rename_person(self):
		sel = self._get_selected()
		if not sel:
			messagebox.showwarning("Select", "Please select a person to rename")
			return
		new = simpledialog.askstring("Rename", f"Rename '{sel}' to:")
		if not new:
			return
		new = new.strip()
		if not new:
			messagebox.showwarning("Invalid", "Name cannot be empty")
			return
		src = os.path.join(self.dataset_dir, sel)
		dst = os.path.join(self.dataset_dir, new)
		if os.path.exists(dst):
			messagebox.showerror("Exists", "Target name already exists")
			return
		try:
			os.rename(src, dst)
			self.refresh()
			messagebox.showinfo("Renamed", f"'{sel}' renamed to '{new}'")
		except Exception as e:
			messagebox.showerror("Error", f"Could not rename: {e}")

	def delete_person(self):
		sel = self._get_selected()
		if not sel:
			messagebox.showwarning("Select", "Please select a person to delete")
			return
		full = os.path.join(self.dataset_dir, sel)
		if not os.path.exists(full):
			messagebox.showerror("Not found", "Selected person not found on disk")
			self.refresh()
			return
		ok = messagebox.askyesno("Delete", f"Delete '{sel}' and all its images? This cannot be undone.")
		if not ok:
			return
		try:
			shutil.rmtree(full)
			self.refresh()
			messagebox.showinfo("Deleted", f"'{sel}' deleted")
		except Exception as e:
			messagebox.showerror("Error", f"Could not delete: {e}")

	def add_images(self):
		sel = self._get_selected()
		if not sel:
			messagebox.showwarning("Select", "Please select a person to add images to")
			return
		files = filedialog.askopenfilenames(title="Select images to add")
		if not files:
			return
		dest_dir = os.path.join(self.dataset_dir, sel)
		try:
			for f in files:
				
				fname = os.path.basename(f)
				target = os.path.join(dest_dir, fname)
				if os.path.exists(target):
					base, ext = os.path.splitext(fname)
					i = 1
					while os.path.exists(os.path.join(dest_dir, f"{base}_{i}{ext}")):
						i += 1
					target = os.path.join(dest_dir, f"{base}_{i}{ext}")
				shutil.copy2(f, target)
			self.refresh()
			messagebox.showinfo("Added", f"{len(files)} file(s) copied to '{sel}'")
		except Exception as e:
			messagebox.showerror("Error", f"Could not add images: {e}")

	def open_folder(self):
		sel = self._get_selected()
		if not sel:
			
			path = self.dataset_dir
		else:
			path = os.path.join(self.dataset_dir, sel)
		if not os.path.exists(path):
			messagebox.showerror("Not found", "Folder does not exist")
			return
		try:
			
			if hasattr(os, 'startfile'):
				os.startfile(path)
			else:
				messagebox.showinfo("Path", path)
		except Exception as e:
			messagebox.showerror("Error", f"Could not open folder: {e}")

	def start_attendance_ui(self):
		
		if start_attendance is None:
			messagebox.showerror("Unavailable", "Attendance module not available (import failed). See console for errors.")
			return
		if self.attendance_thread and self.attendance_thread.is_alive():
			messagebox.showinfo("Running", "Attendance is already running")
			return
		self.attendance_stop_event = threading.Event()
		self.attendance_thread = threading.Thread(target=start_attendance, args=(self.attendance_stop_event,), daemon=True)
		self.attendance_thread.start()
		self.start_att_btn.config(state=tk.DISABLED)
		self.stop_att_btn.config(state=tk.NORMAL)
		self.status_var.set("Attendance: running (camera)")

	def stop_attendance_ui(self):
		
		if not self.attendance_stop_event:
			messagebox.showinfo("Not running", "Attendance is not running")
			return
		self.attendance_stop_event.set()
		
		self.start_att_btn.config(state=tk.NORMAL)
		self.stop_att_btn.config(state=tk.DISABLED)
		self.status_var.set("Attendance: stopping...")
		messagebox.showinfo("Stopped", "Signalled attendance thread to stop. Camera window will close shortly.")


if __name__ == "__main__":
	app = CRUDUI()
	app.mainloop()
