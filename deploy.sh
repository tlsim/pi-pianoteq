#!/usr/bin/env bash

REMOTE=pi@raspberrypi.local

scp dist/pi_pianoteq-1.0.0.tar.gz $REMOTE:/tmp/pi_pianoteq-1.0.0.tar.gz
scp pi_pianoteq.service $REMOTE:/tmp/pi_pianoteq.service

ssh $REMOTE <<EOF
tar -xvf /tmp/pi_pianoteq-1.0.0.tar.gz

sudo mv /tmp/pi_pianoteq.service /etc/systemd/system/pi_pianoteq.service
sudo chmod 644 /etc/systemd/system/pi_pianoteq.service

pip3 install /home/pi/pi_pianoteq-1.0.0

sudo systemctl daemon-reload
sudo systemctl restart pi_pianoteq

rm -r /tmp/pi_pianoteq*
rm -r /home/pi/pi_pianoteq-1.0.0

EOF
