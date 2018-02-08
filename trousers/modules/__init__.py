
from .screenshots import ScreenshotsCheck
from .jsexceptions import ExceptionsCheck
from .webpagetest import WebPageCheck
from .a11yvalidation import A11YValidation
from .loadtest import LoadTestCheck
from .microdatacheck import MicroDataCheck
from .lighthouse import LightHouseCheck

from config import directories

allChecks = {
    "screenshots"  : ScreenshotsCheck(),
    "exceptions"  : ExceptionsCheck(),
    "webpagetest" : WebPageCheck(),
    "a11yvalidation": A11YValidation(),
    "loadtest": LoadTestCheck(),
    "microdata": MicroDataCheck(),
    "lighthouse": LightHouseCheck()
}

def run_test(name, directories, params):
    try:
        print "Running %s" % k        
        allChecks[name].run(
            directories,
            params
        )
    except:
        print "Failed to run check: %s" % name

def run_with_config(chkConfig):

    results = {}

    directories.check()

    for k, v in chkConfig.items():
        if k in allChecks.keys():
            results[k] = run_test(
                name,
                directories,
                v
            )

    return results
