#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3, yaml, os, sys
from trouserlib.trousers import Trousers

BUCKET_NAME = 'prbuilds'
GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')
QUEUE_NAME = os.getenv('QUEUE_NAME', '')

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
    s3 = session.resource('s3')

    # read up the config
    # TODO: config will be inside the repo in the future and found
    # by the trousers processor itself.
    
    config = yaml.load(open("config.yml").read())
    
    # launch trousers
    
    trousers = Trousers(
        GH_NAME,
        GH_TOKEN,
        config
    )

    print "Starting trousers on queue %s" % QUEUE_NAME
    
    trousers.start(
        sqs.get_queue_by_name(
            QueueName=QUEUE_NAME
        ),
        s3.Bucket(
            BUCKET_NAME
        )
    )
