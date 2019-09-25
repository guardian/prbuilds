import subprocess
import time
import os

class LightHouseCheck:

    def nvm_is_absent(self):

        ps = subprocess.Popen(
            'bash -c ". ~/.nvm/nvm.sh; nvm use"',
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.workspace
        )

        out, err = ps.communicate()

        return ps.returncode != 0 or "command not found" in out
    
    def run_with_nvm(self, cmd, directories):

        ps = subprocess.Popen(
            'bash -c ". ~/.nvm/nvm.sh; nvm use; %s"' % cmd,
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.workspace
        )

        out, err = ps.communicate()

        return ps.returncode

    def run_without_nvm(self, cmd, directories):

        ps = subprocess.Popen(
            'bash -c "%s"' % cmd,
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

        print("Checking for NVM...")

        if self.nvm_is_absent:

            print("Nvm not present, running directly")

            ret = self.run_without_nvm(
                "lighthouse --chrome-flags='--headless --no-sandbox' --output=json --output=html --save-assets --output-path=%s %s" % (pth, params["url"]),
                directories
            )

            return {
                "return_code": ret,
                "raw_output": "mock, changeme",
                "metrics": []
            }
            
        else:

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
