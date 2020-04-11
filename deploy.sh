#!/usr/bin/env bash

ssh pi@raspberrypi sudo rm -f /etc/systemd/system/pi_pianoteq.service

scp dist/pi_pianoteq-1.0.0.tar.gz pi@raspberrypi:/tmp/pi_pianoteq-1.0.0.tar.gz
scp pi_pianoteq.service pi@raspberrypi:/tmp/pi_pianoteq.service

ssh pi@raspberrypi tar -xvf /tmp/pi_pianoteq-1.0.0.tar.gz

ssh pi@raspberrypi sudo mv /tmp/pi_pianoteq.service /etc/systemd/system/pi_pianoteq.service
ssh pi@raspberrypi sudo chmod 644 /etc/systemd/system/pi_pianoteq.service

ssh pi@raspberrypi pip3 install /home/pi/pi_pianoteq-1.0.0

ssh pi@raspberrypi sudo systemctl daemon-reload
ssh pi@raspberrypi sudo systemctl start pi_pianoteq

ssh pi@raspberrypi rm -r /tmp/pi_pianoteq*
ssh pi@raspberrypi rm -r /home/pi/pi_pianoteq-1.0.0
