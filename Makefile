DEPLOY_HOST=servicedx.sheltermanager.com
WWW_HOST=wwwdx.sheltermanager.com

all:	compile clean tags minify

dist:	version clean minify
	rm -rf build
	mkdir build
	tar -czvf build/sheltermanager3-`cat VERSION`-src.tar.gz changelog LICENSE src README.md scripts/asm3.conf.example scripts/wsgi
	cd install/deb && ./makedeb.sh && mv *.deb ../../build

distwin32: dist
	cd install/win32 && ./make.sh && mv sheltermanager*exe ../../build/sheltermanager3-`cat ../../VERSION`-win32.exe

tags:
	@echo "[tags] ============================"
	rm -f tag
	ctags -f tags src/*.py src/asm3/*.py src/asm3/publishers/*.py src/asm3/dbms/*.py src/static/js/*.js

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
	rm -f src/__pycache__
	rm -f src/asm3/*.pyc
	rm -f src/asm3/__pycache__
	rm -f src/asm3/dbms/*.pyc
	rm -f src/asm3/dbms/__pycache__
	rm -f src/asm3/locales/*.pyc
	rm -f src/asm3/locales/__pycache__
	rm -f src/asm3/pbkdf2/*.pyc
	rm -f src/asm3/pbkdf2/__pycache__
	rm -f src/asm3/publishers/*.pyc
	rm -f src/asm3/publishers/__pycache__

version:
	# Include me in any release target to stamp the 
	# build date
	@echo "[version] =========================="
	sed "s/^VERSION =.*/VERSION = \"`cat VERSION` [`date`]\"/" src/asm3/i18n.py > i18ndt.py
	sed "s/^BUILD =.*/BUILD = \"`date +%m%d%H%M`\"/" i18ndt.py > i18njs.py
	rm -f i18ndt.py
	mv -f i18njs.py src/asm3/i18n.py
	cp changelog src/static/pages/changelog.txt

minify:
	# Generate minified versions of all javascript in min folder
	@echo "[minify] ============================="
	mkdir -p src/static/js/min
	for i in src/static/js/*.js; do echo $$i; cat $$i | scripts/jsmin/jsmin > src/static/js/min/`basename $$i .js`.min.js; done

compile: compilejs compilepy compilejsmin

compilejs:
	@echo "[compile javascript] ================="
	cd scripts/jslint && ./run.py

compilejsmin:
	@echo "[compile jsmin] ======================"
	gcc -o scripts/jsmin/jsmin scripts/jsmin/jsmin.c

compilepy:
	@echo "[compile python] ====================="
	flake8 --config=scripts/flake8 src/*.py src/asm3/*.py src/asm3/dbms/*.py src/asm3/publishers/*.py

smcom-dev: version clean minify
	@echo "[smcom dev eur01] ===================="
	rsync --progress --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_dev.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncdev only_eur01"

smcom-dev-all: version clean minify
	@echo "[smcom dev all] ======================"
	rsync --progress --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_dev.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncdev"

smcom-stable: version clean minify
	@echo "[smcom stable] ======================="
	@# Having a BREAKING_CHANGES file prevents accidental deploy to stable without dumping sessions or doing it on a schedule
	@if [ -f BREAKING_CHANGES ]; then echo "Cannot deploy due to breaking DB changes" && exit 1; fi;
	rsync --progress --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_stable.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncstable"

smcom-stable-dumpsessions: version clean minify
	@echo "[smcom stable dumpsessions] ==================="
	rsync --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_stable.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncstable dumpsessions"

smcom-stable-tgz: version clean minify
	@echo "[smcom stable tgz] ======================"
	rsync --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_stable.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncstabletgz"

pot:
	@echo "[template] ========================="
	python po/extract_strings.py > po/asm.pot

translation:
	@echo "[translation] ======================"
	cd po && ./po_to_python.py
	mv po/locale*py src/asm3/locales

icons:
	@echo "[icons] ==========================="
	cd src/static/images/icons && ./z_makecss.sh
	mv src/static/images/icons/asm-icon.css src/static/css

manual:
	@echo "[manual] =========================="
	cd doc/manual && $(MAKE) clean html latexpdf
	cp -rf doc/manual/_build/html/* src/static/pages/manual/
	scp -C doc/manual/_build/latex/asm3.pdf root@$(WWW_HOST):/var/www/sheltermanager.com/repo/asm3_help.pdf
	rsync -a doc/manual/_build/html/ root@$(WWW_HOST):/var/www/sheltermanager.com/repo/asm3_help/

test: version
	@echo "[test] ========================="
	cd src && python code.py 5000

tests:
	@echo "[tests] ========================"
	cd test && python suite.py
	rm -f test/*.pyc

testsdb:
	@echo "[testsdb] ========================"
	mysql -u root -proot -e "DROP DATABASE IF EXISTS asmunittest"
	mysql -u root -proot -e "CREATE DATABASE asmunittest"
	cd src && python cron.py maint_db_install MYSQL localhost 3306 root root asmunittest asmunittest

deps:
	@echo "[deps] ========================="
	apt-get install python python-imaging python-webpy python-mysqldb python-psycopg2 python-requests python-memcache python-reportlab
	apt-get install exuberant-ctags nodejs flake8 imagemagick wkhtmltopdf
	apt-get install python-sphinx python-sphinx-rtd-theme texlive-latex-base texlive-latex-extra

