import microdata
import urllib
import json
import sys
import os
from jsonschema import validate


propmap = {
    "http://schema.org/WebPage": "microdata/webpage.jsonschema",
    "http://schema.org/NewsArticle": "microdata/newsarticle.jsonschema",
    "http://schema.org/LiveBlogPosting": "microdata/liveblogposting.jsonschema"
}

class MicroDataCheck:

    def __init__(self):

        """ constructor """

        self.out = "microdata.txt"

    def validate_microdata(self, schemadir, items):

        """ returns a report on the given microdata items """

        results = ""
        
        for item in items:

            typ = str(item.itemtype[0])

            if typ in propmap:
                schemapath = os.path.join(schemadir, propmap[typ])
                schema = json.loads(open(schemapath, "r").read())
                test = json.loads(item.json())
                try:
                    validate(test, schema)
                    results += "  valid %s\n" % typ
                except Exception as e:
                    results += "invalid %s (%s)\n" % (typ, e.message)
                    
            else:
                results += "ignored %s\n" % typ

        return results
            
    def run(self, directories, params):

        items = microdata.get_items(urllib.urlopen(params["url"]))
        results = self.validate_microdata(directories.builtins, items)

        open(
            os.path.join(
                directories.artifacts,
                self.out
            ),"w"
        ).write(results)

        failures = results.count("invalid")

        print results
        
        return {
            "return_code": 0 if failures == 0 else 1,
            "raw_output": results,
            "metrics": [
                ("microdata_failures", "number", failures)
            ]
        }

if __name__ == "__main__":
    md = MicroDataCheck()
    md.run(None, {"url": "http://theguardian.com"})
