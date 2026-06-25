import { useState, useEffect, type SubmitEvent } from 'react';
import './App.css';
import type {
  Artist,
  ArtistsResponse,
  MessageResponse
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

function App() {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [newArtist, setNewArtist] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const fetchArtists = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/artists`);
      const data: ArtistsResponse = await response.json();
      setArtists(data.artists);
    } catch (error) {
      console.error("アーティストの取得に失敗しました", error);
    }
  };

  // 画面の初回読み込み時に登録済みアーティスト一覧を取得
  useEffect(() => {
    const loadArtists = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/artists`);
        const data: ArtistsResponse = await response.json();
        setArtists(data.artists);
      } catch (error) {
        console.error("アーティストの取得に失敗しました", error);
      }
    };
    void loadArtists();
  }, []);

  // アーティスト登録処理
  const handleRegister = async (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault(); // 画面の再読み込みを防ぐ
    setIsLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ artist_name: newArtist })
        });
      const data: MessageResponse = await response.json();
      setMessage(data.message);
      setNewArtist(''); // 入力欄をクリア
      fetchArtists();   // リストを最新状態に更新
    } catch {
      setMessage("通信エラーが発生しました。");
    }
    setIsLoading(false);
  };

  //アーティスト削除処理
  const handleDelete = async (artistId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/artists/${artistId}`,
        {
          method: 'DELETE'
        }
      );
      const data: MessageResponse = await response.json();
      setMessage(data.message);
      fetchArtists(); // リストを最新状態に更新
    } catch {
      setMessage("通信エラーが発生しました。");
    }
    setIsLoading(false);
  };

  // 通知チェック実行処理
  const handleCheck = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/check`, {
        method: 'POST'
      });
      const data: MessageResponse = await response.json();
      setMessage(data.message);
    } catch {
      setMessage("通信エラーが発生しました。");
    }
    setIsLoading(false);
  };

  return (
    <div className="container">
      <h1>🎸 コントロールパネル</h1>
      
      {/* メッセージ表示エリア */}
      {message && <div className="message-box">{message}</div>}

      <h3>1. 監視アーティストの追加</h3>
      <form onSubmit={handleRegister}>
        <input 
          type="text" 
          value={newArtist}
          onChange={(e) => setNewArtist(e.target.value)}
          placeholder="アーティスト名を入力 (例: Vaundy)" 
          required 
          disabled={isLoading}
        />
        <button type="submit" className="btn-blue" disabled={isLoading}>
          {isLoading ? '処理中...' : '登録する'}
        </button>
      </form>

      <h3>現在の監視リスト</h3>
      <ul>
        {artists.length > 0 ? (
          artists.map((artist) => (
            <li key={artist.id}>
              <span>{artist.name}</span>
              <button
                type="button"
                className="btn-delete"
                onClick={() => handleDelete(artist.id)}
                disabled={isLoading}
              >
                削除
              </button>
            </li>
          ))
        ) : (
          <li>まだ誰も登録されていません。</li>
        )}
      </ul>
      
      <hr />
      
      <h3>2. 新着チェックの実行</h3>
      <button onClick={handleCheck} className="btn-green" disabled={isLoading}>
        {isLoading ? '確認中...' : '全アーティストの通知チェックを実行'}
      </button>
    </div>
  );
}

export default App;