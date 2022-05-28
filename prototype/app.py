import streamlit as st
import random
from PIL import Image
import os
import torch
import clip
import csv
from utils import load_model, load_dataset


def main():
    st.title("오늘 뭐먹지?")

    col1, col2, col3 = st.columns(3)
    with col1:
        country_options = st.radio(
            '어떤 국가의 음식을 먹고 싶으신가요?',('잘 모르겠어요.', '한식', '중식', '일식', '미국식', '이탈리안', '아시안', '멕시칸')
        )
    with col2:
        descriptions = st.radio(
            '먹고 싶은 음식을 묘사하는 단어를 골라주세요.', ('잘 모르겠어요.', '매운', '안매운', '달콤한', '바삭한', '간편한', '부드러운', '따뜻한', '차가운','상큼한')
        )
    with col3:
        category_options = st.radio(
            '어떤 종류의 음식을 먹고 싶으신가요?', ('잘 모르겠어요.','디저트', '면', '밥', '고기', '샐러드', '빵(밀가루 음식)', '해산물', '국/탕/찌개/찜')
        )

    to_english = {'한식':'Korean', '중식':'Chinese', '멕시칸':'Mexican', '일식':'Japanese', '미국식':'American', '이탈리안':'Italian', '아시안':'Asian', '잘 모르겠어요.':None,
               '매운':'spicy', '안매운':'mild', '달콤한':'sweet', '바삭한':'crispy', '간편한':'convenient', '부드러운':'tender', '따뜻한':'warm', '차가운':'chilled',
               '디저트':'dessert', '면':'noodle', '밥':'rice', '고기':'meat', '샐러드':'salad', '빵(밀가루 음식)':'flour-based', '해산물':'seafood', '국/탕/찌개/찜':'stew'}
    country_data_path = {'한식':'./data/dataset_v1/korean', '중식':'./data/dataset_v1/chinese', '멕시칸':'./data/dataset_v1/mexican',
                         '일식':'./data/dataset_v1/japanese', '미국식':'./data/dataset_v1/american', '이탈리안':'./data/dataset_v1/italian', '아시안':'./data/dataset_v1/asian'}

    # if country_options and descriptions and category_options:
    if st.button("추천해주세요"):
        st.write(f'선택하신 조건에 맞는 음식을 몇 가지 보여드릴게요.')

        if not to_english[country_options] and not to_english[descriptions] and not to_english[category_options]:
            # TODO: 모두 잘 모르겠어요를 선택한 사람에게는 랜덤으로 음식 골라서 보여주기
            # image_path list에 랜덤으로 이미지 경로 9개를 담아주세요.
            pass

        else:
            with st.spinner("Loading Model and Calculating..."):
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model, preprocess = load_model(device)

                if to_english[country_options]:
                    path_to_dir = country_data_path[country_options]
                else:
                    path_to_dir = './data/dataset_v1'

                images, data_paths = load_dataset(path_to_dir)

                image_labels = torch.cat([preprocess(image).unsqueeze(0) for image in images]).to(device)
                text_input = clip.tokenize(f'a picture of {to_english[descriptions]} {to_english[category_options]} dish').to(device)

                with torch.no_grad():
                    image_features = model.encode_image(image_labels)
                    text_features = model.encode_text(text_input)

                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    text_features /= text_features.norm(dim=-1, keepdim=True)
                    similarity = (100.0 * text_features @ image_features.T).softmax(dim=-1)
                    values, indices = similarity[0].topk(9)

                    image_path = [data_paths[i] for i in indices]

        images = []
        caption = []

        trans = {}
        with open('./data/dataset_v1/food_trans.csv', mode='r') as inp:
            reader = csv.reader(inp)
            trans = {rows[0]:rows[1] for rows in reader}
        
        for idx, image in enumerate(image_path):
            img = Image.open(image)
            img = img.resize((225, 225))
            if idx % 3 == 0:
                images.append([])
                caption.append([])
            images[-1].append(img)
            food_name_eng = image.split('/')[4].split('.')[0]
            try:
                caption[-1].append(trans[food_name_eng[:-1]])
            except KeyError:
                caption[-1].append(food_name_eng[:-1])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.image(images[0], width=150, caption=caption[0])
        with col2:
            st.image(images[1], width=150, caption=caption[1])
        with col3:
            st.image(images[2], width=150, caption=caption[2])

if __name__ == "__main__":
    main()