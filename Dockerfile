FROM tiangolo/uwsgi-nginx:python2.7-alpine3.7
LABEL maintainer="oleg@softservice.org"

COPY static /app/static
COPY templates /app/templates
COPY uwsgi.ini deps.txt main.py /app/
WORKDIR /app
RUN apk update && apk add mongodb
RUN pip install virtualenv && \
    virtualenv --no-site-packages env && \
    source env/bin/activate && \
    pip install -r deps.txt

CMD mkdir /app/db && mongod --dbpath=/app/db --syslog --fork && /usr/bin/supervisord
