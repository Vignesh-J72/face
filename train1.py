from deepface import DeepFace
DeepFace.build_model("ArcFace")
DeepFace.find(img_path="dataset/teja/1.jpg", db_path="dataset/",model_name="ArcFace")
DeepFace.find(img_path='dataset/vasanth/v1.jpg', db_path='dataset/', model_name='ArcFace')