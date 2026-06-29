import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

load_dotenv()


BASE_URL = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"


TOKEN_FILE = Path(".tokens/strava.json")

def load_token_state():
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            if data["expires_at"] < datetime.now().timestamp():
                print("Access token expired. Refreshing...")
                data = refresh_access_token(data)
                print("Access token refreshed.")

            return data
    else:
        raise Exception("Token file not found")

def refresh_access_token(token_state):
    
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    
    
    if not token_state:
        raise Exception("Token state not found. Cannot refresh access token.")
    
    
    response = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": token_state["refresh_token"],
        "client_id": client_id,
        "client_secret": client_secret,
    })
    
    if response.status_code == 200:
        new_token_state = response.json()
        with open(TOKEN_FILE, "w") as f:
            json.dump(new_token_state, f)
        print("Strava token refreshed successfully.")
        
        return new_token_state
    else:
        raise Exception(f"Failed to refresh Strava token: {response.status_code} - {response.text}")
    
    



def get_headers():
    token_state = load_token_state()
    
    if not token_state:
        raise Exception("Token state not found.")
    
    access_token = token_state["access_token"]

        

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def get_strava_activities(end: datetime, start: datetime):
    activities = []
    page = 1
    
    
    
    print(f"Fetching activities from {start} to {end}...")

    while True:
        r = requests.get(
            f"{BASE_URL}/athlete/activities",
            headers=get_headers(),
            params={
                "after": int(start.timestamp()),
                "before": int(end.timestamp()),
                "page": page,
                "per_page": 100,
            },
        )
        print(f"Fetching page {page}... Status code: {r.status_code}")

        if r.status_code != 200:
            raise Exception(f"Error fetching activities: {r.status_code} - {r.text}")

        data = r.json()

        if not data:
            break

        activities.extend(data)
        page += 1

    return activities


def mark_activity_as_commute_and_mute(activity_id: int) -> bool:
    r = requests.put(
        f"{BASE_URL}/activities/{activity_id}",
        headers=get_headers(),
        json={
            "commute": True,
            "hide_from_home": True,
        },
    )

    if r.status_code == 200:
        return True

    print(f"Error updating activity {activity_id}: {r.status_code} - {r.text}")
    return False