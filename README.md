# RideOps

RideOps is a small automation service for keeping Strava commute activity clean with minimal manual work. It fetches recent Strava activities, detects rides or activities that start or end near a configured work location, marks them as commutes, hides them from the home feed, stores processed activity metadata locally, and sends a Telegram notification when a commute is handled.

## What It Does

- Fetches Strava activities for a configurable recent time window.
- Detects commute activities using a Haversine distance check against work coordinates.
- Updates matching Strava activities with `commute: true` and `hide_from_home: true`.
- Stores processed activities in SQLite to avoid duplicate work.
- Refreshes expired Strava access tokens automatically.
- Sends Telegram alerts for newly processed commute activities.


## Project Structure

```text
RideOps/
├── cli.py               # Manual activity processing and backfill commands
├── activity_rules.py    # Commute classification rule
├── req.py               # Strava API client and token refresh logic
├── geo.py               # Distance calculation and work-location matching
├── db.py                # SQLite schema and activity persistence
├── telegram_notify.py   # Telegram message formatting and delivery
├── requirements.txt     # Python dependencies
└── .env.example         # Required environment variables
```

## Requirements

- Python 3
- A Strava API application
- A Strava token state file at `.tokens/strava.json`
- Optional: a Telegram bot token and chat ID for notifications

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Fill in:

```env
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=

WORK_COORD_LAT=
WORK_COORD_LON=
CHECK_RADIUS_METERS=500

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

RideOps also expects Strava token state at:

```text
.tokens/strava.json
```

The token state must include the fields returned by Strava OAuth, including `access_token`, `refresh_token`, and `expires_at`.

## Manual operations

Process one known Strava activity through the same commute workflow used by the
webhook:

```bash
python cli.py process <activity-id>
```

Backfill recent activities manually. The default window is seven days:

```bash
python cli.py backfill
python cli.py backfill --days 30
```

A manual run sends a Telegram notification only after it successfully updates a
commute activity. If Telegram delivery fails, the Strava edit remains in place
and the notification stays pending.

## Docker webhook server

The container runs the FastAPI webhook server, not the batch script. Create
`.env` from `.env.example`, place the refreshable Strava token in
`.tokens/strava.json`, then start it with:

```bash
docker compose up --build -d
```

Docker publishes the service on port 8000. Configure Strava with the public
callback URL `https://<public-host>/strava/webhook`. The `.tokens` directory is
bind-mounted so token refreshes persist on the host; SQLite data is retained in
the `rideops-data` named Docker volume. Ensure `.tokens` is writable by the
container user.

Check service health with:

```bash
curl http://localhost:8000/health
```