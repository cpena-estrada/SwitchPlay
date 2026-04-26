// StatsPage.js
//
// Exists to satisfy class requirements (Phase 5).
// Pulls from /stats/* endpoints which use views + stored procedures.
//
// To remove after the class:
//   1. Delete this file
//   2. Remove StatsPage import + 'stats' page case in App.js
//   3. Remove the "View Stats" button from the choose page in App.js

import { useEffect, useState } from "react";
import "./SwitchPlay.css";
import API_URL from "./api";

function StatsPage({ token, onBack }) {
  const [users, setUsers] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [u, p] = await Promise.all([
        fetch(`${API_URL}/stats/users?token=${token}`).then(r => r.json()),
        fetch(`${API_URL}/stats/platforms?token=${token}`).then(r => r.json()),
      ]);
      setUsers(u);
      setPlatforms(p);
      setLoading(false);
    }
    load();
  }, [token]);

  return (
    <div className="sp-bg">
      <div className="sp-page">
        <header className="sp-header">
          <span className="sp-logo-icon">⇄</span>
          <h1 className="sp-wordmark">SwitchPlay</h1>
          <span className="sp-badge">Stats</span>
        </header>

        {loading && <p className="sp-section-title">Loading…</p>}

        {!loading && (
          <>
            <section className="sp-section">
              <p className="sp-section-title">Transfers by Platform Route</p>
              <table className="sp-table">
                <thead>
                  <tr>
                    <th>From</th><th>To</th><th>Total</th><th>Completed</th><th>Avg Tracks</th>
                  </tr>
                </thead>
                <tbody>
                  {platforms.map((p, i) => (
                    <tr key={i}>
                      <td>{p.source_platform}</td>
                      <td>{p.target_platform}</td>
                      <td>{p.total_transfers}</td>
                      <td>{p.completed_transfers}</td>
                      <td>{p.avg_tracks}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>

            <section className="sp-section">
              <p className="sp-section-title">Users & Transfer Counts</p>
              <table className="sp-table">
                <thead>
                  <tr>
                    <th>Email</th><th>Name</th><th>Total</th><th>Completed</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.user_id}>
                      <td>{u.email}</td>
                      <td>{u.first_name} {u.last_name}</td>
                      <td>{u.total_transfers}</td>
                      <td>{u.completed_transfers}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          </>
        )}

        <div className="sp-actions">
          <button className="sp-btn sp-btn-secondary" onClick={onBack}>← Back</button>
        </div>
      </div>
    </div>
  );
}

export default StatsPage;
