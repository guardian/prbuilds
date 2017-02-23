import subprocess, modules, yaml, logging, os, shutil
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

        ret = self.subprocess.call([
            "git",
            "clone",
            "--depth",
            "1",
            "-b",
            self.branch,
            self.repo,
            directories.workspace
        ])

        if ret != 0:
            raise Exception("Failed to clone %s to %s" % (url, directories.workspace))

    def get_config(self):

        """ return yaml configuration from the cloned repo """

        location = "%s/.trousers/config.yml" % directories.workspace

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

        self.clone_repo(self.repo)

        conf = self.get_config()

        ret = self.subprocess.call([
            "ansible-playbook",
            os.path.join(directories.workspace, conf["setup"]["ansible"]),
            "--extra-vars",
            "branch=%s clone_url=%s" % (self.branch, self.repo),
            "-v"
        ])

        if ret != 0:
            raise Exception("Ansible play did not exit zero")

        return self

    def __exit__(self, type, value, traceback):

        """ stop the running app and clean up """
        conf = self.get_config()

        playbook = os.path.join(directories.workspace, conf["teardown"]["ansible"])

        self.subprocess.call([
            "ansible-playbook", playbook
        ])

        if traceback:
            logging.error("PR Build failed")
            logging.error(traceback)
