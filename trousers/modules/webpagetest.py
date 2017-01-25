
import subprocess, shutil, os

class WebPageCheck:

    def __init__(self):

        """ constructor """

        self.path = "/books/2014/may/21/guardian-journalists-jonathan-freedland-ghaith-abdul-ahad-win-orwell-prize-journalism"
    
    def run(self, host, directories):

        """ run the built-in script """

        ps = subprocess.Popen(
            "./webpagetest.sh %s %s" % (self.path, directories.artifacts),
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
