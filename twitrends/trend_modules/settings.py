import itertools
import json
import logging
import os
import sys
from typing import List


class Settings:
    def __init__(self):
        self.elastic_user = ""
        self.elastic_pass = ""
        self.elastic_ip = ""
        self.elastic_port = ""
        self.twitter_auth_key = ""
        self.twitter_auth_secret = ""
        self.twitter_token_key = ""
        self.twitter_token_secret = ""
        self.keywords: List[str] = []
        self.pattern = ""
        try:
            with open(
                os.path.join(os.path.dirname(__file__), "../trends_settings.json")
            ) as read_h:

                settings = json.load(read_h)
                self.elastic_user = settings["elastic"]["username"]
                self.elastic_pass = settings["elastic"]["password"]
                self.elastic_ip = settings["elastic"]["ip"]
                self.elastic_port = settings["elastic"]["port"]
                self.twitter_auth_key = settings["auth_handle_creds"]["consumer_key"]
                self.twitter_auth_secret = settings["auth_handle_creds"][
                    "consumer_secret"
                ]
                self.twitter_token_key = settings["access_token"]["key"]
                self.twitter_token_secret = settings["access_token"]["secret"]
                keyword = settings["search_keyword"]
                self.keywords = list(
                    map(
                        "".join,
                        itertools.product(*zip(keyword.upper(), keyword.lower())),
                    )
                )
                self.pattern = settings["search_pattern"]

        except FileNotFoundError:
            logging.FATAL("trends_settings.json not found")
            sys.exit(1)
