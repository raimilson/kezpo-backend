from apscheduler.schedulers.background import BackgroundScheduler
import time
from app import list_trackers, update_tracker

scheduler = BackgroundScheduler()

def refresh_all():
    trackers = list_trackers()
    for serial in trackers:
        update_tracker(serial)

scheduler.add_job(refresh_all, "interval", minutes=5)
scheduler.start()

try:
    while True:
        time.sleep(10)
except:
    scheduler.shutdown()

