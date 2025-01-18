
all:	clean compile tags rollup schema

dist:	clean version rollup schema
	rm -rf build
	mkdir build
	tar -czvf build/sheltermanager3-`cat VERSION`-src.tar.gz changelog LICENSE src README.md scripts/asm3.conf.example scripts/wsgi
	cd install/deb && ./makedeb.sh && mv *.deb ../../build

distwin32: dist
	cd install/win32 && ./make.sh && mv sheltermanager*exe ../../build/sheltermanager3-`cat ../../VERSION`-win32.exe

tags:
	@echo "[tags] ============================"
	rm -f tag
	ctags -f tags src/*.py src/asm3/*.py src/asm3/dbms/*.py src/asm3/paymentprocessor/*.py src/asm3/publishers/*.py

cscope:
	@echo "[cscope] ==========================="
	find . -name '*.py' > cscope.files
	find . -name '*.psp' >> cscope.files
	cscope -b -q -k

clean:
	@echo "[clean] ============================"
	rm -f cscope*
	rm -f tags
	rm -f src/*.pyc
	rm -rf src/__pycache__
	rm -f src/asm3/*.pyc
	rm -rf src/asm3/__pycache__
	rm -f src/asm3/dbms/*.pyc
	rm -rf src/asm3/dbms/__pycache__
	rm -f src/asm3/locales/*.pyc
	rm -rf src/asm3/locales/__pycache__
	rm -f src/asm3/paymentprocessor/*.pyc
	rm -rf src/asm3/paymentprocessor/__pycache__
	rm -f src/asm3/pbkdf2/*.pyc
	rm -rf src/asm3/pbkdf2/__pycache__
	rm -f src/asm3/publishers/*.pyc
	rm -rf src/asm3/publishers/__pycache__
	rm -f scripts/schema/schema.db
	rm -f scripts/unittestdb/base.db
	rm -f scripts/unittestdb/test.db

changelog.txt: 
	@echo "[changelog.txt] =============================="
	cat VERSION > src/static/pages/changelog.txt
	echo "======" >> src/static/pages/changelog.txt
	echo >> src/static/pages/changelog.txt
	#git log --no-merges --date=short --oneline --pretty=format:'%C(auto)%h%d %cd [%cn] %s' `cat VERSION_PREVTAG`..HEAD >> src/static/pages/changelog.txt
	git log --no-merges --date=short --oneline --pretty=format:'%cd %s [%an] %C(auto)%h%d' `cat VERSION_PREVTAG`..HEAD >> src/static/pages/changelog.txt

changelog: changelog.txt
	less src/static/pages/changelog.txt

version: changelog.txt
	# Include me in any release target to stamp the 
	# build date
	@echo "[version] =========================="
	echo "#!/usr/bin/env python3" > src/asm3/__version__.py
	echo "VERSION = \"`cat VERSION` [`date`]\"" >> src/asm3/__version__.py
	echo "BUILD = \"`date +%m%d%H%M%S`\"" >> src/asm3/__version__.py

compat:
	# Generate older browser compatible versions of the js files
	@echo "[compat] =============================="
	mkdir -p src/static/js/compat
	rm -f src/static/js/compat/*.js
	npm --silent run babel

rollup: compat
	# Generate a rollup file of all javascript files
	@echo "[rollup] ============================="
	mkdir -p src/static/js/bundle
	# minify the regenerator-runtime
	npm --silent run minify_regenrt
	scripts/rollup/rollup.py > src/static/js/bundle/rollup.js
	scripts/rollup/rollup_compat.py > src/static/js/bundle/rollup_compat.js
	# minify them and remove originals
	npm --silent run minify
	npm --silent run minify_compat
	rm -f src/static/js/bundle/rollup.js src/static/js/bundle/rollup_compat.js

schema: scripts/schema/schema.db version
	# Generate a JSON schema of the database for use when editing
	# SQL within the program
	@echo "[schema] ============================="
	mkdir -p src/static/js/bundle
	scripts/schema/schema.py > src/static/js/bundle/schema.js

scripts/schema/schema.db:
	# Updates the schema.db sqlite database used for building the schema.js file.
	@echo "[schema.db] =========================="
	scripts/schema/make_db.py

compile: compilejs compilepy 

compilejs:
	@echo "[compile javascript] ================="
	npm --silent run jshint

compilepy: version
	@echo "[compile python] ====================="
	flake8 --config=scripts/flake8 src/*.py src/asm3/*.py src/asm3/dbms/*.py src/asm3/publishers/*.py src/asm3/paymentprocessor/*.py

pot:
	@echo "[template] ========================="
	po/extract_strings.py > po/asm.pot

translation:
	@echo "[translation] ======================"
	cd po && ./po_to_python_js.py
	mv po/locale*py src/asm3/locales
	mv po/locale*js src/static/js/locales

icons:
	@echo "[icons] ==========================="
	cd src/static/images/icons && ./z_makecss.sh
	mv src/static/images/icons/asm-icon.css src/static/css

manual:
	@echo "[manual] =========================="
	cd doc/manual && $(MAKE) clean html latexpdf
	cp -rf doc/manual/_build/html/* src/static/pages/manual/
	scp -C doc/manual/_build/latex/asm3.pdf root@wwwdx.sheltermanager.com:/var/www/sheltermanager.com/repo/asm3_help.pdf
	rsync -a doc/manual/_build/html/ root@wwwdx.sheltermanager.com:/var/www/sheltermanager.com/repo/asm3_help/

chipprefixes:
	@echo "[reports] ========================="
	cd chipprefix && ./update_www.sh
	cd chipprefix && ./update_prefixes_all_db_hosts.sh

smcomreports:
	@echo "[smcomreports] ========================="
	cd reports && ./update_www.sh
	cd reports && ./update_reports_all_db_hosts.sh

test: version
	@echo "[test] ========================="
	cd src && python3 main.py 5000

scripts/unittestdb/base.db:
	# Updates the base.db sqlite database used for running unit tests against. 
	# The suite.py file copies base.db to test.db for speed when re-running tests
	@echo "[unittestdb/base.db] =========================="
	scripts/unittestdb/make_db.py

tests: scripts/unittestdb/base.db
	@echo "[tests] ========================"
	cp scripts/unittestdb/base.db scripts/unittestdb/test.db
	cd unittest && python3 suite.py
	rm -f unittest/*.pyc && rm -rf unittest/__pycache__

tests_dbupdates: 
	@echo "[tests_dbupdates] =============="
	rm -f scripts/unittestdb/dbupdates.db
	sqlite3 scripts/unittestdb/dbupdates.db < scripts/unittestdb/asm2_postgres.sql
	sqlite3 scripts/unittestdb/dbupdates.db < scripts/unittestdb/asm2_data.sql
	cd src && python3 cron.py maint_db_update_stdout SQLITE host 21 user pass ../scripts/unittestdb/dbupdates.db dbupdates

deps:
	@echo "[deps] ========================="
	apt-get install python3 python3-cheroot python3-pil python3-mysqldb python3-psycopg2 python3-webpy
	apt-get install python3-memcache python3-requests python3-reportlab python3-xhtml2pdf python3-lxml
	apt-get install python3-qrcode python3-openpyxl
	apt-get install python3-boto3 python3-stripe
	apt-get install python3-sphinx python3-sphinx-rtd-theme texlive-latex-base texlive-latex-extra latexmk
	apt-get install exuberant-ctags flake8 imagemagick wkhtmltopdf nodejs npm memcached
	npm install


