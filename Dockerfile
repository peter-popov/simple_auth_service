FROM python:3.7

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

CMD [ "gunicorn", "-w 2", "-b=0.0.0.0:5000", "simple_auth_service:create_app()" ]