import { useState } from "react";
import "./SwitchPlay.css";
import LoginPage from "./LoginPage";
import SenderPage from "./SenderPage";
import ReceiverPage from "./ReceiverPage";

function App() {
  // Initialize state from localStorage (persists across page reloads/redirects)
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [page, setPage] = useState(localStorage.getItem('page') || 'login');

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
