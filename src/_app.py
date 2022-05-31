import streamlit as st
import random
from PIL import Image
import os
import csv
import requests

from utils import load_model, load_dataset


def main():
    st.title("오늘 뭐먹지?")

    col1, col2, col3 = st.columns(3)
    with col1:
        country_options = st.radio(
            '어떤 국가의 음식을 먹고 싶으신가요?', ('잘 모르겠어요.', '한식', '중식', '일식', '미국식', '이탈리안', '아시안', '멕시칸')
        )
    with col2:
        descriptions = st.radio(
            '먹고 싶은 음식을 묘사하는 단어를 골라주세요.', ('잘 모르겠어요.', '매운', '안매운', '달콤한', '바삭한', '간편한', '부드러운', '따뜻한', '차가운', '상큼한')
        )
    with col3:
        category_options = st.radio(
            '어떤 종류의 음식을 먹고 싶으신가요?', ('잘 모르겠어요.', '디저트', '면', '밥', '고기', '샐러드', '빵(밀가루 음식)', '해산물', '국/탕/찌개/찜')
        )

    to_english = {'한식': 'Korean', '중식': 'Chinese', '멕시칸': 'Mexican', '일식': 'Japanese', '미국식': 'American',
                  '이탈리안': 'Italian', '아시안': 'Asian', '잘 모르겠어요.': None,
                  '매운': 'spicy', '안매운': 'mild', '달콤한': 'sweet', '바삭한': 'crispy', '간편한': 'convenient', '부드러운': 'tender',
                  '따뜻한': 'warm', '차가운': 'chilled', '상큼한': 'fresh',
                  '디저트': 'dessert', '면': 'noodle', '밥': 'rice', '고기': 'meat', '샐러드': 'salad',
                  '빵(밀가루 음식)': 'flour-based', '해산물': 'seafood', '국/탕/찌개/찜': 'stew'}

    country_data_path = {'한식': 'dataset_v1/korean', '중식': 'dataset_v1/chinese', '멕시칸': 'dataset_v1/mexican',
                         '일식': 'dataset_v1/japanese', '미국식': 'dataset_v1/american', '이탈리안': 'dataset_v1/italian',
                         '아시안': 'dataset_v1/asian'}

    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False

    def callback():
        st.session_state.button_clicked = True

    recommend_button = st.button(label='음식 추천해줘!', on_click=callback)

    if recommend_button or st.session_state.button_clicked:
        st.write('선택하신 조건에 맞는 음식을 몇 가지 보여드릴게요.')
        with st.spinner("Loading Data and Model..."):
            data_dir = '/opt/ml/final_project/data'  # 데이터 경로를 설정해주세요.
            if to_english[country_options]:
                path_to_dir = os.path.join(data_dir, country_data_path[country_options])
            else:
                path_to_dir = os.path.join(data_dir, 'dataset_v1')

            if not to_english[country_options] and not to_english[descriptions] and not to_english[category_options]:
                # 아무거나를 선택한 경우, 랜덤으로 보여줌
                image, data_paths = load_dataset(path_to_dir)
                selected_image_path = random.sample(data_paths, 18)
            else:
                input_text = f'a picture of {to_english[descriptions]} {to_english[category_options]} dish'
                input_dict = [
                    ('user_input', input_text),  # user_input = 'A picture of spicy meat dis'
                    ('path_to_dir', path_to_dir) # path_to_dir = 'opt/ml/fianl_project/data/dataset_v1/korean'
                ]

                from urllib import parse
                queries = parse.urlencode(input_dict)
                request_url = "http://localhost:30003/order?" + queries
                response = requests.get(request_url)
                selected_image_path = response.json()

        with open(os.path.join(data_dir, 'food_trans.csv'), mode='r') as inp:
            reader = csv.reader(inp)
            trans = {rows[0]:rows[1] for rows in reader}

        imgs = []
        captions = []
        i = 0
        for image in selected_image_path:
            if i % 3 == 0:
                imgs.append([])
                captions.append([])

            img = Image.open(image)
            img = img.resize((300, 300))  # TODO: 이미지 사이즈 조정
            imgs[-1].append(img)
            i += 1

            food_name_eng = image.split('/')[7].split('.')[0]
            try:
                captions[-1].append(trans[food_name_eng[:-1]])
            except KeyError:
                captions[-1].append(food_name_eng[:-1])

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
                st.image(imgs[3], width=200, caption=captions[3])
            with col2:
                st.image(imgs[4], width=200, caption=captions[4])
            with col3:
                st.image(imgs[5], width=200, caption=captions[5])
            st.session_state.button_clicked=False
        st.session_state.button_clicked = False


if __name__ == "__main__":
    main()
    # TODO: fastAPI