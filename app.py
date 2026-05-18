import os
import sqlite3
import requests
from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ★追加：タイマー機能と、サーバーの起動・終了を管理するツール
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

load_dotenv()

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

# ==========================================
# ★新設：コアロジック（タイマーからもボタンからも呼ばれる）
# ==========================================
def execute_spotify_check():
    print("🤖 [自動実行] Spotifyの新着チェックを開始します...")
    
    conn = sqlite3.connect('notifier.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM artists")
    artists = cursor.fetchall()
    
    if not artists:
        print("🤖 [結果] 監視リストが空のためチェックをスキップします。")
        conn.close()
        return "アーティストが1人も登録されていません。"

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
        print(f"🤖 [通知完了] {len(new_releases)}件の新着をLINEに送りました。")
        return f"{len(new_releases)}件の新着をLINEに通知しました！"
    else:
        print("🤖 [結果] 新着はありませんでした。")
        return "全アーティストをチェックしましたが、新着はありませんでした。"


# ==========================================
# ★新設：サーバーの「開店」と「閉店」のルール (lifespan)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 【開店時（uvicorn起動時）にやること】
    init_db() # データベースの準備
    scheduler = BackgroundScheduler()
    # 専属の監視員に「execute_spotify_check を 1分おきに実行しろ」と命令
    scheduler.add_job(execute_spotify_check, 'interval', minutes=1)
    scheduler.start()
    print("⏰ バックグラウンド・タイマーを起動しました。1分おきに自動チェックします。")

    yield # ここでWebサーバーがお客さんを待ち続ける（稼働中）

    # 【閉店時（Ctrl+Cで停止した時）にやること】
    scheduler.shutdown()
    print("⏰ バックグラウンド・タイマーを安全に停止しました。")

# FastAPIの起動時に、上記のルール(lifespan)を適用する
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# ==========================================
# APIエンドポイント（ルーティング）
# ==========================================

@app.get("/")
def read_root(request: Request):
    conn = sqlite3.connect('notifier.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM artists")
    saved_artists = cursor.fetchall()
    conn.close()

    artist_names = [row[0] for row in saved_artists]
    return templates.TemplateResponse(request=request, name="index.html", context={"artist_names": artist_names})

@app.post("/api/register")
def register_artist(request: Request, artist_name: str = Form(...)):
    sp = get_spotify_client()
    try:
        search_result = sp.search(q=artist_name, type='artist', limit=1)
        artists_found = search_result['artists']['items']
        if not artists_found:
            return templates.TemplateResponse(request=request, name="result.html", context={"message": f"「{artist_name}」に一致するアーティストが見つかりませんでした。"})
            
        exact_artist = artists_found[0]
        artist_id = exact_artist['id']
        formal_name = exact_artist['name']
    except Exception as e:
        return templates.TemplateResponse(request=request, name="result.html", context={"message": f"Spotify検索中にエラーが発生しました: {e}"})

    conn = sqlite3.connect('notifier.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO artists (id, name) VALUES (?, ?)", (artist_id, formal_name))
        conn.commit()
        msg = f"Spotifyから「{formal_name}」を発見！監視リストに登録しました。"
    except sqlite3.IntegrityError:
        msg = f"「{formal_name}」は既に登録されています。"
    finally:
        conn.close()
    
    return templates.TemplateResponse(request=request, name="result.html", context={"message": msg})

# ★変更：ボタンから呼ばれた時も、独立したコアロジックを使い回す
@app.post("/api/check")
def run_check(request: Request):
    # ボタンが押されたら、コアロジックを実行し、その結果の文字列を受け取る
    result_message = execute_spotify_check()
    # 受け取った結果を result.html に埋め込んでブラウザに返す
    return templates.TemplateResponse(request=request, name="result.html", context={"message": result_message})


