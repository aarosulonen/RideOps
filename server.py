import logging
import os

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query

from activity_processor import process_created_activity


logger = logging.getLogger(__name__)
app = FastAPI(title="RideOps Strava Webhook")


@app.get("/webhook")
def validate_webhook(
    mode: str | None = Query(None, alias="hub.mode"),
    verify_token: str | None = Query(None, alias="hub.verify_token"),
    challenge: str | None = Query(None, alias="hub.challenge"),
) -> dict[str, str]:
    expected_token = os.getenv("STRAVA_WEBHOOK_VERIFY_TOKEN")
    if mode != "subscribe" or not expected_token or verify_token != expected_token:
        raise HTTPException(status_code=403, detail="Webhook verification failed")
    if challenge is None:
        raise HTTPException(status_code=400, detail="Missing webhook challenge")
    return {"hub.challenge": challenge}


@app.post("/webhook")
def receive_webhook(event: dict, background_tasks: BackgroundTasks) -> dict[str, str]:
    if event.get("object_type") != "activity" or event.get("aspect_type") != "create":
        return {"status": "ignored"}

    activity_id = event.get("object_id")
    if not isinstance(activity_id, int):
        raise HTTPException(status_code=400, detail="Missing activity object_id")

    background_tasks.add_task(process_created_activity, activity_id)
    logger.info("Accepted create event for activity %s.", activity_id)
    return {"status": "accepted"}
