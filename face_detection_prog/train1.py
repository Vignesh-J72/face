from deepface import DeepFace
import os
def start_train():
    base_directory=os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_directory, "dataset")
    DeepFace.build_model("ArcFace")
    DeepFace.find(img_path=os.path.join(dataset_path, "teja/1.jpg"), db_path=dataset_path, model_name="ArcFace")
    DeepFace.find(img_path=os.path.join(dataset_path, "vasanth/v1.jpg"), db_path=dataset_path, model_name="ArcFace")
    DeepFace.find(img_path=os.path.join(dataset_path, "vikash/a1.jpg"), db_path=dataset_path, model_name="ArcFace")

if __name__=='__main__':
   start_train()