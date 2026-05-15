import os
import sqlite3
import requests  # LINEに手紙を送るための新しい武器
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 環境変数の読み込み
load_dotenv()

# --- LINEに手紙(POSTリクエスト)を送る専用の関数 ---
def send_line_message(notification_text):
    # ① 宛先（エンドポイント）
    url = 'https://api.line.me/v2/bot/message/push'
    
    # ② ヘッダー（身分証明書）
    token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # ③ ボディ（送る相手と、メッセージの中身）
    data = {
        'to': os.getenv('LINE_USER_ID'),
        'messages': [{
            'type': 'text',
            'text': notification_text
        }]
    }
    
    # LINEのサーバーに手紙を叩きつける（POST）
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

# --- 1. データベースの準備 ---
conn = sqlite3.connect('notifier.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS releases (
        id TEXT PRIMARY KEY,
        name TEXT,
        artist TEXT
    )
''')
conn.commit()

# --- 2. Spotify APIから「最新リリース」を取得 ---
client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
artist_id = '26ZBeXl5Gqr3TAv2itmyCU' # indigo la End
results = sp.artist_albums(artist_id, album_type='album,single', limit=1)

# --- 3. 新着判定とLINE通知 ---
if len(results['items']) > 0:
    latest_release = results['items'][0]
    release_id = latest_release['id']
    release_name = latest_release['name']
    release_url = latest_release['external_urls']['spotify']

    cursor.execute("SELECT id FROM releases WHERE id = ?", (release_id,))
    record = cursor.fetchone()

    if record:
        print(f"【通知なし】'{release_name}' は既に確認済みです。")
    else:
        # 新着が見つかった場合、送信するメッセージの文章を組み立てる（\nは改行の意味）
        message_text = f"【🔥新着アラート!!】\nindigo la Endの新しいリリースを発見しました！\n\n『{release_name}』\n{release_url}"
        print("新規リリースを発見。LINEへ通知を送信します...")
        
        # ここでさっき作った関数を呼び出して、LINEに送信！
        status_code = send_line_message(message_text)
        
        if status_code == 200:
            print("✅ LINEへの通知に成功しました！スマホを確認してください。")
            
            # 通知に成功した時だけ、データベースに記憶を書き込む
            cursor.execute("INSERT INTO releases (id, name, artist) VALUES (?, ?, ?)", 
                           (release_id, release_name, "indigo la End"))
            conn.commit()
        else:
            print(f"❌ LINE通知に失敗しました。ステータスコード: {status_code}")

else:
    print("リリース情報が見つかりませんでした。")

conn.close()