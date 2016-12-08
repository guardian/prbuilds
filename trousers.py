
import boto3, time, ansible, subprocess, json

QUEUE_NAME = 'mjwtest';

def listen_and_block(queue):

    """ Wait for an SQS message and then return it """
    
    while True:
        for message in queue.receive_messages():
            return message
        time.sleep(5)

def build(branch="master"):

    """ Run the build script """

    print "Running ansible play for branch: %s" % branch
    
    subprocess.call([
        "ansible-playbook",
        "build.playbook.yml"
    ], stdout=open("log", "w"))

    print "Play finished"

if __name__ == '__main__':

    session = boto3.Session(
        profile_name='frontend',
        region_name='eu-west-1'
    )
    
    sqs = session.resource('sqs')
    
    queue = sqs.get_queue_by_name(
        QueueName=QUEUE_NAME
    )

    print "Waiting for messages"
    
    while True:
        msg = listen_and_block(queue)
        build(json.loads(msg.body)["branch"])
        msg.delete()
        

