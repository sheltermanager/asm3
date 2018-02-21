#!/bin/bash
# Creates a tarball containing a full snapshot of the data in the site
#
# @license https://www.gnu.org/licenses/gpl-3.0.txt GNU/GPL, see LICENSE
ASM_PATH={{ asm_path }}
ASM_DATA={{ asm_data }}

BACKUP_CNF=/etc/cron.daily/backup.d/asm.cnf
BACKUP_DIR=/srv/backups/asm

# How many days worth of tarballs to keep around
num_days_to_keep=5

#----------------------------------------------------------
# No Editing Required below this line
#----------------------------------------------------------
now=`date +%s`
today=`date +%F`

# Dump the database
{% if   asm_db.type == 'POSTGRESQL' %}
PGPASSFILE=$BACKUP_CNF pg_dump -w -U {{ asm_db.user }} -h {{ asm_db.host }} -d {{ asm_db.name }} -p {{ asm_db.port }} > $ASM_DATA/{{ asm_db.name }}.sql
{% elif asm_db.type == 'MYSQL' %}
mysqldump --defaults-extra-file=$BACKUP_CNF {{ asm_db.name }} > $ASM_DATA/{{ asm_db.name }}.sql
{% endif %}

cd $ASM_DATA
tar czf $today.tar.gz {{ asm_db.name }}.sql media
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
