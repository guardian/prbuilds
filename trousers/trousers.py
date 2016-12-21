#!/usr/bin/env python

import boto3, time, ansible, subprocess, json, requests, os, sys
from requests.auth import HTTPBasicAuth

QUEUE_NAME = 'trousers_in';
GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')
AWS_USER = os.getenv('AWS_USER', '') 
AWS_KEY = os.getenv('AWS_KEY', '')

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
            prurl = self.extract_comment_url(msg.body)
            
            self.build(branch)

            print "Pushing comment to: %s" % prurl
            
            try:
                self.github_comment(prurl, "Build complete")
            except:
                print "Failed to comment on pull request"
                
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

        res = self.requests.post(
            url,
            data = '{ "body" : "%s" }' % body,
            auth = HTTPBasicAuth(
                GH_NAME,
                GH_TOKEN
            )
        )

        res.raise_for_status()        

    def extract_comment_url(self, data):
        obj = json.loads(data)
        return obj["pull_request"]["comments_url"]

    def extract_branch(self, data):
        obj = json.loads(data)
        return obj["pull_request"]["head"]["ref"]
    
if __name__ == '__main__':

    # check environment variables existed

    try:
        os.environ['GH_NAME']
        os.environ['GH_TOKEN']
        os.environ['AWS_USER']
        os.environ['AWS_KEY']
    except:
        sys.exit("Environment not correctly set")

    # get the sqs queue
    
    sqs = boto3.Session(
        aws_access_key_id=AWS_USER,
        aws_secret_access_key=AWS_KEY,
        region_name='eu-west-1'    
    ).resource('sqs')

    # launch trousers
    
    trousers = Trousers()

    print "Starting"
    
    trousers.start(
        sqs.get_queue_by_name(
            QueueName=QUEUE_NAME
        )   
    )
