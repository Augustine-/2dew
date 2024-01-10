"""database"""
import sqlite3

import click

from flask import current_app, g

# g is a special object, unique for each request.
# stores data, might be accessed by multiple funcs during the request.
# connection is stored and reused, if get_db is called another time during same req.

# current_app is another special obj, points to the Flask app handling the req.
# when using an app factory, there is no app object created yet--
# but get_db() won't be called until it exists, so current_app can be used.

# sqlite3.connct() establishes a connection to the file pointed at by the 'DATABASE' config key.
# that file doesnt need to exist yet, it will when we init the db later

# sqlite3.Row tells the conn to return rows that behave like dicts. row['col'] == cell


def init_db():
    db = get_db()

    #open_resource opens a file relative to the flaskr package.
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# defines a cli command called init-db that calls the init_db_command() function.
@click.command('init-db')
def init_db_command():
    # clear extant data and create new tables
    init_db()
    click.echo('Initialized database.')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

#if g.db was set, we made a connection. so, we close it like s0:
def close_db(e=None): # pylint: disable=unused-argument
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    # tells flask to call close_db() when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # adds a new command that can be called with `flask`
    app.cli.add_command(init_db_command)
