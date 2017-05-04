import subprocess
import os

class A11YValidation:

    def run(self, directories, params):

        """ run accessibility check validation """

        ps = subprocess.Popen(
            'bash -c ". ~/.nvm/nvm.sh; nvm use; make validate-a11y"',
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.workspace
        )

        out, err = ps.communicate()

        open(
            os.path.join(
                directories.artifacts,
                "a11y-report.txt"
            ),"w"
        ).write(out)

        return {
            "return_code": ps.returncode,
            "raw_output": out
        }
