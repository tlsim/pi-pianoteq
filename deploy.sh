#!/usr/bin/env bash

ssh pi@raspberrypi sudo rm -rf /opt/pi-pianoteq
ssh pi@raspberrypi sudo rm -f /etc/systemd/system/pi-pianoteq.service

ssh pi@raspberrypi sudo mkdir -p /opt/pi-pianoteq

scp dist/pi-pianoteq-1.0.0.tar.gz pi@raspberrypi:/tmp/pi-pianoteq-1.0.0.tar.gz
scp pi-pianoteq.service pi@raspberrypi:/tmp/pi-pianoteq.service

ssh pi@raspberrypi tar -xvf /tmp/pi-pianoteq-1.0.0.tar.gz

ssh pi@raspberrypi sudo mv /tmp/pi-pianoteq.service /etc/systemd/system/pi-pianoteq.service
ssh pi@raspberrypi sudo chmod 644 /etc/systemd/system/pi-pianoteq.service

ssh pi@raspberrypi pip3 install /home/pi/pi-pianoteq-1.0.0

ssh pi@raspberrypi sudo systemctl start pi-pianoteq

ssh pi@raspberrypi rm -r /tmp/pi-pianoteq*
