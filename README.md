# 오늘 뭐 먹지? 🍚
Naver Boostcamp AI tech 3rd final project

---

# 1. Who are we?
## Team 외않되조?
👉 팀 한줄 설명!
### 👥 Members
강나경|김산|김현지|정민지|최지연
:-:|:-:|:-:|:-:|:-:
<img src='https://avatars.githubusercontent.com/u/59854630?v=4' height=80 width=80px></img>|<img src='https://avatars.githubusercontent.com/u/80572018?v=4' height=80 width=80px></img>|<img src='https://avatars.githubusercontent.com/u/15031359?v=4' height=80 width=80px></img>|<img src='https://avatars.githubusercontent.com/u/82785580?v=4' height=80 width=80px></img>|<img src='https://avatars.githubusercontent.com/u/97504669?v=4' height=80 width=80px></img>  
[Github](https://github.com/angieKang)|[Github](https://github.com/mounKim)|[Github](https://github.com/TB2715)|[Github](https://github.com/minji2744)|[Github](https://github.com/jeeyeon51)

# 2. Introduction
## 프로젝트 개요
- 개발 배경
  -   2019년에는 약 32%의 사용자가 “중식”과 같은 상위 메뉴를 주문하였으나, 2020년에는 상위 메뉴를 주문하는 경우가 27.4%로 줄어들어 단순히 “중식”을 검색하기 보다, “짜장면”, “마라탕”과 같이 구체적인 메뉴를 주문하는 경향이 늘어난 것을 확인 (배민트렌드 2021 25쪽 배달 앱 내 소비자의 다양한 메뉴 주문 경향)
  -   이러한 사용자 패턴을 기반으로 소비자들이 “다양한 메뉴 추천을 잘 하는 서비스”를 필요로 하지 않을까라고 생각하여 “나의 취향에 맞는 다양한 음식 메뉴를 추천하는 서비스”를 제안

- 주요 기능
  - 사용자가 입력/선택한 query를 만족하는 음식 메뉴를 제안 
  - Input: 사용자 입력 문장 또는 선택 단어 
    - `e.g. 바삭바삭하고 매콤한 음식 먹고 싶어`
    - `e.g. "바삭한", "매콤한"`
  - Output: 요구조건을 만족하는 음식 메뉴  
    - `e.g. 김치전`

## Data
- 이미지 데이터 총 221종
  - [kaggle/food101](https://www.kaggle.com/datasets/dansbecker/food-101)
  - [AI Hub/한국 이미지(음식) 소개](https://aihub.or.kr/aidata/13594)
  - 웹 크롤링 

## Model
![model structure](https://user-images.githubusercontent.com/59854630/172411812-9ee15f3c-e8ae-409c-96f2-3b7662964c85.png)
- [CLIP](https://openai.com/blog/clip/)을 활용한 text-image retrieval  
- Query expansion
  - WordNet  

# 3. Demo
![Hnet-image (1)](https://user-images.githubusercontent.com/59854630/172417493-b3f2733e-bb26-4c56-9afd-d436a8ed048b.gif)

# 4. Equipment & Software
- [OS] Linux version 4.4.0-59-generic
- [CPU / GPU] Intel(R) Xeon(R) Gold 5220 CPU @ 2.20GHz / Tesla V100-SXM2-32GB 
- [Collaboration Tool] Git-hub / Slack / Notion 
- [IDE] VSCode / PyCharm / Jupyter lab

# 5. Getting Started

## Code structure
```
├── README.md
├── .gitignore
└── data
│   ├── dataset_v2
│   │   ├── eastern
│   │   ├── korean
│   │   └── western
│   ├── contry_data_path.json
│   ├── food_properties.json
│   ├── food_trans.csv
│   ├── query_list.json
│   └── to_english.json
└── src
    ├── _app.py
    ├── main.py
    └── utils.py
```
## How to run
### fastapi
`python3 main.py`

### Streamlit 
`streamlit run _app.py --server.port=30002`
