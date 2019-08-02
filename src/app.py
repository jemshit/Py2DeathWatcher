#!/usr/bin/env python3
"""
chmod +x src/app.py for creating files
"""

from os.path import exists

from log import log
from os_timer import TAB_FILE, LOG_FILE, USER_CRONTAB_ENABLED, OsTimer
from twitter_api import ACCESS_TOKEN_FILENAME, create_api_helper, TwitterApiHelper
from watcher import Watcher


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
