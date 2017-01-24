
# PR-Builds

PR-Builds is a CI-Like build system which monitors incomming GitHub Pull requests, and
builds pushed code. The twist is that it is designed to fully run the app under test,
and then perform runtime regression testing against the live app, the results of which
are stamped onto the Pull Request.

This is a proof of concept system, and is implemented as a ~~small~~ moderate amount of 
glue code around the Ansible provisioning tool.

## Architecture

PR Builds is made up of two main components:

1. Ether - a process that pretends to be CAPI and responds with mock data.
2. Trousers - the script which handles the app build/test/github comment

These two pieces of software are run together on one or more worker machines.

In addition to this there is also a lambda which allows the builds to be triggered off
a http endpoint (i.e. a webhook for GitHub to integrate with).

The lifecycle of a PR Build looks like this:

1. GitHub webhook calls the lambda http endpoint
2. The Lambda publishes the message from GitHub into an SQS Queue
3. EC2 worker instances running the Trousers script recieve the messages from the SQS Queue
4. Trousers runs an Ansible play to build, run and test the code associated with the PR

The Queue-based architecture was chosen because it means the system can be scaled up
from a single worker instance to many, and ensures that the workload persists if something
goes wrong.

## Supported Checks

PRBuilds supports the following checks to be ran against the app under test

* Screenshots (frontend only right now)
* Exceptions (grabs all Javascript exceptions thrown when visiting a given url)
* WebPageTest (grabs latency, page weight and timing information for a given url)

## Docker

A Dockerfile is provided to assist with local testing of the app. Note that you will need
to have AWS environment variables (AWS_ACCESS_KEY_ID etc) populated locally before you
run the Docker instance to allow the frontend repo to run.

To build the image:

    docker build -t prbuilds .

To run the built image:

    docker run -dit \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    -e GH_NAME=MatthewJWalls \
    -e GH_TOKEN=<github token> \
    -e QUEUE_NAME=trousers_test \
    prbuilds

## Cloud Deployment

* CloudFormation template included
    * Parameters specify GitHub credentials and Queue name
* Instances clone down this repo and run the install script
* To update software, kill all the instances and let new ones launch
    * This should not cause lost work since the Queue will persist

## Ongoing work

* Scala rewrite for RiffRaff deployability
* Decouple from the Guardian frontend repo
* Robustness (error recovery, dummy ELB for healthchecks, etc)
