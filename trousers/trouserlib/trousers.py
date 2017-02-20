
import traceback, logging

from .runner import Runner
from .reporter import Reporter
from .sqs import Listener
from .github import GitHubService
from .artifacts import ArtifactService

ARTIFACTS_DIR = '/home/ubuntu/artifacts'

class Trousers:

    def __init__(self, ghName, ghToken):

        """ constructor """

        self.github = GitHubService(ghName, ghToken)
        self.artifacts = ArtifactService()

    def start(self, queue, bucket):

        """ trousers main processor """

        listener = Listener()
        reporter = Reporter()

        while True:

            msg, pr = listener.receive(queue)

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

            msg.delete()
            
            print "PR Build %s success" % pr.prnum
