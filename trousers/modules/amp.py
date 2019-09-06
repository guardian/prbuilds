
import requests
import os
import json

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

    def check_page(self, url):
        response = requests.post(
            self.API, 
            json={ 
                "htmlStrings":[ 
                    self.get_local_html(url)
                ]
            }
        )
        return response.content

    def run(self, directories, params):

        reportPath = os.path.join(
            directories.artifacts,
            "amp-report.txt"
        )

        def write_to_report(url, result):
            prettyJson = json.dumps(json.loads(result), indent = 2, sort_keys=False)
            open(reportPath ,"a").write("\nFor page %s:\n%s\n" % (url, prettyJson))
        
        if 'url' in params:
            write_to_report(params["url"], self.check_page(params["url"]))
        elif 'urls' in params:
            for url in params["urls"]:
                write_to_report(url, self.check_page(url))

        with open(os.path.join(directories.artifacts, "amp-report.txt"), 'r') as f:

            report = f.read()

            print("Final content was: %s" % report)            
            
            return {
                "return_code": 200 if report.count("false") == 0 else 500,
                "raw_output": report,
                "metrics": [
                    ("failed_endpoints", "number", report.count("false"))
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
        { "urls" : ["https://www.theguardian.com/money/2017/mar/10/ministers-to-criminalise-use-of-ticket-tout-harvesting-software", "https://amp.theguardian.com/money/2017/mar/10/ministers-to-criminalise-use-of-ticket-tout-harvesting-software"] }
    )

    print(result)

    result = ac.run(
        DirectoriesMock(),
        { "url" : "https://amp.theguardian.com/money/2017/mar/10/ministers-to-criminalise-use-of-ticket-tout-harvesting-software" }
    )

    print(result)
