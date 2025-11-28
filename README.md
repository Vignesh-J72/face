This is a small program that detects the face of a person using DeepFace.

USAGE:  
1.Create a folder under dataset with the name of the person to be detected.  
2.Paste the images in the folder.  
3.Run train1.py  
4.Run detect1.py to detect the faces.

Note:  
The DeepFace model is only called every 10 frames to save on computation costs. It can be changed by modifying the 'THRESHOLD_INTERVAL' variable.