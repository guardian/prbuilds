#!/usr/bin/env python

import unittest, json, boto3, os

from trouserlib.trousers import Trousers
from trouserlib.artifacts import ArtifactService
from trouserlib.pullrequest import PullRequest
from trouserlib.github import GitHubService
from trouserlib.sqs import Listener

class MockSubprocess:
    def call(self, args):
        self.lastArgs = args
        return 0

class MockResponse:
    def __init__(self, statusCode=200, text="OK"):
        self.status_code = statusCode
        self.text = text
    def raise_for_status(self):
        pass
    def json(self):
            return json.loads(self.text)

class MockRequests:
    def __init__(self, mockResponse=MockResponse()):
        self.response = mockResponse
    def post(self, url, data, auth):
        self.lastUrl = url
        self.lastData = data
        return self.response
    def get(self, url):
        self.lastUrl = url
        self.lastData = None
        return self.response
    def patch(self, url, data, auth):
        self.lastUrl = url
        self.lastData = data
        return self.response

class MockBucket:
    def upload_file(self, source, dest, ExtraArgs):
        self.source = source
        self.dest = dest
        self.args = ExtraArgs

class GitHubServiceTests(unittest.TestCase):

    """ does not talk to the real github """

    def test_post_comment(self):
        s = GitHubService("PRBuilds", "token")
        r = MockRequests()
        s.requests = r
        s.post_comment("url", "payload")
        self.assertEqual(r.lastUrl, "url")
        self.assertTrue("payload" in r.lastData)

    def test_has_comment(self):
        s = GitHubService("PRBuilds", "token")
        s.requests = MockRequests(
            MockResponse(200, open("data/gh_comment_api_response.json").read())
        )

        self.assertTrue(
            s.has_comment(
                "https://api.github.com/repos/guardian/frontend/issues/15499/comments"
            ) != None
        )

    def test_has_no_comment(self):
        s = GitHubService("Wooooow", "token")
        s.requests = MockRequests(
            MockResponse(200, open("data/gh_comment_api_response.json").read())
        )

        self.assertTrue(
            s.has_comment(
                "https://api.github.com/repos/guardian/frontend/issues/15499/comments"
            ) == None
        )

    def test_update_comment_when_one_exists(self):

        s = GitHubService("PRBuilds", "token")
        s.requests = MockRequests(
            MockResponse(200, open("data/gh_comment_api_response.json").read())
        )

        s.update_comment(
            "https://api.github.com/repos/guardian/frontend/issues/15499/comments",
            "This is the body"
        )

        self.assertEqual(
            s.requests.lastUrl,
            "https://api.github.com/repos/guardian/frontend/issues/comments/271269042"
        )

    def test_update_comment_when_none_exist(self):

        s = GitHubService("Wooooow", "token")
        s.requests = MockRequests(
            MockResponse(200, open("data/gh_comment_api_response.json").read())
        )

        s.update_comment(
            "https://api.github.com/repos/guardian/frontend/issues/15499/comments",
            "This is the body"
        )


class SQSTests(unittest.TestCase):

    def test_pull_request_event(self):
        mock = json.loads(open("data/gh_pull.mock").read())
        listener = Listener()
        action = listener.githubEventToAction(mock)
        self.assertTrue(action.hasPullRequest())
        self.assertEqual(action.repoName, "prbuildstub")
        self.assertEqual(action.cloneUrl, "https://github.com/MatthewJWalls/prbuildstub.git")
        self.assertEqual(action.pullRequest.prNum, 2)
        self.assertEqual(action.pullRequest.commentUrl, "https://api.github.com/repos/MatthewJWalls/prbuildstub/issues/1/comments")
        self.assertEqual(action.getKey(), "PR-2")

    def test_master_event(self):
        mock = json.loads(open("data/gh_master.mock").read())
        listener = Listener()
        action = listener.githubEventToAction(mock)
        self.assertFalse(action.hasPullRequest())
        self.assertEqual(action.repoName, "prbuildstub")
        self.assertEqual(action.cloneUrl, "https://github.com/MatthewJWalls/prbuildstub.git")
        self.assertEqual(action.getKey(), "master")


class ArtifactServiceTests(unittest.TestCase):

    def test_collect(self):
        a = ArtifactService()
        files = a.collect("./data")
        self.assertEqual(len([x for x in files]), 3)

    def test_content_type(self):
        a = ArtifactService()
        self.assertEqual(a.content_type("a.jpg"), "image/jpeg")
        self.assertEqual(a.content_type("a.png"), "image/png")
        self.assertEqual(a.content_type("a.txt"), "text/plain")
        self.assertEqual(a.content_type("a"), "text/plain")


class TrousersTests(unittest.TestCase):

    def test_compose_github_comment(self):

        from trouserlib.trousers import Reporter

        r = Reporter()

        msg = r.compose_github_comment("1",[
                "/home/ubuntu/artifacts/screenshots/a.jpg",
                "/home/ubuntu/artifacts/screenshots/b.jpg",
                "/home/ubuntu/artifacts/thrown-exceptions.txt",
                "/home/ubuntu/artifacts/performanceComparisonSummary.txt"
            ],{
                "screenshots": {"return code": 0, "raw_output": "picard"},
                "exceptions": {"return code": 0, "raw_output": "EXCEPTION"},
                "webpagetest": {"return code": 0, "raw_output": "WarningWarning"}
            }
        )

        print msg

        self.assertTrue("PR-1" in msg)
        self.assertTrue("screenshots/a.jpg" in msg)
        self.assertTrue("screenshots/b.jpg" in msg)
        self.assertTrue("thrown-exceptions.txt" in msg)
        self.assertTrue("-automated message" in msg)


if __name__ == '__main__':
    unittest.main()
