import { useState } from "react";
import "./SwitchPlay.css";

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setLoading(true);
    const response = await fetch(
      `http://localhost:8000/auth/login?email=${email}&password=${password}`,
      { method: 'POST' }
    );
    const data = await response.json();
    setLoading(false);

    if (response.ok) {
      onLogin(data.access_token);
    } else {
      alert(data.detail);
    }
  }

  return (
    <div className="sp-bg">
      <div className="sp-login-card">
        <div className="sp-logo-block">
          <span className="sp-logo-icon">⇄</span>
          <h1 className="sp-wordmark">SwitchPlay</h1>
          <p className="sp-tagline">Move your music, keep your vibe.</p>
        </div>

        <div className="sp-form">
          <div className="sp-input-group">
            <label className="sp-label">Email</label>
            <input
              className="sp-input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="sp-input-group">
            <label className="sp-label">Password</label>
            <input
              className="sp-input"
              placeholder="••••••••"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button
            className={`sp-btn sp-btn-primary ${loading ? 'sp-btn-loading' : ''}`}
            onClick={handleLogin}
            disabled={loading}
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;