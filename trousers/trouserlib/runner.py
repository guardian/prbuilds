import subprocess, jinja2, modules

class Runner:

    def __enter__(self, repo, branch):

        """ set up the running app via an ansible play """
        
        ret = self.subprocess.call([
            "ansible-playbook",
            "build.playbook.yml",
            "--extra-vars",
            "branch=%s clone_url=%s" % (branch, repo),
            "-v"
        ])

        if ret != 0:
            raise Exception("Ansible play did not exit zero")

        return self

    def run_tests(self):

        """ run tests against a running app """
        
        return modules.run_all()

    def __exit__(self, type, value, traceback):

        """ stop the running app and clean up """

        self.subprocess.call([
            "ansible-playbook",
            "cleanup.playbook.yml"
        ])        
