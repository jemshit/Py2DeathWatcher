import json
import time
from typing import List

from tweepy import Status

from log import log
from os_timer import OsTimer, log_next_schedule
from twitter_api import TwitterApiHelper

WATCH_END_EPOCH_SEC = 1577836800  # 2020, 01/01, 00:00:00 GMT
HOURS_IN_A_DAY = 24
SECONDS_IN_A_DAY = 24 * 60 * 60
MINUTES_IN_A_DAY = 24 * 60

TWITTER_USER_ID = "Python2Watcher"
WATCH_END_TEXT = "Now My Watch Has Ended!"

DAY_SCHEDULE_TIME = 6


class Watcher:
    def __init__(self, api_helper: TwitterApiHelper, os_timer: OsTimer):
        log("\n-->> Creating Watcher...")
        self.api_helper = api_helper
        self.os_timer = os_timer

    def create_text(self, time: int, unit: str) -> str:
        return f"{time} {unit} left. #python #python2"

    def is_this_tweet_sent(self, text: str) -> bool:
        timeline: List[Status] = self.api_helper.get_user_timeline(TWITTER_USER_ID)
        if len(timeline) == 0:
            return False
        else:
            recent_tweet_json = json.dumps(timeline[0]._json)
            recent_tweet = json.loads(recent_tweet_json)
            recent_tweet_text: str = recent_tweet["text"]

            recent_tweet_text_words = recent_tweet_text.split()
            text_words = text.split()

            if len(recent_tweet_text_words) >= 2 and len(text_words) >= 2:
                if recent_tweet_text_words[0] == text_words[0] and recent_tweet_text_words[1] == text_words[1]:
                    return True
                else:
                    return False
            else:
                return True if recent_tweet_text == text else False

    def post_left_units_tweet(self, time: int, unit: str, units: str):
        tweet = self.create_text(time, units if time > 1 else unit)
        if not self.is_this_tweet_sent(tweet):
            self.api_helper.post_tweet(tweet)
            log(f"-> Tweet Sent: \"{tweet}\"")
        else:
            log(f"-> Tweet Already Exists: \"{tweet}\"")

    def post_watch_ended_tweet(self):
        self.api_helper.post_tweet(WATCH_END_TEXT)
        log(f"-> Tweet Sent: \"{WATCH_END_TEXT}\"")
        log("\n WATCH HAS ENDED!")

    def start_the_watch(self, now_epoch_sec: int = time.time()):
        left_sec = WATCH_END_EPOCH_SEC - now_epoch_sec

        if left_sec <= 0:
            self.end_the_watch()

        left_days = int(left_sec / SECONDS_IN_A_DAY)

        if left_days < 1:
            left_hours = int(left_sec / 60 / 60)
            if left_hours >= 1:
                self.post_left_units_tweet(left_hours, "hour", "hours")

                if left_hours == 1:
                    # [1-2) hours
                    if self.os_timer.is_repeating_hour_scheduled() is not None:
                        self.os_timer.cancel_repeating_hour()

                    # check every minute for 0-59 minutes
                    minute_job = self.os_timer.is_repeating_minute_scheduled()
                    if minute_job is None:
                        self.os_timer.schedule_repeating_minute()
                    else:
                        log_next_schedule(minute_job)
                else:
                    # >1 hours
                    hour_job = self.os_timer.is_repeating_hour_scheduled()
                    if hour_job is None:
                        self.os_timer.schedule_repeating_hour()
                    else:
                        log_next_schedule(hour_job)
            else:
                left_mins = int(left_sec / 60)
                if left_mins >= 1:
                    self.post_left_units_tweet(left_mins, "minute", "minutes")

                    minute_job = self.os_timer.is_repeating_minute_scheduled()
                    if minute_job is None:
                        self.os_timer.schedule_repeating_minute()
                    else:
                        log_next_schedule(minute_job)

                elif self.is_this_tweet_sent(WATCH_END_TEXT):
                    self.end_the_watch()

                else:
                    self.post_watch_ended_tweet()
                    self.end_the_watch()

        else:
            self.post_left_units_tweet(left_days, "day", "days")
            if left_days >= 2:
                day_job = self.os_timer.is_repeating_day_scheduled()
                if day_job is None:
                    self.os_timer.schedule_repeating_day(DAY_SCHEDULE_TIME)
                else:
                    log_next_schedule(day_job)
            else:
                # [1-2) days left
                if self.os_timer.is_repeating_day_scheduled() is not None:
                    self.os_timer.cancel_repeating_day()

                # check every hour for 0-23 hours
                hour_job = self.os_timer.is_repeating_hour_scheduled()
                if hour_job is None:
                    self.os_timer.schedule_repeating_hour()
                else:
                    log_next_schedule(hour_job)

    def end_the_watch(self):
        log("End the Watch!")
        self.os_timer.cancel_all_timers()
