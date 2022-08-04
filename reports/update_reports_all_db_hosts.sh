#!/bin/bash

# Send the update smcom_client.py file to all of our database servers

./update.py

source ../../smcom_asmdb/hostsrc

for i in $ALL_DB_SERVERS; do
    HOST=${i}dx.sheltermanager.com
    echo $HOST
    scp reports.txt root@${HOST}:/root/asmdb/
done

