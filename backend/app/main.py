from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from backend.app.database import init_db
from backend.app.api.artists import router as artists_router
from backend.app.services.release_checker import execute_spotify_check

load_dotenv()

# ==========================================
# サーバーの「開店」と「閉店」のルール (lifespan)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(execute_spotify_check, 'interval', hours=1, max_instances=1, coalesce=True)
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
