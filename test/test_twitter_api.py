import os
from typing import List
from unittest import TestCase

from tweepy import Status

from src.log import log
from src.twitter_api import store_access_tokens, read_access_tokens, create_api_helper, TwitterApiHelper


def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)


class FakeTwitterApiHelper(TwitterApiHelper):

    def __init__(self):
        super().__init__()
        self.access_token = "access_token"
        self.access_token_secret = "access_token_secret"

        self.tweet_1 = "tweet_1"
        self.tweet_2 = "tweet_2"

    def get_tokens_from_user(self) -> (str, str):
        return self.access_token, self.access_token_secret

    def set_access_tokens(self, access_token: str, access_token_secret: str):
        # NoOp
        pass

    def get_user_timeline(self, id: str) -> List[Status]:
        status_1 = Status()
        status_1._json = {"text": "tweet_1"}
        status_2 = Status()
        status_2._json = {"text": "tweet_2"}
        return [status_2, status_1]

    def post_tweet(self, text: str) -> Status:
        log(f"Fake Tweet Sent: \"{text}\"")
        status = Status()
        status._json = {"text": f"{text}"}
        return status


class TestTwitterApi(TestCase):

    def setUp(self) -> None:
        self.acc_token_filename = "access_tokens_test.txt"

        delete_file(self.acc_token_filename)
        self.addCleanup(delete_file, self.acc_token_filename)

    def test_read_store_access_tokens(self):
        access_token, access_token_secret = ("acc", "acc_sec")

        store_access_tokens(self.acc_token_filename, access_token, access_token_secret)
        result_acc, result_acc_sec = read_access_tokens(self.acc_token_filename)

        self.assertEqual(access_token, result_acc)
        self.assertEqual(access_token_secret, result_acc_sec)

    def test_create_api_helper(self):
        fake_api_helper = FakeTwitterApiHelper()

        create_api_helper(self.acc_token_filename, fake_api_helper)

        result_acc, result_acc_sec = read_access_tokens(self.acc_token_filename)
        self.assertEqual(fake_api_helper.access_token, result_acc)
        self.assertEqual(fake_api_helper.access_token_secret, result_acc_sec)
