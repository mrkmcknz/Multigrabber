#!/usr/local/bin/python3.5
import argparse
import aiohttp
import asyncio


async def fetch(session, url):
    with aiohttp.Timeout(10):
        async with session.get(url) as response:
            return await response.read()

async def run(filepath):

    tasks = []

    async with aiohttp.ClientSession() as session:
        with open(filepath, "r") as input:
            for url in input:
                task = asyncio.ensure_future(fetch(session, url))
                tasks.append(task)

            data = await asyncio.gather(*tasks)
            # Do what you want with the data here


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', dest="filepath", required=True, metavar="FILE",
        help="path to file containing urls to be processed")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(args.filepath))
    loop.run_until_complete(future)
