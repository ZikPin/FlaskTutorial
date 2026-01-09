import sqlite3
from datetime import datetime

import click
from flask import current_app, g

# g is a special object that is unique to each request
# current_app is another special object that points to the flask application handling the request

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect( # establishing the connection to the database file in current_app config
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # allows accessing the columns by name

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None: # if g.db was set, then we close it
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# defines a command line command called init-db that calls the init_db function
# and shows a success message to the user
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')


# tells how to interpret timestamp values in the database: convert value to datetime.datetime
sqlite3.register_converter(
    'timestamp', lambda v : datetime.fromisoformat(v.decode())
)


def init_app(app):
    app.teardown_appcontext(close_db) # tells Flask to call that function when cleaning up after returning the response
    app.cli.add_command(init_db_command) # adds a new command that can be called with the flask command