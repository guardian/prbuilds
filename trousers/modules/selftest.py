import subprocess
import os

class SelfTest:

    def run(self, directories, params):

        """ run self check """

        ps = subprocess.Popen(
            "chromium-browser --headless %s" % (params["url"]),
            shell=True,
            stdout=subprocess.PIPE
        )

        out, err = ps.communicate()

        return {
            "return_code": 0,
            "raw_output": out,
            "metrics": []
        }
