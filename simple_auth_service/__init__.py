from flask import Flask
from flasgger import Swagger

app = Flask(__name__)

from simple_auth_service import auth_view, user_view, vehicles_view

app.register_blueprint(auth_view.bp)
app.register_blueprint(user_view.bp)
app.register_blueprint(vehicles_view.bp)


swagger_template = {
    "info": {"title": "Simple Auth Service"},
    "securityDefinitions": {"basicAuth": {"type": "basic"}},
}

swagger = Swagger(app, template=swagger_template)


def create_app():
    return app
