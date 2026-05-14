import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# .envファイルから秘密の環境変数を読み込む
load_dotenv()

# Spotify APIの認証設定
client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# ターゲットのアーティストID（indigo la End）
artist_id = '26ZBeXl5Gqr3TAv2itmyCU'

# アーティスト情報を取得
artist = sp.artist(artist_id)

print("=== データ取得成功 ===")
# get()を使えば、もしキーが無くてもエラーにならず None が返る
print(f"アーティスト名: {artist.get('name')}")

# followersは仕様変更で消えた可能性が高いのでコメントアウトで封印する
# print(f"フォロワー数: {artist['followers']['total']}") 

print(f"ジャンル: {artist.get('genres')}")

print("\n=== Spotifyから届いた生のデータ ===")
print(artist)
