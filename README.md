
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

## Using Docker to test PRBuilds

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

Once the container launches, it will automatically begin a test run against mock data. The mock data for this test run is currently contained in the trousers/data/gh_pull file. Be aware that PRBuilds running in the container will pull down the target repository, run all the associated checks, and comment on the GitHub pull request for real.

## Integrating new checks into PRBuilds

To create a new kind of check for PRBuilds to run, you need to introduce a new class inside of the trousers/modules directory. This class should have a single function, 'run' which takes two parameters for directories and params.

You also need to edit the trousers/github_comment.template to include your new test. The value returned from your run function will be passed to the template.

If your check code is simple integrating with an external API over the internet, or invoking a task you expect to be present on the repository under test (such as a 'make' style command) then this should be all you need.

If you would like to bundle a script or binary into PRBuilds that you want to execute as a check, you can place these static scripts/binaries into the trousers/builtins package, and then invoke them from your PRBuilds check (See the jsexceptions check - this uses a builtin phantomjs script)

## Cloud Deployment

* CloudFormation template included
    * Parameters specify GitHub credentials and Queue name
* Instances clone down this repo and run the install script
* To update software, kill all the instances and let new ones launch
    * This should not cause lost work since the Queue will persist

## Ongoing work

* Scala rewrite for RiffRaff deployability
* Unhardcode the test data for the Docker run

