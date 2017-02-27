
import traceback, logging, time, config

from .runner import Runner
from .reporter import Reporter
from .sqs import Listener
from .github import GitHubService
from .artifacts import ArtifactService
from .monitoring import MonitoringService

ARTIFACTS_DIR = '/home/ubuntu/artifacts'

class Trousers:

    def __init__(self, ghName, ghToken):

        """ constructor """

        self.github = GitHubService(ghName, ghToken)
        self.artifacts = ArtifactService()
        self.monitoring = MonitoringService()
        self.idle = True
        self.started = 0

    def is_unhealthy(self):

        """ unhealthy if a build is running after n minutes """

        return not self.idle and int(time.time()) - self.started > config.maxBuildTimeSeconds

    def process(self, pr, bucket):

        """ process a message coming off the queue """

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

        logging.info("PR Build %s success" % pr.prnum)

    def start(self, queue, bucket):

        """ trousers main processor """

        listener = Listener()
        reporter = Reporter()

        self.monitoring.monitor(self)

        while True:

            msg, pr = listener.receive(queue)

            self.idle = False
            self.started = int(time.time())

            try:
                self.process(pr, bucket)
            except:
                logging.warning("PR Build failed.")

            msg.delete()

            self.idle = True
