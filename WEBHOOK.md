# Strava webhook server

RideOps exposes its Strava callback at `/strava/webhook`.

## Setup

1. Set a long random `STRAVA_WEBHOOK_VERIFY_TOKEN` in `.env`.
2. Start the service:

   ```bash
   docker compose up --build -d
   ```

   For direct local execution:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
   .\.venv\Scripts\uvicorn server:app --host 0.0.0.0 --port 8000
   ```

3. Expose the service over public HTTPS and create the Strava push subscription using:

   ```text
   https://<public-host>/strava/webhook
   ```

   Use the same verification token in the Strava subscription request.

## Endpoints

- `GET /strava/webhook` validates a Strava subscription. It verifies `hub.mode` and `hub.verify_token`, then returns the `hub.challenge` value.
- `POST /strava/webhook` immediately acknowledges incoming events. Only `activity` `create` events are queued for background processing; update, delete, and athlete events are acknowledged as ignored.
- `GET /health` is the container health endpoint.

## Processing

The webhook event supplies an activity ID, so RideOps fetches the full activity from Strava before evaluating it. An activity with a start or end point inside the configured work radius is marked as a commute and hidden from the home feed. Successfully updated commutes are saved in SQLite for deduplication.

After a successful Strava commute update, webhook processing sends one Telegram notification and marks the activity notified only when delivery succeeds. A Telegram failure does not undo the Strava edit; the notification remains pending.

## Required Strava permissions

The authorizing athlete needs `activity:read` and `activity:write`. Add `activity:read_all` when Only Me activities must be read or updated.