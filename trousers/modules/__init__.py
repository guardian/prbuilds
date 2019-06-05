
from .screenshots import ScreenshotsCheck
from .jsexceptions import ExceptionsCheck
from .webpagetest import WebPageCheck
from .a11yvalidation import A11YValidation
from .loadtest import LoadTestCheck
from .microdatacheck import MicroDataCheck
from .lighthouse import LightHouseCheck
from .amp import AmpCheck
from .selftest import SelfTest

allChecks = {
    "screenshots"  : ScreenshotsCheck(),
    "exceptions"  : ExceptionsCheck(),
    "webpagetest" : WebPageCheck(),
    "a11yvalidation": A11YValidation(),
    "loadtest": LoadTestCheck(),
    "microdata": MicroDataCheck(),
    "lighthouse": LightHouseCheck(),
    "amp": AmpCheck(),
    "selftest": SelfTest(),
}

def run_test(name, directories, params, logger):
    try:
        ret = allChecks[name].run(
            directories,
            params
        )
        logger.info("Check %s [SUCCESS]" % name)
        return ret
    except Exception as e:
        logger.info("Check %s [FAILED]" % name)
        logger.info(e)
        return None

def run_with_config(chkConfig, directories, logger):

    results = {}

    directories.check()

    for k, v in chkConfig.items():
        if k in allChecks.keys(): 
            res = run_test(
                k,
                directories,
                v,
                logger
            )
            if res is not None:
                results[k] = res


    return results
