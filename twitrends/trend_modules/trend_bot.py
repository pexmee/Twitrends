import datetime
import logging
import signal
import sys
import threading
from http.client import IncompleteRead
from threading import Thread
from time import sleep
from typing import Callable, Dict, Generator, List, Optional, Union

import tweepy
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from trend_modules.settings import TWEET_IDS, IndexDump, Settings


class Seppuku:
    """Makes threads commit suicide, gracefully"""

    def __init__(self):
        self.seppuku = False
        signal.signal(signal.SIGINT, self.instant_seppuku)
        signal.signal(signal.SIGTERM, self.instant_seppuku)

    def instant_seppuku(self, *args):
        self.seppuku = True


class TrendTweetListener(tweepy.StreamListener):
    def __init__(self, api, bot):
        self.api = api
        self.me = api.me()
        self.bot = bot

    def on_status(self, tweet):
        body: Dict[str, Union[str, int]] = {}

        if not tweet.retweeted and not tweet.text.startswith("RT @"):
            for rule in self.bot.settings.rules:
                match_ = rule.pattern.search(tweet.text)

                if match_:
                    logging.debug("adding tweet to index_dumps..")

                    body["tweet_id"] = tweet.id_str
                    body["created_at"] = str(tweet.created_at)
                    body["timestamp"] = datetime.datetime.now().isoformat()
                    body["retweet_count"] = tweet.retweet_count
                    body["likes"] = tweet.favorite_count
                    body["substring"] = match_.group(0).upper()

                    if rule.make_link:
                        body["google_link"] = (
                            "https://www.google.com/search?q=" + body["substring"]
                        )

                    self.bot.dump_findings(IndexDump(rule.index_name, body))

    def on_error(self, status):
        logging.error(f"error in tweet listener {status}")


class TrendThread(Thread):
    """
    Thread to be used by TrendBot.

    TrendThread will stop when sig_kill is set to False.
    """

    def __init__(self, name: str, target: Callable):
        Thread.__init__(self)
        self.target = target
        self.sig_kill = False
        self.name = name

    def run(self):
        logging.info(f"running thread {self.name}")

        while not self.sig_kill:
            self.target()

        logging.info(f"{self.name} stopped")


def threads_alive(threads: List[TrendThread]):
    """Returns whether all threads are alive."""
    return True in [thread.isAlive() for thread in threads]


