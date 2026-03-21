import time
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import load_config
from .generator import generate_workout
from .email_handler import send_workout_email, check_for_replies
from .state import increment_week, get_week_index
import logging

logger = logging.getLogger(__name__)

FLORIDA_TZ = ZoneInfo("America/New_York")


def daily_routine():
    config = load_config()['schedule']
    now_florida = datetime.now(FLORIDA_TZ)
    today = now_florida.strftime('%A')

    logger.info(f"Checking routine for Florida day: {today} at {now_florida.strftime('%H:%M:%S %Z')}")

    if today in config['days']:
        day_index = config['days'].index(today)
        workout = generate_workout(day_index)
        send_workout_email(workout)
        check_for_replies()
        increment_week()
    else:
        logger.info(f"No workout scheduled for {today}")


def send_test_workout():
    """Send a test workout email for day 0 (Push day)"""
    workout = generate_workout(0)
    send_workout_email(workout)
    logger.info("Test workout email sent.")


def start_scheduler():
    config = load_config()['schedule']
    target_time_str = config['time']  # e.g. "06:00"
    target_hour, target_min = map(int, target_time_str.split(':'))

    logger.info(f"Scheduler started. Target: {target_time_str} Florida time (America/New_York)")

    last_run_date = None  # tracks the date we last sent, prevents double-sends

    while True:
        now_florida = datetime.now(FLORIDA_TZ)
        current_hour = now_florida.hour
        current_min = now_florida.minute
        today_date = now_florida.date()

        # Reduced-noise debug (every 5 min)
        if current_min % 5 == 0:
            logger.info(
                f"Florida: {now_florida.strftime('%Y-%m-%d %H:%M:%S %Z')} | "
                f"Hour: {current_hour:02d}:{current_min:02d}"
            )

        # 5-minute window instead of exact minute match — prevents missed triggers
        in_window = (
            current_hour == target_hour
            and target_min <= current_min <= target_min + 4
        )

        if in_window and last_run_date != today_date:
            logger.info("Target time reached — executing daily routine")
            try:
                daily_routine()
                last_run_date = today_date
            except Exception as e:
                logger.exception(f"daily_routine() failed: {e}")
                # Don't set last_run_date so it retries next loop iteration

        # Check for email replies on the hour
        if current_min == 0:
            try:
                check_for_replies()
            except Exception as e:
                logger.exception(f"check_for_replies() failed: {e}")

        time.sleep(30)  # 30s for better reliability than 60s
