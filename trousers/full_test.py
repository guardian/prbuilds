#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from trouserlib.trousers import Trousers
from trouserlib.metrics import Metrics

GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')
QUEUE_NAME = os.getenv('QUEUE_NAME', '')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'prbuilds')
REPORTING = os.getenv('REPORTING', 'github')

if __name__ == '__main__':

    # launch trousers

    trousers = Trousers(
        REPORTING, GH_NAME, GH_TOKEN
    )

    print "Starting test run"

    class MockPullRequestEvent:
        def __init__(self):
            self.body = open("data/gh_pull.mock").read()
        def delete(self):
            pass

    class MockMasterEvent:
        def __init__(self):
            self.body = open("data/gh_master.mock").read()
        def delete(self):
            pass

    class MockQueue:
        def __init__(self):
            self.messages = [MockMasterEvent()]
        def receive_messages(self):
            if len(self.messages) == 0:
                return []
            else:
                return [self.messages.pop()]

    class MockBucket:
        def upload_file(self, localpath, key, ExtraArgs):
            pass

    class MockWaiter:
        def wait(self, TableName):
            pass

    class MockTableClient:
        def get_waiter(self, name):
            return MockWaiter()

    class MockTableMeta:
        client = MockTableClient()

    class MockDynamoTable:
        meta = MockTableMeta()
        def put_item(self, Item):
            print "putting metric"
            print Item

    class MockDynamo:
        def Table(self, name):
            return MockDynamoTable()
        def create_table(self, TableName, ProvisionedThroughput, AttributeDefinitions, KeySchema):
            return MockDynamoTable()

    m = Metrics(MockDynamo())
    m.init_tables()
    m.put_metric("a", 1, "b", "string", "ok")

    os.environ["PRBUILDS_ROOT"] = os.path.join(os.getenv("HOME"), "prbuilds/")

    print "PRBUILDS_ROOT set to %s" % os.getenv("PRBUILDS_ROOT")

    trousers.start(
        MockQueue(),
        MockBucket(),
        MockDynamo()
    )
