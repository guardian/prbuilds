
import threading, logging, multiprocessing, time
import config
from flask import Flask, abort

logger = logging.getLogger("buildlog")

app = Flask(__name__)

class MonitoringService:

    def __init__(self):
        self.target = None

    def healthcheck(self):
        if self.target.is_healthy():
            return ":)"
        else:
            logger.info("Healthcheck returning unhealthy")
            return abort(500)
        
    def start(self):

        """ Worker thread to start the web server """

        logger.info("Starting health monitor on //localhost:%s/healthcheck" % config.healthcheckPort)

        app.add_url_rule(
            config.healthcheckEndpoint,
            view_func=self.healthcheck
        )

        app.run(debug=False, host='0.0.0.0', port=config.healthcheckPort)

    def monitor(self, target):

        """ Run a webserver to server monitoring results at the healthcheck endpoint. """

        self.target = target

        t = threading.Thread(name="monitor", target=self.start)
        t.start()

        return t
