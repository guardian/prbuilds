
import subprocess, shutil, os

class WebPageCheck:

    def __init__(self):

        """ constructor """

        self.path = "/books/2014/may/21/guardian-journalists-jonathan-freedland-ghaith-abdul-ahad-win-orwell-prize-journalism"

    def run(self, host, directories):

        repo = "https://github.com/michaelwmcnamara/single-page-performance-tester.git"

        """ Remove the last version """

        if os.path.isdir(os.path.join(directories.root, "single-page-performance-tester")):
            shutil.rmtree(os.path.join(directories.root, "single-page-performance-tester"))
        
        """ Clone the repo """

        ps = subprocess.Popen(
            "git clone %s" % repo,
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.root
        )
        
        out, err = ps.communicate()

        """ run the start script """

        cmd = "bash runme.sh %s%s %s/" % (host, self.path, directories.artifacts)

        ps = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            cwd=os.path.join(
                directories.root,
                "single-page-performance-tester"
            )
        )

        out, err = ps.communicate()        
    
        return {
            "return_code": ps.returncode,
            "raw_output": out
        }

