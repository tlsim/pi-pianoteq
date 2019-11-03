#!/usr/bin/env bash

ssh pi@raspberrypi sudo rm -rf /opt/pi-pianoteq
ssh pi@raspberrypi sudo rm -f /etc/systemd/system/pi-pianoteq.service

ssh pi@raspberrypi sudo mkdir -p /opt/pi-pianoteq

scp -r src pi@raspberrypi:/tmp/pi-pianoteq/
scp pi-pianoteq.service pi@raspberrypi:/tmp/pi-pianoteq/pi-pianoteq.service

ssh pi@raspberrypi sudo mv /tmp/pi-pianoteq/pi-pianoteq.service /etc/systemd/system/pi-pianoteq.service
ssh pi@raspberrypi sudo mv -v /tmp/pi-pianoteq/* /opt/pi-pianoteq
ssh pi@raspberrypi sudo chmod 644 /etc/systemd/system/pi-pianoteq.service

ssh pi@raspberrypi sudo systemctl start pi-pianoteq

ssh pi@raspberrypi rm -r /tmp/pi-pianoteq
