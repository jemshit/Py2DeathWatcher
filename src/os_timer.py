"""
for using custom cron tab (link): "crontab /home/username/mycrontab"
view (linked crontab file) : "crontab -l"
edit (linked crontab file): "crontab -e"
remove (unlink): "crontab -r"

use "mail" to read logs. press "enter" for details of each mail
"""

import os
from datetime import datetime

from crontab import CronTab, CronItem

from config import PROJECT_DIR
from log import log

DAY_SCHEDULE_ID = "daySchedule"
HOUR_SCHEDULE_ID = "hourSchedule"
MINUTE_SCHEDULE_ID = "minuteSchedule"

USER_CRONTAB_ENABLED = True
TAB_FILE = os.path.join(PROJECT_DIR, "files/cron_jobs.tab")
LOG_FILE = os.path.join(PROJECT_DIR, "files/cron_log.txt")

SCRIPT_PATH = os.path.abspath(os.path.join(PROJECT_DIR, "src/app.py"))
ACTIVATE_VENV = f". {PROJECT_DIR}/venv/bin/activate"
DEACTIVATE_VENV = f"deactivate"
COMMAND = f"{ACTIVATE_VENV}; {SCRIPT_PATH} >> {LOG_FILE} 2>&1; {DEACTIVATE_VENV}"


class OsTimer:
    def __init__(self):
        # loads current user's cronTab, unix only
        self.cron = CronTab(user=True)

    # day
    def is_repeating_day_scheduled(self) -> CronItem:
        job_iterator = self.cron.find_comment(DAY_SCHEDULE_ID)
        return next(job_iterator, None)

    def schedule_repeating_day(self, hour: int):
        job: CronItem = self.cron.new(command=COMMAND, comment=DAY_SCHEDULE_ID)
        job.day.every(1)
        job.hour.on(hour)
        job.minute.on(0)
        job.enable()
        try:
            log(f"Scheduled Job: {job.description(use_24hour_time_format=True)}")
        except ValueError:
            # https://github.com/pypa/pipenv/issues/187
            log(f"Scheduled Daily Job")
        self.cron.write_to_user()

    def cancel_repeating_day(self):
        self.cron.remove_all(comment=DAY_SCHEDULE_ID)
        self.cron.write_to_user()

    # hour
    def is_repeating_hour_scheduled(self) -> CronItem:
        job_iterator = self.cron.find_comment(HOUR_SCHEDULE_ID)
        return next(job_iterator, None)

    def schedule_repeating_hour(self):
        job: CronItem = self.cron.new(command=COMMAND, comment=HOUR_SCHEDULE_ID)
        # job.every(1).hours()
        job.hour.every(1)
        job.minute.on(1)
        job.enable()
        try:
            log(f"Scheduled Job: {job.description(use_24hour_time_format=True)}")
        except ValueError:
            # https://github.com/pypa/pipenv/issues/187
            log(f"Scheduled Hourly Job")
        self.cron.write_to_user()

    def cancel_repeating_hour(self):
        self.cron.remove_all(comment=HOUR_SCHEDULE_ID)
        self.cron.write_to_user()

    # minute
    def is_repeating_minute_scheduled(self) -> CronItem:
        job_iterator = self.cron.find_comment(MINUTE_SCHEDULE_ID)
        return next(job_iterator, None)

    def schedule_repeating_minute(self):
        job: CronItem = self.cron.new(command=COMMAND, comment=MINUTE_SCHEDULE_ID)
        job.minute.every(1)
        job.enable()
        try:
            log(f"Scheduled Job: {job.description(use_24hour_time_format=True)}")
        except ValueError:
            # https://github.com/pypa/pipenv/issues/187
            log(f"Scheduled Minute Job")
        self.cron.write_to_user()

    def cancel_repeating_minute(self):
        self.cron.remove_all(comment=MINUTE_SCHEDULE_ID)
        self.cron.write_to_user()

    #
    def cancel_all_timers(self):
        self.cron.remove_all(comment=DAY_SCHEDULE_ID)
        self.cron.remove_all(comment=HOUR_SCHEDULE_ID)
        self.cron.remove_all(comment=MINUTE_SCHEDULE_ID)
        self.cron.write_to_user()


def log_next_schedule(job: CronItem):
    schedule = job.schedule(date_from=datetime.now())
    next_datetime = schedule.get_next()
    log(f"\nNext Schedule Date: {next_datetime}")


if __name__ == '__main__':
    OsTimer().schedule_repeating_minute()
