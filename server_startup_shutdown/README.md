To install java, run `sudo apt-get update; sudo apt-get -y install openjdk-17-jre-headless`

To install script dependencies, run the following:
```
sudo apt-get install -y python3 python3-pip
sudo pip3 install mcstatus
sudo chmod +x /home/ubuntu/minecraft-server/server_startup_shutdown/*.sh
```

To set the scripts to run on startup, run `crontab -e` and paste in the contents of `crontab.txt`, then run `sudo crontab -e` and paste in the contents of `sudo_crontab.txt`
