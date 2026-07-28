import activity_processor


def test_commute_activity_is_updated_and_recorded(monkeypatch):
    activity = {"id": 12345, "name": "Ride to work"}
    updated_ids = []
    inserted = []
    monkeypatch.setattr(activity_processor, "get_activity_by_strava_id", lambda _: None)
    monkeypatch.setattr(activity_processor, "get_strava_activity", lambda _: activity)
    monkeypatch.setattr(activity_processor, "is_commute", lambda _: True)
    monkeypatch.setattr(
        activity_processor,
        "mark_activity_as_commute_and_mute",
        lambda activity_id: updated_ids.append(activity_id) or True,
    )
    monkeypatch.setattr(activity_processor, "insert_activity", inserted.append)

    activity_processor.process_created_activity(12345)

    assert updated_ids == [12345]
    assert inserted == [activity]


def test_non_commute_activity_is_not_updated_or_recorded(monkeypatch):
    activity = {"id": 12345, "name": "Weekend ride"}
    monkeypatch.setattr(activity_processor, "get_activity_by_strava_id", lambda _: None)
    monkeypatch.setattr(activity_processor, "get_strava_activity", lambda _: activity)
    monkeypatch.setattr(activity_processor, "is_commute", lambda _: False)
    monkeypatch.setattr(
        activity_processor,
        "mark_activity_as_commute_and_mute",
        lambda _: (_ for _ in ()).throw(AssertionError("must not update")),
    )
    monkeypatch.setattr(
        activity_processor,
        "insert_activity",
        lambda _: (_ for _ in ()).throw(AssertionError("must not insert")),
    )

    activity_processor.process_created_activity(12345)


def test_existing_activity_is_not_fetched_or_updated(monkeypatch):
    monkeypatch.setattr(activity_processor, "get_activity_by_strava_id", lambda _: object())
    monkeypatch.setattr(
        activity_processor,
        "get_strava_activity",
        lambda _: (_ for _ in ()).throw(AssertionError("must not fetch")),
    )

    activity_processor.process_created_activity(12345)


def test_fetch_failure_is_contained(monkeypatch):
    monkeypatch.setattr(activity_processor, "get_activity_by_strava_id", lambda _: None)
    monkeypatch.setattr(activity_processor, "get_strava_activity", lambda _: None)

    activity_processor.process_created_activity(12345)
