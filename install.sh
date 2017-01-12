#!/bin/bash

# Must be ran from the root of a prbuilds clone.
# Must set GH_NAME, GH_TOKEN and QUEUE_NAME in environment first.

parent=$(pwd)

# install libs

sudo apt-get install -y python-dev libffi-dev libssl-dev build-essential

# use easy install to get pip instead of apt-get so we get
# a recent version instead of whatever ubuntu has

sudo easy_install pip
sudo pip install virtualenv

# install python dependencies

virtualenv venv
source venv/bin/activate
pip install -r trousers/requirements.txt

# run the software

cd $parent/ether
screen -d -m python ether.py

cd $parent/trousers
screen -d -m python trousers.py
