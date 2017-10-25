
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

        """ Add or overwrite github comment """

        existing = self.has_comment(url)
        
        if existing:
            self.overwrite_comment(existing["url"], body)
        else:
            self.post_comment(url, body)

    def overwrite_comment(self, url, body):

        """ overwrite comment on the given api url with body """

	payload = { "body": body }
        
        res = self.requests.patch(
            url,
            data = json.dumps(payload),
            auth = HTTPBasicAuth(
                self.name,
                self.token
            )
        )

        res.raise_for_status()        
    
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
