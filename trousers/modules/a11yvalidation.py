import subprocess
import os

def escape_ansi(line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)

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
        out_escaped = escape_ansi(out)

        open(
            os.path.join(
                directories.artifacts,
                "a11y-report.txt"
            ),"w"
        ).write(out_escaped)

        return {
            "return_code": ps.returncode,
            "raw_output": out
        }
