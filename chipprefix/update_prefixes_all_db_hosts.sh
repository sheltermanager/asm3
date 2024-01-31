#!/bin/bash

# Send the updated chipprefixes.txt file to all of our database servers

source ../../smcom_asmdb/hostsrc

for i in $ALL_DB_SERVERS; do
    HOST=${i}dx.sheltermanager.com
    echo $HOST
    scp -C chipprefixes.txt root@${HOST}:/root/asmdb/
done

