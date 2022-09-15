"""
Poll the latest data saved by the MiniCyclop software and send it on to the TCS redis system
"""

import time
import os
import argparse
import redis
import logging

from pathlib import Path

from minicyclop.io import read_latest

log = logging.getLogger(__name__)
logging.basicConfig(filename=Path.home() / "tcs_logger.txt", encoding='utf-8', level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description='Utility for logging MiniCyclop data to redis')

    parser.add_argument(
        '-f', '--filename',
        metavar="<latest data file>",
        help="File containing latest saved data from the MiniCyclop seeing monitor",
        default=Path.home() / "MMT/minicyclop/data/MiniCyclop/Data/Last_Seeing_Data.txt"
    )

    args = parser.parse_args()

    log.info(f"Monitoring {args.filename} for seeing data...")

    # initialize with existing file so stale data doesn't get sent
    latest_data = read_latest(args.filename)
    last_time = latest_data['obstime']

    if 'REDISHOST' in os.environ:
        redis_host = os.environ['REDISHOST']
    else:
        redis_host = 'redis.mmto.arizona.edu'

    if 'REDISPORT' in os.environ:
        redis_port = os.environ['REDISPORT']
    else:
        redis_port = 6379

    if 'REDISPW' in os.environ:
        redis_server = redis.StrictRedis(host=redis_host, port=redis_port, password=os.environ['REDISPW'], db=0)
    else:
        redis_server = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

    while True:
        try:
            latest_data = read_latest(args.filename)
            if latest_data['obstime'] > last_time:
                log.info(f"New data found at {latest_data['obstime_str']}: seeing = {latest_data['seeing']}\"")
                last_time = latest_data['obstime']
                latest_data['measurement_timestamp'] = latest_data['obstime_str']
                for k in ['seeing', 'flux', 'r0', 'measurement_timestamp']:
                    redis_key = f"seeing_monitor_{k}"
                    redis_server.set(redis_key, latest_data[k])
                    redis_server.publish(redis_key, latest_data[k])
            else:
                log.debug("Waiting for data...")
        except Exception as e:
            log.warning(f"Problem updating seeing values in redis: {e}")

        time.sleep(1)
