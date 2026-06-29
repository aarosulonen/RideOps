from req import get_strava_activities, mark_activity_as_commute_and_mute
from geo import is_near_home, is_near_work
from db import insert_activity, get_activity_by_strava_id, init_db


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

    return is_near_work(start_latlon[0], start_latlon[1]) or is_near_work(end_latlon[0], end_latlon[1])


if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    init_db()  # Initialize the database and create the activities table if it doesn't exist

    DRY_RUN = False  # Change to False when you want to actually update Strava

    end_time = datetime.now()
    start_time = end_time - timedelta(days=100)

    activities = get_strava_activities(end=end_time, start=start_time)

    for activity in activities:
        given_strava_id = activity["id"]
        existing_activity = get_activity_by_strava_id(given_strava_id)
        
        if existing_activity:
            print(f"Activity {given_strava_id} already exists in the database. Skipping.")
            continue
    

        if is_commute(activity):
                  
            activity_id = activity["id"]
            name = activity.get("name", "Unnamed activity")
            start_date = activity.get("start_date")

            print(f"Commute activity found: {name} on {start_date}")

            if DRY_RUN:
                print(f"DRY RUN: would mute and mark as commute: {activity_id}")
            else:
                success = mark_activity_as_commute_and_mute(activity_id)

                if success:
                    print(f"Updated activity {activity_id}")
                    insert_activity(activity)