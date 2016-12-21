#!/usr/bin/env python

import boto3, time, ansible, subprocess, json, requests, os, sys
from requests.auth import HTTPBasicAuth

ARTIFACTS_DIR = '/home/ubuntu/workspace/screenshots'
QUEUE_NAME = 'trousers_in';
BUCKET_NAME = 'prbuilds'
GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')
AWS_USER = os.getenv('AWS_USER', '') 
AWS_KEY = os.getenv('AWS_KEY', '')

class Trousers:

    def __init__(self):

        """ constructor """

        self.subprocess = subprocess
        self.requests = requests
        
    def start(self, queue, bucket):

        """ busy waiting loop """
        
        while True:
            self.process_message(
                self.receive(queue, 2)
            )

    def process_message(self, msg):

        """ process a message coming off the sqs queue """
        
        branch = self.extract_branch(msg.body)
        repo = self.extract_clone_url(msg.body)
        prnum = self.extract_prnum(msg.body)
        prurl = self.extract_comment_url(msg.body)

        try:
            self.build(repo, branch)
            self.upload_artifacts(bucket, prnum, ARTIFACTS_DIR)
            self.github_comment(prurl, "PR Regression test complete")
        except:
            print "PR build failed"

        msg.delete()            

    def receive(self, queue, interval=5):

        """ Wait for an SQS message and then return it """
    
        while True:
            for message in queue.receive_messages():
                return message
            time.sleep(interval)

    def build(self, repo, branch="master"):

        """ Run the build script """

        print "Running ansible play for branch: %s" % branch

        self.subprocess.call([
            "ansible-playbook",
            "build.playbook.yml",
            "--extra-vars",
            "branch=%s clone_url=%s" % (branch, repo),
            "-v"
        ])

    def upload_artifacts(self, bucket, prnum, directory):

        """ Upload results to S3 """

        def upload(path):
            bucket.upload_file(
                path, "PR-%s/screenshots/%s" % (prnum, os.path.basename(path))
            )

        for root, directories, filenames in os.walk(directory):
            for filename in filenames:
                print "Uploading file '%s' to S3" % filename
                upload(os.path.join(root,filename))

    def github_comment(self, url, body):

        """ Add github comment using url endpoint """
        
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

    def extract_clone_url(self, data):
        obj = json.loads(data)
        return obj["pull_request"]["head"]["repo"]["clone_url"]

    def extract_prnum(self, data):
        obj = json.loads(data)
        return obj["pull_request"]["number"]
    
if __name__ == '__main__':

    # check environment variables existed

    try:
        os.environ['GH_NAME']
        os.environ['GH_TOKEN']
        os.environ['AWS_USER']
        os.environ['AWS_KEY']
    except:
        sys.exit("Environment not correctly set")

    # get the sqs queue and results bucket

    session = boto3.Session(
        aws_access_key_id=AWS_USER,
        aws_secret_access_key=AWS_KEY,
        region_name='eu-west-1'    
    )
    
    sqs = session.resource('sqs')
    s3 = session.resource('s3')
    
    # launch trousers
    
    trousers = Trousers()

    print "Starting"
    
    trousers.start(
        sqs.get_queue_by_name(
            QueueName=QUEUE_NAME
        ),
        s3.Bucket(
            BUCKET_NAME
        )
    )
