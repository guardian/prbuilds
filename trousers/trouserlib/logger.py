import time, logging, boto3

class CloudWatchLoggingHandler(logging.StreamHandler):

    def __init__(self, client, group, stream):

        """ constructor """

        logging.StreamHandler.__init__(self)
        self.group = group
        self.stream = "%s-%d" % (stream, int(round(time.time() * 1000)))
        self.client = client
        self.sequenceToken = None
        self.setLevel(logging.INFO)

        self.init_logs()

    def init_logs(self):

        """ set up log groups and streams """
        
        try:
            self.client.create_log_group(logGroupName=self.group)
        except Exception as ex:
             print "Failed to create log group. It probably already existed so ignoring"

        try:
            self.client.create_log_stream(logGroupName=self.group, logStreamName=self.stream)
        except Exception as ex:
             print "Failed to create log stream. It probably already existed so ignoring"

    def write_log(self, msg):

        """ write a single log message """

        if self.client is None:
            return

        timestamp = int(round(time.time() * 1000))

        if self.sequenceToken is None:

            response = self.client.put_log_events(
                logGroupName=self.group,
                logStreamName=self.stream,
                logEvents=[
                    {
                        'timestamp': timestamp,
                        'message': msg
                    }
                ]
            )

            self.sequenceToken = response["nextSequenceToken"]

        else:

            response = self.client.put_log_events(
                logGroupName=self.group,
                logStreamName=self.stream,
                logEvents=[
                    {
                        'timestamp': timestamp,
                        'message': msg
                    }
                ],
                sequenceToken=self.sequenceToken
            )

            self.sequenceToken = response["nextSequenceToken"]
    
    def emit(self, record):

        """ overrides StreamHandler """

        self.write_log(self.format(record))

if __name__ == "__main__":

    """ self test """

    session = boto3.Session(
        region_name='eu-west-1'
    )

    cwl = session.client('logs')

    logger = logging.getLogger("buildlog")
    logger.addHandler(CloudWatchLoggingHandler(cwl, "prbuilds", "testing"))
    logger.setLevel(logging.INFO)
    logger.info("Log testing 1, ignore")
    logger.info("Log testing 2, ignore")
    logger.info("Log testing 3, ignore")