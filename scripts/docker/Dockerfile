FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

ADD ./ /tmp/asm3

WORKDIR /tmp/asm3/install/deb

RUN ./makedeb.sh && rm -rf sheltermanager3

RUN apt-get update \
    && apt-get install -y make apache2 nodejs npm python3 python3-pip python3-pil python3-webpy python3-mysqldb python3-psycopg2 \
    && apt-get install -y imagemagick \
    && apt-get install -y wkhtmltopdf \
    && apt-get install -y python3-reportlab \
    && apt-get install -y python3-requests \
    && apt-get install -y python3-boto3 \
    && apt-get install -y memcached \
    && apt-get install -y python3-memcache \
    && apt-get install -y libapache2-mod-wsgi-py3 \
    && apt-get install -y python3-xhtml2pdf 


RUN dpkg -i sheltermanager3_`cat ../../VERSION`_all.deb

RUN pip install stripe

RUN npm install


RUN a2enmod wsgi
RUN a2ensite asm3
CMD service apache2 restart && tail -f /var/log/apache2/error.log
