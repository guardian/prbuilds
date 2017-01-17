#!/bin/bash

# Must be ran from the root of a prbuilds clone.
# Must set GH_NAME, GH_TOKEN and QUEUE_NAME in environment first.

parent=$(pwd)

echo "Installing as user $(whoami)"

# when this script is ran from aws UserData, $HOME might not be set
# which causes the install of nvm to wig out!

if [[ "$HOME" == "" ]]; then
    echo "Resetting HOME"
    export HOME=/home/ubuntu
fi

# install libs

sudo apt-get install -y python-dev libffi-dev libssl-dev build-essential

# use easy install to get pip instead of apt-get so we get
# a recent version instead of whatever ubuntu has

sudo easy_install pip
sudo pip install virtualenv

# install latest phantomjs (we want 2.1.1. as it fixes some bugs)

if [[ "$(which phantomjs)" == "" ]]; then
    cd /home/ubuntu
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
    tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2
    sudo ln phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs
fi

# install python dependencies

virtualenv venv
source venv/bin/activate
pip install -r trousers/requirements.txt

# run the software

echo "Launching ether"

cd $parent/ether
screen -d -L -m python ether.py

echo "Launching trousers"

cd $parent/trousers
screen -d -L -m python trousers.py
