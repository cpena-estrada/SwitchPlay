import { useState } from "react";

function SenderPage({ token }) {
  const [sourcePlatform, setSourcePlatform] = useState('');
  const [targetPlatform, setTargetPlatform] = useState('');
  const [playlists, setPlaylists] = useState([]);
  const [shareCode, setShareCode] = useState(null);

  async function fetchPlaylists() {
    if (sourcePlatform === 'spotify') {
      const response = await fetch(
        `http://localhost:8000/spotify/playlists?token=${token}`
      );
      const data = await response.json();

      if (response.ok) {
        setPlaylists(data);
      } else {
        alert(data.detail);
      }
    } else if (sourcePlatform === 'apple_music') {
      alert('Apple Music playlist fetching not supported yet');
    }
  }

  async function handleTransfer(playlistId, playlistName) {
    const response = await fetch(
      `http://localhost:8000/transfers?token=${token}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_platform: sourcePlatform,
          target_platform: targetPlatform,
          playlist_id: playlistId,
          title: playlistName
        })
      }
    );
    const data = await response.json();

    if (response.ok) {
      setShareCode(data.share_code);
    } else {
      alert(data.detail);
    }
  }

  async function connectPlatform() {
    window.location.href = `http://localhost:8000/auth/spotify?token=${token}`;
  }

  // Step 1: Pick platforms
  if (!sourcePlatform || !targetPlatform) {
    return (
      <div>
        <h1>SwitchPlay — Send</h1>

        <h3>Transfer FROM:</h3>
        <button onClick={() => setSourcePlatform('spotify')}>Spotify</button>
        <button onClick={() => setSourcePlatform('apple_music')}>Apple Music</button>

        <h3>Transfer TO:</h3>
        <button onClick={() => setTargetPlatform('spotify')}>Spotify</button>
        <button onClick={() => setTargetPlatform('apple_music')}>Apple Music</button>

        {sourcePlatform && <p>From: {sourcePlatform}</p>}
        {targetPlatform && <p>To: {targetPlatform}</p>}
      </div>
    );
  }

  // Step 2: Connect source platform if needed, then show playlists
  return (
    <div>
      <h1>SwitchPlay — Send</h1>
      <p>{sourcePlatform} → {targetPlatform}</p>

      <button onClick={connectPlatform}>Connect {sourcePlatform}</button>
      <button onClick={fetchPlaylists}>Load My Playlists</button>

      {shareCode && (
        <div>
          <h2>Transfer Created!</h2>
          <p>Share this code with the receiver: <strong>{shareCode}</strong></p>
        </div>
      )}

      {playlists.length > 0 && (
        <div>
          <h2>Your Playlists</h2>
          {playlists.map((p) => (
            <div key={p.id}>
              <h3>{p.name}</h3>
              <p>{p.total_tracks} tracks</p>
              <button onClick={() => handleTransfer(p.id, p.name)}>Transfer</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SenderPage;
