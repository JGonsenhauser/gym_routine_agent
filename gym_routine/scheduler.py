import schedule
import time
from datetime import datetime
from .config import load_config
from .generator import generate_workout
from .email_handler import send_workout_email, check_for_replies
from .state import increment_week, get_week_index
import logging

logging.basicConfig(level=logging.INFO)

def daily_routine():
    config = load_config()['schedule']
    today = datetime.now().strftime('%A')
    if today in config['days']:
        day_index = config['days'].index(today)
        workout = generate_workout(day_index)
        send_workout_email(workout)
        check_for_replies()
        increment_week()

def send_test_workout():
    """Send a test workout email for day 0 (Push day)"""
    workout = generate_workout(0)
    send_workout_email(workout)
    logging.info("Test workout email sent.")

def start_scheduler():
    config = load_config()['schedule']
    schedule.every().day.at(config['time']).do(daily_routine)
    # Also check for replies every hour or so
    schedule.every(1).hours.do(check_for_replies)

    logging.info("Scheduler started. Waiting for scheduled times...")
    while True:
        schedule.run_pending()
        time.sleep(60)