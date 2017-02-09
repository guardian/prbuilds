import subprocess, modules

class Runner:

    def __init__(self, repo, branch, config):

        """ Constructor """

        self.subprocess = subprocess
        self.repo = repo
        self.branch = branch
        self.chkConfig = config
        
    def __enter__(self):

        """ set up the running app via an ansible play """

        playbook = self.chkConfig["setup"]["ansible"]
        
        ret = self.subprocess.call([
            "ansible-playbook",
            playbook,
            "--extra-vars",
            "branch=%s clone_url=%s" % (self.branch, self.repo),
            "-v"
        ])

        if ret != 0:
            raise Exception("Ansible play did not exit zero")

        return self

    def run_tests(self):

        """ run tests against a running app """
        
        return modules.run_with_config(self.chkConfig["checks"])

    def __exit__(self, type, value, traceback):

        """ stop the running app and clean up """

        playbook = self.chkConfig["teardown"]["ansible"]
        
        self.subprocess.call([
            "ansible-playbook", playbook
        ])        
