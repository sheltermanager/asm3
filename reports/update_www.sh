#!/bin/bash

HOST=wwwdx.sheltermanager.com

./update.py
scp -C reports.txt root@${HOST}:/var/www/sheltermanager.com/repo/
echo "uploaded reports.txt to ${HOST}"
