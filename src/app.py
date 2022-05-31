import streamlit as st
import random
from PIL import Image
import os
import torch
import clip
import csv
from utils import load_model, load_dataset
import json


def main():
    st.title("오늘 뭐먹지?")
    data_dir = '../data'

    country_option = st.selectbox(
        '어떤 지역의 음식을 먹고 싶으신가요?', ('잘 모르겠어요.', '한식', '동양', '서양')
    )

    with open(os.path.join(data_dir, 'food_properties.json'), 'r') as json_file:
        food_properties = json.load(json_file)

    col1, col2 = st.columns(2)
    with col1:
        if country_option in ['한식', '동양']:
            category_option = st.selectbox(
                '어떤 종류의 음식을 먹고 싶으신가요?', food_properties["한식/동양"].keys()
            )
        else:
            category_option = st.selectbox(
                '어떤 종류의 음식을 먹고 싶으신가요?', food_properties[country_option].keys()
            )
    with col2:
        if country_option in ['한식', '동양']:
            description = st.selectbox(
                '먹고 싶은 음식을 묘사하는 단어를 골라주세요.', food_properties["한식/동양"][category_option]
            )
        else:
            description = st.selectbox(
                '먹고 싶은 음식을 묘사하는 단어를 골라주세요.', food_properties[country_option][category_option]
            )

    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked=False

    def callback():
        st.session_state.button_clicked=True

    recommend_button = st.button(label='음식 추천해줘!', on_click=callback)

    if recommend_button or st.session_state.button_clicked:
        with open(os.path.join(data_dir, 'to_english.json'), 'r') as json_file:
            to_english = json.load(json_file)
        country_option, category_option, description = to_english[country_option], to_english[category_option], to_english[description]

        country_data_path = {'korean': 'dataset_v2/korean', 'eastern': 'dataset_v2/eastern', 'western': 'dataset_v2/western'}

        st.write('선택하신 조건에 맞는 음식을 몇 가지 보여드릴게요.')
        with st.spinner("Loading Data and Model..."):
            if country_option:
                path_to_dir = os.path.join(data_dir, country_data_path[country_option])
            else:
                path_to_dir = os.path.join(data_dir, 'dataset_v2')
            images, data_paths = load_dataset(path_to_dir)

            if not country_option and not description and not category_option:
                selected_image_path = random.sample(data_paths, 36)
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model, preprocess = load_model(device)
                image_labels = torch.cat([preprocess(image).unsqueeze(0) for image in images]).to(device)
                text_input = clip.tokenize(f'a picture of {description} {category_option} dish').to(device) # TODO: 텍스트 쿼리 description 여러 개 실험해보기

                with torch.no_grad():
                    image_features = model.encode_image(image_labels)
                    text_features = model.encode_text(text_input)

                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    text_features /= text_features.norm(dim=-1, keepdim=True)
                    similarity = (100.0 * text_features @ image_features.T).softmax(dim=-1)
                    values, indices = similarity[0].topk(36)

                    selected_image_path = [data_paths[i] for i in indices]

        with open(os.path.join(data_dir, 'food_trans.csv'), mode='r') as inp:
            reader = csv.reader(inp)
            trans = {rows[0]:rows[1] for rows in reader}

        imgs = [[]]
        captions = [[]]
        items = []
        i = 0
        for image in selected_image_path:
            if i % 3 == 0 and imgs[-1]:
                imgs.append([])
                captions.append([])

            food_name_eng = image.split('/')[4].split('.')[0]

            if trans[food_name_eng[:-1]] not in items:
                captions[-1].append(trans[food_name_eng[:-1]])
                items.append(trans[food_name_eng[:-1]])
                img = Image.open(image)
                img = img.resize((300, 300))
                imgs[-1].append(img)
                i += 1

        col1, col2, col3 = st.columns(3)
        with col1:
            placeholder1 = st.image(imgs[0], width=200, caption=captions[0])
        with col2:
            placeholder2 = st.image(imgs[1], width=200, caption=captions[1])
        with col3:
            placeholder3 = st.image(imgs[2], width=200, caption=captions[2])

        if st.button("다른 음식 보여줘"):
            placeholder1.empty()
            placeholder2.empty()
            placeholder3.empty()

            with col1:
                try: st.image(imgs[3], width=200, caption=captions[3])
                except: pass
            with col2:
                try: st.image(imgs[4], width=200, caption=captions[4])
                except: pass
            with col3:
                try: st.image(imgs[5], width=200, caption=captions[5])
                except: pass
            st.session_state.button_clicked=False

if __name__ == "__main__":
    main()
    # TODO: fastAPI
