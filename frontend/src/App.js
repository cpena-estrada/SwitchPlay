import { useState } from "react";
import LoginPage from "./LoginPage";
import SenderPage from "./SenderPage";
import ReceiverPage from "./ReceiverPage";

function App() {
  const [token, setToken] = useState(null);
  const [page, setPage] = useState('login');

  if (page === 'login' && !token) {
    return <LoginPage onLogin={(t) => { setToken(t); setPage('choose'); }} />;
  }

  if (page === 'choose') {
    return (
      <div>
        <h1>SwitchPlay</h1>
        <p>What do you want to do?</p>
        <button onClick={() => setPage('sender')}>Send a Playlist</button>
        <button onClick={() => setPage('receiver')}>Receive a Playlist</button>
      </div>
    );
  }

  if (page === 'sender') {
    return <SenderPage token={token} />;
  }

  if (page === 'receiver') {
    return <ReceiverPage token={token} />;
  }
}

export default App;
