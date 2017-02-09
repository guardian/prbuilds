#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from trouserlib.trousers import Trousers

BUCKET_NAME = 'prbuilds'
GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')
QUEUE_NAME = os.getenv('QUEUE_NAME', '')

if __name__ == '__main__':

    config = {
        "setup" : { "ansible" : "build.playbook.yml" },
        "teardown" : { "ansible" : "cleanup.playbook.yml" },        
        "checks": {
            "screenshots" : {
                "url": "http://localhost:9000/books/2014/may/21/guardian-journalists-jonathan-freedland-ghaith-abdul-ahad-win-orwell-prize-journalism"
            },
            "exceptions" : {
                "url": "http://localhost:9000/books/2014/may/21/guardian-journalists-jonathan-freedland-ghaith-abdul-ahad-win-orwell-prize-journalism"
            }
        }
    }
    
    # launch trousers
    
    trousers = Trousers(
        GH_NAME, GH_TOKEN, config
    )

    print "Starting trousers on queue %s" % QUEUE_NAME

    class MockMessage:
        def __init__(self):
            self.body = open("data/gh_pull.mock").read()
        def delete(self):
            pass
    
    class MockQueue:
        def receive_messages(self):
            return [MockMessage()]

    class MockBucket:
        def upload_file(self, localpath, key, ExtraArgs):
            pass
        
    trousers.start(
        MockQueue(),
        MockBucket()
    )
