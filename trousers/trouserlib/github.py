
import requests, json
from requests.auth import HTTPBasicAuth

class GitHubService:

    def __init__(self, name, token):

        """ constructor """

        self.name = name
        self.token = token
        self.requests = requests

    def has_comment(self, url):

        """ have we already commented on this pr """
        
        res = self.requests.get(url)

        res.raise_for_status()

        for post in res.json():
            if post["user"]["login"] == self.name:
                return post

        return None

    def update_comment(self, url, body):

        """ Add github comment only if it doesn't exist """

        if not self.has_comment(url):
            self.post_comment(url, body)
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
