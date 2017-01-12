#!/usr/bin/env python

import boto3, time, ansible, subprocess, json, requests, os, sys
import traceback, logging
from requests.auth import HTTPBasicAuth

ARTIFACTS_DIR = '/home/ubuntu/workspace/screenshots'
BUCKET_NAME = 'prbuilds'
GH_NAME = os.getenv('GH_NAME', '')
GH_TOKEN = os.getenv('GH_TOKEN', '')
QUEUE_NAME = os.getenv('QUEUE_NAME', '')

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

    def has_comment(self, url, including):

        """ Is the given text included anywhere """
        
        res = self.requests.get(url)

        res.raise_for_status()

        for post in res.json():
            if including in post["body"]:
                return True

        return False
        
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


class ArtifactService:

    def collect(self, directory):

        """ return list of all the artifacts in given directory """

        facts = []

        for root, directories, filenames in os.walk(directory):
            facts += [os.path.join(root, f) for f in filenames]

        return facts

    def upload(self, bucket, prefix, artifacts):

        """ Upload given artifact files to S3 """

        def upload(path):
            bucket.upload_file(
                path,
                "%s/%s" % (prefix, os.path.basename(path)),
                ExtraArgs={ 'ContentType': 'image/png', 'ACL': 'public-read' }
            )

        for filename in artifacts:
            print "Uploading file '%s' to S3" % filename
            upload(filename)
    

class Trousers:

    def __init__(self):

        """ constructor """

        self.subprocess = subprocess
        self.github = GitHubService()
        self.artifacts = ArtifactService()
        
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

        msg += "\n -automated message"
            
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

            facts = self.artifacts.collect(
                ARTIFACTS_DIR
            )

            self.artifacts.upload(
                bucket,
                "PR-%s/screenshots" % pr.prnum,
                facts
            )

            if not self.github.has_comment(pr.commentUrl, "-automated message"):
                self.github.post_comment(
                    pr.commentUrl,
                    self.compose_github_comment(
                        pr.prnum,
                        facts
                    )
                )

            print "PR Build %s success" % pr.prnum

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
    
    # launch trousers
    
    trousers = Trousers()

    print "Starting trousers on queue %s" % QUEUE_NAME
    
    trousers.start(
        sqs.get_queue_by_name(
            QueueName=QUEUE_NAME
        ),
        s3.Bucket(
            BUCKET_NAME
        )
    )
