import os
import io
import requests
import zipfile
import onnxruntime as ort
import numpy as np
import cv2
from tokenizer import Tokenizer

def download_zipfile(path,url):
    if os.path.exists(path):
        return
    print("downloading",url)
    response = requests.get(url)
    if response.ok:
        file_like_object = io.BytesIO(response.content)
        zipfile_object = zipfile.ZipFile(file_like_object)    
        zipfile_object.extractall(".")
    print("downloaded")
    
def download_clip():
    download_zipfile('clip_image_model_vitb32.onnx','http://www.agentspace.org/download/clip.zip')

download_clip()

tokenizer = Tokenizer('bpe_simple_vocab_16e6.txt.gz')
providers = ['CPUExecutionProvider']
image_model = ort.InferenceSession('clip_image_model_vitb32.onnx', providers=providers)
text_model = ort.InferenceSession('clip_text_model_vitb32.onnx', providers=providers)

def normalize(embeddings):
    return embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def image_clip(image,cropping = True):
    image_blob = cv2.dnn.blobFromImage(image, 1.0/255, (224,224), swapRB=True, crop=cropping)
    image_blob -= np.array([0.48145466, 0.4578275, 0.40821073]).reshape((3, 1, 1))
    image_blob /= np.array([0.26862954, 0.26130258, 0.27577711]).reshape((3, 1, 1))
    image_embedding = image_model.run(None, {"IMAGE": image_blob})[0]
    return image_embedding
    
def text_clip(texts):
    text_blobs = tokenizer.encode_text(texts)
    text_embeddings = text_model.run(None, {"TEXT": text_blobs})[0]
    return text_embeddings
    
def cosine_similarity(embedding, embeddings, factor=100):
    logits = (normalize(embedding) @ normalize(embeddings).T)[0]
    probabilities = softmax(logits*factor)
    return probabilities

def clip(image, texts_embeddings, cropping = True):
    image_embedding = image_clip(image, cropping)
    probabilities = cosine_similarity(image_embedding, text_embeddings)
    return probabilities

if __name__ == "__main__":

    texts = [
        "a mandarine", 
        "two mandarines", 
        "a man showing a mandarine", 
        "a girl showing a mandarine", 
        "a ball", 
        "two balls", 
        "a man showing a ball", 
        "a girl showing a ball", 
        "an iron",
        "a man showing an iron",
    ]
    text_embeddings = text_clip(texts)
    
    for image_name in ['mandarine.jpg','ball.jpg']:
    
        image = cv2.imread(image_name)
    
        probabilities = clip(image,texts)
        for text, probability in zip(texts, probabilities):
            print(f"{text}: {probability:.3f}")

        print()

"""
a mandarine: 0.055
two mandarines: 0.029
a man showing a mandarine: 0.898
a girl showing a mandarine: 0.010
a ball: 0.001
two balls: 0.002
a man showing a ball: 0.004
a girl showing a ball: 0.000
an iron: 0.000
a man showing an iron: 0.000
"""

"""
a mandarine: 0.001
two mandarines: 0.000
a man showing a mandarine: 0.025
a girl showing a mandarine: 0.000
a ball: 0.091
two balls: 0.023
a man showing a ball: 0.828
a girl showing a ball: 0.020
an iron: 0.001
a man showing an iron: 0.011
"""