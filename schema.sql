-- ====== SwitchPlay Database Schema ====== --

-- ====== users table ====== --
CREATE TABLE IF NOT EXISTS users (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  first_name  VARCHAR(100) NOT NULL,
  last_name   VARCHAR(100) NOT NULL,
  email       VARCHAR(255) NOT NULL UNIQUE,
  password    VARCHAR(255) NOT NULL,
  created_at  TIMESTAMP DEFAULT now()
);

-- ====== transfer_requests table ====== --
CREATE TABLE IF NOT EXISTS transfer_requests (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  share_code        VARCHAR(50) NOT NULL UNIQUE,
  title             VARCHAR(255) NOT NULL,
  source_platform   VARCHAR(50) NOT NULL CHECK (source_platform IN ('spotify', 'apple_music', 'youtube_music')),
  target_platform   VARCHAR(50) NOT NULL CHECK (target_platform IN ('spotify', 'apple_music', 'youtube_music')),
  status            VARCHAR(50) NOT NULL DEFAULT 'created' CHECK (status IN ('created', 'accepted', 'completed')),
  sender_id         UUID NOT NULL REFERENCES users(id),
  receiver_id       UUID REFERENCES users(id),
  created_at        TIMESTAMP DEFAULT now()
);

-- ====== transfer_items table ====== --
CREATE TABLE IF NOT EXISTS transfer_items (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  song_name             VARCHAR(255) NOT NULL,
  artist_name           VARCHAR(255) NOT NULL,
  album                 VARCHAR(255),
  match_status          VARCHAR(50) DEFAULT 'pending' CHECK (match_status IN ('pending', 'matched', 'not_found')),
  transfer_request_id   UUID NOT NULL REFERENCES transfer_requests(id),
  created_at            TIMESTAMP DEFAULT now()
);

-- ====== platform_auth table ====== --
CREATE TABLE IF NOT EXISTS platform_auth (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id         UUID NOT NULL REFERENCES users(id),
  platform        VARCHAR(50) NOT NULL CHECK (platform IN ('spotify', 'apple_music', 'youtube_music')),
  access_token    TEXT NOT NULL,
  refresh_token   TEXT,
  expires_at      TIMESTAMP,
  created_at      TIMESTAMP DEFAULT now(),
  UNIQUE(user_id, platform)
);
