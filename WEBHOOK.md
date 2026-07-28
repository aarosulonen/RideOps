# Strava webhook server

Set `STRAVA_WEBHOOK_VERIFY_TOKEN` to a long random value in `.env`, then either
start the Docker service or run the server directly:

```powershell
docker compose up --build -d
```

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\uvicorn server:app --host 0.0.0.0 --port 8000
```

Expose `https://<public-host>/strava/webhook` through a public HTTPS tunnel or
deployment, then create the Strava push subscription with that URL and the same
verification token. The athlete token needs `activity:read` and `activity:write`;
add `activity:read_all` when Only Me activities must be read or updated.

The endpoint immediately acknowledges deliveries. It fetches and processes only
new activity events: an activity beginning or ending inside the configured work
radius is marked as a commute and hidden from the home feed.