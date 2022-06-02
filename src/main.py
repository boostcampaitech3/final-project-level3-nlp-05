from fastapi import FastAPI, UploadFile, File
# from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
# from uuid import UUID, uuid4
from typing import List, Union, Optional, Dict, Any

from datetime import datetime
import clip

import uvicorn
import torch
import os
import time

from utils import load_dataset, load_model, remove_duplicate

app = FastAPI()

orders = []
DATA_DIR = '/opt/ml/final_project/data'  # 경로 설정
FEEDBACK_DIR = '../feedback'


class UserFeedback(BaseModel):
    rate: int
    description: str
    email: Optional[str] = None


@app.get("/")
def hello_word():
    return {"hello": "world"}


@app.post('/feedback', description='유저 피드백을 저장합니다')
def save_user_feedback(user_feedback: UserFeedback):
    print(user_feedback)
    try:
        if not os.path.exists(FEEDBACK_DIR):
            os.makedirs(FEEDBACK_DIR)

        with open(os.path.join(FEEDBACK_DIR, 'user_feedback.tsv'), 'a', newline='',encoding='utf-8') as wf:
            now = time.localtime()
            user_time = "%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

            wf.writelines(f'{user_time}\t{user_feedback.rate}\t{user_feedback.description}\t{user_feedback.email}\n')
    except OSError:
        print("Error: Failed to create the directory.")


@app.get("/order", description='주문을 요청합니다')
def make_order(user_input: str = 'a picture of spicy meat dish',
               path_to_dir: str = '/opt/ml/final_project/data/dataset_v1/korean'):
    return predict_from_user_input(user_input, path_to_dir)


def predict_from_user_input(user_input: str, path_to_dir: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = load_model(device)
    images, data_paths = load_dataset(path_to_dir)
    image_labels = torch.cat([preprocess(image).unsqueeze(0) for image in images]).to(device)
    text_input = clip.tokenize(user_input).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_labels)
        text_features = model.encode_text(text_input)

        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        similarity = (100.0 * text_features @ image_features.T).softmax(dim=-1)
        values, indices = similarity[0].topk(20)

        selected_image_path = [data_paths[i] for i in indices]
        return_list = remove_duplicate(selected_image_path)

    return return_list


if __name__=='__main__':
    # uvicorn.run(app, host='0.0.0.0', port=8003)
    uvicorn.run(app, host='0.0.0.0', port=30003)