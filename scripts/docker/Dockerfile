FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

ADD ./ /tmp/asm3

WORKDIR /tmp/asm3/install/deb

RUN ./makedeb.sh && rm -rf sheltermanager3

RUN apt-get update \
    && apt-get install -y make python3 python3-pil python3-webpy python3-mysqldb python3-psycopg2 \
    && apt-get install -y imagemagick \
    && apt-get install -y wkhtmltopdf \
    && apt-get install -y python3-reportlab \
    && apt-get install -y python3-requests \
    && apt-get install -y python3-boto3

RUN dpkg -i sheltermanager3_`cat ../../VERSION`_all.deb

CMD service sheltermanager3 start && tail -f /var/log/sheltermanager3.log
