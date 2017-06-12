import subprocess
import os

class LoadTestCheck:

    def __init__(self):

        """ constructor """

        self.out  = "loadtesting.txt"

    def run(self, directories, params):

        """ run very basic load test using apache ab """

        ps = subprocess.Popen(
            "ab -n 100 -c 10 %s" % (params["url"]),
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

        return {
            "return_code": ps.returncode,
            "raw_output": out
        }
