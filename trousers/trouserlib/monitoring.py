
import threading, logging, multiprocessing, time
import config
from flask import Flask, abort

logger = logging.getLogger("monitor")

app = Flask(__name__)

class MonitoringService:

    def __init__(self):
        self.target = None

    def healthcheck(self):
        if self.target.is_unhealthy():
            abort(500)
        return ":)"

    def start(self):

        """ Worker thread to start the web server """

        logger.info("Starting monitor on //localhost:%s/healthcheck" % config.healthcheckPort)

        app.add_url_rule(
            config.healthcheckEndpoint,
            view_func=self.healthcheck
        )

        app.run(debug=False, port=config.healthcheckPort)

    def monitor(self, target):

        """ Run a webserver to server monitoring results at the healthcheck endpoint. """

        self.target = target

        t = threading.Thread(name="monitor", target=self.start)
        t.start()

        return t
