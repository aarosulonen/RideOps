import logging
from dataclasses import dataclass

import requests

from activity_rules import is_commute
from db import get_activity_by_strava_id, insert_activity, mark_activity_notified
from req import BASE_URL, get_headers, mark_activity_as_commute_and_mute
from telegram_notify import TelegramNotificationError, send_activity_notification


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessResult:
    status: str
    activity: dict | None = None
    notification_attempted: bool = False


def get_strava_activity(activity_id: int) -> dict | None:
    response = requests.get(
        f"{BASE_URL}/activities/{activity_id}",
        headers=get_headers(),
    )
    if response.status_code == 200:
        return response.json()

    logger.warning(
        "Unable to fetch activity %s from Strava: %s - %s",
        activity_id,
        response.status_code,
        response.text,
    )
    return None


def notify_activity(activity: dict) -> bool:
    try:
        send_activity_notification(activity)
    except TelegramNotificationError as error:
        logger.warning("Telegram notification failed for activity %s: %s", activity["id"], error)
        return False

    mark_activity_notified(activity["id"])
    logger.info("Telegram notification sent for activity %s.", activity["id"])
    return True


def process_created_activity(activity_id: int) -> ProcessResult:
    """Apply RideOps' commute rule and notify for a newly-created activity."""
    if get_activity_by_strava_id(activity_id):
        logger.info("Activity %s was already updated; skipping.", activity_id)
        return ProcessResult("already_processed")

    activity = get_strava_activity(activity_id)
    if not activity:
        logger.warning("Could not fetch new Strava activity %s.", activity_id)
        return ProcessResult("fetch_failed")

    if not is_commute(activity):
        logger.info("Activity %s is not a commute.", activity_id)
        return ProcessResult("not_commute", activity)

    if mark_activity_as_commute_and_mute(activity_id):
        insert_activity(activity)
        logger.info("Updated commute activity %s.", activity_id)
        notify_activity(activity)
        return ProcessResult("updated", activity, notification_attempted=True)

    logger.warning("Could not update commute activity %s.", activity_id)
    return ProcessResult("update_failed", activity)