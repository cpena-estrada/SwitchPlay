import { useState } from "react";
import "./SwitchPlay.css";
import API_URL from "./api";

const PLATFORM_META = {
  spotify:     { label: "Spotify",     emoji: "🟢", color: "#1DB954" },
  apple_music: { label: "Apple Music", emoji: "🍎", color: "#fc3c44" },
};

function PlatformCard({ id, selected, onSelect }) {
  const m = PLATFORM_META[id];
  return (
    <button
      className={`sp-platform-card ${selected ? 'sp-platform-card--selected' : ''}`}
      style={{ '--accent': m.color }}
      onClick={() => onSelect(id)}
    >
      <span className="sp-platform-emoji">{m.emoji}</span>
      <span className="sp-platform-label">{m.label}</span>
      {selected && <span className="sp-platform-check">✓</span>}
    </button>
  );
}

function SenderPage({ token }) {
  const [sourcePlatform, setSourcePlatform] = useState('');
  const [targetPlatform, setTargetPlatform] = useState('');
  const [playlists, setPlaylists] = useState([]);
  const [shareCode, setShareCode] = useState(null);
  const [loadingPlaylists, setLoadingPlaylists] = useState(false);
  const [transferringId, setTransferringId] = useState(null);

  async function fetchPlaylists() {
    if (sourcePlatform === 'spotify') {
      setLoadingPlaylists(true);
      const response = await fetch(`${API_URL}/spotify/playlists?token=${token}`);
      const data = await response.json();
      setLoadingPlaylists(false);
      if (response.ok) setPlaylists(data);
      else alert(data.detail);
    } else if (sourcePlatform === 'apple_music') {
      setLoadingPlaylists(true);
      const response = await fetch(
        `${API_URL}/apple/playlists?token=${token}`
      );
      const data = await response.json();
      setLoadingPlaylists(false);
      if (response.ok) setPlaylists(data);
      else alert(data.detail);
    }
  }

  async function handleTransfer(playlistId, playlistName) {
    setTransferringId(playlistId);
    const response = await fetch(`${API_URL}/transfers?token=${token}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_platform: sourcePlatform,
        target_platform: targetPlatform,
        playlist_id: playlistId,
        title: playlistName
      })
    });
    const data = await response.json();
    setTransferringId(null);
    if (response.ok) setShareCode(data.share_code);
    else alert(data.detail);
  }

  async function connectPlatform() {
    if (sourcePlatform === 'spotify') {
      window.location.href = `${API_URL}/auth/spotify?token=${token}`;

    } else if (sourcePlatform === 'apple_music') {
      // get developer token from backend
      const response = await fetch(
        `${API_URL}/auth/apple/developer-token?token=${token}`
      );
      const data = await response.json();

      // configure MusicKit with developer token
      const music = await window.MusicKit.configure({
        developerToken: data.developer_token,
        app: { name: 'SwitchPlay', build: '1.0' }
      });

      // open Apple's login popup — user signs in with Apple ID
      const musicUserToken = await music.authorize();

      // send the Music User Token to our backend to save in platform_auth
      const saveResponse = await fetch(
        `${API_URL}/auth/apple/callback?token=${token}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ music_user_token: musicUserToken })
        }
      );
      const saveData = await saveResponse.json();

      if (saveResponse.ok) {
        alert('Apple Music connected!');
      } else {
        alert(saveData.detail);
      }
    }
  }

  const ready = sourcePlatform && targetPlatform;

  return (
    <div className="sp-bg">
      <div className="sp-page">
        <header className="sp-header">
          <span className="sp-logo-icon">⇄</span>
          <h1 className="sp-wordmark">SwitchPlay</h1>
          <span className="sp-badge">Send</span>
        </header>

        <section className="sp-section">
          <p className="sp-section-title">Transfer FROM</p>
          <div className="sp-platform-row">
            {Object.keys(PLATFORM_META).map(id => (
              <PlatformCard key={id} id={id} selected={sourcePlatform === id} onSelect={setSourcePlatform} />
            ))}
          </div>
        </section>

        <div className="sp-arrow-divider">↓</div>

        <section className="sp-section">
          <p className="sp-section-title">Transfer TO</p>
          <div className="sp-platform-row">
            {Object.keys(PLATFORM_META).map(id => (
              <PlatformCard key={id} id={id} selected={targetPlatform === id} onSelect={setTargetPlatform} />
            ))}
          </div>
        </section>

        {ready && (
          <div className="sp-actions">
            <button className="sp-btn sp-btn-secondary" onClick={connectPlatform}>
              Connect {PLATFORM_META[sourcePlatform].label}
            </button>
            <button className="sp-btn sp-btn-primary" onClick={fetchPlaylists} disabled={loadingPlaylists}>
              {loadingPlaylists ? 'Loading…' : 'Load My Playlists'}
            </button>
          </div>
        )}

        {shareCode && (
          <div className="sp-share-box">
            <p className="sp-share-label">Share this code with the receiver</p>
            <div className="sp-share-code">{shareCode}</div>
          </div>
        )}

        {playlists.length > 0 && (
          <section className="sp-section">
            <p className="sp-section-title">Your Playlists</p>
            <div className="sp-playlist-list">
              {playlists.map((p) => (
                <div className="sp-playlist-item" key={p.id}>
                  <div className="sp-playlist-info">
                    <span className="sp-playlist-name">{p.name}</span>
                    <span className="sp-playlist-meta">{p.total_tracks} tracks</span>
                  </div>
                  <button
                    className="sp-btn sp-btn-small"
                    onClick={() => handleTransfer(p.id, p.name)}
                    disabled={transferringId === p.id}
                  >
                    {transferringId === p.id ? '…' : 'Transfer'}
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default SenderPage;