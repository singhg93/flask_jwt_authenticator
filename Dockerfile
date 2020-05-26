# create a debian image
FROM debian:latest

# update and install the necessary dpendencies
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip nginx # python3-venv

# install gunicorn if using gunicorn
# RUN python3 -m pip install gunicorn

# install uwsgi
RUN python3 -m pip install uwsgi

# copy the requirements file to the app folder
COPY ./requirements.txt ./app/
# change the working directory to the app folder
WORKDIR ./app

# install all the requirements
RUN python3 -m pip install -r requirements.txt

# copy the source files to the app folder
COPY ./ .

# RUN python3 -m venv venv
# RUN . ./venv/bin/activate

# copy the nginx conf to the app appropriate place
COPY ./nginx.conf /etc/nginx/sites-available/app

# create a symbolic link to allow nginx to recognize the config
RUN ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled

# set some environment variables
ENV FLASK_APP=jwtAuthenticator
ENV FLASK_ENV=development
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# create database migrations
RUN flask db init
RUN flask db migrate -m "initial migrations"
RUN flask db upgrade


# let port 80 be accessible to the ouside world
EXPOSE 80

# CMD nginx && gunicorn -w 4 -b unix:somesocket.sock -m 777 wsgi:app --access-logfile - --log-level debug -g www-data
# run nginx and the flask app using uwsgi
CMD nginx && uwsgi --ini uwsgi.ini
# CMD nginx && gunicorn -w 4 -b 0.0.0.0:5000  wsgi:app
