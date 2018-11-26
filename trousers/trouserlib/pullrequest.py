
import json

class PullRequest:

    def __init__(self, obj):

        head = json.loads(obj)

        if not "pull_request" in head:
            self.action = "unknown"
            self.commentUrl = ""
            self.branch = ""
            self.cloneUrl = ""
            self.repoName = ""
            self.prnum = ""
        else:
            data = head["pull_request"]
            self.action = head["action"]
            self.commentUrl = data["comments_url"]
            self.branch = data["head"]["ref"]
            self.cloneUrl = data["head"]["repo"]["clone_url"]
            self.repoName = data["head"]["repo"]["name"]
            self.prnum = data["number"]
