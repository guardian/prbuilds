
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

    def process(self, pr, bucket, metricService):

        """ process a message coming off the queue """

        with Runner(pr.cloneUrl, pr.branch) as runner:

            results = runner.run_tests()

            """ artifacts """
            facts = self.artifacts.collect(config.directories.artifacts)
            self.artifacts.upload(bucket, "PR-%s" % pr.prnum, facts)

            """ metrics """
            metrics = [results[k]["metrics"] for k in [k for k in results]]
            for metric in [item for sublist in metrics for item in sublist]:
                metricService.put_metric(
                    pr.cloneUrl,
                    pr.prnum,
                    metric[0],
                    metric[1],
                    metric[2]
                )

            """ github comment """

            if self.reporting == "github":
                
                reporter = Reporter()
            
                comment = reporter.compose_github_comment(
                    pr.prnum,
                    facts,
                    results
                )

                self.github.update_comment(
                    pr.commentUrl,
                    comment
                )

            logging.info()

        logging.info("PR Build %s success" % pr.prnum)

    def start(self, queue, bucket, dynamo):

        """ trousers main processor """

        listener = Listener()
        metrics = Metrics(dynamo)
        
        self.monitoring.monitor(self)
        metrics.init_tables()

        while True:

            msg, pr = listener.receive(queue)

            self.idle = False
            self.started = int(time.time())

            try:
                self.process(pr, bucket, metrics)
            except Exception as e:

                logging.warning("PR Build failed.")

            msg.delete()

            self.idle = True
