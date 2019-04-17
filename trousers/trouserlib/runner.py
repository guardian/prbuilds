import subprocess, modules, yaml, logging, os, shutil
import traceback as tb

class Runner:

    def __init__(self, repo, branch, directories, logger):

        """ constructor """

        self.subprocess = subprocess
        self.repo = repo
        self.branch = branch
        self.directories = directories
        self.logger = logger

        if os.path.isdir(self.directories.artifacts):
            shutil.rmtree(self.directories.artifacts)

        os.mkdir(self.directories.artifacts)

        if not os.path.exists(self.directories.workspaceRoot):
            os.mkdir(self.directories.workspaceRoot)

    def clone_repo(self, url):

        """ clone down the remote repo """

        # full clone once

        self.logger.info("Cloning into %s" % self.directories.workspace)

        if not os.path.exists(self.directories.workspace):

            ret = self.subprocess.call([
                "git",
                "clone",
                self.repo,
                self.directories.workspace
            ])

            if ret != 0:
                raise Exception("Failed to clone %s" % url)

        if not os.path.exists(self.directories.workspace):
            raise Exception("workspace not created")

        # fetch & reset

        old = os.getcwd()
        os.chdir(self.directories.workspace)

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

        location = os.path.join(self.directories.workspace, ".prbuilds/config.yml")

        self.logger.info("Looking for configuration at %s" % location)

        try:
            return yaml.load(open(location).read())
        except:
            raise Exception("Failed to load configuration file from %s" % location)

    def run_tests(self):

        """ run tests against a running app """

        self.logger.info("Running tests")

        return modules.run_with_config(
            self.get_config()["checks"],
            self.directories,
            self.logger
        )

    def __enter__(self):

        """ set up the running app via an ansible play """

        self.clone_repo(self.repo)

        conf = self.get_config()

        playbook = os.path.join(self.directories.workspace, conf["setup"]["ansible"])

        self.logger.info("Running ansible playbook at %s" % playbook)

        try:
            ret = self.subprocess.call([
                "ansible-playbook",
                playbook,
                "--extra-vars",
                "branch=%s clone_url=%s workspace=%s" % (self.branch, self.repo, self.directories.workspace),
                "-v"
            ])
        except:
            raise Exception("Ansible threw an exception")

        if ret != 0:
            raise Exception("Ansible play did not exit zero")

        return self

    def __exit__(self, type, value, traceback):

        """ stop the running app and clean up """

        conf = self.get_config()

        playbook = os.path.join(self.directories.workspace, conf["teardown"]["ansible"])

        self.subprocess.call([
            "ansible-playbook", playbook
        ])

        if traceback:
            self.logger.warning("Traceback was not falsy, it was in fact:")
            tb.print_tb(traceback)
