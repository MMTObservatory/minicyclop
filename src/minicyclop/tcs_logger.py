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

log = logging.getLogger('MiniCyclop')
log.setLevel(logging.DEBUG)


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

    last_time = None

    while True:
        latest_data = read_latest(args.filename)
        if latest_data['obstime'] != last_time:
            log.debug(f"New data found at {latest_data['obstime_str']}: seeing = {latest_data['seeing']}\"")
            last_time = latest_data['obstime']
        else:
            log.debug("Waiting for data...")

        time.sleep(1)
