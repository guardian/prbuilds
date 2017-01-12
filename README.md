
# PR-Builds

PR-Builds is a CI-Like build system which monitors incomming GitHub Pull requests, and
builds pushed code. The twist is that it is designed to fully run the app under test,
and then perform runtime regression testing against the live app, the results of which
are stamped onto the Pull Request.

This is a proof of concept system, and is implemented as a small amount of glue code
around the Ansible provisioning tool.

## Implementation

PR Builds is made up of two main components:

1. Ether - a process that pretends to be CAPI and responds with mock data.
2. Trousers - the script which handles the app build/test/github comment

In addition to this there is also a lambda which allows the builds to be triggered off
a http endpoint (i.e. a webhook for GitHub to integrate with).

The lifecycle of a PR Build looks like this:

1. GitHub webhook calls the lambda http endpoint
2. The Lambda publishes the message from GitHub into an SQS Queue
3. EC2 Instances running the Trousers script recieve the messages from the SQS Queue
4. Trousers runs an Ansible play to build, run and test the code associated with the PR

The Queue-based architecture was chosen because it means the system can be scaled up
from a single builde instance to many, and ensures that the workload persists if something
goes wrong.

## Cloud Deployment

* CloudFormation template included
    * Parameters specify GitHub credentials and Queue name
* Instances clone down this repo and run the install script
* To update software, kill all the instances and let new ones launch
    * This should not cause lost work since the Queue will persist

## Ongoing work

* Scala rewrite for RiffRaff deployability
* Better modularisation of the tests to be ran
* Remove hardcoding for the Guardian frontend
