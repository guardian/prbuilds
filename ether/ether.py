#!/usr/bin/env python

from flask import Flask
app = Flask(__name__)

default = "article"

slugmap = {
    "nobel-prize-in-economics-due-to-be-unveiled-business-live": "liveblog",
    "guardian-journalists-jonathan-freedland-ghaith-abdul-ahad-win-orwell-prize-journalism": "article"
}

def handle(slug):

    if slug in slugmap:
        print "returning %s" % slugmap[slug]
        return open("data/%s" % slugmap[slug], "r").read()
    else:
        print "returning default"
        return open("data/%s" % default, "r").read()

@app.route('/<category>/<subcategory>/<year>/<mon>/<day>/<slug>')
def subcat(category, subcategory, year, mon, day, slug):
    return handle(slug)

@app.route('/<category>/<year>/<mon>/<day>/<slug>')
def article(category, year, mon, day, slug):
    return handle(slug)

if __name__ == '__main__':
    app.run(debug=False, port=9001)