class TrendBot:
    """
    Monitors Twitter activity matching a keyword and pattern.
    Sends matches to an Elasticsearch instance with the index set as 'tweet'.

    TrendBot defaults to not include tweet content nor username in dumps to Elasticsearch.
    """

    def __init__(self):
        self.settings = Settings()
        self.es = Elasticsearch(
            f"https://{self.settings.elastic_user}:{self.settings.elastic_pass}@{self.settings.elastic_ip}:{self.settings.elastic_port}",
            ca_certs=False,
            verify_certs=False,
            timeout=30,
            max_retries=3,
            retry_on_timeout=True,
        )

        logging.info(f"elasticsearch alive: {self.es.ping()}")

        twitter_auth = tweepy.OAuthHandler(
            self.settings.twitter_auth_key,
            self.settings.twitter_auth_secret,
        )
        twitter_auth.set_access_token(
            self.settings.twitter_token_key,
            self.settings.twitter_token_secret,
        )
        self.twitter_api = tweepy.API(twitter_auth)
        self.twitter_api.verify_credentials()
        self.tweet_listener = TrendTweetListener(self.twitter_api, self)
        self.tweet_stream = tweepy.Stream(self.twitter_api.auth, self.tweet_listener)
        self.mutex = threading.Lock()
        self.index_dumps: List[
            IndexDump
        ] = []  # Used to hold index dumps if mutex is locked while updating

    def stream_twitter(
        self,
    ):
        """Streams twitter posts, filtering on provided keywords"""

        try:
            keywords: List[str] = []

            for rule in self.settings.rules:
                keywords += rule.keyword

            self.tweet_stream.filter(track=keywords)

        except IncompleteRead as exc:
            logging.exception("IncompleteRead in stream_twitter:", exc_info=exc)

        except Exception as exc:
            logging.exception("unknown exception in stream_twitter:", exc_info=exc)

    def dump_findings(self, index_dump: Optional[IndexDump] = None):
        """
        Dumps all findings to Elasticsearch and caches tweet IDs in twitter_ids.txt.
        If mutex is locked this only saves dump in memory.
        """
        if index_dump:
            self.index_dumps.append(index_dump)

        if self.mutex.acquire(False):
            try:
                logging.info("dumping findings")

                with open(
                    TWEET_IDS,
                    "a",
                ) as id_h:

                    for index_dump in self.index_dumps:

                        if index_dump.body.get("tweet_id"):
                            print(
                                f'{index_dump.body["tweet_id"]}:{index_dump.name}',
                                end="\n",
                                file=id_h,
                            )
                            self.es.index(index=index_dump.name, body=index_dump.body)

                    self.index_dumps.clear()
            finally:
                self.mutex.release()

        else:
            logging.info("mutex was locked, passing")
            pass

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass

    def update_tweets(self):
        """
        Updates all tweets saved in Elasticsearch if they need to be updated with new values.
        """

        def update_fields(
            obj: TrendBot, tweet_ids: List[int], ids_names: Dict[int, str]
        ):
            try:
                for tweet in obj.twitter_api.statuses_lookup(tweet_ids):

                    for rule in self.settings.rules:
                        if rule.index_name != ids_names[tweet.id]:
                            continue

                        # Query Elasticsearch for the object with this tweet id
                        try:
                            res = obj.es.search(
                                index=rule.index_name,
                                body={"query": {"match": {"tweet_id": tweet.id_str}}},
                            )
                        except NotFoundError as exc:
                            logging.debug(
                                "NotFoundError in update_fields, couldn't find index in database",
                                exc_info=exc,
                            )
                            continue

                        # Sanity check, we don't know if these fields are guaranteed to exist
                        try:

                            for hit in res["hits"]["hits"]:

                                updated_fields: Dict[
                                    str, Dict[str, Union[int, str]]
                                ] = {"doc": {}}

                                if (
                                    hit["_source"]["retweet_count"]
                                    < tweet.retweet_count
                                ):
                                    logging.info(
                                        f"updated {tweet.id_str} with retweets: {tweet.retweet_count}"
                                    )
                                    updated_fields["doc"][
                                        "retweet_count"
                                    ] = tweet.retweet_count

                                if hit["_source"]["likes"] < tweet.favorite_count:
                                    logging.info(
                                        f"updated {tweet.id_str} with likes: {tweet.favorite_count}"
                                    )
                                    updated_fields["doc"][
                                        "likes"
                                    ] = tweet.favorite_count

                                if updated_fields:
                                    updated_fields["doc"][
                                        "updated_timestamp"
                                    ] = datetime.datetime.now().isoformat()

                                    obj.es.update(
                                        index=rule.index_name,
                                        id=hit["_id"],
                                        body=updated_fields,
                                    )

                        except KeyError as exc:
                            logging.exception(
                                "KeyError in update_fields - couldn't find expected result",
                                exc_info=exc,
                            )

            except Exception as exc:
                logging.exception("exception in update_fields", exc_info=exc)

        try:
            sleep(100)
            logging.info("updating tweets")
            buffer: List[int] = []
            ids_names: Dict[int, str] = {}

            # Hold your horses, this is gonna take a while,
            # especially if there's a lot of cached IDs
            self.mutex.acquire()

            for id in self._tweet_cache():
                id = id.split(":")
                ids_names[int(id[0])] = id[1]
                buffer.append(int(id[0]))

                # Twitter only allows lookup of up to 100 entries at a time.
                if len(buffer) == 100:
                    update_fields(self, buffer, ids_names)
                    buffer.clear()
                    ids_names.clear()

            if buffer:
                update_fields(self, buffer, ids_names)

        except Exception as exc:
            logging.exception("exception in update_tweets:", exc_info=exc)

        finally:
            self.mutex.release()

            if self.index_dumps:
                self.dump_findings()

    @staticmethod
    def _run_parallel(*functions: Callable):
        """
        Starts all provided functions on separate TrendThreads.
        Terminates threads if SIGINT or SIGTERM is received.
        """

        logging.debug("starting threads")
        threads: List[TrendThread] = []
        name = 0
        killer = Seppuku()

        for func in functions:
            thread = TrendThread("thread#" + str(name), func)
            thread.daemon = True
            thread.start()
            threads.append(thread)
            name += 1

        while threads_alive(threads) and not killer.seppuku:
            try:
                for thread in threads:
                    if thread is not None and thread.is_alive():
                        thread.join(1)

            except KeyboardInterrupt as exc:
                logging.debug("received CTRL+C, killing threads..", exc_info=exc)
                for thread in threads:
                    thread.sig_kill = True

            else:
                if killer.seppuku:
                    logging.info("received SIGINT or SIGTERM")

                    for thread in threads:
                        thread.sig_kill = True
                    logging.info("death by seppuku")

    def listen(self):
        """listens to tweets with provided keyword"""
        try:
            self._run_parallel(self.stream_twitter, self.update_tweets)

        except Exception as exc:
            logging.exception("exception in listen:", exc_info=exc)
            sys.exit(1)

    @staticmethod
    def _tweet_cache() -> Union[Generator[str, None, None], List]:
        """Retrieves twitter IDs saved in twitter_ids.txt"""

        try:
            with open(TWEET_IDS) as read_h:
                for row in read_h:
                    yield row.strip()

        except FileNotFoundError as exc:
            logging.info("couldn't find tweet cache, sending empty list", exc_info=exc)
            return []
