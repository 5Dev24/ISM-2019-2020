#!/bin/bash

ServiceFile=/lib/systemd/system/ISM-2019-2020.service
StartFile=/home/pi/ISM-2019-2020/Firmware/start.sh

# Update system
sudo apt update
sudo apt -y upgrade

# Make sure python 3.x is installed
sudo apt -y install python3

# Install pip so we can install requirements
sudo apt -y install python3-pip

# Install pybluez linux dependancies
sudo apt -y install pkg-config libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev python-dev

# Install firmware's modules
sudo pip3 install -r /home/pi/ISM-2019-2020/Firmware/requirements.txt

# Clear up excess packages
sudo apt -y autoremove

# Check if service file exists, if it does: delete it
if [ -f "$ServiceFile" ]
then
	sudo chmod 777 "$ServiceFile"
	sudo rm -f "$ServiceFile"
fi

# Create service file
sudo touch "$ServiceFile"

# Allow all access
sudo chmod 777 "$ServiceFile"

# Write to file
sudo echo "[Unit]
Description=ISM-2019-2020

[Service]
ExecStart=$StartFile

[Install]
WantedBy=multi-user.target">> "$ServiceFile"

# Set permissions back
sudo chmod 644 "$ServiceFile"

# Tell systemd to start during boot
sudo systemctl daemon-reload
sudo systemctl enable ISM-2019-2020.service

# Make start.sh file executable
sudo chmod +x "$StartFile"

# Restart system
sudo reboot