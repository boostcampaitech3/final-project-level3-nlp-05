import streamlit as st
import random
from PIL import Image
import os
import torch
import clip
import csv
from utils import load_model, load_dataset
import json
import re


def main():
    st.title("오늘 뭐먹지?")
    data_dir = '../data'
    with open(os.path.join(data_dir, 'food_properties.json'), 'r') as json_file:
        food_properties = json.load(json_file)

    if "next_button_clicked" not in st.session_state:
        st.session_state.next_button_clicked=False
        st.session_state.count = 0
    if "recommend_button_clicked" not in st.session_state:
        st.session_state.recommend_button_clicked=False

    def next_button_callback():
        st.session_state.next_button_clicked=True
        st.session_state.count += 1
    def recommend_button_callback():
        st.session_state.recommend_button_clicked=True

    placeholder = st.empty()
    with placeholder.container():
        country_option = st.radio(
            '추천받고 싶은 옵션을 선택해주세요.', ('아무거나', '한식', '아시안, 일식, 중식', '양식')
        )
        next_button = st.button(label="다음", on_click=next_button_callback, key='next')

    if next_button or st.session_state.next_button_clicked:
        if country_option == '양식':
            country = "양식"
        else:
            country = "한식/동양"

        placeholder.empty()

        with placeholder.container():
            category_option = st.radio(
                '추천받고 싶은 옵션을 선택해주세요.', food_properties[country].keys()
            )

        if st.session_state.count == 2:
            placeholder.empty()

            placeholder = st.empty()
            description = placeholder.radio(
                '추천받고 싶은 옵션을 선택해주세요.', food_properties[country][category_option]
            )

            place_recommend = st.empty()
            recommend_button = place_recommend.button(label='음식 추천해줘!', on_click=recommend_button_callback)

            if recommend_button or st.session_state.recommend_button_clicked:
                placeholder.empty()
                place_recommend.empty()

                place1 = st.empty()
                place1.write('잠시 후에 선택하신 조건에 맞는 음식을 몇 가지 보여드릴게요.')

                with st.sidebar:
                    st.write(f"1) {country_option}")
                    st.write(f"2) {category_option}")
                    st.write(f"3) {description}")

                with open(os.path.join(data_dir, 'to_english.json'), 'r') as json_file:
                    to_english = json.load(json_file)
                to_english['아무거나'] = ''
                country_option, category_option, description = to_english[country_option], to_english[category_option], to_english[description]

                country_data_path = {'korean': 'dataset_v2/korean', 'eastern': 'dataset_v2/eastern', 'western': 'dataset_v2/western'}

                if country_option:
                    path_to_dir = os.path.join(data_dir, country_data_path[country_option])
                else:
                    path_to_dir = os.path.join(data_dir, 'dataset_v2')
                images, data_paths = load_dataset(path_to_dir)

                if not country_option and not description and not category_option:
                    selected_image_path = random.sample(data_paths, 30)
                else:
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                    model, preprocess = load_model(device)
                    image_labels = torch.cat([preprocess(image).unsqueeze(0) for image in images]).to(device)

                    text = f'a picture of {description} {category_option} dish'
                    text = re.sub(r' +', ' ', text)
                    text_input = clip.tokenize(text).to(device)
                    # text_input = clip.tokenize("").to(device) # 테스트 용 쿼리 (윗 줄을 주석처리 하고 사용해주세요)

                    with torch.no_grad():
                        image_features = model.encode_image(image_labels)
                        text_features = model.encode_text(text_input)

                        image_features /= image_features.norm(dim=-1, keepdim=True)
                        text_features /= text_features.norm(dim=-1, keepdim=True)
                        similarity = (100.0 * text_features @ image_features.T).softmax(dim=-1)
                        values, indices = similarity[0].topk(30)

                        selected_image_path = [data_paths[i] for i in indices]

                with open(os.path.join(data_dir, 'food_trans.csv'), mode='r') as inp:
                    reader = csv.reader(inp)
                    trans = {rows[0]:rows[1] for rows in reader}

                imgs = [[]]
                captions = [[]]
                items = []
                i = 0
                for image in selected_image_path:
                    if i % 2 == 0 and imgs[-1]:
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

                if len(imgs[-1]) < 2:
                    del imgs[-1]

                col1, col2 = st.columns(2)
                i = list(range(len(imgs)))
                random.shuffle(i)
                start = 0
                with col1:
                    placeholder1 = st.image(imgs[i[start]], width=300, caption=captions[i[start]])
                with col2:
                    placeholder2 = st.image(imgs[i[start+1]], width=300, caption=captions[i[start+1]])

                if "refresh_count" not in st.session_state:
                    st.session_state.refresh_count = 0
                def callback():
                    st.session_state.refresh_count += 1

                place2 = st.empty()
                place3 = st.empty()
                refresh = place2.button(label="다른 음식 보여줘!", on_click=callback)
                end = place3.button(label="종료")

                if refresh:
                    start += 2
                    placeholder1.empty()
                    placeholder2.empty()

                    with col1:
                        st.image(imgs[i[start]], width=300, caption=captions[i[start]])
                    with col2:
                        st.image(imgs[i[start+1]], width=300, caption=captions[i[start+1]])

                    if st.session_state.refresh_count == 2:
                        place2.empty()
                        st.session_state.recommend_button_clicked = False
                        st.session_state.next_button_clicked = False
                        st.session_state.count = 0
                        st.session_state.refresh_count = 0

                if end:
                    placeholder1.empty()
                    placeholder2.empty()
                    place1.empty()
                    place2.empty()
                    place3.empty()
                    st.session_state.recommend_button_clicked = False
                    st.session_state.next_button_clicked = False
                    st.session_state.count = 0
                    st.session_state.refresh_count = 0

if __name__ == "__main__":
    main()
