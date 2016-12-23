#!/usr/birzxcasdpoi/sn/env python

import boto3, time, ansible, subprocess, json, requests, os, sys
import traceback, logging
from requests.auth import HTTPBasicAuth

ARTIFACTS_DIR = '/home/ubuntu/workspace/screenshots'
QUEUE_NAME = 'trousers_in';
BUCKET_NAME = 'prbuilds'
GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')

class Trousers:

    def __init__(self):

        """ constructor """

        self.subprocess = subprocess
        self.requests = requests
        
    def start(self, queue, bucket):

        """ busy waiting loop """
        
        while True:
            self.process_message(
                self.receive(queue, 2),
                bucket
            )

    def compose_github_comment(self, prnum, artifacts):

        """ format a nice github message """

        msg = "PR build results: \n"

        for artifact in artifacts:
            msg += "* https://s3-eu-west-1.amazonaws.com/prbuilds/PR-%s/screenshots/%s \n" % (prnum, os.path.basename(artifact))	

        return msg

    def process_message(self, msg, bucket):

        """ process a message coming off the sqs queue """
        
        try:

            branch = self.extract_branch(msg.body)
            repo = self.extract_clone_url(msg.body)
            prnum = self.extract_prnum(msg.body)
            prurl = self.extract_comment_url(msg.body)

            self.build(repo, branch)

            facts = self.upload_artifacts(bucket, prnum, ARTIFACTS_DIR)

            self.github_comment(prurl, self.compose_github_comment(prnum, facts))

            print "PR Build success"

        except Exception as err:

            logging.error("PR Build failed")
            logging.error(err)
            logging.error(traceback.format_exc())
	    
	    open("messages.log", "w").write(msg.body)

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

	def artifact_list():
            for root, directories, filenames in os.walk(directory):
                for filename in filenames:
                    yield os.path.join(root, filename)

        def upload(path):
            bucket.upload_file(
                path, 
                "PR-%s/screenshots/%s" % (prnum, os.path.basename(path)),
                ExtraArgs={ 'ContentType': 'image/png', 'ACL': 'public-read' }
            )

        for filename in artifact_list():
            print "Uploading file '%s' to S3" % filename
            upload(filename)

        return artifact_list()

    def github_comment(self, url, body):

        """ Add github comment using url endpoint """
       
	payload = { "body": body }
        
        res = self.requests.post(
            url,
            data = json.dumps(payload),
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
    except:
        sys.exit("Environment not correctly set")

    # get the sqs queue and results bucket

    session = boto3.Session(
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
