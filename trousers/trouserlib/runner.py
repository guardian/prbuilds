import subprocess, modules, yaml, logging, os, shutil
import traceback as tb
from config import directories

class Runner:

    def __init__(self, repo, branch):

        """ constructor """

        self.subprocess = subprocess
        self.repo = repo
        self.branch = branch

        if os.path.isdir(directories.artifacts):
            shutil.rmtree(directories.artifacts)

        os.mkdir(directories.artifacts)

    def clone_repo(self, url):
        
        """ clone down the remote repo """
        
        # full clone once

        if not os.path.exists(directories.workspace):
            
            ret = self.subprocess.call([
                "git",
                "clone",
                self.repo,
                directories.workspace
            ])

            if ret != 0:
                raise Exception("Failed to clone %s" % url)

        # fetch & reset

        old = os.getcwd()
        os.chdir(directories.workspace)

        self.subprocess.call([
            "git",
            "fetch"
        ])

        ret = self.subprocess.call([
            "git",
            "reset",
            "--hard",
            "origin/%s" % self.branch
        ])

        os.chdir(old)

        if ret != 0:
            raise Exception("Failed to pull branch: %s" % self.branch)

    def get_config(self):

        """ return yaml configuration from the cloned repo """

        location = "%s/.prbuilds/config.yml" % directories.workspace

        try:
            return yaml.load(open(location).read())
        except:
            raise Exception("Failed to load configuration file from %s" % location)

    def run_tests(self):

        """ run tests against a running app """

        logging.info("Running tests")

        return modules.run_with_config(
            self.get_config()["checks"]
        )

    def __enter__(self):

        """ set up the running app via an ansible play """

        logging.info("Cleaning up")
        self.cleanup()
        logging.info("Cloning")
        self.clone_repo(self.repo)
        logging.info("Setting up")
        self.setup()

        return self

    def setup(self):

        ret = self.subprocess.call([
            "ansible-playbook",
            os.path.join(directories.override, "setup.playbook.yml"),
            "--extra-vars",
            "branch=%s clone_url=%s" % (self.branch, self.repo),
            "-v"
        ])

        if ret != 0:
            raise Exception("PR Build setup failed")
    
    def cleanup(self):

        playbook = os.path.join(directories.override, "cleanup.playbook.yml")
        
        self.subprocess.call([
            "ansible-playbook", playbook
        ])
        
    def __exit__(self, type, value, traceback):
        pass
