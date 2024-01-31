#!/bin/bash

HOST=wwwdx.sheltermanager.com

scp -C chipprefixes.txt root@${HOST}:/var/www/sheltermanager.com/repo/
echo "uploaded chipprefixes.txt to ${HOST}"
