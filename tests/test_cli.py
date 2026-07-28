import cli
from activity_processor import ProcessResult
from telegram_notify import TelegramNotificationError


def test_process_command_notifies_after_an_update(monkeypatch):
    activity = {"id": 12345, "name": "Ride to work"}
    initialized = []
    notified = []
    marked_notified = []
    monkeypatch.setattr(cli, "init_db", lambda: initialized.append(True))
    monkeypatch.setattr(
        cli,
        "process_created_activity",
        lambda activity_id: ProcessResult("updated", activity),
    )
    monkeypatch.setattr(cli, "send_activity_notification", notified.append)
    monkeypatch.setattr(cli, "mark_activity_notified", marked_notified.append)

    assert cli.main(["process", "12345"]) == 0
    assert initialized == [True]
    assert notified == [activity]
    assert marked_notified == [12345]


def test_process_command_keeps_notification_pending_after_telegram_failure(monkeypatch):
    activity = {"id": 12345, "name": "Ride to work"}
    marked_notified = []
    monkeypatch.setattr(cli, "init_db", lambda: None)
    monkeypatch.setattr(
        cli,
        "process_created_activity",
        lambda activity_id: ProcessResult("updated", activity),
    )
    monkeypatch.setattr(
        cli,
        "send_activity_notification",
        lambda _: (_ for _ in ()).throw(TelegramNotificationError("unavailable")),
    )
    monkeypatch.setattr(cli, "mark_activity_notified", marked_notified.append)

    assert cli.main(["process", "12345"]) == 0
    assert marked_notified == []


def test_backfill_defaults_to_seven_days_and_processes_each_activity(monkeypatch):
    processed_ids = []
    list_calls = []
    monkeypatch.setattr(cli, "init_db", lambda: None)
    monkeypatch.setattr(
        cli,
        "get_strava_activities",
        lambda end, start: list_calls.append((start, end)) or [{"id": 1}, {"id": 2}],
    )
    monkeypatch.setattr(
        cli,
        "process_created_activity",
        lambda activity_id: processed_ids.append(activity_id) or ProcessResult("not_commute"),
    )

    assert cli.main(["backfill"]) == 0
    assert (list_calls[0][1] - list_calls[0][0]).days == 7
    assert processed_ids == [1, 2]
