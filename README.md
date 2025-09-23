Event Scraper + Slack Commands
==============================

Run a scraper for Eventbrite pages, save to MongoDB, post Slack notifications, and provide a `/events` slash command to query recent events.

Requirements
------------
- Python 3.13 (project includes `venv/`)
- MongoDB running locally or remotely
- Slack workspace and custom app
- ngrok (or any public tunneling solution) for slash commands

Setup
-----
1. Create and activate virtualenv, install deps:
   ```bash
   cd /Users/tylersmith/eventScraper
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create `.env` (copy from `.env.example`):
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_SIGNING_SECRET=your-signing-secret
   SLACK_CHANNEL_ID=C0123456789
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/
   ```

3. Slack app configuration:
   - OAuth & Permissions → Bot Token Scopes: `chat:write`, `commands`
   - Install App → copy Bot User OAuth Token
   - Basic Information → copy Signing Secret
   - Slash Commands: create `/events` with Request URL: `https://<your-ngrok>.ngrok.io/slack/commands`

Run
---
Scraper (saves new events, posts Slack summaries):
```bash
python main.py
```

Slash command server:
```bash
python -m app.server
# in another terminal
ngrok http 5000
```

Use in Slack
------------
- `/events newbrunswick 5`
- `/events nj 10`
- Defaults: region = `nj`, limit = 5

Health check
------------
`GET /health` → `{ ok: true }`


