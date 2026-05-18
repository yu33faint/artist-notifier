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

# ==========================================
# ② バックエンド（名前での検索・登録処理）
# ==========================================
# 引数の名前を artist_name に変更
# ==========================================
# ② バックエンド（名前での検索・登録処理）
# ==========================================
# ★追加: 引数に request: Request を追加した
@app.post("/api/register")
def register_artist(request: Request, artist_name: str = Form(...)):
    sp = get_spotify_client()
    try:
        search_result = sp.search(q=artist_name, type='artist', limit=1)
        artists_found = search_result['artists']['items']
        
        if not artists_found:
            # ★変更: JSONではなく、HTMLテンプレートにメッセージを渡して返す
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
    
    # ★変更: 最終的な結果も、HTMLテンプレートで返す
    return templates.TemplateResponse(request=request, name="result.html", context={"message": msg})


# ==========================================
# ③ バックエンド（全チェックと通知処理）
# ==========================================
# ★追加: 引数に request: Request を追加した
@app.post("/api/check")
def run_check(request: Request):
    conn = sqlite3.connect('notifier.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM artists")
    artists = cursor.fetchall()
    
    if not artists:
        conn.close()
        return templates.TemplateResponse(request=request, name="result.html", context={"message": "アーティストが1人も登録されていません。"})

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

    # ★変更: LINE通知の有無にかかわらず、結果をHTMLテンプレートで返す
    if new_releases:
        message_text = "🔥新着アラート!!🔥\n\n" + "\n\n".join(new_releases)
        send_line_message(message_text)
        return templates.TemplateResponse(request=request, name="result.html", context={"message": f"{len(new_releases)}件の新着をLINEに通知しました！"})
    else:
        return templates.TemplateResponse(request=request, name="result.html", context={"message": "全アーティストをチェックしましたが、新着はありませんでした。"})


