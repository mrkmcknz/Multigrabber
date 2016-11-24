#!/usr/local/bin/python3.5
import argparse
import asyncio
import hashlib

import aiohttp
import arrow
import feedparser
from elasticsearch import Elasticsearch
from elasticsearch import helpers

async def fetch(session, url):
    try:
        with aiohttp.Timeout(10):
            async with session.get(url) as response:
                return await response.read()
    except Exception as e:
        print(e)


async def run(filepath, es):

    tasks = []
    actions = []

    async with aiohttp.ClientSession() as session:
        with open(filepath, "r") as input:
            for url in input:
                task = asyncio.ensure_future(fetch(session, url))
                tasks.append(task)

            data = await asyncio.gather(*tasks, return_exceptions=False)
            results = [parse_rss_feed(i) for i in data]
            for feed in results:
                actions = es_action(feed, actions)
            helpers.bulk(es, actions)


def es_action(feed, actions):

    for item in feed:
        action = {
            "_id": hashlib.md5(item['link'].encode('utf-8')).hexdigest(),
            "_index": "news",
            "_type": "feed",
            "_source": item,
            "op_type": "create"
        }
        actions.append(action)
    return actions


def rss_item(item):

    data = {
        "title": item.get('title'),
        "link": item.get('link'),
        "description": item.get('description'),
        "published_on": arrow.get(item.get('published_parsed')).isoformat()
    }
    return data


def parse_rss_feed(feed):

    parse = feedparser.parse(feed)
    return [rss_item(item) for item in parse.entries]

if __name__ == '__main__':

    # By default we make a connection to: 0.0.0.0:9200
    es = Elasticsearch()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', dest="filepath", required=True, metavar="FILE",
        help="path to file containing urls to be processed")
    args = parser.parse_args()

    import time
    start = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(args.filepath, es))
    loop.run_until_complete(future)
    end = time.time()
    print(end - start)
