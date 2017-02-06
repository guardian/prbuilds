def pushes_only(pr):
    return pr.action in ["opened", "synchronize"]

class Listener:

    def receive(self, queue, filt=pushes_only, interval=5):

        """ Wait for an SQS message and then return it """
    
        while True:
            for message in queue.receive_messages():
                if filt(message):
                    return message
            time.sleep(interval)
