import { useState } from "react";
import "./SwitchPlay.css";
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
      <div className="sp-bg">
        <div className="sp-login-card">
          <div className="sp-logo-block">
            <span className="sp-logo-icon">⇄</span>
            <h1 className="sp-wordmark">SwitchPlay</h1>
            <p className="sp-tagline">What do you want to do?</p>
          </div>
          <div className="sp-form">
            <button className="sp-btn sp-btn-primary" onClick={() => setPage('sender')}>
              Send a Playlist
            </button>
            <button className="sp-btn sp-btn-secondary" onClick={() => setPage('receiver')}>
              Receive a Playlist
            </button>
          </div>
        </div>
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