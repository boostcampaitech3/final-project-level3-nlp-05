import streamlit as st
import os, json
import requests


def first_page():
    st.title('어떤 지역의 음식을 먹고 싶으신가요?')
    country_option = st.radio(
        '어떤 지역의 음식을 먹고 싶으신가요?', ('아무거나', '한식', '동양', '서양')
    )
    st.session_state['country_option'] = country_option

    _, _, col3, col4 = st.columns(4)
    with col4:
        st.button('다음', on_click=change_page, args=(1, ))


def second_page():
    st.title('second_page')
    # prepare
    food_properties = st.session_state['food_properties']

    # user_choice_list
    country_option = st.session_state['country_option']

    if country_option in ['한식', '동양']:
        category_option = st.radio(
            '어떤 종류의 음식을 먹고 싶으신가요?', food_properties["한식/동양"].keys()
        )
    else:
        category_option = st.radio(
            '어떤 종류의 음식을 먹고 싶으신가요?', food_properties[country_option].keys()
        )
    st.session_state['category_option'] = category_option

    col1, _, _, col4 = st.columns(4)
    with col1:
        st.button('이전', on_click=change_page, args=(-1, ))
    with col4:
        st.button('다음', on_click=change_page, args=(1, ))

    # _, col2, col3, _ = st.columns(4)
    # with col2:
    #     st.button('이전2', on_click=change_page, args=(-1, ))
    # with col3:
    #     st.button('다음2', on_click=change_page, args=(1, ))


def third_page():
    st.title('third_page')
    # st.json(st.session_state)

    # user_choice_list
    food_properties = st.session_state['food_properties']
    country_option = st.session_state['country_option']
    category_option = st.session_state['category_option']

    if country_option in ['한식', '동양']:
        description = st.radio(
            '먹고 싶은 음식을 묘사하는 단어를 골라주세요.', food_properties["한식/동양"][category_option]
        )
    else:
        description = st.radio(
            '먹고 싶은 음식을 묘사하는 단어를 골라주세요.', food_properties[country_option][category_option]
        )
    st.session_state['description'] = description

    col1, _, _, col4 = st.columns(4)
    with col1:
        st.button('이전', on_click=change_page, args=(-1,))
    with col4:
        st.button('추천받기', on_click=change_page, args=(1,))


def fourth_page():
    st.title('외않되조가 추천하는 식사 메뉴!')

    with st.spinner("Loading Data and Model..."):
        get_recommend_food_image_list()
        st.write(st.session_state['selected_image_path'])

    _, col2, _ = st.columns(3)
    with col2:
        st.button('다음 페이지', on_click=None)

    _, col2, _ = st.columns(3)
    with col2:
        st.button('처음으로', on_click=reset_page)


def change_page(move):
    st.session_state['page_control'] += move


def reset_page():
    del st.session_state['page_control']
    del st.session_state['country_option']
    del st.session_state['category_option']


def load_food_properties(data_dir):
    with open(os.path.join(data_dir, 'food_properties.json'), 'r') as json_file:
        food_properties = json.load(json_file)
    return food_properties


def load_to_english(data_dir):
    with open(os.path.join(data_dir, 'to_english.json'), 'r') as json_file:
        to_english = json.load(json_file)
    return to_english


def get_recommend_food_image_list():
    to_english = st.session_state['to_english']

    country_option = st.session_state['country_option']
    category_option = st.session_state['category_option']
    description = st.session_state['description']
    country_option, category_option, description = to_english[country_option], to_english[category_option], to_english[
        description]

    if country_option:
        path_to_dir = os.path.join(DATA_DIR, country_data_path[country_option])
    else:
        path_to_dir = os.path.join(DATA_DIR, 'dataset_v1')

    input_text = f'a picture of {description} {category_option} dish'
    input_dict = [
        ('user_input', input_text),  # user_input = 'A picture of spicy meat dis'
        ('path_to_dir', path_to_dir)  # path_to_dir = 'opt/ml/fianl_project/data/dataset_v1/korean'
    ]

    from urllib import parse
    queries = parse.urlencode(input_dict)
    request_url = "http://localhost:30003/order?" + queries
    response = requests.get(request_url)
    selected_image_path = response.json()
    st.session_state['selected_image_path'] = selected_image_path


if __name__ == "__main__":
    DATA_DIR = '../data'
    country_data_path = {'korean': 'dataset_v2/korean', 'eastern': 'dataset_v2/eastern',
                         'western': 'dataset_v2/western'}

    st.session_state['food_properties'] = load_food_properties(DATA_DIR)
    st.session_state['to_english'] = load_to_english(DATA_DIR)

    if 'page_control' in st.session_state:
        st.write(st.session_state['page_control'])
        if st.session_state['page_control'] == 1:
            first_page()

        elif st.session_state['page_control'] == 2:
            st.write(st.session_state['country_option'])
            second_page()

        elif st.session_state['page_control'] == 3:
            st.write(st.session_state['country_option'], st.session_state['category_option'])
            third_page()

        else:
            st.write(st.session_state['country_option'], st.session_state['category_option'], st.session_state['description'])
            fourth_page()

    else:
        st.session_state['page_control'] = 1
        first_page()
