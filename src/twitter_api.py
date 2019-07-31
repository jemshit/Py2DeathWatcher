import os
import sys
from os.path import exists
from typing import List
import toml

import tweepy
from tweepy import OAuthHandler, API, User, Status

SRC_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.abspath(os.path.join(SRC_DIR, os.pardir))
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

from src.log import log

API_SECRETS_FILE = os.path.join(PROJECT_DIR, "files/twitter_api_secrets.toml")
API_SECRETS = toml.load(f=API_SECRETS_FILE)
API_KEY: str = API_SECRETS["TWITTER_API_KEY_PY2WATCHER"]
API_SECRET_KEY: str = API_SECRETS['TWITTER_API_SECRET_KEY_PY2WATCHER']

ACCESS_TOKEN_FILENAME = os.path.join(PROJECT_DIR, "files/access_token.txt")


class TwitterApiHelper:

    def __init__(self):
        log(f"-->> Creating TwitterApiHelper with\n\tApi Key: {API_KEY}\n\tApi Secret Key: {API_SECRET_KEY}")
        self.auth: OAuthHandler = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
        self.api: API = tweepy.API(self.auth)

    def set_access_tokens(self, access_token: str, access_token_secret: str):
        log(
            f"-->> Access tokens are set and API instance is recreated.\n\tAccess Token: {access_token}\n\tAccess Token Secret: {access_token_secret}")

        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth)

    def get_user(self, account_name: str) -> User:
        return self.api.get_user(account_name)

    def get_my_timeline(self) -> List[Status]:
        return self.api.home_timeline()

    def get_user_timeline(self, id: str) -> List[Status]:
        return self.api.user_timeline(id=id)

    def post_tweet(self, text: str) -> Status:
        return self.api.update_status(text)

    def delete_tweet(self, tweet_id: str) -> Status:
        return self.api.destroy_status(tweet_id)

    def __get_auth_url(self) -> str:
        try:
            auth_url = self.auth.get_authorization_url()
        except tweepy.TweepError as error:
            log(f"Error when getting auth_url: {error}")
            auth_url = ""

        return auth_url

    def get_tokens_from_user(self) -> (str, str):
        auth_url = self.__get_auth_url()
        if not auth_url:
            log("auth_url is empty!")
            exit(1)
        else:
            log(f"Redirect URL generated. Click and give access to the App. Then Copy PIN number\n\t: {auth_url}")
            verifier = str(input("Enter PIN:")).strip()

            if not verifier:
                log("PIN is empty!")
                exit(1)
            else:
                try:
                    self.auth.get_access_token(verifier)
                    access_token = self.auth.access_token
                    access_token_secret = self.auth.access_token_secret
                    log(f"\n\tAccess Token is: {access_token}")
                    log(f"\tAccess Token Secret is: {access_token_secret}")
                    return access_token, access_token_secret
                except tweepy.TweepError as error:
                    log(f"Can not get access_token: {error}")
                    exit(1)


def store_access_tokens(filename: str, access_token: str, access_token_secret: str):
    with open(filename, 'wt') as file:
        file.write(access_token)
        file.write("\n")
        file.write(access_token_secret)


def read_access_tokens(filename: str) -> (str, str):
    file = open(filename, 'rt')
    file.seek(0)
    try:
        access_token = file.readline()
        access_token_secret = file.readline()
        file.close()
        return access_token.rstrip("\n"), access_token_secret.rstrip("\n")
    except Exception:
        file.close()
        return "", ""


def create_api_helper(token_filename: str,
                      api_helper: TwitterApiHelper) -> TwitterApiHelper:
    log("-->> Creating TwitterApiHelper...")

    if not exists(token_filename):
        access_token, access_token_secret = api_helper.get_tokens_from_user()
        store_access_tokens(token_filename, access_token, access_token_secret)
    else:
        access_token, access_token_secret = read_access_tokens(token_filename)
        if not access_token or not access_token_secret:
            access_token, access_token_secret = api_helper.get_tokens_from_user()
            store_access_tokens(token_filename, access_token, access_token_secret)

    api_helper.set_access_tokens(access_token, access_token_secret)

    return api_helper
