
import logging, time, json

from .pullrequest import PullRequest
from .prbuildaction import PRBuildAction

def pushes_only(action):
    return action in ["opened", "synchronize"]

class Listener:

    def githubEventToAction(self, event):

        if "pull_request" in event and pushes_only(event["action"]):
            return PRBuildAction(
                event["pull_request"]["head"]["ref"],
                event["pull_request"]["head"]["repo"]["clone_url"],
                event["pull_request"]["head"]["repo"]["name"],
                PullRequest(
                    event["pull_request"]["comments_url"],
                    event["pull_request"]["number"]
                )
            )
        elif "ref" in event and "master" in event["ref"]:
            return PRBuildAction(
                "master",
                event["repository"]["clone_url"],
                event["repository"]["name"]
            )
        else:
            raise Exception("Unknown message type")

    def receive(self, queue, interval=5):

        """ Wait for an SQS message and then return it """

        while True:

            for message in queue.receive_messages():
                try:
                    action = self.githubEventToAction(json.loads(message.body))
                    return (message, action)
                except Exception as e:
                    logging.warning("Discarded github event")
                    logging.warning(e)
                    logging.warning(message.body)
                    message.delete()

            time.sleep(interval)
