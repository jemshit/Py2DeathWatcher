from typing import List
from unittest import TestCase
from unittest.mock import MagicMock, Mock

from crontab import CronTab
from tweepy import Status

from src.os_timer import OsTimer
from src.watcher import Watcher, WATCH_END_TEXT, WATCH_END_EPOCH_SEC


class FakeWatcher(Watcher):
    pass


class TwitterApiHandler(object):
    pass


def __create_fake_user_timeline() -> List[Status]:
    status_1 = Status()
    status_1._json = {"text": "tweet_1 1. #"}
    status_2 = Status()
    status_2._json = {"text": "tweet_2 2. #"}
    return [status_2, status_1]


FAKE_USER_TIMELINE: List[Status] = __create_fake_user_timeline()


class TestWatcher(TestCase):

    def setUp(self) -> None:
        self.mock_api_helper: TwitterApiHandler = MagicMock()
        self.mock_os_timer: OsTimer = MagicMock()
        self.watcher = Watcher(self.mock_api_helper, self.mock_os_timer)

    def test_create_text(self):
        expected_day = "1 day left. #python #python2"

        result = self.watcher.create_text(1, 'day')

        self.assertEqual(expected_day, result)

    def test_is_this_tweet_sent_2(self):
        self.mock_api_helper.get_user_timeline = Mock(return_value=FAKE_USER_TIMELINE)
        tweet = "tweet_2 2. #"

        result = self.watcher.is_this_tweet_sent(tweet)

        self.assertEqual(True, result)

    def test_is_this_tweet_sent_3(self):
        self.mock_api_helper.get_user_timeline = Mock(return_value=FAKE_USER_TIMELINE)
        tweet = "tweet_3 1. #"

        result = self.watcher.is_this_tweet_sent(tweet)

        self.assertEqual(False, result)

    def test_post_left_units_tweet(self):
        self.mock_api_helper.post_tweet = MagicMock()

        self.watcher.post_left_units_tweet(1, "day", "days")

        assert self.mock_api_helper.post_tweet.called
        call_args, call_kwargs = self.mock_api_helper.post_tweet.call_args
        self.assertEqual("1 day left. #python #python2", call_args[0])

    def test_post_left_units_tweet_2(self):
        self.mock_api_helper.post_tweet = MagicMock()

        self.watcher.post_left_units_tweet(2, "day", "days")

        assert self.mock_api_helper.post_tweet.called
        call_args, call_kwargs = self.mock_api_helper.post_tweet.call_args
        self.assertEqual("2 days left. #python #python2", call_args[0])

    def test_post_watch_ended_tweet(self):
        self.mock_api_helper.post_tweet = MagicMock()

        self.watcher.post_watch_ended_tweet()

        assert self.mock_api_helper.post_tweet.called
        call_args, call_kwargs = self.mock_api_helper.post_tweet.call_args
        self.assertEqual(WATCH_END_TEXT, call_args[0])

    def test_start_watch_days_left(self):
        today = 1564053631  # 25.07.2019
        self.watcher.post_left_units_tweet = MagicMock()

        self.watcher.start_the_watch(today)

        assert self.watcher.post_left_units_tweet.called
        call_args, call_kwargs = self.watcher.post_left_units_tweet.call_args
        self.assertEqual(159, call_args[0])

    def test_start_watch_days_left_is_repeating_days_true(self):
        today = 1564053631  # 25.07.2019
        mock_crontab = Mock()
        mock_crontab.schedule = Mock()
        mock_crontab.schedule.get_next = Mock(return_value="Next Schedule")
        self.mock_os_timer.is_repeating_day_scheduled = Mock(return_value=mock_crontab)

        self.watcher.start_the_watch(today)

        assert not self.mock_os_timer.schedule_repeating_day.called

    def test_start_watch_days_left_is_repeating_days_false(self):
        today = 1564053631  # 25.07.2019
        self.mock_os_timer.is_repeating_day_scheduled = Mock(return_value=None)

        self.watcher.start_the_watch(today)

        assert self.mock_os_timer.schedule_repeating_day.called

    def test_start_watch_less_days_left(self):
        today = 1577710800  # 30.12.2019 13:00:00
        self.mock_os_timer.is_repeating_day_scheduled = Mock(return_value=CronTab())
        self.mock_os_timer.is_repeating_hour_scheduled = Mock(return_value=None)

        self.watcher.start_the_watch(today)

        assert self.mock_os_timer.cancel_repeating_day.called
        assert self.mock_os_timer.schedule_repeating_hour.called

    def test_start_watch_hours_left(self):
        today = 1577831400  # 31.12.2019, 22:30
        self.watcher.post_left_units_tweet = MagicMock()

        self.watcher.start_the_watch(today)

        assert self.watcher.post_left_units_tweet.called
        call_args, call_kwargs = self.watcher.post_left_units_tweet.call_args
        self.assertEqual(1, call_args[0])

    def test_start_watch_hours_left_timer(self):
        today = 1577822400  # 31.12.2019, 20:00
        self.mock_os_timer.is_repeating_hour_scheduled = Mock(return_value=None)

        self.watcher.start_the_watch(today)

        assert self.mock_os_timer.schedule_repeating_hour.called

    def test_start_watch_hours_left_timer_less(self):
        today = 1577831400  # 31.12.2019, 22:30
        self.mock_os_timer.is_repeating_hour_scheduled = Mock(return_value=CronTab())
        self.mock_os_timer.is_repeating_minute_scheduled = Mock(return_value=None)

        self.watcher.start_the_watch(today)

        assert self.mock_os_timer.cancel_repeating_hour.called
        assert self.mock_os_timer.schedule_repeating_minute.called

    def test_start_watch_mins_left(self):
        today = 1577835000  # 31.12.2019, 23:30
        self.watcher.post_left_units_tweet = MagicMock()

        self.watcher.start_the_watch(today)

        assert self.watcher.post_left_units_tweet.called
        call_args, call_kwargs = self.watcher.post_left_units_tweet.call_args
        self.assertEqual(30, call_args[0])

    def test_start_watch_mins_left_timer(self):
        today = 1577835000  # 31.12.2019, 23:30
        self.mock_os_timer.is_repeating_minute_scheduled = Mock(return_value=None)

        self.watcher.start_the_watch(today)

        assert self.mock_os_timer.schedule_repeating_minute.called

    def test_start_watch_past_deadline(self):
        today = WATCH_END_EPOCH_SEC + 1
        self.watcher.end_the_watch = MagicMock()

        self.watcher.start_the_watch(today)

        assert self.watcher.end_the_watch.called

    def test_start_watch_mins_left_timer_less(self):
        today = 1577836770  # 31.12.2019, 23:59:30
        self.mock_api_helper.get_user_timeline = Mock(return_value=[])
        self.watcher.post_watch_ended_tweet = MagicMock()
        self.watcher.end_the_watch = MagicMock()

        self.watcher.start_the_watch(today)

        assert self.watcher.post_watch_ended_tweet.called
        assert self.watcher.end_the_watch.called

    def test_start_watch_ended(self):
        today = 1577836770  # 31.12.2019, 23:59:30
        self.watcher.post_watch_ended_tweet = MagicMock()

        self.watcher.is_this_tweet_sent = Mock(return_value=False)
        self.watcher.start_the_watch(today)

        assert self.watcher.post_watch_ended_tweet.called

    def test_start_watch_ended_already(self):
        today = 1577836770  # 31.12.2019, 23:59:30
        self.watcher.end_the_watch = MagicMock()
        self.watcher.is_this_tweet_sent = Mock(return_value=True)

        self.watcher.start_the_watch(today)

        assert self.watcher.end_the_watch.called
