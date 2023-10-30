#!/bin/bash
#
# @license https://www.gnu.org/licenses/gpl-3.0.txt GNU/GPL, see LICENSE

ASM_PATH={{ asm_path }}
ASM_DATA={{ asm_data }}

BACKUP_DIR=/srv/backups/asm

DB_HOST={{ asm_db.host }}
DB_PORT={{ asm_db.port }}
DB_NAME={{ asm_db.name }}
DB_USER={{ asm_db.user }}


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

# Dump the database
{% if   asm_db.type == 'POSTGRESQL' %}
sudo -u postgres pg_dump > $DB_NAME > $ASM_DATA/$DB_NAME.sql
{% elif asm_db.type == 'MYSQL' %}
mysqldump --defaults-extra-file=/etc/mysql/debian $DB_NAME > $ASM_DATA/$DB_NAME.sql
{% endif %}

cd $ASM_DATA
tar czf $today.tar.gz $DB_NAME.sql media
mv $today.tar.gz $BACKUP_DIR

# Purge any backup tarballs that are too old
cd $BACKUP_DIR
for file in `ls`
do
	atime=`stat -c %Y $file`
	if [ $(( $now - $atime >= $num_days_to_keep*24*60*60 )) = 1 ]
	then
		rm $file
	fi
done
