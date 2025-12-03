from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
import os

app = FastAPI()

# 讀取 Render 的環境變數
MONGODB_URI = os.environ.get("MONGODB_URI")

# 連線 MongoDB
client = MongoClient(MONGODB_URI)
db = client["testdb"]     # 你的資料庫
collection = db["items"]  # 你的 collection


@app.get("/", response_class=HTMLResponse)
def dashboard():
    data = list(collection.find({}, {"_id": 0}))

    # HTML 標頭
    html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>EmoGo Dashboard</title>
        <style>
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #f2f2f2; }
            img { width: 120px; }
            video { width: 200px; }
            a.button {
                padding: 6px 12px; 
                background: #4CAF50;
                color: white;
                border-radius: 4px;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <h1>EmoGo Data Dashboard</h1>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Sentiment</th>
                <th>GPS</th>
                <th>Snapshot</th>
                <th>Vlog</th>
                <th>Text</th>
                <th>Download</th>
            </tr>
    """

    # 將每筆資料插入表格
    for item in data:
        timestamp = item.get("timestamp", "")
        sentiment = item.get("sentiment", "")
        gps = item.get("gps", {})
        lat = gps.get("lat", "")
        lng = gps.get("lng", "")
        snapshot = item.get("snapshot", "")
        vlog = item.get("vlog", "")
        text = item.get("text", "")

        # HTML 轉義 + 顯示
        html += f"""
        <tr>
            <td>{timestamp}</td>
            <td>{sentiment}</td>
            <td>{lat}, {lng}</td>
            <td>
                {'<img src="' + snapshot + '">' if snapshot else 'N/A'}
            </td>
            <td>
                {'<video controls src="' + vlog + '"></video>' if vlog else 'N/A'}
            </td>
            <td>{text}</td>
            <td>
                <a class="button" href="{snapshot}" download>Snapshot</a><br><br>
                <a class="button" href="{vlog}" download>Vlog</a>
            </td>
        </tr>
        """

    # HTML 結尾
    html += """
        </table>
    </body>
    </html>
    """

    return HTMLResponse(content=html)
