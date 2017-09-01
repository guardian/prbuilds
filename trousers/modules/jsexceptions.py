import subprocess
import os

class ExceptionsCheck:

    def __init__(self):

        """ constructor """

        self.out  = "thrown-exceptions.txt"

    def run(self, directories, params):

        """ run exceptions checker test """

        ps = subprocess.Popen(
            "phantomjs exceptions.js %s" % (params["url"]),
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.builtins
        )

        out, err = ps.communicate()

        open(
            os.path.join(
                directories.artifacts,
                "thrown-exceptions.js"
            ),"w"
        ).write(out)

        return {
            "return_code": ps.returncode,
            "raw_output": out,
            "metrics": [
                ("exceptions_count", "number", out.count("EXCEPTION"))
            ]
        }
