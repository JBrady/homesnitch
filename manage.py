from flask.cli import FlaskGroup
from backend.api import app
from backend.extensions import db
from backend.models import User, Report


def create_app():
    return app


cli = FlaskGroup(create_app=create_app)


if __name__ == '__main__':
    cli()
