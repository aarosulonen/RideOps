import activity_processor
from telegram_notify import TelegramNotificationError


def _prepare_successful_commute(monkeypatch):
    activity = {"id": 12345, "name": "Ride to work"}
    monkeypatch.setattr(activity_processor, "get_activity_by_strava_id", lambda _: None)
    monkeypatch.setattr(activity_processor, "get_strava_activity", lambda _: activity)
    monkeypatch.setattr(activity_processor, "is_commute", lambda _: True)
    monkeypatch.setattr(activity_processor, "mark_activity_as_commute_and_mute", lambda _: True)
    monkeypatch.setattr(activity_processor, "insert_activity", lambda _: None)
    return activity


def test_successful_webhook_edit_sends_and_marks_telegram_notification(monkeypatch):
    activity = _prepare_successful_commute(monkeypatch)
    notified = []
    marked_notified = []
    monkeypatch.setattr(activity_processor, "send_activity_notification", notified.append)
    monkeypatch.setattr(activity_processor, "mark_activity_notified", marked_notified.append)

    result = activity_processor.process_created_activity(12345)

    assert result.status == "updated"
    assert result.notification_attempted is True
    assert notified == [activity]
    assert marked_notified == [12345]


def test_telegram_failure_keeps_successful_webhook_edit_pending(monkeypatch):
    _prepare_successful_commute(monkeypatch)
    marked_notified = []
    monkeypatch.setattr(
        activity_processor,
        "send_activity_notification",
        lambda _: (_ for _ in ()).throw(TelegramNotificationError("unavailable")),
    )
    monkeypatch.setattr(activity_processor, "mark_activity_notified", marked_notified.append)

    result = activity_processor.process_created_activity(12345)

    assert result.status == "updated"
    assert result.notification_attempted is True
    assert marked_notified == []
