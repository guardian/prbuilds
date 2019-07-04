
import os
from os import path

DEFAULT_ROOT = "/home/ubuntu"

class Directories:
    def __init__(self, root, repoName):
        self.root = root
        self.workspaceRoot = path.join(root,"workspace/")
        self.workspace = path.join(root,"workspace/", repoName + "/")
        self.artifacts = path.join(root,"artifacts/")
        self.builtins  = path.join(root,"prbuilds/trousers/builtins/")
    def check(self):
        assert path.isdir(self.root)
        assert path.isdir(self.workspaceRoot)
        assert path.isdir(self.artifacts)
        #assert path.isdir(self.builtins)

def directoriesForRepo(repoName):
    root = os.getenv("PRBUILDS_ROOT", DEFAULT_ROOT)
    return Directories(root, repoName)

prbuildsRoot = os.getenv("PRBUILDS_ROOT", DEFAULT_ROOT)
healthcheckEndpoint = "/healthcheck"
healthcheckPort = 9002
maxBuildTimeSeconds = 40*60
requiredFreeSpaceMB = 100
