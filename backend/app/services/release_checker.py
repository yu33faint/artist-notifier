from backend.app.database import get_db_connection
from backend.app.services.line_notification import send_line_message
from backend.app.services.spotify import get_spotify_client
from backend.app.repositories.artists import get_all_artist_records
from backend.app.repositories.releases import get_all_release_ids

def execute_spotify_check():
    print("Spotifyの新着チェックを開始します...")
    
    artists = get_all_artist_records()
    
    if not artists:
        print("🤖 [結果] 監視リストが空のためチェックをスキップします。")
        return "アーティストが1人も登録されていません。"
    
    notified_release_ids = get_all_release_ids()

    conn = get_db_connection()
    cursor = conn.cursor()

    sp = get_spotify_client()
    new_releases = []
    new_release_records = []

    for target_id, target_name in artists:
        try:
            results = sp.artist_albums(target_id, album_type='album,single', limit=1)
            if len(results['items']) == 0:
                continue

            latest_release = results['items'][0]
            release_id = latest_release['id']
            release_name = latest_release['name']
            release_url = latest_release['external_urls']['spotify']

            if release_id not in notified_release_ids:
                new_releases.append(f"【{target_name}】\n『{release_name}』\n{release_url}")
                new_release_records.append((release_id, release_name, target_name))

        except Exception as e:
            print(f"エラー発生 ({target_name}): {e}")
            continue

    if new_releases:
        message_text = "🔥新着アラート!!🔥\n\n" + "\n\n".join(new_releases)
        try:
            send_line_message(message_text)

            cursor.executemany(
                "INSERT INTO releases (id, name, artist) VALUES (?, ?, ?)",
                new_release_records
            )
            conn.commit()
        finally:
            conn.close()

        print(f"🤖 [通知完了] {len(new_releases)}件の新着をLINEに送りました。")
        return f"{len(new_releases)}件の新着をLINEに通知しました！"
    
    else:
        conn.close()
        print("🤖 [結果] 新着はありませんでした。")
        return "全アーティストをチェックしましたが、新着はありませんでした。"