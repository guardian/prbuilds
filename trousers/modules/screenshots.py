import subprocess, shutil, os

class ScreenshotsCheck:

    def run(self, directories, params):

        ps = subprocess.Popen(
            'bash -c ". ~/.nvm/nvm.sh; nvm use; make screenshots"',
            shell=True,
            stdout=subprocess.PIPE,
            cwd=directories.workspace
        )

        out, err = ps.communicate()

        if ps.returncode == 0:
            shutil.copytree(
                os.path.join(directories.workspace, "screenshots"),
                os.path.join(directories.artifacts, "screenshots")
            )

        return {
            "return_code": ps.returncode,
            "raw_output": out
        }
