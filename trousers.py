#!/usr/bin/env python

import boto3, time, ansible, subprocess, json, requests, os
from requests.auth import HTTPBasicAuth

QUEUE_NAME = 'mjwtest';
GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')

class Trousers:

    def __init__(self):

        """ constructor """

        self.subprocess = subprocess
        self.requests = requests
        
    def start(self, queue):

        """ busy waiting loop """
        
        while True:
            msg = self.receive(queue, 2)
            branch = self.extract_branch(msg.body)
            self.build(branch)
            msg.delete()
    
    def receive(self, queue, interval=5):

        """ Wait for an SQS message and then return it """
    
        while True:
            for message in queue.receive_messages():
                return message
            time.sleep(interval)

    def build(self, branch="master"):

        """ Run the build script """

        print "Running ansible play for branch: %s" % branch

        self.subprocess.call([
            "ansible-playbook",
            "build.playbook.yml",
            "--extra-vars",
            "branch=%s" % branch,
            "-v"
        ])

    def github_comment(self, url, body):

        self.requests.post(
            url,
            data = { 'body' : body },
            auth = HTTPBasicAuth(
                GH_NAME,
                GH_TOKEN
            )
        )

    def extract_branch(self, data):
        obj = json.loads(data)
        return obj["pull_request"]["head"]["ref"]
    
if __name__ == '__main__':

    sqs = boto3.Session(
        profile_name='frontend',
        region_name='eu-west-1'
    ).resource('sqs')
    
    trousers = Trousers()

    print "Starting"
    
    trousers.start(
        sqs.get_queue_by_name(
            QueueName=QUEUE_NAME
        )   
    )
