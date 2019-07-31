"""
chmod +x src/app.py for creating files
"""

import os
import sys
from os.path import exists

SRC_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.abspath(os.path.join(SRC_DIR, os.pardir))
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

from src.watcher import Watcher
from src.log import log
from src.os_timer import TAB_FILE, LOG_FILE, OsTimer, USER_CRONTAB_ENABLED
from src.twitter_api import ACCESS_TOKEN_FILENAME, create_api_helper, TwitterApiHelper


def initialize_files():
    if not USER_CRONTAB_ENABLED and not exists(TAB_FILE):
        log("\nCreating CRON TAB file for first time")
        file = open(TAB_FILE, "w+")
        # file.write("MAILTO=\"\"")  # to disable all emails from cron job
        file.close()

    if not exists(LOG_FILE):
        log("\nCreating CRON LOG file for first time")
        file = open(LOG_FILE, "w+")
        file.close()

    if not exists(ACCESS_TOKEN_FILENAME):
        log("\nCreating ACCESS_TOKEN FILE for first time")
        file = open(LOG_FILE, "w+")
        file.close()


if __name__ == '__main__':
    log("\n-------------------------------")
    initialize_files()

    api_helper = create_api_helper(ACCESS_TOKEN_FILENAME, TwitterApiHelper())

    os_timer = OsTimer()
    watcher = Watcher(api_helper, os_timer)
    watcher.start_the_watch()

    log("\n-------------------------------")
