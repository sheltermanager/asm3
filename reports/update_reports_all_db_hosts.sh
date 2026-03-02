#!/bin/bash

# Send the updated reports.txt file to all of our database servers

./update.py

source ../../smcom_asmdb/hostsrc

for i in $ALL_DB_SERVERS; do
    HOST=${i}.sheltermanager.com
    echo $HOST
    scp -C reports.txt root@${HOST}:/root/asmdb/
done

