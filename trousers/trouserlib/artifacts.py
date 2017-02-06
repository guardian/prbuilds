
import os

ARTIFACTS_DIR = '/home/ubuntu/artifacts'

class ArtifactService:

    def collect(self, directory):

        """ return list of all the artifacts in given directory """

        facts = []

        for root, directories, filenames in os.walk(directory):
            facts += [os.path.join(root, f) for f in filenames]

        return facts

    def content_type(self, path):
        return {
            "jpg": "image/jpeg",
            "png": "image/png",
            "text": "text/plain"
        }.get(path.split(".")[-1], "text/plain")
    
    def upload(self, bucket, prefix, artifacts):

        """ Upload given artifact files to S3 """

        def upload(path):
            bucket.upload_file(
                path,
                "%s/%s" % (prefix, os.path.relpath(path, start=ARTIFACTS_DIR)),
                ExtraArgs={
                    'ContentType': self.content_type(path),
                    'ACL': 'public-read'
                }
            )

        for filename in artifacts:
            print "Uploading file '%s' to S3" % os.path.basename(filename)
            upload(filename)
