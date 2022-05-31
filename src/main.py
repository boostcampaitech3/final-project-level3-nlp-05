from fastapi import FastAPI, UploadFile, File
# from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
# from uuid import UUID, uuid4
from typing import List, Union, Optional, Dict, Any

from datetime import datetime
import clip

import uvicorn
import torch

from utils import load_dataset, load_model

app = FastAPI()

orders = []
DATA_DIR = '/opt/ml/final_project/data'  # 경로 설정


# class Order(BaseModel):
#     id: UUID = Field(default_factory=uuid4)
#     products: List[Product] = Field(default_factory=list)
#     created_at: datetime = Field(default_factory=datetime.now)
#     updated_at: datetime = Field(default_factory=datetime.now)
#
#     @property
#     def bill(self):
#         return sum([product.price for product in self.products])
#
#     def add_product(self, product: Product):
#         if product.id in [existing_product.id for existing_product in self.products]:
#             return self
#
#         self.products.append(product)
#         self.updated_at = datetime.now()
#         return self

@app.get("/")
def hello_word():
    return {"hello": "world"}

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
        values, indices = similarity[0].topk(18)

        selected_image_path = [data_paths[i] for i in indices]
    return selected_image_path


if __name__=='__main__':
    # uvicorn.run(app, host='0.0.0.0', port=8003)
    uvicorn.run(app, host='0.0.0.0', port=30003)