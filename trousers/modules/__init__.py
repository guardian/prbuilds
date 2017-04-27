from .screenshots import ScreenshotsCheck
from .jsexceptions import ExceptionsCheck
from .webpagetest import WebPageCheck
from .a11yvalidate import A11yValidate
from os import path

allChecks = {
    "sceenshots"   : ScreenshotsCheck(),
    "exceptions"   : ExceptionsCheck(),
    "webpagetest"  : WebPageCheck(),
    "a11yvalidate" : A11yValidate(),
}

default_host = "http://localhost:9000"

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

def run_all():

    results = {}

    directories = Directories(
        root="/home/ubuntu"
    )

    directories.check()

    for k, v in allChecks.items():

        print "Running %s" % k
        results[k] = v.run(default_host, directories)

    return results
