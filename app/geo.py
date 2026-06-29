from math import radians, sin, cos, sqrt, atan2
import dotenv
import os

dotenv.load_dotenv()
home_lat = float(os.getenv("HOME_COORDS_LAT"))
home_lon = float(os.getenv("HOME_COORDS_LON"))
work_lat = float(os.getenv("WORK_COORDS_LAT"))
work_lon = float(os.getenv("WORK_COORDS_LON"))

is_near_radius = float(os.getenv("IS_NEAR_RADIUS", 500))  # Default to 500 meters if not set



# Haversine formula to calculate the distance between two coordinates in meters
def distance_between_coords(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
  
  
def is_near_home(lat, lon):
    return distance_between_coords(lat, lon, home_lat, home_lon) <= is_near_radius
  
def is_near_work(lat, lon):
    return distance_between_coords(lat, lon, work_lat, work_lon) <= is_near_radius