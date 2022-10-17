from base64 import encodebytes
from PIL import Image
import os, io

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def getImage(image_path):
    img_path = os.path.join(PROJECT_ROOT, image_path) 
    pil_img = Image.open(img_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img