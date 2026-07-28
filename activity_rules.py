from geo import is_near_work


def is_commute(activity: dict) -> bool:
    start_latlon = activity.get("start_latlng")
    end_latlon = activity.get("end_latlng")

    if (
        not start_latlon
        or not end_latlon
        or len(start_latlon) != 2
        or len(end_latlon) != 2
        or None in start_latlon
        or None in end_latlon
    ):
        print(f"Activity {activity.get('name')} is missing start or end coordinates.")
        return False

    return is_near_work(start_latlon[0], start_latlon[1]) or is_near_work(
        end_latlon[0], end_latlon[1]
    )
