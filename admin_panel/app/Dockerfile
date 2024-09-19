FROM python:3.11.9

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings.__init__'


COPY requirements.txt requirements.txt

RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir


COPY run_uwsgi.sh run_uwsgi.sh
COPY uwsgi/uwsgi.ini uwsgi.ini

COPY . .


EXPOSE 8000

ENTRYPOINT ["sh", "/opt/app/run_uwsgi.sh"]
