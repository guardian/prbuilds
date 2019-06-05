
# PR-Builds

PRBuilds records the runtime performance characteristics of webapps at the Pull Request stage, and
stamps the results onto the GitHub PR.

Whereas a CI system runs your tests and analyses your *code*, PRBuilds fully runs the app under
test and checks it's runtime behavior. PRBuilds exposes your app to the public internet as well,
so it can integrate with 3rd party web-based testing tools.

## Architecture

PR Builds is made up of two main components:

1. Ether - a service that pretends to be CAPI and responds with mock data.
2. Trousers - the service which builds your app and runs the checks

PRBuilds runs as one or more worker machines, each running both Ether and Trousers. You can
arbitraily add more workers to scale up with no additional configuration.

The worker instances grab messages off of an SQS Queue, and there is lambda which exposes a http
endpoint for GitHub webhooks to integrate with.

The lifecycle of a PR Build looks like this:

1. GitHub webhook calls the lambda http endpoint
2. The Lambda publishes the message from GitHub into an SQS Queue
3. EC2 worker instances running the Trousers service recieve the messages from the SQS Queue
4. Trousers runs an Ansible play to build, run and test the code associated with the PR

cloudformation files are provided if you want to run your own stack

## Integrating a webapp with PRBuilds

1. Create a directory called .prbuilds at the root of your repository
2. Create a ./prbuilds/config.yml file that looks like this

```
    setup:
      ansible: .prbuilds/setup.playbook.yml
    teardown:
      ansible: .prbuilds/cleanup.playbook.yml
    checks:
      screenshots:
        url: http://theguardian.com
      exceptions:
        url: http://theguardian.com
      ...etc...
```

3. Create the associated setup.playbook.yml and cleanup.playbook.yml. These files are ansible scripts
   that describe how to run, and how to kill and clean up, your app. [example](https://github.com/guardian/frontend/tree/master/.prbuilds)

4. Configure your GitHub repo to include a webhook that points to the PRBuilds lambda endpoint.

## Supported Checks

PRBuilds supports the following checks to be ran against the app under test

|Config file name|Config file params|Desc                                    |
|----------------|------------------|----------------------------------------|
| screenshots    | url              | take a screenshot                      |
| exceptions     | url              | record javascript exceptions DEPRECATED|
| webpagetest    | url              | run webpagetest tool DEPRECATED        |
| loadtest       | url              | run apache benchmark                   |
| microdata      | url              | validate microdata structured data     |
| a11yvalidation | url              | run a11y accessibility check           |
| amp            | url              | run AMP validation check               |


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
    -e GH_NAME=NOONE \
    -e GH_TOKEN=NOTHING \
    -e QUEUE_NAME=trousers_test \
    prbuilds

Once the container launches, it will automatically begin a test run against mock data. The mock data for this test run is currently contained in the trousers/data/gh_pull file. Be aware that PRBuilds running in the container will pull down the target repository, run all the associated checks, and comment on the GitHub pull request for real.

## Integrating new checks into PRBuilds

To create a new kind of check for PRBuilds to run, you need to introduce a new class inside of the trousers/modules directory. This class should have a single function, 'run' which takes two parameters for directories and params.

Next, alter the trousers/modules/__init__.py file to include your new module in the map

Finally, you need to edit the trousers/github_comment.template to include your new test. The value returned from your module's ```run``` function will be passed to the template.

If you would like to bundle a script or binary into PRBuilds that you want to execute as a check, you can place these static scripts/binaries into the trousers/builtins package, and then invoke them from your PRBuilds check (See the jsexceptions check - this uses a builtin phantomjs script)

## Metrics

Each test can generate metrics which will be logged into a Dynamo table.

## Cloud Deployment

* CloudFormation template included
    * Parameters specify GitHub credentials and Queue name
* Instances clone down this repo and run the install script
* To update software, kill all the instances and let new ones launch
    * This should not cause lost work since the Queue will persist

## Ongoing work

* Scala rewrite for RiffRaff deployability
* Unhardcode the test data for the Docker run

