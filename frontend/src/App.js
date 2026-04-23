import { useState, useEffect } from "react";
import "./SwitchPlay.css";
import LoginPage from "./LoginPage";
import SenderPage from "./SenderPage";
import ReceiverPage from "./ReceiverPage";
import API_URL from "./api";

const PLATFORM_META = {
  spotify:     { label: "Spotify",     emoji: "🟢", color: "#1DB954" },
  apple_music: { label: "Apple Music", emoji: "🍎", color: "#fc3c44" },
};

function App() {
  // Initialize state from localStorage (persists across page reloads/redirects)
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [page, setPage] = useState(localStorage.getItem('page') || 'login');
  const [spotifyConnected, setSpotifyConnected] = useState(false);
  const [appleConnected, setAppleConnected] = useState(false);

  // Wrapper functions that update both React state AND localStorage
  function updateToken(t) {
    setToken(t);
    if (t) localStorage.setItem('token', t);
    else localStorage.removeItem('token');
  }

  function updatePage(p) {
    setPage(p);
    localStorage.setItem('page', p);
  }

  function logout() {
    updateToken(null);
    updatePage('login');
  }

  useEffect(() => {
    if (token && page === 'choose') {
      fetch(`${API_URL}/auth/status?token=${token}`)
        .then(r => r.json())
        .then(data => {
          setSpotifyConnected(data.spotify_connected);
          setAppleConnected(data.apple_connected);
        })
        .catch(() => {});
    }
  }, [token, page]);

  async function connectPlatform(platform) {
    if (platform === 'spotify') {
      window.location.href = `${API_URL}/auth/spotify?token=${token}`;
    } else if (platform === 'apple_music') {
      const response = await fetch(`${API_URL}/auth/apple/developer-token?token=${token}`);
      const data = await response.json();

      const music = await window.MusicKit.configure({
        developerToken: data.developer_token,
        app: { name: 'SwitchPlay', build: '1.0' }
      });

      const musicUserToken = await music.authorize();

      const saveResponse = await fetch(`${API_URL}/auth/apple/callback?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ music_user_token: musicUserToken })
      });
      const saveData = await saveResponse.json();

      if (saveResponse.ok) {
        setAppleConnected(true);
        alert('Apple Music connected!');
      } else {
        alert(saveData.detail);
      }
    }
  }

  if (page === 'login' && !token) {
    return <LoginPage onLogin={(t) => { updateToken(t); updatePage('choose'); }} />;
  }

  // Persistent top-right Log Out button — shown on every authenticated page
  const LogoutButton = (
    <button className="sp-logout-btn" onClick={logout}>
      Log Out
    </button>
  );

  if (page === 'choose') {
    const platforms = [
      { id: 'spotify', connected: spotifyConnected },
      { id: 'apple_music', connected: appleConnected },
    ];

    return (
      <div className="sp-bg">
        {LogoutButton}
        <div className="sp-login-card">
          <div className="sp-logo-block">
            <span className="sp-logo-icon">⇄</span>
            <h1 className="sp-wordmark">SwitchPlay</h1>
            <p className="sp-tagline">What do you want to do?</p>
          </div>
          <div className="sp-form">
            <button className="sp-btn sp-btn-primary" onClick={() => updatePage('sender')}>
              Send a Playlist
            </button>
            <button className="sp-btn sp-btn-secondary" onClick={() => updatePage('receiver')}>
              Receive a Playlist
            </button>
          </div>
          <div className="sp-connect-section">
            <p className="sp-connect-label">Connected Platforms</p>
            <div className="sp-platform-row">
              {platforms.map(({ id, connected }) => {
                const m = PLATFORM_META[id];
                return (
                  <button
                    key={id}
                    className={`sp-platform-card ${connected ? 'sp-platform-card--selected' : ''}`}
                    style={{ '--accent': m.color }}
                    onClick={() => connectPlatform(id)}
                  >
                    <span className="sp-platform-label">{m.label}</span>
                    <span className="sp-platform-connect-cta">
                      {connected ? '✓ Connected' : 'Connect'}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (page === 'sender') {
    return (
      <>
        {LogoutButton}
        <SenderPage token={token} onLogout={logout} onBack={() => updatePage('choose')} />
      </>
    );
  }

  if (page === 'receiver') {
    return (
      <>
        {LogoutButton}
        <ReceiverPage token={token} onLogout={logout} onBack={() => updatePage('choose')} />
      </>
    );
  }
}

export default App;
