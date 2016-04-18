#!/bin/sh
sudo apt-get install -y python
sudo apt-get install -y python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
sudo pip install Scrapy
sudo pip install beautifulsoup

wget https://www.dropbox.com/s/1xtjeia2fnogtnu/reflected_xss_scanner.zip
unzip reflected_xss_scanner.zip
cd reflected_xss_scanner
sudo python setup.py install

export PYTHONUNBUFFERED=1
export PYTHONPATH=$PWD

sudo chmod 777 -R reflected_xss_scanner

#to run:
#cd reflected_xss_scanner;python main.py