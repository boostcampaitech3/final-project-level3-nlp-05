import streamlit as st
import os, json
import requests
import random
from PIL import Image
from utils import load_dataset, load_to_english, load_to_english, load_food_properties, load_country_data_path, \
    load_food_trans, remove_duplicate
from urllib import parse


def first_page():
    st.title('Step 1. 어떤 지역의 음식을 먹고 싶으신가요?')
    country_option = st.radio(
        '', ('아무거나', '한식', '아시안, 일식, 중식', '양식')
    )
    st.session_state['country_option'] = country_option

    # prev, next button
    _, _, col3, col4 = st.columns(4)
    with col4:
        st.button('다음', on_click=change_page, args=(1, ))


def second_page():
    st.title('Step 2. 어떤 종류의 음식을 먹고 싶으신가요?')
    # prepare
    food_properties = st.session_state['food_properties']

    # user_choice_list
    country_option = st.session_state['country_option']

    # viewer
    if country_option != '양식':
        category_option = st.radio(
            '', food_properties['한식/동양'].keys()  # TODO: HARD FIX
        )
    else:
        category_option = st.radio(
            '', food_properties[country_option].keys()
        )
    st.session_state['category_option'] = category_option

    # prev, next button
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
    st.title('Step 3. 먹고 싶은 음식을 묘사하는 단어를 골라주세요.')
    # st.json(st.session_state)

    # user_choice_list
    food_properties = st.session_state['food_properties']
    country_option = st.session_state['country_option']
    category_option = st.session_state['category_option']

    if country_option != '양식':
        description = st.radio(
            '', food_properties["한식/동양"][category_option]
        )
    else:
        description = st.radio(
            '', food_properties[country_option][category_option]
        )
    st.session_state['description'] = description

    # prev, next button
    col1, _, _, col4 = st.columns(4)
    with col1:
        st.button('이전', on_click=change_page, args=(-1,))
    with col4:
        st.button('추천받기', on_click=change_page, args=(1,))


def fourth_page():
    st.title('외않되조가 추천하는 식사 메뉴!')
    next = False
    prev = False

    # Viewer start
    selected_image_path = st.session_state['selected_image_path']
    trans = st.session_state['food_trans']

    # st.write(selected_image_path)

    image_dict = []
    # recommend_page = 0
    # if st.session_state['recommend_page'] < 0:
    #     recommend_page = 0
    # elif st.session_state['recommend_page'] > 2:
    #     recommend_page = 2
    # else:
    recommend_page = st.session_state['recommend_page']

    start_idx = 0 + 4*recommend_page
    end_idx = 4 + 4*recommend_page

    for img_path in selected_image_path[start_idx : end_idx]:
        food_name_eng = img_path.split('/')[-1].split('.')[0]
        img = Image.open(img_path)
        img = img.resize((300, 300))

        image_dict.append({
            'img': img,
            'caption': trans[food_name_eng[:-1]]
        })

    col1, col2 = st.columns(2)
    # random.shuffle(image_dict)
    # st.write(image_dict)

    start = 0
    with col1:
        placeholder1 = st.image(image_dict[start]['img'], width=300, caption=image_dict[start]['caption'])
        placeholder3 = st.image(image_dict[start+2]['img'], width=300, caption=image_dict[start+2]['caption'])
    with col2:
        placeholder2 = st.image(image_dict[start+1]['img'], width=300, caption=image_dict[start+1]['caption'])
        placeholder4 = st.image(image_dict[start + 3]['img'], width=300, caption=image_dict[start+3]['caption'])

    # prev, next button
    _, col2, col3, _ = st.columns(4)
    with col2:
        if st.session_state['recommend_page'] != 0:
            st.button('◀ 이전', on_click=move_recommend_page, args=(-1,))
    with col3:
        if st.session_state['recommend_page'] != 2 and not next:
            st.button('다음 ▶', on_click=move_recommend_page, args=(1,))

    col1, _, _, col4 = st.columns(4)
    with col1:
        st.button('처음으로', on_click=reset_page)
    with col4: 
        st.button('설문조사', on_click=change_page, args=(1,))


def user_feedback_scene():
    # 점수
    st.title('🤔 서비스 만족도 조사입니다.')
    score = st.slider('(필수) 추천 받은 음식에 대해 얼마나 만족하시나요? (0~5)', 0, 5, 3)
    st. write(score,"점을 주셨습니다!")

    # 이유/개선사항
    reason = st.text_input('위의 점수를 주신 이유가 무엇인가요? 개선이 필요한 사항이나 에러가 있었다면 알려주세요!', '')
    if reason != '':
        st.write("의견 감사드립니다.🥰")
    else: 
        st.write("작성 후 꼭 엔터를 눌러주세요!")

    # 기프티콘 추첨을 위한 전화번호 수집.
    st.write('---')
    st.write('🎁 설문에 참여해 주신 분들을 대상으로 추첨을 통해 소정의 기프티콘을 증정할 예정입니다.')
    st.write('개인정보는 기프티콘 추첨을 위해 수집합니다. 개인정보는 추첨 이후 폐기될 예정입니다. 정보가 정확하지 않을 경우 추첨에 배제될 수 있습니다.')
    email = st.text_input('이벤트 참여를 원하시는 분들은 이메일 주소를 작성해주세요.', placeholder='example@oeanhdoejo.co.kr')
    if email != '':
        st.write("설문에 참여해주셔서 감사합니다.🥰")
    else:
        st.write("이메일 작성 후 꼭 엔터를 눌러주세요!")

    # for server
    input_dict = [
        ('rate', int(score)),  # score = '5'
        ('description', reason),  # reason = '~한 부분은 에러인 것 같습니다.'
        ('email', email)  # email = 'example@oeanhdoejo.co.kr'
    ]

    st.button('이전', on_click=change_page, args=(-1,))

    _, col2, _ = st.columns(3)
    with col2:
        send_uf = st.button('제출하기', on_click=send_user_feedback, args=(input_dict,))


