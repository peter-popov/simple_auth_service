FROM ubuntu:18.04


ENV LANG="C.UTF-8" LC_ALL="C.UTF-8" PATH="/opt/venv/bin:$PATH" PIP_NO_CACHE_DIR="false"

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-setuptools \
    && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
COPY . /app

ENV FLASK_APP=simple_auth_service

CMD [ "flask", "run", "--host=0.0.0.0" ]