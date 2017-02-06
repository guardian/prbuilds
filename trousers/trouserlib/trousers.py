
import traceback, logging

from .runner import Runner
from .reporter import Reporter
from .sqs import Listener
from .pullrequest import PullRequest
from .github import GitHubService
from .artifacts import ArtifactService

ARTIFACTS_DIR = '/home/ubuntu/artifacts'            
    
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
