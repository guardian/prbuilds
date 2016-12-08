import unittest, json
from trousers import Trousers

class MockSubprocess:
    def call(self, args):
        self.lastArgs = args

class MockRequests:
    def post(self, url, data, auth):
        self.lastUrl = url
        self.lastData = data
        
class TrousersTests(unittest.TestCase):

    def test_extract_branch(self):
        mock = open("gh_pull.mock").read()
        t = Trousers()
        self.assertTrue(t.extract_branch(mock) == "changes")

    def test_build_calls_ansible(self):
        t = Trousers()
        p = MockSubprocess()
        t.subprocess = p
        t.build("hello")
        self.assertEqual(p.lastArgs[0], "ansible-playbook")
        self.assertEqual(p.lastArgs[3], "branch=hello")

    def test_github_comment(self):
        t = Trousers()
        r = MockRequests()
        t.requests = r
        t.github_comment("url", "testing")
        self.assertTrue("url" in r.lastUrl)
        self.assertEqual(r.lastData["body"], "testing")
        
if __name__ == '__main__':
        unittest.main()
