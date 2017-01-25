#!/bin/bash

cd ~/

rm -rf single-page-performance-tester

git clone https://github.com/michaelwmcnamara/single-page-performance-tester.git

cd single-page-performance-tester

bash runme.sh "$(curl http://169.254.169.254/latest/meta-data/public-hostname):9000$1" "$2"
