import { useState } from "react";

function ReceiverPage({ token }) {
  const [shareCode, setShareCode] = useState('');
  const [transfer, setTransfer] = useState(null);
  const [message, setMessage] = useState(null);

  async function viewTransfer() {
    const response = await fetch(
      `http://localhost:8000/transfers/${shareCode}`
    );
    const data = await response.json();

    if (response.ok) {
      setTransfer(data);
    } else {
      alert(data.detail);
    }
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
    setMessage('Creating playlist... this may take a moment.');
    const response = await fetch(
      `http://localhost:8000/transfers/${shareCode}/complete?token=${token}`,
      { method: 'POST' }
    );
    const data = await response.json();

    if (response.ok) {
      setMessage(`Playlist created! ${data.matched} songs matched, ${data.not_found} not found.`);
    } else {
      alert(data.detail);
    }
  }

  return (
    <div>
      <h1>SwitchPlay — Receive</h1>

      <input
        placeholder="Enter share code"
        value={shareCode}
        onChange={(e) => setShareCode(e.target.value)}
      />
      <button onClick={viewTransfer}>View Transfer</button>

      {transfer && (
        <div>
          <h2>{transfer.title}</h2>
          <p>{transfer.source_platform} → {transfer.target_platform}</p>
          <p>Status: {transfer.status}</p>

          <h3>Songs ({transfer.tracks.length})</h3>
          {transfer.tracks.map((t, index) => (
            <p key={index}>{t.song_name} — {t.artist_name}</p>
          ))}

          {transfer.status === 'created' && (
            <button onClick={acceptTransfer}>Accept Transfer</button>
          )}

          {transfer.status === 'accepted' && (
            <button onClick={completeTransfer}>Complete Transfer</button>
          )}
        </div>
      )}

      {message && <p><strong>{message}</strong></p>}
    </div>
  );
}

export default ReceiverPage;
