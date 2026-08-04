# RideOps

RideOps automatically handles Strava commute activities. Its webhook server evaluates newly created activities, marks qualifying rides as commutes, and hides them from the home feed. A CLI is available for manual processing and recovery backfills.

## What it does

- Receives Strava activity-create webhook events at `/strava/webhook`.
- Fetches full activity details from Strava and applies the configured work-radius rule.
- Updates qualifying activities with `commute: true` and `hide_from_home: true`.
- Stores successfully updated commutes in SQLite to avoid duplicate updates.
- Refreshes expired Strava access tokens automatically.
- Sends Telegram alerts after successful commute updates from the webhook or manual CLI.

## Project structure

```text
RideOps/
├── server.py             # FastAPI webhook and health endpoints
├── activity_processor.py # Shared activity processing workflow
├── activity_rules.py     # Commute classification rule
├── cli.py                # Manual process and backfill commands
├── req.py                # Strava API client and token refresh logic
├── db.py                 # SQLite schema and activity persistence
├── telegram_notify.py    # Telegram message formatting and delivery
├── Dockerfile            # Webhook server image
├── docker-compose.yml    # Persistent local/host deployment
└── .env.example          # Required environment variables
```

## Configuration

Create `.env` from `.env.example` and provide:

```env
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_WEBHOOK_VERIFY_TOKEN=

WORK_COORD_LAT=
WORK_COORD_LON=
CHECK_RADIUS_METERS=500

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Place the refreshable [Strava OAuth token JSON](https://developers.strava.com/docs/authentication/) at `.tokens/strava.json`. It must include `access_token`, `refresh_token`, and `expires_at`.

The authorizing athlete needs `activity:read` and `activity:write`. Add `activity:read_all` when Only Me activities must be read or updated.

## Docker webhook server

Start the production-style local service:

```bash
docker compose up --build -d
```

The server listens on port 8000. [Configure Strava](https://developers.strava.com/docs/webhooks/) with the public callback URL:

```text
https://<public-host>/strava/webhook
```

Docker bind-mounts `.tokens` so token refreshes persist on the host and stores SQLite data in the `rideops-data` named volume. The server initializes the database on startup. Check it with:

```bash
curl http://localhost:8000/health
```

The container defaults to UID/GID `1000:1000` so it can update the
bind-mounted token file. If the host user has different IDs, set them when
building:

```bash
RIDEOPS_UID=$(id -u) RIDEOPS_GID=$(id -g) docker compose up --build -d
```

## Manual operations

Install development dependencies when running locally:

```bash
python -m pip install -r requirements-dev.txt
```

Process one known activity through the same commute workflow used by the webhook:

```bash
python cli.py process <activity-id>
```

Backfill recent activities manually; the default window is seven days:

```bash
python cli.py backfill
python cli.py backfill --days 30
```

Every successful commute update sends one Telegram notification. If Telegram delivery fails, the Strava edit remains in place and its notification stays pending.

## Tests

```bash
python -m pytest -q
```
