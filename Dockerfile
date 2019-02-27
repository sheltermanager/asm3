FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

ADD ./ /tmp/asm3

WORKDIR /tmp/asm3/install/deb

RUN ./makedeb.sh && rm -rf sheltermanager3

RUN apt-get update \
    && apt-get install -y make python python-pil python-webpy python-mysqldb python-psycopg2 memcached python-memcache \
    && apt-get install -y imagemagick \
    && apt-get install -y wkhtmltopdf \
    && apt-get install -y python-reportlab \
    && apt-get install -y python-requests \
    && apt-get install -y python-boto3

RUN dpkg -i sheltermanager3_`cat ../../VERSION`_all.deb

CMD service sheltermanager3 start && tail -f /var/log/sheltermanager3.log
