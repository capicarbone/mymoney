import os
import click
import pymongo
from flask import Flask

from flask_mongoengine import MongoEngine
import api
from werkzeug.security import generate_password_hash

from models.user import User
from models.transaction import Transaction
from models.statement import Statement

# TODO: Improve to recommended approach https://flask.palletsprojects.com/en/1.1.x/cli/#custom-scripts
def add_commands(app):

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

    @app.cli.command('fix_assignment_word_for_fund_documents')
    def fix_assignment_word_for_fund_documents():
        host_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost/mymoney')
        database_name = pymongo.uri_parser.parse_uri(os.environ.get('MONGODB_URI', 'mongodb://localhost/mymoney'))['database']
        mongo_client = pymongo.MongoClient(host_uri)
        db = mongo_client[database_name]

        db.fund.update({}, {'$rename': {'percentage_assigment': 'percentage_assignment'}}, multi=True)

        click.echo("Fix applied")

    @app.cli.command('recreate-month-statements')
    def recreate_month_statements():
        """
        Command for recreate month statements from existing transactions.
        TODO: Add parameters for more targeted work
        :return:
        """
        transactions = Transaction.objects().all()
        Statement.objects().delete()

        for t in transactions:
            Statement.add_to_statement(t)

        click.echo("Month statements recreated!")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        app.config['MONGODB_SETTINGS'] = {
            'host': os.environ.get('MONGODB_URI', 'mongodb://localhost/mymoney'),
            'retryWrites': False
        }

    MongoEngine(app)
    app.register_blueprint(api.bp)

    add_commands(app)

    return app






