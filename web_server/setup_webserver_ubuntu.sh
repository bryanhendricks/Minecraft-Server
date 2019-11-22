#!/bin/bash
sudo apt-get update
sudo apt-get install python3 python3-pip awscli apache2 -y
sudo ln -s /usr/bin/python3 /usr/bin/python
sudo pip3 install mcstatus boto3
sudo mkdir /root/.aws
sudo cp credentials /root/.aws/credentials
sudo cp config /root/.aws/config
sudo a2dismod mpm_event
sudo a2enmod mpm_prefork cgi
sudo cp 000-default.conf /etc/apache2/sites-enabled/000-default.conf
sudo cp index.py /var/www/html/index.py
sudo cp handle_input.py /var/www/html/handle_input.py
sudo cp raw_form.html /var/www/html/raw_form.html
sudo chmod 755 /var/www/html/*.py
sudo service apache2 restart
