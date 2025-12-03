from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pymongo import MongoClient
import os
import csv
from io import StringIO

app = FastAPI()

# 讀取 Render 的環境變數
MONGODB_URI = os.environ.get("MONGODB_URI")

# 連線 MongoDB
client = MongoClient(MONGODB_URI)
db = client["testdb"]     # 你的資料庫
collection = db["items"]  # 你的 collection

MEDIA_FOLDER = "media"  # media 資料夾位置

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
        <a class="button" href="/download/csv">Download CSV</a><br><br>
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
            <td>{'<img src="/media/' + snapshot + '">' if snapshot else 'N/A'}</td>
            <td>{'<video controls src="/media/' + vlog + '"></video>' if vlog else 'N/A'}</td>
            <td>{text}</td>
            <td>
                {f'<a class="button" href="/download/snapshot/{snapshot}">Snapshot</a><br><br>' if snapshot else ''}
                {f'<a class="button" href="/download/vlog/{vlog}">Vlog</a>' if vlog else ''}
            </td>
        </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# 單筆檔案下載
@app.get("/download/snapshot/{filename}")
def download_snapshot(filename: str):
    path = os.path.join(MEDIA_FOLDER, filename)
    return FileResponse(path, media_type='image/jpeg', filename=filename)

@app.get("/download/vlog/{filename}")
def download_vlog(filename: str):
    path = os.path.join(MEDIA_FOLDER, filename)
    return FileResponse(path, media_type='video/mp4', filename=filename)

# 下載整份文字資料 CSV
@app.get("/download/csv")
def download_csv():
    data = list(collection.find({}, {"_id": 0}))
    si = StringIO()
    writer = csv.writer(si)
    # CSV 標題
    writer.writerow(["timestamp", "sentiment", "lat", "lng", "snapshot", "vlog", "text"])
    for item in data:
        gps = item.get("gps", {})
        writer.writerow([
            item.get("timestamp", ""),
            item.get("sentiment", ""),
            gps.get("lat", ""),
            gps.get("lng", ""),
            item.get("snapshot", ""),
            item.get("vlog", ""),
            item.get("text", "")
        ])
    si.seek(0)
    return FileResponse(
        path_or_file=StringIO(si.getvalue()),
        media_type='text/csv',
        filename="emogo_data.csv"
    )

# 提供 media 資料夾檔案給前端
from fastapi.staticfiles import StaticFiles
app.mount("/media", StaticFiles(directory=MEDIA_FOLDER), name="media")
