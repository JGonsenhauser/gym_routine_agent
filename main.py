#!/usr/bin/env python3

import argparse
import logging
import os

# Centralized logging — file + console
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'gym_agent.log')),
        logging.StreamHandler()
    ]
)

from gym_routine.scheduler import start_scheduler, send_test_workout

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gym Routine Email Agent")
    parser.add_argument('--test', action='store_true', help='Send a test workout email immediately')
    args = parser.parse_args()

    if args.test:
        send_test_workout()
    else:
        start_scheduler()