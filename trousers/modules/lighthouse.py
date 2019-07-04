import subprocess
import time
import os

class LightHouseCheck:

    def run_with_nvm(self, cmd, directories):

        ps = subprocess.Popen(
            'bash -c ". ~/.nvm/nvm.sh; nvm use; %s"' % cmd,
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.workspace
        )

        out, err = ps.communicate()

        return ps.returncode

    def run(self, directories, params):

        """ run lighthouse """

        pth = os.path.join(
            directories.artifacts,
            "%s.html" % int(time.time())
        )

        ret = self.run_with_nvm(
            "lighthouse --chrome-flags='--headless --no-sandbox' --output=json --output=html --save-assets --output-path=%s %s" % (pth, params["url"]),
            directories
        )

        return {
            "return_code": ret,
            "raw_output": "mock, changeme",
            "metrics": []
        }

if __name__ == "__main__":

    """ test """

    class DirectoriesMock:
        artifacts = "./"
        workspace = "./"

    lh = LightHouseCheck()

    lh.run(
        DirectoriesMock(),
        {"url" : "https://theguardian.co.uk"}
    )
