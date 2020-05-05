import os
import click
from flask import Flask

from flask_mongoengine import MongoEngine
import api
from werkzeug.security import generate_password_hash

from models.user import User


app = Flask(__name__, instance_relative_config=True)

app.config['MONGODB_SETTINGS'] = {
    'host': os.environ.get('MONGODB_URI', 'mongodb://localhost/mymoney')
}

MongoEngine(app)

@app.cli.command('create-user')
@click.argument('name')
@click.argument('email')
@click.argument('password')
def create_user(name, email, password):
    user = User(name=name,
                email=email,
                password_hash=generate_password_hash(password))
    user.save()
    click.echo("User for email {} created!".format(email))

app.register_blueprint(api.bp)
