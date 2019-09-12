#!/bin/sh

cd `dirname $0`

# Clear the image out
rm -rf sheltermanager3

# Remake the paths
mkdir -p sheltermanager3/usr/share/doc/sheltermanager3
mkdir -p sheltermanager3/usr/lib/sheltermanager3
mkdir -p sheltermanager3/etc/apt/sources.list.d
mkdir -p sheltermanager3/etc/cron.daily
mkdir -p sheltermanager3/etc/init.d
mkdir -p sheltermanager3/etc/logrotate.d
mkdir -p sheltermanager3/etc/rsyslog.d
mkdir -p sheltermanager3/etc/systemd/system
mkdir -p sheltermanager3/DEBIAN

# Update the app
cp -rf ../../src/* sheltermanager3/usr/lib/sheltermanager3/

# Add docs
cp ../../README.md sheltermanager3/usr/share/doc/sheltermanager3

# Add the example config
cp ../../scripts/asm3.conf.example sheltermanager3/etc/asm3.conf

# Add logging
echo "local3.*                          -/var/log/asm3.log" > sheltermanager3/etc/rsyslog.d/asm3.conf

# Log rotate
echo "/var/log/asm3.log
{
        rotate 7
        daily
        missingok
        notifempty
        delaycompress
        compress
        postrotate
                invoke-rc.d rsyslog rotate > /dev/null
        endscript
}" > sheltermanager3/etc/logrotate.d/asm3

# Add our repository to the list file
echo "deb http://public.sheltermanager.com/deb/ ./" > sheltermanager3/etc/apt/sources.list.d/sheltermanager3.list

# Create the init.d stop/start script for sysv
echo '#!/bin/sh
# /etc/init.d/sheltermanager3
### BEGIN INIT INFO
# Provides:          sheltermanager3
# Required-Start:    $syslog
# Required-Stop:     $syslog
# Should-Start:      $network
# Should-Stop:       $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start and stop the sheltermanager3 server daemon
# Description:       Controls the main sheltermanager3 server daemon
### END INIT INFO
DAEMON=/usr/bin/env
RUNAS=www-data
ARGS="python3 /usr/lib/sheltermanager3/code.py 5000"
PIDFILE="/var/run/sheltermanager3.pid"
WD=/usr/lib/sheltermanager3
. /lib/lsb/init-functions
case "$1" in
  start)
    echo "Starting sheltermanager3 ..." >&2
    /sbin/start-stop-daemon --start --pidfile $PIDFILE --chuid $RUNAS --chdir $WD -b --make-pidfile --exec $DAEMON $ARGS &> /var/log/sheltermanager3.log
    ;;
  stop)
    echo "Stopping sheltermanager3 ..." >&2
    /sbin/start-stop-daemon --stop --pidfile $PIDFILE --verbose
    ;;
  restart)
    echo "Restarting sheltermanager3 ..." >&2
    /sbin/start-stop-daemon --stop --pidfile $PIDFILE --verbose
    /sbin/start-stop-daemon --start --pidfile $PIDFILE --chuid $RUNAS --chdir $WD -b --make-pidfile --exec $DAEMON $ARGS &> /var/log/sheltermanager3.log
    ;;
  *)
    echo "Usage: /etc/init.d/sheltermanager3 {start|stop|restart}" >&2
    exit 1
    ;;
esac
exit 0
' > sheltermanager3/etc/init.d/sheltermanager3
chmod +x sheltermanager3/etc/init.d/sheltermanager3

# Create the systemd unit file
echo '[Unit]
Description=Animal Shelter Manager
After=network.target syslog.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 code.py 5000
Restart=on-failure
WorkingDirectory=/usr/lib/sheltermanager3
User=www-data
Group=www-data
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target
' > sheltermanager3/etc/systemd/system/sheltermanager3.service

# Generate the control file
#echo "Generating control file..."
echo "Package: sheltermanager3
Version: `cat ../../VERSION`
Section: contrib
Priority: optional
Architecture: all
Essential: no
Depends: debconf, python3-webpy, python3-pil, python3-memcache, python3-requests, python3-mysqldb, python3-psycopg2
Suggests: mysql-server, imagemagick, wkhtmltopdf, python3-sqlite
Installed-Size: `du -s -k sheltermanager3 | awk '{print$1}'`
Maintainer: ASM Team [info@sheltermanager.com]
Provides: sheltermanager3
Description: Web-based management solution for animal shelters and sanctuaries
 Animal Shelter Manager is the most popular, free management package
 for animal sanctuaries and welfare charities. This is version 3, built
 around Python and HTML5." > sheltermanager3/DEBIAN/control

# Generate the postinst file
# Puts the init script into default run levels
echo "#!/bin/sh
if [ -f /bin/systemctl ]; then
    systemctl enable sheltermanager3
else
    update-rc.d sheltermanager3 defaults
fi
" > sheltermanager3/DEBIAN/postinst
chmod +x sheltermanager3/DEBIAN/postinst

# Generate the prerm file to remove the service 
echo "#!/bin/sh
if [ -f /bin/systemctl ]; then
    systemctl stop sheltermanager3
    systemctl disable sheltermanager3
else
    /etc/init.d/sheltermanager3 stop
    update-rc.d sheltermanager3 remove
fi
# Don't stop the package manager if these fail
exit 0
" > sheltermanager3/DEBIAN/prerm
chmod +x sheltermanager3/DEBIAN/prerm

# Generate the sheltermanager3.cron.daily script
echo "#!/bin/sh
cd /usr/lib/sheltermanager3
python3 cron.py all
" > sheltermanager3/etc/cron.daily/sheltermanager3
chmod +x sheltermanager3/etc/cron.daily/sheltermanager3

# Build the deb package
dpkg -b sheltermanager3 sheltermanager3_`cat ../../VERSION`_all.deb


