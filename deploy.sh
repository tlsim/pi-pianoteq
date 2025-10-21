#!/usr/bin/env bash

REMOTE=tom@192.168.0.169

scp dist/pi_pianoteq-1.0.0.tar.gz $REMOTE:/tmp/pi_pianoteq-1.0.0.tar.gz
scp pi_pianoteq.service $REMOTE:/tmp/pi_pianoteq.service

ssh $REMOTE <<EOF
tar -xvf /tmp/pi_pianoteq-1.0.0.tar.gz

sudo mv /tmp/pi_pianoteq.service /etc/systemd/system/pi_pianoteq.service
sudo chmod 644 /etc/systemd/system/pi_pianoteq.service

pip3 install --break-system-packages /home/tom/pi_pianoteq-1.0.0

sudo systemctl daemon-reload
sudo systemctl enable pi_pianoteq
sudo systemctl restart pi_pianoteq

rm -r /tmp/pi_pianoteq*
rm -r /home/tom/pi_pianoteq-1.0.0

EOF
