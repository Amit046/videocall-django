# 📹 VideoCall — Django WebRTC Video Calling App

A full-featured video calling web application built with **Django + Django Channels + WebRTC**.

## Features

- 🎥 Peer-to-peer video calls (WebRTC)
- 🔗 Shareable room codes — no sign-up needed
- 💬 In-call text chat
- 🎤 Mute/unmute microphone
- 📷 Toggle camera on/off
- 🖥️ Screen sharing
- 👥 Participant list
- 📋 One-click room code copy

## Quick Start

### 1. Install dependencies

```bash
cd videocall
pip install -r requirements.txt
```

### 2. Run migrations

```bash
python manage.py migrate
```

### 3. Start the server

```bash
# Using Daphne (recommended — supports WebSockets)
daphne -p 8000 videocall.asgi:application

# OR using Django dev server (Django 4.2+ supports ASGI natively)
python manage.py runserver
```

### 4. Open your browser

Visit: http://localhost:8000

## How to Use

1. **Create a Room** — Enter your name and a room name, click "Create Room"
2. **Share the Code** — Copy the room code from the top bar and share it
3. **Others Join** — They enter the code on the home page to join

## Architecture

```
Browser A                     Server (Django Channels)             Browser B
   |                               |                                   |
   |──── WebSocket connect ───────>|<────── WebSocket connect ─────────|
   |──── join (username) ─────────>|                                   |
   |<─── existing_users ──────────|                                   |
   |──── offer (SDP) ────────────>|──── offer (SDP) ─────────────────>|
   |<─── answer (SDP) ────────────|<──── answer (SDP) ────────────────|
   |──── ice_candidate ──────────>|──── ice_candidate ───────────────>|
   |<─────────────── Direct P2P WebRTC Video/Audio ─────────────────>|
```

- **Signaling**: Django Channels (WebSockets) using In-Memory channel layer
- **Media**: WebRTC peer-to-peer (no media server needed)
- **STUN**: Google's public STUN servers for NAT traversal

## Production Notes

- Replace `InMemoryChannelLayer` with Redis: `pip install channels-redis`
- Set `SECRET_KEY` to a secure value
- Add a TURN server for users behind strict NATs
- Set `DEBUG = False` and configure `ALLOWED_HOSTS`
- Use a proper database (PostgreSQL) instead of SQLite
