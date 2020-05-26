FROM debian:latest

RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip nginx # python3-venv

RUN python3 -m pip install gunicorn
RUN python3 -m pip install uwsgi

COPY ./requirements.txt ./app/
WORKDIR ./app

# RUN python3 -m venv venv
# RUN . ./venv/bin/activate

COPY ./nginx.conf /etc/nginx/sites-available/app

RUN ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled

RUN python3 -m pip install -r requirements.txt

COPY ./ .

ENV FLASK_APP=jwtAuthenticator
ENV FLASK_ENV=development
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8


EXPOSE 80
# CMD nginx && gunicorn -w 4 -b unix:somesocket.sock -m 777 wsgi:app --access-logfile - --log-level debug -g www-data
CMD nginx && uwsgi --ini uwsgi.ini
# CMD nginx && gunicorn -w 4 -b 0.0.0.0:5000  wsgi:app
