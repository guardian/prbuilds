
import json

class PullRequest:

    def __init__(self, obj):
        head = json.loads(obj)
        data = head["pull_request"]
        self.commentUrl = data["comments_url"]
        self.branch = data["head"]["ref"]
        self.cloneUrl = data["head"]["repo"]["clone_url"]
        self.prnum = data["number"]
        self.action = head["action"]
