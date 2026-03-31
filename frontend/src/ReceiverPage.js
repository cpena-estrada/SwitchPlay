import { useState } from "react";
import "./SwitchPlay.css";

function ReceiverPage({ token }) {
  const [shareCode, setShareCode] = useState('');
  const [transfer, setTransfer] = useState(null);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);

  async function viewTransfer() {
    setLoading(true);
    const response = await fetch(`http://localhost:8000/transfers/${shareCode}`);
    const data = await response.json();
    setLoading(false);
    if (response.ok) setTransfer(data);
    else alert(data.detail);
  }

  async function acceptTransfer() {
    const response = await fetch(
      `http://localhost:8000/transfers/${shareCode}/accept?token=${token}`,
      { method: 'POST' }
    );
    const data = await response.json();
    if (response.ok) {
      setTransfer({ ...transfer, status: 'accepted' });
      setMessage('Transfer accepted! Click Complete to create the playlist.');
    } else {
      alert(data.detail);
    }
  }

  async function completeTransfer() {
    setMessage('Creating playlist… this may take a moment.');
    const response = await fetch(
      `http://localhost:8000/transfers/${shareCode}/complete?token=${token}`,
      { method: 'POST' }
    );
    const data = await response.json();
    if (response.ok) {
      setMessage(`✓ Playlist created! ${data.matched} songs matched, ${data.not_found} not found.`);
    } else {
      alert(data.detail);
    }
  }

  const PLATFORM_LABEL = { spotify: 'Spotify', apple_music: 'Apple Music' };

  return (
    <div className="sp-bg">
      <div className="sp-page">
        <header className="sp-header">
          <span className="sp-logo-icon">⇄</span>
          <h1 className="sp-wordmark">SwitchPlay</h1>
          <span className="sp-badge sp-badge--receive">Receive</span>
        </header>

        <section className="sp-section">
          <p className="sp-section-title">Enter your share code</p>
          <div className="sp-code-row">
            <input
              className="sp-input sp-input-code"
              placeholder="e.g. A3X9-KQ2"
              value={shareCode}
              onChange={(e) => setShareCode(e.target.value)}
            />
            <button className="sp-btn sp-btn-primary" onClick={viewTransfer} disabled={loading || !shareCode}>
              {loading ? '…' : 'Look Up'}
            </button>
          </div>
        </section>

        {transfer && (
          <section className="sp-section sp-transfer-card">
            <div className="sp-transfer-header">
              <h2 className="sp-transfer-title">{transfer.title}</h2>
              <span className="sp-transfer-route">
                {PLATFORM_LABEL[transfer.source_platform] || transfer.source_platform}
                {' → '}
                {PLATFORM_LABEL[transfer.target_platform] || transfer.target_platform}
              </span>
              <span className={`sp-status sp-status--${transfer.status}`}>{transfer.status}</span>
            </div>

            <div className="sp-track-list">
              <p className="sp-section-title">{transfer.tracks.length} Songs</p>
              {transfer.tracks.map((t, i) => (
                <div className="sp-track-item" key={i}>
                  <span className="sp-track-num">{i + 1}</span>
                  <div className="sp-track-info">
                    <span className="sp-track-name">{t.song_name}</span>
                    <span className="sp-track-artist">{t.artist_name}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="sp-actions">
              {transfer.status === 'created' && (
                <button className="sp-btn sp-btn-primary" onClick={acceptTransfer}>
                  Accept Transfer
                </button>
              )}
              {transfer.status === 'accepted' && (
                <button className="sp-btn sp-btn-primary" onClick={completeTransfer}>
                  Complete Transfer
                </button>
              )}
            </div>
          </section>
        )}

        {message && (
          <div className="sp-message">{message}</div>
        )}
      </div>
    </div>
  );
}

export default ReceiverPage;