import itertools
import json
import logging
import os
import re
import sys
from typing import Dict, List, Union

TWEET_IDS = os.path.join(os.path.dirname(__file__), "../twitter_ids.txt")


class IndexDump:
    def __init__(self, name: str, body: Dict[str, Union[str, int]]):
        self.name = name
        self.body = body


class SearchRule:
    def __init__(self, index_name: str, keyword: str, pattern: str, make_link: bool):
        self.index_name = index_name
        self.keyword = list(
            map(
                "".join,
                itertools.product(*zip(keyword.upper(), keyword.lower())),
            )
        )
        self.pattern = re.compile(pattern, re.I | re.M)
        self.make_link = make_link


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
        self.rules: List[SearchRule] = []

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
                for rule in settings["search_rules"].keys():
                    self.rules.append(
                        SearchRule(
                            index_name=rule,
                            keyword=settings["search_rules"][rule]["search_keyword"],
                            pattern=settings["search_rules"][rule]["search_pattern"],
                            make_link=settings["search_rules"][rule]["make_link"],
                        )
                    )

        except FileNotFoundError:
            logging.FATAL("trends_settings.json not found")
            sys.exit(1)
