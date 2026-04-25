import { useState } from "react";
import "./SwitchPlay.css";
import API_URL from "./api";

function LoginPage({ onLogin }) {
  const [mode, setMode] = useState('login');   // 'login' or 'signup'
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setLoading(true);
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    setLoading(false);

    if (response.ok) onLogin(data.access_token);
    else alert(data.detail);
  }

  async function handleSignUp() {
    setLoading(true);
    const response = await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ first_name: firstName, last_name: lastName, email, password })
    });
    const data = await response.json();
    setLoading(false);

    if (response.ok) {
      // account created — now log them in automatically
      await handleLogin();
    } else {
      alert(data.detail);
    }
  }

  const isLogin = mode === 'login';

  return (
    <div className="sp-bg">
      <div className="sp-login-card">
        <div className="sp-logo-block">
          <span className="sp-logo-icon">⇄</span>
          <h1 className="sp-wordmark">SwitchPlay</h1>
          <p className="sp-tagline">Move your music, keep your vibe.</p>
        </div>

        <div className="sp-form">
          {!isLogin && (
            <div className="sp-name-row">
              <div className="sp-input-group">
                <label className="sp-label">First Name</label>
                <input
                  className="sp-input"
                  placeholder="Jane"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                />
              </div>
              <div className="sp-input-group">
                <label className="sp-label">Last Name</label>
                <input
                  className="sp-input"
                  placeholder="Doe"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                />
              </div>
            </div>
          )}

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
            onClick={isLogin ? handleLogin : handleSignUp}
            disabled={loading}
          >
            {loading ? (isLogin ? 'Signing in…' : 'Creating account…') : (isLogin ? 'Sign In' : 'Create Account')}
          </button>

          <p className="sp-toggle">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button className="sp-toggle-btn" onClick={() => setMode(isLogin ? 'signup' : 'login')}>
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>

          <div className="sp-divider"><span>or</span></div>

          <button
            className="sp-btn sp-btn-google"
            onClick={() => window.location.href = `${API_URL}/auth/google`}
          >
            <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="" width="18" />
            Continue with Google
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
