
import traceback, logging, time, config

from .runner import Runner
from .reporter import Reporter
from .sqs import Listener
from .github import GitHubService
from .artifacts import ArtifactService
from .monitoring import MonitoringService
from .metrics import Metrics

class Trousers:

    def __init__(self, reporting, ghName, ghToken):

        """ constructor """

        self.reporting = reporting
        self.github = GitHubService(ghName, ghToken)
        self.artifacts = ArtifactService()
        self.monitoring = MonitoringService()
        self.idle = True
        self.started = 0

    def is_unhealthy(self):

        """ unhealthy if a build is running after n minutes """

        return not self.idle and int(time.time()) - self.started > config.maxBuildTimeSeconds

    def process(self, action, bucket, metricService):

        """ process a message coming off the queue """

        directories = config.directoriesForRepo(action.repoName)

        with Runner(action.cloneUrl, action.branch, directories) as runner:

            results = runner.run_tests()

            """ artifacts """
            facts = self.artifacts.collect(directories.artifacts)
            self.artifacts.upload(bucket, action.getKey(), facts)

            """ metrics """
            metrics = [results[k]["metrics"] for k in [k for k in results]]
            for metric in [item for sublist in metrics for item in sublist]:
                metricService.put_metric(
                    action.cloneUrl,
                    action.getKey(),
                    metric[0],
                    metric[1],
                    metric[2]
                )

            """ github comment """

            if self.reporting == "github" and action.hasPullRequest():

                reporter = Reporter()

                comment = reporter.compose_github_comment(
                    action.pullRequest.prNum,
                    facts,
                    results
                )

                self.github.update_comment(
                    action.pullRequest.commentUrl,
                    comment
                )

        logging.info("PR Build success")

    def start(self, queue, bucket, dynamo):

        """ trousers main processor """

        listener = Listener()
        metrics = Metrics(dynamo)

        self.monitoring.monitor(self)
        metrics.init_tables()

        while True:

            msg, action = listener.receive(queue)

            self.idle = False
            self.started = int(time.time())

            try:
                self.process(action, bucket, metrics)
            except Exception as e:
                logging.warning("PR Build failed.")
                logging.error(str(e))

            msg.delete()

            self.idle = True
