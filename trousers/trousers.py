#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3, os, sys, logging

from trouserlib.trousers import Trousers
from trouserlib.logger import CloudWatchLoggingHandler

GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')
QUEUE_NAME = os.getenv('QUEUE_NAME', '')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'prbuilds')
REPORTING = os.getenv('REPORTING', 'github')

if __name__ == '__main__':

    # check environment variables existed

    try:
        os.environ['GH_NAME']
        os.environ['GH_TOKEN']
        os.environ['QUEUE_NAME']
    except:
        sys.exit("Environment variables missing")

    # get the sqs queue and results bucket

    session = boto3.Session(
        region_name='eu-west-1'
    )

    sqs = session.resource('sqs')
    dyn = session.resource('dynamodb')
    s3  = session.resource('s3')
    cwl = session.resource('logs')

    # configure logging

    logger = logging.getLogger("buildlog")
    logger.addHandler(logging.FileHandler("buildlog.log"))
    logger.addHandler(CloudWatchLoggingHandler(cwl, "prbuilds", "buildlog"))
    logger.setLevel(logging.INFO)

    # launch trousers

    trousers = Trousers(
        REPORTING,
        GH_NAME,
        GH_TOKEN
    )

    print "Starting trousers on queue %s" % QUEUE_NAME

    trousers.start(
        sqs.get_queue_by_name(
            QueueName=QUEUE_NAME
        ),
        s3.Bucket(
            BUCKET_NAME
        ),
        dyn
    )
