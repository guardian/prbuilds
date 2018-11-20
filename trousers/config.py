
from os import path

class Directories:
    def __init__(self, root, repoName):
        self.root = root
        self.workspaceRoot = path.join(root,"workspace/")
        self.workspace = path.join(root,"workspace/", repoName + "/")
        self.prbuilds  = path.join(root,"prbuilds/")
        self.artifacts = path.join(root,"artifacts/")
        self.builtins  = path.join(root,"prbuilds/trousers/builtins/")
    def check(self):
        assert path.isdir(self.root)
        assert path.isdir(self.workspace)
        assert path.isdir(self.prbuilds)
        assert path.isdir(self.artifacts)
        assert path.isdir(self.builtins)

def directoriesForRepo(repoName):
    root = "/home/ubuntu"
    return Directories(root, repoName)

healthcheckEndpoint = "/healthcheck"
healthcheckPort = 9002
maxBuildTimeSeconds = 40*60
