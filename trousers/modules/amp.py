
import requests
import os

class AmpCheck:

    def __init__(self):

        """ constructor """

        self.out = "thrown-exceptions.txt"
        self.API = "https://tung2a7iji.execute-api.eu-west-1.amazonaws.com/PROD/validate/html"

    def get_local_html(self, endpoint):

        response = requests.get(endpoint)

        if response.status_code != 200:
            raise Exception("Non-200 response from endpoint for AMP test")

        return response.content

    def run(self, directories, params):

        response = requests.post(
            self.API, 
            json={ 
                "htmlStrings":[ 
                    self.get_local_html(params["url"])
                ]
            }
        )

        open(
            os.path.join(
                directories.artifacts,
                "amp-report.txt"
            ),"w"
        ).write(response.content)

        return {
            "return_code": response.status_code,
            "raw_output": response.content,
            "metrics": [
                ("failed_endpoints", "number", response.content.count("false"))
            ]
        }

if __name__ == "__main__":

    """ test """

    class DirectoriesMock:
        artifacts = "./"
        workspace = "./"

    ac = AmpCheck()

    result = ac.run(
        DirectoriesMock(),
        { "url" : "https://amp.theguardian.com/money/2017/mar/10/ministers-to-criminalise-use-of-ticket-tout-harvesting-software" }
    )

    print(result)
