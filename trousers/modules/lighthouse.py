import subprocess
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
    
    def install(self, directories):

        if self.run_with_nvm("lighthouse --version", directories) == 0:
            return

        self.run_with_nvm("npm install -g lighthouse", directories)

        if self.run_with_nvm("lighthouse --version", directories) != 0:
            raise Exception("Unable to install lighthouse")
            
    def run(self, directories, params):

        """ run lighthouse """

        self.install(directories)

        pth = os.path.join(
            directories.artifacts,
            "lighthouse.html"
        )
        
        ret = self.run_with_nvm(
            "lighthouse --chrome-flags='--headless --no-sandbox' --output-path=%s %s" % (pth, params["url"]),
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

