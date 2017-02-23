
from os import path

class Directories:
    def __init__(self, root):
        self.root = root
        self.workspace = path.join(root,"workspace/")
        self.prbuilds  = path.join(root,"prbuilds/")
        self.artifacts = path.join(root,"artifacts/")
        self.builtins  = path.join(root,"prbuilds/trousers/builtins/")
    def check(self):
        assert path.isdir(self.root)
        assert path.isdir(self.workspace)
        assert path.isdir(self.prbuilds)
        assert path.isdir(self.artifacts)
        assert path.isdir(self.builtins)

root = "/home/ubuntu"
directories = Directories(root)
