Animal Shelter Manager v3 (sheltermanager3)
===========================================

This program is covered by the terms of the GNU General Public Licence v3. 
See the file LICENSE in this directory for details.

As of version 45, ASM no longer supports Python 2.

Dependencies
------------

If you are using a Debian-based system (eg: Ubuntu), then the following will
install all the software you need to run ASM. If you are using the
sheltermanager3 deb package it already has dependencies set for these and will
install them for you.

* apt-get install make python3 python3-webpy python3-pil python3-mysqldb python3-psycopg2

Extra, non-mandatory packages:

* apt-get install python3-memcache memcached (for multiprocess sessions)
* apt-get install imagemagick (for scaling/compressing PDFs to save on storage)
* apt-get install wkhtmltopdf (for creating PDFs from HTML document templates)
* apt-get install python3-xhtml2pdf (pure Python lib for creating PDFs from HTML document templates)
* apt-get install python3-reportlab (for creating mailing label PDFs)
* apt-get install python3-requests (needed for HTTP comms to other publishing services)
* apt-get install python3-boto3 (needed for Amazon S3 media storage)
* pip/pip3 install stripe (for requesting payments via Stripe)

Packages necessary for building, static checkers, installers and manuals:

* apt-get install exuberant-ctags nodejs npm pychecker python3-sphinx
  python3-sphinx-rtd-theme texlive-latex-base texlive-latex-extra latexmk

Node and npm are used for transpiling javascript code for older browsers and
linting javascript files. To install all build time javascript dependences,
run this command in the source folder:

* npm install

If you're using Debian and want to do development, you can use "make deps"
as a convenient way to install the needed dependencies.

Debian python3-webpy
--------------------

The version of web.py currently packaged in Debian Buster (and possibly Ubuntu)
as python3-webpy has a fault. It cannot serve static content and will only work
if you deploy your application with mod_wsgi, uwsgi, etc.

You can fix it manually by editing
/usr/lib/python3/dist-packages/web/httpserver.py and adding the new line
self.directory = os.getcwd() at line 198 at the bottom of the __init__
function, like this:

```
class StaticApp(SimpleHTTPRequestHandler):
    """WSGI application for serving static files."""
    def __init__(self, environ, start_response):
        self.headers = []
        self.environ = environ
        self.start_response = start_response
        self.directory = os.getcwd()
```

You do not need this fix if you are deploying your application to run with
Apache as recommended, this only applies to running a standalone server via
code.py from the command line.

In a development environment, you can start a test instance on port 5000 with:

```
make test
```

Logging
-------

ASM logs to the Unix syslog USER facility (/var/log/user.log for most installs)
by default. This can be changed in the configuration.

Configuring ASM
---------------

If you used the debian package, edit the file /etc/asm3.conf

If you did not, copy scripts/asm3.conf.example to /etc/asm3.conf and then edit it.

Set the following values:

```
asm3_dbtype = (POSTGRESQL, MYSQL or SQLITE)
asm3_dbhost = (hostname of your server)
asm3_dbport = (port of your server if using tcp)
asm3_dbusername = 
asm3_dbpassword = 
asm3_dbname = (name of the database, can be file path if type is SQLITE)
```

If you are using MySQL or POSTGRESQL, make sure you have issued a CREATE DATABASE
and the database already exists (however the schema can be empty).

ASM will look for its config file in this order until it finds one:

1. In an environment variable called ASM3_CONF
2. In $INSTALL_DIR/asm3.conf (the folder asm3 python modules are installed in)
3. In $HOME/.asm3.conf (the home directory of the user running asm3)
4. In /etc/asm3.conf

Setting up Apache/WSGI
----------------------

Set up Apache to serve the application.

The version 44 Debian package has libapache2-mod-wsgi-py3 as a dependency and
will install Apache 2 if you don't already have it available. 

For older versions, install Apache with:

```
apt-get install apache2 libapache2-mod-wsgi-py3
```

As of version 44, the package will also include a site file
/etc/apache2/sites-available/asm3.conf with the following content:

```
WSGIScriptAlias /asm3 /usr/lib/sheltermanager3/code.py/
Alias /asm3/static /usr/lib/sheltermanager3/static
<Directory /usr/lib/sheltermanager3>
    Require all granted
</Directory>
```

For older versions, you will have to create this file manually.

Once Apache is installed and you have the site file, to activate ASM, run:

```
a2enmod wsgi
a2ensite asm3
service apache2 restart
```

You should now be able to visit ASM at http://localhost/asm3

Creating the default database
-----------------------------

After the ASM service has started, visit http://localhost/asm3/database
to create the database schema (hitting just http://localhost/asm3 will
redirect there if no database has been setup yet).

Daily tasks
-----------

ASM has a batch of routines that need to be run every day. These
should be run a few hours before people will start inputting for the
day.

These routines include recalculating denormalised data such as animal age, time
on shelter, updating the waiting list and publishing data externally.

To run them, make sure the environment is setup as before and run
python3 cron.py all

See the cron.py file for more information on mode parameters to run 
specific tasks only.

The Debian package automatically adds the daily tasks to /etc/cron.daily 


