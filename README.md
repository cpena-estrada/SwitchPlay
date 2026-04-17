# SwitchPlay

Transfer playlists between **Spotify** and **Apple Music** — no third-party services required. A sender shares a 6-character code, a receiver enters it and imports the playlist directly into their account.

---

## How It Works

1. **Sender** connects their source platform (Spotify or Apple Music), picks a playlist, and selects a target platform. SwitchPlay generates a short share code.
2. **Receiver** enters the share code, connects their target platform account, and SwitchPlay searches for each track and builds the playlist automatically.
3. A match report shows which songs transferred successfully and which weren't found.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI · Uvicorn |
| Frontend | React 19 |
| Database | PostgreSQL |
| Auth | JWT · Spotify OAuth · Apple MusicKit JS |
| Deployment | Docker · Fly.io |

---

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL database
- Spotify Developer app ([developer.spotify.com](https://developer.spotify.com))
- Apple Developer account with a MusicKit key

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```env
DATABASE_URL=

SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT_URI=

APPLE_KEY_ID=
APPLE_TEAM_ID=
APPLE_PRIVATE_KEY_PATH=
APPLE_PRIVATE_KEY=

ALLOWED_ORIGINS=http://localhost:3000

SECRET_KEY=your-secret-key
```

---

## Local Development

### Database

Run the schema against your PostgreSQL instance:

```bash
psql $DATABASE_URL -f schema.sql
```

### Backend

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API runs at `http://127.0.0.1:8000` — interactive docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000`.

---

## Docker

Build and run the backend with Docker:

```bash
docker build -t switchplay .
docker run -p 8080:8080 --env-file .env switchplay
```

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/login` | Log in, receive JWT |
| `GET` | `/auth/spotify` | Redirect to Spotify OAuth |
| `GET` | `/auth/callback` | Spotify OAuth callback |
| `POST` | `/auth/apple/callback` | Save Apple Music user token |
| `GET` | `/spotify/playlists` | List user's Spotify playlists |
| `GET` | `/apple/playlists` | List user's Apple Music playlists |
| `POST` | `/transfers` | Create a transfer + share code |
| `GET` | `/transfers/{share_code}` | Look up a transfer by code |
| `POST` | `/transfers/{share_code}/accept` | Receiver accepts a transfer |
| `POST` | `/transfers/{share_code}/complete` | Complete transfer to target platform |

---

## Database Schema

```
users               — accounts
platform_auth       — Spotify / Apple Music tokens per user
transfer_requests   — playlist transfer with status + share code
transfer_items      — individual tracks + match status
```

---

## License

MIT
