import os
import sqlite3
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse

# 環境変数の読み込み
load_dotenv()

app = FastAPI()

# ==========================================
# 共通ツール：LINEに手紙を送る関数
# ==========================================
def send_line_message(notification_text):
    url = 'https://api.line.me/v2/bot/message/push'
    token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'to': os.getenv('LINE_USER_ID'),
        'messages': [{'type': 'text', 'text': notification_text}]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

# ==========================================
# ① メニュー1：お店の入り口（Web画面の提供）
# ==========================================
@app.get("/", response_class=HTMLResponse)
def read_root():
    # ユーザーがブラウザで見る「コントロールパネル」の設計図
    html_content = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>アーティスト管理システム</title>
        <style>
            body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #f0f8ff; }
            button { padding: 15px 30px; font-size: 20px; cursor: pointer; background-color: #06C755; color: white; border: none; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            button:hover { background-color: #05A546; }
        </style>
    </head>
    <body>
        <h1>🎸 新着情報コントロールパネル</h1>
        <p>下のボタンを押すと、システムがSpotifyを巡回し、新着があればLINEへ通知を飛ばします。</p>
        
        <form action="/api/check" method="post">
            <button type="submit">LINE通知チェックを実行する</button>
        </form>
    </body>
    </html>
    """
    return html_content

# ==========================================
# ② メニュー2：キッチンの裏側（チェックと通知の実行）
# ==========================================
# GETではなく「POST（実行しろ！）」という命令を受け取る
@app.post("/api/check")
def run_check():
    # 1. データベースの準備
    conn = sqlite3.connect('notifier.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS releases (id TEXT PRIMARY KEY, name TEXT, artist TEXT)''')
    conn.commit()

    # 2. Spotify APIから情報取得
    client_credentials_manager = SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    artist_id = '26ZBeXl5Gqr3TAv2itmyCU' # indigo la End
    
    try:
        results = sp.artist_albums(artist_id, album_type='album,single', limit=1)
    except Exception as e:
        conn.close()
        return {"status": "error", "message": f"Spotify通信エラー: {e}"}

    # 3. 新着判定とLINE通知
    if len(results['items']) > 0:
        latest_release = results['items'][0]
        release_id = latest_release['id']
        release_name = latest_release['name']
        release_url = latest_release['external_urls']['spotify']

        cursor.execute("SELECT id FROM releases WHERE id = ?", (release_id,))
        record = cursor.fetchone()

        if record:
            conn.close()
            # 既に通知済みの場合は、画面にJSONで結果を返す
            return {"status": "success", "message": f"【通知なし】'{release_name}' は既に確認済みです。"}
        else:
            # 新着ならLINEに通知を送る
            message_text = f"【🔥新着アラート!!】\nindigo la Endの新しいリリースを発見しました！\n\n『{release_name}』\n{release_url}"
            status_code = send_line_message(message_text)
            
            if status_code == 200:
                cursor.execute("INSERT INTO releases (id, name, artist) VALUES (?, ?, ?)", 
                               (release_id, release_name, "indigo la End"))
                conn.commit()
                conn.close()
                return {"status": "success", "message": f"【新着あり】LINEに通知を送信しました！ ({release_name})"}
            else:
                conn.close()
                return {"status": "error", "message": f"LINE通知失敗 (コード: {status_code})"}
    else:
        conn.close()
        return {"status": "success", "message": "リリース情報が見つかりませんでした。"}



