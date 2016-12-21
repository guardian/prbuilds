#!/usr/bin/env python

import unittest, json
from trousers import Trousers

class MockSubprocess:
    def call(self, args):
        self.lastArgs = args

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

class TrousersTests(unittest.TestCase):

    def test_extract_branch(self):
        mock = open("gh_pull.mock").read()
        t = Trousers()
        self.assertTrue(t.extract_branch(mock) == "overridable-devinfra")

    def test_build_calls_ansible(self):
        t = Trousers()
        p = MockSubprocess()
        t.subprocess = p
        t.build("repo", "hello")
        self.assertEqual(p.lastArgs[0], "ansible-playbook")
        self.assertEqual(p.lastArgs[3], "branch=hello clone_url=repo")

    def test_github_comment(self):
        t = Trousers()
        r = MockRequests()
        t.requests = r
        t.github_comment("url", "testing")
        self.assertTrue("url" in r.lastUrl)
        self.assertTrue("testing" in r.lastData)

    def test_extract_comment_url(self):
        t = Trousers()
        mock = open("gh_pull.mock").read()
        self.assertEqual(
            t.extract_comment_url(mock),
            "https://api.github.com/repos/MatthewJWalls/dotfiles/issues/1/comments"
        )
        
if __name__ == '__main__':
        unittest.main()
