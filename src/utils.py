from PIL import Image
import os
import clip
import streamlit as st
import json, csv


@st.cache
def load_model(device):
    return clip.load("ViT-B/32", device=device)


def load_dataset(data_path):
    if data_path == '../data/dataset_v2':
        files = []
        for d in os.listdir(data_path):
            for file in os.listdir(os.path.join(data_path, d)):
                files.append(os.path.join(data_path, d, file))
    else:
        files = [os.path.join(data_path, file) for file in os.listdir(data_path)]

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


def remove_duplicate(selected_image_path):
    return_list = []
    name_list = set()
    for img_path in selected_image_path:
        if len(return_list) == 8:
            break

        food_name = (img_path.split('/')[-1]).split('.')[0]
        if not food_name[:-1] in name_list:
            name_list.add(food_name[:-1])
            return_list.append(img_path)
    return return_list


def load_food_properties(data_dir):
    with open(os.path.join(data_dir, 'food_properties.json'), 'r') as json_file:
        food_properties = json.load(json_file)
    return food_properties


def load_to_english(data_dir):
    with open(os.path.join(data_dir, 'to_english.json'), 'r') as json_file:
        to_english = json.load(json_file)
    return to_english


def load_country_data_path(data_dir):
    with open(os.path.join(data_dir, 'country_data_path.json'), 'r') as json_file:
        country_data_path = json.load(json_file)
    return country_data_path


def load_food_trans(data_dir):
    with open(os.path.join(data_dir, 'food_trans.csv'), mode='r') as inp:
        reader = csv.reader(inp)
        trans = {rows[0]: rows[1] for rows in reader}
    return trans


def load_query_list(data_dir):
    with open(os.path.join(data_dir, 'query_list.json'), 'r') as json_file:
        query_list = json.load(json_file)
    return query_list