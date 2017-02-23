
import subprocess, shutil, os

class WebPageCheck:

    def run(self, directories, params):

        """ run the built-in script """

        ps = subprocess.Popen(
            "./webpagetest.sh %s %s" % (params["url"], directories.artifacts),
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.builtins
        )

        out, err = ps.communicate()

        content = open(
            os.path.join(
                directories.artifacts,
                "performanceComparisonSummary.txt"
            )
        ).read()

        return {
            "return_code": ps.returncode,
            "raw_output": content
        }
