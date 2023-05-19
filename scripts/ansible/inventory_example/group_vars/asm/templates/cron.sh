#!/bin/bash
#
# @license https://www.gnu.org/licenses/gpl-3.0.txt GNU/GPL, see LICENSE

ASM_PATH={{ asm_path }}
ASM_DATA={{ asm_data }}

BACKUP_CNF=/etc/cron.daily/backup.d/asm.cnf
BACKUP_DIR=/srv/backups/asm

DB_NAME={{ asm_db.name }}


# How many days worth of tarballs to keep around
num_days_to_keep=5

#----------------------------------------------------------
# ASM configured cron activies
#----------------------------------------------------------
ASM3_CONF=$ASM_DATA/asm3.conf python3 $ASM_PATH/src/cron.py daily &> /var/log/cron/asm
ASM3_CONF=$ASM_DATA/asm3.conf python3 $ASM_PATH/src/cron.py publish_3pty &>> /var/log/cron/asm

#----------------------------------------------------------
# Backups
#----------------------------------------------------------
now=`date +%s`
today=`date +%F`

cd $BACKUP_DIR
# Only back up the database - the media files are backed up in a different way
# The media is too big to store several days of copies on the same hard drive.
sudo -u postgres pg_dump $DB_NAME > $today.sql
gzip $today.sql

# Purge any backup tarballs that are too old
for file in `ls`
do
	atime=`stat -c %Y $file`
	if [ $(( $now - $atime >= $num_days_to_keep*24*60*60 )) = 1 ]
	then
		rm $file
	fi
done
