from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import os

app = FastAPI()

# 讀取 Render 的環境變數
MONGODB_URI = os.environ.get("MONGODB_URI")

# 連線 MongoDB
client = MongoClient(MONGODB_URI)
db = client["testdb"]  # 可以改成你自己的 DB 名
collection = db["items"]  # 可以改成你自己的 collection

@app.get("/")
def export_data():
    data = list(collection.find({}, {"_id": 0})) 
    return JSONResponse(content=data)

