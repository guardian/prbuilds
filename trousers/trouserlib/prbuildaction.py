
class PRBuildAction:

    def __init__(self, branch, cloneUrl, repoName, pullRequest=None):
        self.branch = branch
        self.cloneUrl = cloneUrl
        self.repoName = repoName
        self.pullRequest = pullRequest

    def hasPullRequest(self):
        return self.pullRequest != None

    def getKey(self):
        return "PR-%s" % self.pullRequest.prNum if self.hasPullRequest() else "%s-master" % self.repoName
