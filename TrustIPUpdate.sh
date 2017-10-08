#!/bin/sh
python /root/EmailRelayUpdate/EmailRelayUpdate.py
systemctl restart postfix
