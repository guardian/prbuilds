import subprocess

class A11yValidate:

    def run(self, host, directories):

        ps = subprocess.Popen(
            'bash -c ". ~/.nvm/nvm.sh; nvm use; make validate-a11y"',
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.workspace
        )

        out, err = ps.communicate()

        return {
            "return_code": ps.returncode,
            "raw_output": out
        }
