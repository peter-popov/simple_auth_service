FROM python:3.7

ENV LANG="C.UTF-8" LC_ALL="C.UTF-8" PIP_NO_CACHE_DIR="false"

#RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
#    python3-pip \
#    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
COPY . /app

ENV FLASK_APP=simple_auth_service

CMD [ "gunicorn", "-w 2", "-b=0.0.0.0:5000", "simple_auth_service:create_app()" ]