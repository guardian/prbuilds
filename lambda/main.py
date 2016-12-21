import os
import json
import boto3

QUEUE_NAME = os.environ['SQS_QUEUE']
AWS_USER = os.environ['AWS_USER']
AWS_KEY = os.environ['AWS_KEY']

def github_webhook_to_sqs(event, context):

    """ When called, dumps the content of event.body into an sqs queue """
    
    if "body" not in event:
        
        return { "message" : "Hook was called with no body" }
    
    try:
        
        sqs = boto3.Session(
            aws_access_key_id=AWS_USER,
            aws_secret_access_key=AWS_KEY,
            region_name='eu-west-1'
        ).resource('sqs')
        
        queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)
        
        queue.send_message(MessageBody=event["body"])
        
        return { "message" : "Message posted to %s" % QUEUE_NAME }
    
    except:
        
        return { "message" : "Message posting failed" }


