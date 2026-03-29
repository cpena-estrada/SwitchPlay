import { useState } from "react";

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  async function handleLogin() {
    const response = await fetch(
      `http://localhost:8000/auth/login?email=${email}&password=${password}`,
      { method: 'POST' }
    );
    const data = await response.json();

    if (response.ok) {
      onLogin(data.access_token);
    } else {
      alert(data.detail);
    }
  }

  return (
    <div>
      <h1>SwitchPlay</h1>
      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        placeholder="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}

export default LoginPage;
