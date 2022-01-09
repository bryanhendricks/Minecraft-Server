#!/bin/bash
sudo apt-get update
sudo apt-get install python3 python3-pip awscli apache2 -y
sudo ln -s /usr/bin/python3 /usr/bin/python
sudo -u ubuntu pip3 install mcstatus boto3
sudo -u ubuntu mkdir /home/ubuntu/.aws
sudo -u ubuntu cp credentials /home/ubuntu/.aws/credentials
sudo -u ubuntu cp config /home/ubuntu/.aws/config

sudo -u ubuntu a2dismod mpm_event
sudo -u ubuntu a2enmod mpm_prefork cgi
sudo -u root cp 000-default.conf /etc/apache2/sites-available/000-default.conf
sudo -u root cp index.py /var/www/html/index.py
sudo -u root cp handle_input.py /var/www/html/handle_input.py
sudo -u root cp raw_form.html /var/www/html/raw_form.html
sudo -u root chmod 755 /var/www/html/*.py
sudo -u root service apache2 restart