def thanks_scene():
    st.balloons()
    st.title('제출 완료되었습니다! 감사합니다!!')

    _, col2, _ = st.columns(3)
    with col2:
        st.button('처음으로', on_click=reset_page)


def move_recommend_page(move):
    if st.session_state['recommend_page'] <= 0 and move == -1:
        return
    elif st.session_state['recommend_page'] >= 2 and move == 1:
        return
    else:
        st.session_state['recommend_page'] += move


def change_page(move):
    st.session_state['page_control'] += move

    if st.session_state['page_control'] == 4:
        get_recommend_food_image_list()


def reset_page():
    del st.session_state['page_control']
    del st.session_state['country_option']
    del st.session_state['category_option']
    del st.session_state['selected_image_path']


def send_user_feedback(user_feedback):
    # queries = parse.urlencode(user_feedback)
    request_url = f"{SERVER_IP_ADDRESS}feedback"
    response = requests.post(request_url, json=user_feedback)
    change_page(1)


def get_recommend_food_image_list():
    st.session_state['recommend_page'] = 0

    to_english = st.session_state['to_english']

    country_option = st.session_state['country_option']
    category_option = st.session_state['category_option']
    description = st.session_state['description']
    country_data_path = st.session_state['country_data_path']

    country_option, category_option, description = to_english[country_option], \
                                                   to_english[category_option], \
                                                   to_english[description]
    path_to_dir = os.path.join(DATA_DIR, country_data_path[country_option])

    if not country_option and not description and not category_option:
        images, data_paths = load_dataset(path_to_dir)
        selected_image_path = random.sample(data_paths, st.session_state['top_k'])
        selected_image_path = remove_duplicate(selected_image_path)

    else:
        path_to_dir = os.path.join(DATA_DIR, country_data_path[country_option])

        input_text = f'a picture of {description} {category_option} dish'
        input_dict = [
            ('user_input', input_text),  # user_input = 'A picture of spicy meat dis'
            ('path_to_dir', path_to_dir)  # path_to_dir = 'opt/ml/fianl_project/data/dataset_v1/korean'
        ]

        queries = parse.urlencode(input_dict)
        request_url = f"{SERVER_IP_ADDRESS}order?{queries}"
        response = requests.get(request_url)
        selected_image_path = response.json()

    random.shuffle(selected_image_path)
    # st.write(selected_image_path)  # DEBUGGING
    st.session_state['selected_image_path'] = selected_image_path


def print_current_selections(user_checklist: list):
    return st.multiselect('현재까지 선택한 사항들', user_checklist,
                           default = user_checklist,
                           disabled = True)


if __name__ == "__main__":
    DATA_DIR = '../data'
    TOP_K = 30
    SERVER_IP_ADDRESS = 'http://localhost:30003/'

    if 'is_loaded' not in st.session_state:
        st.session_state['top_k'] = TOP_K
        st.session_state['food_properties'] = load_food_properties(DATA_DIR)
        st.session_state['to_english'] = load_to_english(DATA_DIR)
        st.session_state['country_data_path'] = load_country_data_path(DATA_DIR)
        st.session_state['food_trans'] = load_food_trans(DATA_DIR)
        st.session_state['is_loaded'] = True

    if 'page_control' in st.session_state:
        # st.write(st.session_state['page_control'])
        if st.session_state['page_control'] == 1:
            first_page()

        elif st.session_state['page_control'] == 2:
            # st.write(st.session_state['country_option'])
            print_current_selections([st.session_state['country_option']])
            second_page()

        elif st.session_state['page_control'] == 3:
            # st.write(st.session_state['country_option'], st.session_state['category_option'])
            print_current_selections([st.session_state['country_option'], st.session_state['category_option']])
            third_page()

        elif st.session_state['page_control'] == 4: 
            # st.write(st.session_state['country_option'], st.session_state['category_option'], st.session_state['description'])
            print_current_selections([st.session_state['country_option'], st.session_state['category_option'], st.session_state['description']])
            fourth_page()

        elif st.session_state['page_control'] == 5:
            user_feedback_scene()

        else:
            thanks_scene()


    else:
        st.session_state['page_control'] = 1
        first_page()
