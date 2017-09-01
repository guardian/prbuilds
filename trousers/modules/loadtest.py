import subprocess
import os
import re

class LoadTestCheck:

    def __init__(self):

        """ constructor """

        self.out  = "loadtesting.txt"

    def run(self, directories, params):

        """ run very basic load test using apache ab """

        ps = subprocess.Popen(
            "ab -n 2000 -c 100 %s" % (params["url"]),
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.builtins
        )

        out, err = ps.communicate()

        open(
            os.path.join(
                directories.artifacts,
                self.out
            ),"w"
        ).write(out)

        timetaken = re.findall('Time taken for tests:\s+(\d+\.\d+) seconds', out)[0]
        return {
            "return_code": ps.returncode,
            "raw_output": out,
            "metrics": [
                ("load_test_seconds", "number", timetaken)
            ]
        }
