
import subprocess, shutil, os

class WebPageCheck:

    def run(self, host, directories):

        """ run the built-in script """

        ps = subprocess.Popen(
            "webpagetest.sh",
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.builtins
        )
        
        out, err = ps.communicate()        
        
        return {
            "return_code": ps.returncode,
            "raw_output": out
        }
