
import requests
from requests.auth import HTTPBasicAuth

class GitHubService:

    def __init__(self, name, token):

        """ constructor """

        self.name = name
        self.token = token
        self.requests = requests

    def has_comment(self, url, including):

        """ Is the given text included anywhere """
        
        res = self.requests.get(url)

        res.raise_for_status()

        for post in res.json():
            if including in post["body"]:
                return True

        return False
        
    def post_comment(self, url, body):

        """ Add github comment using url endpoint """
       
	payload = { "body": body }
        
        res = self.requests.post(
            url,
            data = json.dumps(payload),
            auth = HTTPBasicAuth(
                self.name,
                self.token
            )
        )

        res.raise_for_status()
