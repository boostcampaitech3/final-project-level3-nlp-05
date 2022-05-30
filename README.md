# Final-project

## Repository 구조
-  해당 레포지토리는 서버 기준으로 `opt/ml/final_project` 폴더의 세부 구조입니다. 

```
├── README.md
├── .gitignore
└── data
│   ├── dataset_v1
│   │   ├── american
│   │   ├── asian
│   │   ├── chinese
│   │   ├── ...
│   │   └── mexican
│   ├── food_properties.json
│   └── food_trans.csv
└── src
    ├── app.py
    ├── main.py
    └── utils.py
```

<br />

## How to run

### Streamlit 
`streamlit run app.py --server.port=30002`

### fastapi
`python3 main.py`
