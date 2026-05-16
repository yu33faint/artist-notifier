import os
import sqlite3
import requests
from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 環境変数の読み込みとアプリの初期化
load_dotenv()
app = FastAPI()

# テンプレート（HTML）が入っているフォルダを指定
templates = Jinja2Templates(directory="templates")

# ==========================================
# 共通ツール
# ==========================================
def send_line_message(notification_text):
    url = 'https://api.line.me/v2/bot/message/push'
    token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = {'to': os.getenv('LINE_USER_ID'), 'messages': [{'type': 'text', 'text': notification_text}]}
    requests.post(url, headers=headers, json=data)

def get_spotify_client():
    manager = SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
    )
    return spotipy.Spotify(client_credentials_manager=manager)

def init_db():
    conn = sqlite3.connect('notifier.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS artists (id TEXT PRIMARY KEY, name TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS releases (id TEXT PRIMARY KEY, name TEXT, artist TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# APIエンドポイント（ルーティング）
# ==========================================

# ① トップ画面の表示（HTMLを返す）
@app.get("/")
def read_root(request: Request):
    conn = sqlite3.connect('notifier.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM artists")
    saved_artists = cursor.fetchall()
    conn.close()

    # DBのデータをシンプルなリストに変換
    artist_names = [row[0] for row in saved_artists]

    # index.htmlに変数（artist_names）を渡してブラウザに返す
    # 引数がどの役割を持つか、名前を明記して確実に渡す
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"artist_names": artist_names}
    )

# ② アーティストの登録処理
@app.post("/api/register")
def register_artist(artist_id: str = Form(...)):
    sp = get_spotify_client()
    try:
        artist_info = sp.artist(artist_id)
        artist_name = artist_info['name']
    except Exception:
        return {"status": "error", "message": "無効なIDか、Spotifyでアーティストが見つかりませんでした。"}

    conn = sqlite3.connect('notifier.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO artists (id, name) VALUES (?, ?)", (artist_id, artist_name))
        conn.commit()
        result = {"status": "success", "message": f"「{artist_name}」を監視リストに登録しました！"}
    except sqlite3.IntegrityError:
        result = {"status": "error", "message": "そのアーティストは既に登録されています。"}
    finally:
        conn.close()
    
    return result

# ③ 全アーティストの新着チェック処理
@app.post("/api/check")
def run_check():
    conn = sqlite3.connect('notifier.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM artists")
    artists = cursor.fetchall()
    
    if not artists:
        conn.close()
        return {"status": "error", "message": "アーティストが1人も登録されていません。"}

    sp = get_spotify_client()
    new_releases = []

    for target_id, target_name in artists:
        try:
            results = sp.artist_albums(target_id, album_type='album,single', limit=1)
            if len(results['items']) == 0:
                continue

            latest_release = results['items'][0]
            release_id = latest_release['id']
            release_name = latest_release['name']
            release_url = latest_release['external_urls']['spotify']

            cursor.execute("SELECT id FROM releases WHERE id = ?", (release_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO releases (id, name, artist) VALUES (?, ?, ?)", (release_id, release_name, target_name))
                new_releases.append(f"【{target_name}】\n『{release_name}』\n{release_url}")
        except Exception as e:
            print(f"エラー発生 ({target_name}): {e}")
            continue

    conn.commit()
    conn.close()

    if new_releases:
        message_text = "🔥新着アラート!!🔥\n\n" + "\n\n".join(new_releases)
        send_line_message(message_text)
        return {"status": "success", "message": f"{len(new_releases)}件の新着をLINEに通知しました！"}
    else:
        return {"status": "success", "message": "新着はありませんでした。"}



