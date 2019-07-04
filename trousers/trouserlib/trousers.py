
import os, traceback, logging, time, config

from .runner import Runner
from .reporter import Reporter
from .sqs import Listener
from .github import GitHubService
from .artifacts import ArtifactService
from .monitoring import MonitoringService
from .metrics import Metrics

logger = logging.getLogger("buildlog")

class Trousers:

    def __init__(self, reporting, ghName, ghToken):

        """ constructor """

        self.reporting = reporting
        self.github = GitHubService(ghName, ghToken)
        self.artifacts = ArtifactService()
        self.monitoring = MonitoringService()
        self.idle = True
        self.started = 0

    def is_healthy(self):

        """ we are healthy under these conditions """

        s = os.statvfs(config.prbuildsRoot)
        freeSpaceMB = (((s.f_frsize * s.f_bavail) / 1000) / 1000)

        health = {
            "has free space": freeSpaceMB > config.requiredFreeSpaceMB,
            "no long running build": self.idle or int(time.time()) - self.started < config.maxBuildTimeSeconds
        }

        for k in {k for k, v in health.items() if not v}:
            logger.warning("check failed: %s" % k)

        return False not in health.values()

    def process(self, action, bucket, metricService):

        """ process a message coming off the queue """

        directories = config.directoriesForRepo(action.repoName)

        logger.info("Running build for branch %s" % action.branch)

        if not action.hasPullRequest():
            logger.info("Looks like this is a master build")

        with Runner(action.cloneUrl, action.branch, directories, logger) as runner:

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

                logger.info("Reporting to pull request: %s" % action.pullRequest.prNum)

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

        logger.info("PR Build success")

    def start(self, queue, bucket, dynamo):

        """ trousers main processor """

        listener = Listener()
        metrics = Metrics(dynamo)

        self.monitoring.monitor(self)
        metrics.init_tables()

        if not self.is_healthy():
            logger.error("PRBuilds was unhealthy at startup. Not proceeding")
            raise Exception("PRBuilds was unhealthy at startup")

        while True:

            msg, action = listener.receive(queue)

            self.idle = False
            self.started = int(time.time())

            try:
                self.process(action, bucket, metrics)
            except Exception as e:
                logger.warning("PR Build failed.")
                logger.error(str(e))

            msg.delete()

            self.idle = True
