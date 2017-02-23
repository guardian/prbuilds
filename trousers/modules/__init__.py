
from .screenshots import ScreenshotsCheck
from .jsexceptions import ExceptionsCheck
from .webpagetest import WebPageCheck
from config import directories

allChecks = {
    "screenshots"  : ScreenshotsCheck(),
    "exceptions"  : ExceptionsCheck(),
    "webpagetest" : WebPageCheck()
}

def run_with_config(chkConfig):

    results = {}

    directories.check()

    for k, v in chkConfig.items():
        if k in allChecks.keys():
            print "Running %s" % k
            results[k] = allChecks[k].run(
                directories,
                params=v
            )

    return results
