
import os, time, subprocess, urllib, jinja2, traceback, logging, modules

from .pullrequest import PullRequest
from .github import GitHubService
from .artifacts import ArtifactService

class Trousers:

    def __init__(self, ghName, ghToken):

        """ constructor """

        self.subprocess = subprocess
        self.github = GitHubService()
        self.artifacts = ArtifactService(ghName, ghToken)
        
    def start(self, queue, bucket):

        """ busy waiting loop """
        
        while True:
            self.process_message(
                self.receive(queue, 2),
                bucket
            )

    def compose_github_comment(self, prnum, artifacts=[], results=[]):

        """ format a nice github message """
        
        def link(artifact):
            pre = "https://s3-eu-west-1.amazonaws.com/prbuilds"
            pth = "PR-%s/%s \n" % (prnum, urllib.quote(os.path.relpath(artifact, ARTIFACTS_DIR)))
            return "[%s](%s/%s)" % (os.path.basename(artifact), pre, pth.strip())

        def links_for(test):
            return [link(f) for f in artifacts if test in f]
        
        template = jinja2.Template(
            open("github_comment.template").read().decode("utf-8")
        )

        return template.render(
            artifacts=artifacts,
            results=results,
            link=link,
            links_for=links_for
        )
        
    def process_message(self, msg, bucket):

        """ process a message coming off the sqs queue """
        
        try:

            pr = PullRequest(msg.body)

            if pr.action not in ["opened", "synchronize"]:
                print "PR not being opened/pushed to. Ignoring"
                msg.delete()
                return

            self.set_up(
                pr.cloneUrl,
                pr.branch
            )

            results = self.run_tests()

            facts = self.artifacts.collect(
                ARTIFACTS_DIR
            )

            self.artifacts.upload(
                bucket,
                "PR-%s" % pr.prnum,
                facts
            )

            if not self.github.has_comment(pr.commentUrl, "-automated message"):
                self.github.post_comment(
                    pr.commentUrl,
                    self.compose_github_comment(
                        pr.prnum,
                        facts,
                        results
                    )
                )

            print "PR Build %s success" % pr.prnum

        except Exception as err:

            logging.error("PR Build failed")
            logging.error(err)
            logging.error(traceback.format_exc())

        try:
            self.tear_down()
        except Exception as err:
            logging.error("Teardown failed")
	    
        msg.delete()            

    def receive(self, queue, interval=5):

        """ Wait for an SQS message and then return it """
    
        while True:
            for message in queue.receive_messages():
                return message
            time.sleep(interval)

    def set_up(self, repo, branch):

        ret = self.subprocess.call([
            "ansible-playbook",
            "build.playbook.yml",
            "--extra-vars",
            "branch=%s clone_url=%s" % (branch, repo),
            "-v"
        ])

        if ret != 0:
            raise Exception("Ansible play did not exit zero")

    def run_tests(self):

        """ run tests against a running app """
        
        return modules.run_all()

    def tear_down(self):

        """ stop the running app and clean up """

        self.subprocess.call([
            "ansible-playbook",
            "cleanup.playbook.yml"
        ])        
