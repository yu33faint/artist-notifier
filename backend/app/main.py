from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from backend.app.database import get_db_connection, init_db
from backend.app.services.spotify import get_spotify_client
from backend.app.api.artists import router as artists_router
from backend.app.services.line_notification import send_line_message

load_dotenv()

# ==========================================
# コアロジック（タイマーからもAPIからも呼ばれる）
# ==========================================
def execute_spotify_check():
    print("🤖 [自動実行] Spotifyの新着チェックを開始します...")
    
    conn = get_db_connection()
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
                cursor.execute("INSERT INTO releases (id, name, artist) VALUES (?, ?, ?)", (release_id,        release_name, target_name))
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
# サーバーの「開店」と「閉店」のルール (lifespan)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(execute_spotify_check, 'interval', minutes=1)
    scheduler.start()
    print("⏰ バックグラウンド・タイマーを起動しました。")
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
app.include_router(artists_router)

# CORSの設定 (Reactのデフォルトポート5173からのアクセスを許可)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/check")
def run_check():
    result_message = execute_spotify_check()
    return {"status": "success", "message": result_message}
