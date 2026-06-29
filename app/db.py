import sqlite3

DB_PATH = "rideops.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY,
            strava_id INTEGER UNIQUE,
            name TEXT,
            distance REAL,
            moving_time INTEGER,
            elapsed_time INTEGER,
            total_elevation_gain REAL,
            type TEXT,
            start_date TEXT,
            start_date_local TEXT,
            timezone TEXT,
            utc_offset REAL,
            notified INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    
    
def insert_activity(activity):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO activities (
            strava_id, name, distance, moving_time, elapsed_time,
            total_elevation_gain, type, start_date, start_date_local,
            timezone, utc_offset, notified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        activity['id'], activity['name'], activity['distance'],
        activity['moving_time'], activity['elapsed_time'],
        activity['total_elevation_gain'], activity['type'],
        activity['start_date'], activity['start_date_local'],
        activity['timezone'], activity['utc_offset'], 0
    ))
    
    conn.commit()
    conn.close()
  
def get_activity_by_strava_id(strava_id):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  
  cursor.execute('''
      SELECT * FROM activities
      WHERE strava_id = ?
  ''', (strava_id,))
  
  activity = cursor.fetchone()
  conn.close()
  
  return activity
