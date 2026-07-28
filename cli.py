import argparse
from datetime import datetime, timedelta

from activity_processor import process_created_activity
from db import init_db, mark_activity_notified
from req import get_strava_activities
from telegram_notify import TelegramNotificationError, send_activity_notification


def process_and_notify(activity_id: int) -> None:
    result = process_created_activity(activity_id)
    print(f"Activity {activity_id}: {result.status}")

    if result.status != "updated" or result.activity is None:
        return

    try:
        send_activity_notification(result.activity)
    except TelegramNotificationError as error:
        print(f"Telegram notification failed for activity {activity_id}: {error}")
    else:
        mark_activity_notified(activity_id)
        print(f"Telegram notification sent for activity {activity_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RideOps manual operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    process_parser = subparsers.add_parser("process", help="Process one Strava activity")
    process_parser.add_argument("activity_id", type=int)

    backfill_parser = subparsers.add_parser("backfill", help="Process recent Strava activities")
    backfill_parser.add_argument("--days", type=int, default=7)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    init_db()

    if args.command == "process":
        process_and_notify(args.activity_id)
        return 0

    if args.days < 1:
        raise ValueError("--days must be at least 1")

    end_time = datetime.now()
    start_time = end_time - timedelta(days=args.days)
    activities = get_strava_activities(end=end_time, start=start_time)
    for activity in activities:
        process_and_notify(activity["id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
