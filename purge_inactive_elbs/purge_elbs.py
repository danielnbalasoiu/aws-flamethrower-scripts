#!/usr/bin/env python3
# Copyright 2021 Chris Farris <chrisf@primeharbor.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from botocore.exceptions import ClientError
from time import sleep
import boto3
import csv
import datetime as dt
import json
import logging
import os
import re
import sys


def main(args, logger):
    # If they specify a profile use it. Otherwise do the normal thing
    if args.profile:
        session = boto3.Session(profile_name=args.profile)
    else:
        session = boto3.Session()

    # Read the worklist from the passed in CSV file
    with open(args.infile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for a in reader:
            # Create a boto client in the correct region
            client = session.client("elb", region_name=a['Region'])
            if args.actually_do_it:
                client.delete_load_balancer(LoadBalancerName=a['LoadBalancerName'])
                logger.info(f"Deleted {a['LoadBalancerName']}")
            else:
                logger.info(f"Would Delete {a['LoadBalancerName']}")


def do_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="print debugging info", action='store_true')
    parser.add_argument("--error", help="print error info only", action='store_true')
    parser.add_argument("--timestamp", help="Output log with timestamp and toolname", action='store_true')
    parser.add_argument("--profile", help="Use this CLI profile (instead of default or env credentials)")
    parser.add_argument("--actually-do-it", help="Actually Perform the snapshot and deletion", action='store_true')
    parser.add_argument("--infile", help="CSV File of images to deregister and delete associated snapshots", required=True)

    args = parser.parse_args()

    return(args)

if __name__ == '__main__':

    args = do_args()

    # Logging idea stolen from: https://docs.python.org/3/howto/logging.html#configuring-logging
    # create console handler and set level to debug
    logger = logging.getLogger(sys.argv[0])
    ch = logging.StreamHandler()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.error:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    # Silence Boto3 & Friends
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    # create formatter
    if args.timestamp:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        formatter = logging.Formatter('%(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    try:
        main(args, logger)
    except KeyboardInterrupt:
        exit(1)
    except ClientError as e:
        if e.response['Error']['Code'] == "RequestExpired":
            print("Credentials expired")
            exit(1)
        else:
            raise
