#!/usr/bin/env python

import unittest, json, boto3, os
from trousers import Trousers, PullRequest, GitHubService, ArtifactService

class MockSubprocess:
    def call(self, args):
        self.lastArgs = args
        return 0

class MockResponse:
    def __init__(self):
        self.status_code = 200
        self.text = "OK"
    def raise_for_status(self):
        pass
    
class MockRequests:
    def post(self, url, data, auth):
        self.lastUrl = url
        self.lastData = data
        return MockResponse()

class MockBucket:
    def upload_file(self, source, dest, ExtraArgs):
        self.source = source
        self.dest = dest
        self.args = ExtraArgs


class GitHubServiceTests(unittest.TestCase):

    def test_post_comment(self):
        s = GitHubService()
        r = MockRequests()
        s.requests = r
        s.post_comment("url", "payload")
        self.assertEqual(r.lastUrl, "url")
        self.assertTrue("payload" in r.lastData)

    def test_has_comment(self):
        s = GitHubService()
        self.assertTrue(
            s.has_comment(
                "https://api.github.com/repos/guardian/frontend/issues/15499/comments",
                "PR build"
            )
        )

    def test_has_no_comment(self):
        s = GitHubService()
        self.assertFalse(
            s.has_comment(
                "https://api.github.com/repos/guardian/frontend/issues/15499/comments",
                "WoooWooooowoowoww"
            )
        )
        
class PullRequestTests(unittest.TestCase):

    def test_fields(self):
        mock = open("data/gh_pull.mock").read()
        pull = PullRequest(mock)
        self.assertEqual(pull.branch, "overridable-devinfra")
        self.assertTrue("dotfiles" in pull.cloneUrl)
        self.assertTrue("dotfiles" in pull.commentUrl)
        self.assertEqual(pull.prnum, 1)

class ArtifactServiceTests(unittest.TestCase):

    def test_collect(self):
        a = ArtifactService()
        files = a.collect("./data")
        self.assertEqual(len([x for x in files]), 1)

    def test_content_type(self):
        a = ArtifactService()
        self.assertEqual(a.content_type("a.jpg"), "image/jpeg")
        self.assertEqual(a.content_type("a.png"), "image/png")
        self.assertEqual(a.content_type("a.txt"), "text/plain")
        self.assertEqual(a.content_type("a"), "text/plain")

class TrousersTests(unittest.TestCase):
        
    def test_build_calls_ansible(self):
        t = Trousers()
        p = MockSubprocess()
        t.subprocess = p
        t.build("repo", "hello")
        self.assertEqual(p.lastArgs[0], "ansible-playbook")
        self.assertEqual(p.lastArgs[3], "branch=hello clone_url=repo")

    def test_compose_github_comment(self):
        t = Trousers()
        msg = t.compose_github_comment("1", [
            "/home/ubuntu/artifacts/screenshots/a.jpg",
            "/home/ubuntu/artifacts/screenshots/b.jpg"
        ])
        self.assertTrue("PR-1" in msg)
        self.assertTrue("screenshots/a.jpg" in msg)
        self.assertTrue("screenshots/b.jpg" in msg)


if __name__ == '__main__':
        unittest.main()
