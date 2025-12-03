from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pymongo import MongoClient
import os

app = FastAPI()

# 讀取 Render 的環境變數
MONGODB_URI = os.environ.get("MONGODB_URI")

# 連線 MongoDB
client = MongoClient(MONGODB_URI)
db = client["testdb"]     # 你的資料庫
collection = db["items"]  # 你的 collection

# media 資料夾路徑
MEDIA_DIR = "media"

# 提供照片下載
@app.get("/download/snapshot/{filename}")
def download_snapshot(filename: str):
    path = os.path.join(MEDIA_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="image/jpeg", filename=filename)
    return {"error": "File not found"}

# 提供影片下載
@app.get("/download/vlog/{filename}")
def download_vlog(filename: str):
    path = os.path.join(MEDIA_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="video/mp4", filename=filename)
    return {"error": "File not found"}

# Dashboard 頁面
@app.get("/", response_class=HTMLResponse)
def dashboard():
    data = list(collection.find({}, {"_id": 0}))

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

    for item in data:
        timestamp = item.get("timestamp", "")
        sentiment = item.get("sentiment", "")
        gps = item.get("gps", {})
        lat = gps.get("lat", "")
        lng = gps.get("lng", "")
        snapshot = item.get("snapshot", "")
        vlog = item.get("vlog", "")
        text = item.get("text", "")

        html += f"""
        <tr>
            <td>{timestamp}</td>
            <td>{sentiment}</td>
            <td>{lat}, {lng}</td>
            <td>
                {'<img src="/download/snapshot/' + snapshot + '">' if snapshot else 'N/A'}
            </td>
            <td>
                {'<video controls src="/download/vlog/' + vlog + '"></video>' if vlog else 'N/A'}
            </td>
            <td>{text}</td>
            <td>
                {'<a class="button" href="/download/snapshot/' + snapshot + '">Snapshot</a><br><br>' if snapshot else ''}
                {'<a class="button" href="/download/vlog/' + vlog + '">Vlog</a>' if vlog else ''}
            </td>
        </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return HTMLResponse(content=html)
