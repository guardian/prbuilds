import jinja2, urllib, os

ARTIFACTS_DIR = '/home/ubuntu/artifacts'

class Reporter:

    def compose_github_comment(self, prnum, artifacts=[], results=[]):

        """ format a nice github message """
        
        def link(artifact):
            pre = "https://s3-eu-west-1.amazonaws.com/prbuilds"
            pth = "PR-%s/%s \n" % (prnum, urllib.quote(os.path.relpath(artifact, ARTIFACTS_DIR)))
            return "[%s](%s/%s)" % (os.path.basename(artifact), pre, pth.strip())

        def links_for(test):
            return [link(f) for f in artifacts if test in f]
        
        template = jinja2.Template(
            open("github_comment.template").read().decode("utf-8")
        )

        return template.render(
            artifacts=artifacts,
            results=results,
            link=link,
            links_for=links_for
        )
