import schedule
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import load_config
from .generator import generate_workout
from .email_handler import send_workout_email, check_for_replies
from .state import increment_week, get_week_index
import logging

logging.basicConfig(level=logging.INFO)

FLORIDA_TZ = ZoneInfo("America/New_York")

def daily_routine():
    config = load_config()['schedule']
    now_florida = datetime.now(FLORIDA_TZ)
    today = now_florida.strftime('%A')
    
    logging.info(f"Checking routine for Florida day: {today} at {now_florida.strftime('%H:%M:%S %Z')}")
    
    if today in config['days']:
        day_index = config['days'].index(today)
        workout = generate_workout(day_index)
        send_workout_email(workout)
        check_for_replies()
        increment_week()
    else:
        logging.info(f"No workout scheduled for {today}")

def send_test_workout():
    """Send a test workout email for day 0 (Push day)"""
    workout = generate_workout(0)
    send_workout_email(workout)
    logging.info("Test workout email sent.")

def start_scheduler():
    config = load_config()['schedule']
    target_time_str = config['time']  # e.g. "03:00"
    target_hour, target_min = map(int, target_time_str.split(':'))
    
    logging.info(f"Scheduler started. Target: {target_time_str} Florida time (America/New_York)")
    
    while True:
        now_florida = datetime.now(FLORIDA_TZ)
        current_hour = now_florida.hour
        current_min  = now_florida.minute
        
        # Reduced-noise debug (every 5 min)
        if current_min % 5 == 0:
            logging.info(
                f"Florida: {now_florida.strftime('%Y-%m-%d %H:%M:%S %Z')} | "
                f"Hour: {current_hour:02d}:{current_min:02d}"
            )
        
        if current_hour == target_hour and current_min == target_min:
            logging.info("Target time reached — executing daily routine")
            daily_routine()
            time.sleep(70)  # avoid multiple triggers in same minute
        
        if current_min == 0:
            check_for_replies()
        
        time.sleep(60)