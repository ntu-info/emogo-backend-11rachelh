from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import os

app = FastAPI()

# 讀取 Render 的環境變數
MONGODB_URI = os.environ.get("MONGODB_URI")

# 連線 MongoDB
client = MongoClient(MONGODB_URI)
db = client["emogo"]  # 可以改成你自己的 DB 名
collection = db["records"]  # 可以改成你自己的 collection

@app.get("/")
def home():
    return {"message": "EmoGo backend is running"}

@app.get("/export")
def export_data():
    data = list(collection.find({}, {"_id": 0}))  # _id 不要給助教看
    return JSONResponse(content=data)
