DEPLOY_HOST=servicedx.sheltermanager.com
WWW_HOST=wwwdx.sheltermanager.com

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

version:
	# Include me in any release target to stamp the 
	# build date
	@echo "[version] =========================="
	sed "s/^VERSION =.*/VERSION = \"`cat VERSION` [`date`]\"/" src/asm3/i18n.py > i18ndt.py
	sed "s/^BUILD =.*/BUILD = \"`date +%m%d%H%M`\"/" i18ndt.py > i18njs.py
	rm -f i18ndt.py
	mv -f i18njs.py src/asm3/i18n.py
	cp changelog src/static/pages/changelog.txt

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
	scripts/rollup/rollup.py > src/static/js/bundle/rollup.js
	scripts/rollup/rollup_compat.py > src/static/js/bundle/rollup_compat.js
	# minify them and remove originals
	npm --silent run minify
	npm --silent run minify_compat
	rm -f src/static/js/bundle/rollup.js src/static/js/bundle/rollup_compat.js

schema: scripts/schema/schema.db
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

compilepy:
	@echo "[compile python] ====================="
	flake8 --config=scripts/flake8 src/*.py src/asm3/*.py src/asm3/dbms/*.py src/asm3/publishers/*.py src/asm3/paymentprocessor/*.py

smcom-dev: clean version schema
	@echo "[smcom dev us17b] ===================="
	rsync --progress --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_dev.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncdev only_us17b"

smcom-dev-all: clean version schema
	@echo "[smcom dev all] ======================"
	rsync --progress --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_dev.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncdev"

smcom-stable: clean version rollup schema
	@echo "[smcom stable] ======================="
	@# Having a BREAKING_CHANGES file prevents accidental deploy to stable without dumping sessions or doing it on a schedule
	@if [ -f BREAKING_CHANGES ]; then echo "Cannot deploy due to breaking DB changes" && exit 1; fi;
	rsync --progress --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_stable.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncstable invalidatecache restartapache"

smcom-stable-dumpsessions: clean version rollup schema
	@echo "[smcom stable dumpsessions] ==================="
	rsync --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_stable.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncstable dumpsessions invalidatecache restartapache"

smcom-stable-tgz: clean version rollup schema
	@echo "[smcom stable tgz] ======================"
	rsync --exclude '*.pyc' --exclude '__pycache__' --delete -r src/ root@$(DEPLOY_HOST):/usr/local/lib/asm_stable.new
	ssh root@$(DEPLOY_HOST) "/root/scripts/sheltermanager_sync_asm.py syncstabletgz"

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
	scp -C doc/manual/_build/latex/asm3.pdf root@$(WWW_HOST):/var/www/sheltermanager.com/repo/asm3_help.pdf
	rsync -a doc/manual/_build/html/ root@$(WWW_HOST):/var/www/sheltermanager.com/repo/asm3_help/

test: version
	@echo "[test] ========================="
	cd src && python3 code.py 5000

tests:
	@echo "[tests] ========================"
	cd test && python3 suite.py
	rm -f test/*.pyc && rm -rf test/__pycache__

deps:
	@echo "[deps] ========================="
	apt-get install python3 python3-pip python3-cheroot python3-pil python3-mysqldb python3-psycopg2
	apt-get install python3-memcache python3-requests python3-reportlab python3-xhtml2pdf
	apt-get install python3-sphinx python3-sphinx-rtd-theme texlive-latex-base texlive-latex-extra
	apt-get install exuberant-ctags flake8 imagemagick wkhtmltopdf nodejs npm
	npm install


