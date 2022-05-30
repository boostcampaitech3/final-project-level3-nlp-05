from PIL import Image
import os
import clip
import streamlit as st


@st.cache
def load_model(device):
    return clip.load("ViT-B/32", device=device)

def load_dataset(data_path):
    if data_path == '/opt/ml/project/data/dataset_v1':
        files = []
        for d in os.listdir(data_path):
            for file in os.listdir(os.path.join(data_path, d)):
                files.append(os.path.join(data_path, d, file))
    else: files = [os.path.join(data_path, file) for file in os.listdir(data_path)]

    images = []
    data_paths = []
    with open('./error.txt', 'w') as f:
        for file in files:
            try:
                img = Image.open(file)
                images.append(img)
                data_paths.append(file)
            except:
                f.write(file)
                f.write('\n')
    f.close()

    return images, data_paths