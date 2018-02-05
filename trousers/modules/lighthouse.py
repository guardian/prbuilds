import subprocess
import os

class LightHouseCheck:

    def __init__(self):

        """ constructor """

        self.out  = "thrown-exceptions.txt"

    def install(self):

        subprocess.call("which lighthouse", shell=True)
        
        if subprocess.call("lighthouse --version", shell=True) == 0:
            return
        
        subprocess.call("npm install -g lighthouse", shell=True)

        if subprocess.call("lighthouse --version", shell=True) != 0:
            raise Exception("Unable to install lighthouse")
            
    def run(self, directories, params):

        """ run lighthouse """

        self.install()

        pth = os.path.join(
            directories.artifacts,
            "lighthouse.html"
        )
        
        ps = subprocess.Popen(
            "lighthouse --output-path=%s %s" % (pth, params["url"]),
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

