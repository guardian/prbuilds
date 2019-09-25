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

# If we have aws credentials in the environment, copy them into the
# aws profile. This is to workaround an annoyance with running frontend
# inside of docker (frontend refuses to load credentials from the env,
# so you have to have an aws profile to run it in Docker outside of aws)

if [[ "$AWS_ACCESS_KEY_ID" != "" ]]; then
    aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID --profile frontend
    aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY --profile frontend
    aws configure set aws_session_token $AWS_SESSION_TOKEN --profile frontend
fi

# install libs

sudo add-apt-repository --yes ppa:canonical-chromium-builds/stage

sudo apt-get update

sudo apt-get install -y python-dev libffi-dev libssl-dev build-essential apache2-utils software-properties-common chromium-browser

# make sure chrome installed properly

if [[ "$(which chromium-browser)" == "" ]]; then
    echo "Failed to install chromium-browser"
    exit 1
fi

npm install -g lighthouse

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

cd $parent

virtualenv venv
source venv/bin/activate
pip install -r trousers/requirements.txt

# run the software

echo "Launching ether"

cd $parent/ether
screen -d -L -m python ether.py

echo "Launching trousers"

cd $parent/trousers

if [[ "$1" == "-test" ]]; then
    screen -d -L -m python full_test.py
    echo "Running prbuilds in test-mode."
else
    screen -d -L -m python trousers.py
    echo "Blocking until killed"    
fi

sleep 5
echo "$(pwd)"
tail -f screenlog.0
bash

