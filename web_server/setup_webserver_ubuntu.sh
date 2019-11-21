#!/bin/bash
sudo apt-get update
sudo apt-get install python3 python3-pip awscli apache2 -y
pip3 install mcstatus boto3
mkdir ~/.aws
copy credentials ~/.aws/credentials
copy config ~/.aws/config
sudo a2dismod mpm_event
sudo a2enmod mpm_prefork cgi
sudo cp 000-default.conf /etc/apache2/sites-enabled/000-default.conf
sudo service apache2 restart
sudo ln -s index.py /var/www/html/index.py
sudo chmod 755 index.py
