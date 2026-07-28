import logging

import requests

from main import is_commute
from db import get_activity_by_strava_id, insert_activity
from req import BASE_URL, get_headers, mark_activity_as_commute_and_mute


logger = logging.getLogger(__name__)


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


def process_created_activity(activity_id: int) -> None:
    """Apply RideOps' commute rule to a newly-created Strava activity."""
    if get_activity_by_strava_id(activity_id):
        logger.info("Activity %s was already updated; skipping.", activity_id)
        return

    activity = get_strava_activity(activity_id)
    if not activity:
        logger.warning("Could not fetch new Strava activity %s.", activity_id)
        return

    if not is_commute(activity):
        logger.info("Activity %s is not a commute.", activity_id)
        return

    if mark_activity_as_commute_and_mute(activity_id):
        insert_activity(activity)
        logger.info("Updated commute activity %s.", activity_id)
    else:
        logger.warning("Could not update commute activity %s.", activity_id)
