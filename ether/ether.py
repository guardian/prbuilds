#!/usr/bin/env python

from flask import Flask
app = Flask(__name__)

@app.route('/<category>/<year>/<mon>/<day>/<slug>')
def article(category, year, mon, day, slug):
    return open("data/article", "r").read()

if __name__ == '__main__':
    app.run(debug=False, port=9001)
