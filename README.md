Animal Shelter Manager v3 (sheltermanager3)
===========================================

This program is covered by the terms of the GNU General Public Licence v3. 
See the file LICENSE in this directory for details.

Dependencies
------------

If you are using a Debian-based system (eg: Ubuntu), then the following
will install all the software you need to run ASM. If you are using the 
sheltermanager3 deb package it already has dependencies set for these
and will install them for you.

* apt-get install make python python-imaging python-webpy python-mysqldb python-psycopg2

Extra, non-mandatory packages:

* apt-get install imagemagick (for scaling/compressing PDFs to save on storage)
* apt-get install wkhtmltopdf (for creating PDFs from HTML document templates)
* apt-get install python-requests python-ndg-httpsclient python-pyasn1 (needed for all HTTPS publishers - PetLink, MeetAPet, VetEnvoy)

Packages necessary for building static checkers, installers and manuals:

* apt-get install nodejs pychecker python-sphinx python-sphinx-rtd-theme texlive-latex-base texlive-latex-extra

If you're using Debian and want to do development, you can use "make deps"
to install the needed dependencies.

Logging
-------

ASM logs to the Unix syslog USER facility (/var/log/user.log for most installs)
by default. This can be changed in the sitedefs.

Configuring a database
----------------------

Find the sitedefs.py file in the source. If you used the Debian package,
it will be located in /usr/lib/sheltermanager3

Set the following values:

ASM3_DBTYPE (POSTGRESQL, MYSQL or SQLITE)
ASM3_DBHOST
ASM3_DBPORT
ASM3_DBUSERNAME
ASM3_DBPASSWORD
ASM3_DBNAME (can be sqlite3 file if type is SQLITE)

If you are using MySQL, make sure you have issued a CREATE DATABASE
and the database already exists (however the schema can be empty).

Starting the service
--------------------

The Debian package creates an init.d script called sheltermanager3,
which is automatically added to the correct runlevels
after package installation.

For manual setups, run "python code.py 5000" to start the service. An
HTTP server will start running on port 5000, listening on all 
interfaces.

You can change the HTTP server binding by passing a local interface
IP and a different port if you prefer. Eg: "python code.py 127.0.0.1:4999"
to only listen for connections from the local machine on port 4999.

Visit http://localhost:5000 with your web browser to connect to
the service.

Creating the default database
-----------------------------

After the ASM service has started, visit http://localhost:5000/database
to create the database schema (hitting just http://localhost:5000 will
redirect there if no database has been setup yet).

Daily tasks
-----------

ASM has a batch of routines that need to be run every day. These
should be run a few hours before people will start inputting for the
day.

These routines include recalculating denormalised data such as animal age, time
on shelter, updating the waiting list and publishing to the internet.

To run them, make sure the environment is setup as before and run
python cron.py all

See the cron.py file for more information on mode parameters to run 
specific tasks only.

The Debian package automatically adds the daily tasks to /etc/cron.daily 

Using Apache/WSGI
-----------------

To use Apache/WSGI instead of the CherryPy WSGI server, then (these 
instructions assume Debian):

1. Stop the sheltermanager3 service running and remove it from the
   existing system runlevels:
   
   * /etc/init.d/sheltermanager3 stop
   * update-rc.d sheltermanager3 remove
   
2. Install apache2 with mod_wsgi. Make sure mod_wsgi is enabled.

   * apt-get install apache2 libapache2-mod-wsgi
   * a2enmod wsgi

3. Add the WSGI config to your Apache site config. The default site config
   as installed by Debian is in /etc/apache2/sites-available/default
   
   Add this at the bottom of the file (outside of the VirtualHost tag).

```
WSGIScriptAlias /asm /usr/lib/sheltermanager3/code.py/
WSGIPythonPath /usr/lib/python2.6:/usr/lib/python2.6/dist-packages:/usr/lib/sheltermanager3:/usr/lib/sheltermanager3/locale
Alias /asm/static /usr/lib/sheltermanager3/static
AddType text/html .py
<Directory /usr/lib/sheltermanager3>
        Order deny,allow
        Allow from all
</Directory>
```

   This assumes that your ASM3 is located at /usr/lib/sheltermanager3
   (the default for our Debian package) and Python2.6 - change if you have
   Python2.7


4. Restart Apache and navigate to http://localhost/asm

    * /etc/init.d/apache2 restart


