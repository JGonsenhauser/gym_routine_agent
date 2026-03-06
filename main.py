#!/usr/bin/env python3

import argparse
from gym_routine.scheduler import start_scheduler, send_test_workout

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gym Routine Email Agent")
    parser.add_argument('--test', action='store_true', help='Send a test workout email immediately')
    args = parser.parse_args()

    if args.test:
        send_test_workout()
    else:
        start_scheduler()