#!/usr/bin/env python

import boto3, time, ansible, subprocess, json, requests, os, sys
import traceback, logging
from requests.auth import HTTPBasicAuth

ARTIFACTS_DIR = '/home/ubuntu/workspace/screenshots'
QUEUE_NAME = 'trousers_in';
BUCKET_NAME = 'prbuilds'
GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')

class PullRequest:
    def __init__(self, obj):
        head = json.loads(obj)
        data = head["pull_request"]
        self.commentUrl = data["comments_url"]
        self.branch = data["head"]["ref"]
        self.cloneUrl = data["head"]["repo"]["clone_url"]
        self.prnum = data["number"]
        self.action = head["action"]

class GitHubService:

    def __init__(self):

        """ constructor """
        
        self.requests = requests
    
    def post_comment(self, url, body):

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

        
class Trousers:

    def __init__(self):

        """ constructor """

        self.subprocess = subprocess
        self.github = GitHubService()
        
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

            pr = PullRequest(msg.body)

            if pr.action not in ["opened", "synchronize"]:
                print "PR not being opened/pushed to. Ignoring"
                msg.delete()
                return

            self.build(
                pr.cloneUrl,
                pr.branch
            )

            facts = self.collect_artifacts(
                ARTIFACTS_DIR
            )

            self.upload_artifacts(
                bucket,
                "PR-%s/screenshots" % pr.prnum,
                facts
            )

            self.github.post_comment(
                pr.commentUrl,
                self.compose_github_comment(
                    pr.prnum,
                    facts
                )
            )

            print "PR Build success"

        except Exception as err:

            logging.error("PR Build failed")
            logging.error(err)
            logging.error(traceback.format_exc())
	    
        msg.delete()            

    def receive(self, queue, interval=5):

        """ Wait for an SQS message and then return it """
    
        while True:
            for message in queue.receive_messages():
                return message
            time.sleep(interval)

    def build(self, repo, branch="master"):

        """ Run the build script """

        ret = self.subprocess.call([
            "ansible-playbook",
            "build.playbook.yml",
            "--extra-vars",
            "branch=%s clone_url=%s" % (branch, repo),
            "-v"
        ])

        if ret != 0:
            raise Exception("Ansible play did not exit zero")

    def collect_artifacts(self, directory):

        """ collect a list of all the artifacts from this run """

        facts = []

        for root, directories, filenames in os.walk(directory):
            facts += [os.path.join(root, f) for f in filenames]

        return facts

    def upload_artifacts(self, bucket, prefix, artifacts):

        """ Upload results to S3 """

        def upload(path):
            bucket.upload_file(
                path, 
                "%s/%s" % (prefix, os.path.basename(path)),
                ExtraArgs={ 'ContentType': 'image/png', 'ACL': 'public-read' }
            )

        for filename in artifacts:
            print "Uploading file '%s' to S3" % filename
            upload(filename)


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
