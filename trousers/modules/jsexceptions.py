import subprocess
import os

class ExceptionsCheck:

    def __init__(self):

        """ constructor """

        self.path = "/books/2014/may/21/guardian-journalists-jonathan-freedland-ghaith-abdul-ahad-win-orwell-prize-journalism"
        self.out  = "thrown-exceptions.txt"
    
    def run(self, host, directories):

        """ run exceptions checker test """

        url  = "%s%s" % (host, self.path)        

        ps = subprocess.Popen(
            "phantomjs exceptions.js %s" % (url),
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
            "raw_output": out
        }
