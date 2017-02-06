
import os, time, subprocess, urllib, jinja2, traceback, logging, modules

from .pullrequest import PullRequest
from .github import GitHubService
from .artifacts import ArtifactService

ARTIFACTS_DIR = '/home/ubuntu/artifacts'

def pushes_only(pr):
    return pr.action in ["opened", "synchronize"]

class Listener:

    def receive(self, queue, filt=pushes_only, interval=5):

        """ Wait for an SQS message and then return it """
    
        while True:
            for message in queue.receive_messages():
                if filt(message):
                    return message
            time.sleep(interval)
            
class Runner:

    def __enter__(self, repo, branch):

        """ set up the running app via an ansible play """
        
        ret = self.subprocess.call([
            "ansible-playbook",
            "build.playbook.yml",
            "--extra-vars",
            "branch=%s clone_url=%s" % (branch, repo),
            "-v"
        ])

        if ret != 0:
            raise Exception("Ansible play did not exit zero")

        return self

    def run_tests(self):

        """ run tests against a running app """
        
        return modules.run_all()

    def __exit__(self, type, value, traceback):

        """ stop the running app and clean up """

        self.subprocess.call([
            "ansible-playbook",
            "cleanup.playbook.yml"
        ])        

class Reporter:

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
    
class Trousers:

    def __init__(self, ghName, ghToken):

        """ constructor """

        self.subprocess = subprocess
        self.github = GitHubService(ghName, ghToken)
        self.artifacts = ArtifactService()

    def start(self, queue, bucket):

        """ trousers main processor """
        
        listener = Listener()
        runner   = Runner()
        reporter = Reporter()

        while True:
            
            msg = listener.receive(queue)
            prs = PullRequest(msg.body)
            
            try:

                with Runner(pr.cloneUrl, pr.branch) as runner:

                    results = runner.run_tests()
                    facts = self.artifacts.collect(ARTIFACTS_DIR)

                    self.artifacts.upload(bucket, "PR-%s" % pr.prnum, facts)
                    
                    comment = reporter.compose_github_comment(
                        pr.prnum,
                        facts,
                        results
                    )
                    
                    self.github.update_comment(
                        pr.commentUrl,
                        comment,
                        "-automated message"
                    )

            except Exception as err:

                logging.error("PR Build failed")
                logging.error(err)
                logging.error(traceback.format_exc())

            print "PR Build %s success" % pr.prnum                

            msg.delete()                    
