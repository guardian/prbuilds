import subprocess
import os

class LightHouseCheck:

    def install(self, directories):

        subprocess.call("which lighthouse", shell=True)
        
        if subprocess.call("lighthouse --version", shell=True) == 0:
            return

        ps = subprocess.Popen(
            'bash -c ". ~/.nvm/nvm.sh; nvm use; npm install -g lighthouse"',
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.workspace
        )

        out, err = ps.communicate()

        print "lighthouse install errors: %s" % err
        
        if subprocess.call("lighthouse --version", shell=True) != 0:
            raise Exception("Unable to install lighthouse")
            
    def run(self, directories, params):

        """ run lighthouse """

        self.install(directories)

        pth = os.path.join(
            directories.artifacts,
            "lighthouse.html"
        )
        
        ps = subprocess.Popen(
            "lighthouse --chrome-flags=\"--headless --no-sandbox\" --output-path=%s %s" % (pth, params["url"]),
            shell=True,
            stdout=subprocess.PIPE
        )

        out, err = ps.communicate()

        return {
            "return_code": ps.returncode,
            "raw_output": out,
            "metrics": []
        }

if __name__ == "__main__":

    """ test """

    class DirectoriesMock:
        artifacts = "./"

    lh = LightHouseCheck()

    lh.run(
        DirectoriesMock(),
        {"url" : "https://theguardian.co.uk"}
    )

