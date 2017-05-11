
from .pullrequest import PullRequest
import time

def pushes_only(pr):
    return pr.action in ["opened", "synchronize"]

class Listener:

    def receive(self, queue, filt=pushes_only, interval=5):

        """ Wait for an SQS message and then return it """
    
        while True:
            for message in queue.receive_messages():
                pr = PullRequest(message.body)
                if filt(pr):
                    return (message, pr)
                else:
                    message.delete()
            time.sleep(interval)
