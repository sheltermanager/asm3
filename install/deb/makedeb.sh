#!/bin/sh

cd `dirname $0`

# Clear the image out
rm -rf sheltermanager3

# Remake the paths
mkdir -p sheltermanager3/usr/share/doc/sheltermanager3
mkdir -p sheltermanager3/usr/lib/sheltermanager3
mkdir -p sheltermanager3/etc/apache2/sites-available
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

# Add apache config
echo "WSGIScriptAlias /asm3 /usr/lib/sheltermanager3/main.py/
Alias /asm3/static /usr/lib/sheltermanager3/static
<Directory /usr/lib/sheltermanager3>
    Require all granted
</Directory>" > sheltermanager3/etc/apache2/sites-available/asm3.conf

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

# Generate the sheltermanager3.cron.daily script
echo "#!/bin/sh
cd /usr/lib/sheltermanager3
python3 cron.py all 2>/dev/null
" > sheltermanager3/etc/cron.daily/sheltermanager3
chmod +x sheltermanager3/etc/cron.daily/sheltermanager3

# Build the list of config files
echo "/etc/asm3.conf" > sheltermanager3/DEBIAN/conffiles
echo "/etc/cron.daily/sheltermanager3" >> sheltermanager3/DEBIAN/conffiles
echo "/etc/apache2/sites-available/asm3.conf" >> sheltermanager3/DEBIAN/conffiles
echo "/etc/rsyslog.d/asm3.conf" >> sheltermanager3/DEBIAN/conffiles
echo "/etc/logrotate.d/asm3" >> sheltermanager3/DEBIAN/conffiles

# Add our repository to the list file
echo "deb [trusted=yes] https://public.sheltermanager.com/deb/ ./" > sheltermanager3/etc/apt/sources.list.d/sheltermanager3.list

# Generate the control file
#echo "Generating control file..."
echo "Package: sheltermanager3
Version: `cat ../../VERSION`
Section: contrib
Priority: optional
Architecture: all
Essential: no
Depends: debconf, memcached, libapache2-mod-wsgi-py3, python3-cheroot, python3-pil, python3-memcache, python3-requests, python3-mysqldb, python3-psycopg2, python3-reportlab, python3-xhtml2pdf, python3-lxml
Suggests: mysql-server, imagemagick, wkhtmltopdf, python3-stripe, python3-boto, python3-openpyxl, python3-qrcode
Installed-Size: `du -s -k sheltermanager3 | awk '{print$1}'`
Maintainer: ASM Team [info@sheltermanager.com]
Provides: sheltermanager3
Description: Web-based management solution for animal shelters and sanctuaries
 Animal Shelter Manager is the most popular, free management package
 for animal sanctuaries and welfare charities. This is version 3, built
 around Python and HTML5." > sheltermanager3/DEBIAN/control

# Build the deb package
# NOTE: -Zxz is specify xz compression for compatibility with Debian systems, Ubuntu uses zstd compression by default
PKGNAME=sheltermanager3_`cat ../../VERSION`_all.deb
dpkg-deb -b -Zxz sheltermanager3 $PKGNAME

