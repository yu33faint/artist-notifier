import { useEffect, useState } from 'react';
import type { Release, ReleasesResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function ReleaseHistory() {
  const [releases, setReleases] = useState<Release[]>([]);

  useEffect(() => {
    const loadReleases = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/releases`);
        const data: ReleasesResponse = await response.json();
        setReleases(data.releases);
      } catch (error) {
        console.error("通知履歴の取得に失敗しました。", error);
      }
    };
    void loadReleases();
  }, []);

  return (
    <>
      <h3>3. 通知履歴</h3>
      <ul>
        {releases.length > 0 ? (
          releases.map((release) => (
            <li key={release.id} className="release-item">
              <span className="release-date">{formatDate(release.notified_at)}</span>
              <span>【{release.artist}】『{release.name}』</span>
              {release.url && (
                <a className="release-link" href={release.url} target="_blank" rel="noreferrer">
                  Spotifyで開く
                </a>
              )}
            </li>
          ))
        ) : (
          <li>通知履歴はまだありません。</li>
        )}
      </ul>
    </>
  );
}

export default ReleaseHistory;
