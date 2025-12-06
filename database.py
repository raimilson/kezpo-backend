import sqlite3

DB_NAME = "trackers.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial TEXT,
            timestamp INTEGER,
            latitude REAL,
            longitude REAL,
            confidence INTEGER,
            accuracy INTEGER,
            status INTEGER,
            battery TEXT,
            UNIQUE(serial, timestamp)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS trackers (
            serial TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def add_tracker(serial):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO trackers (serial) VALUES (?)", (serial,))
    conn.commit()
    conn.close()

def list_trackers():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT serial FROM trackers")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def store_positions(serial, positions):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for p in positions:
        c.execute("""
            INSERT OR IGNORE INTO positions
            (serial, timestamp, latitude, longitude, confidence, accuracy, status, battery)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            serial,
            p["seenTime"],
            p["latitude"],
            p["longitude"],
            p.get("confidence", 0),
            p.get("accuracy", 0),
            p.get("status", 0),
            p.get("batteryStatus", "")
        ))
    conn.commit()
    conn.close()

def get_positions(serial):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, latitude, longitude, confidence FROM positions
        WHERE serial = ?
        ORDER BY timestamp ASC
    """, (serial,))
    rows = c.fetchall()
    conn.close()
    return rows

