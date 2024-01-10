"""configure tests

Pytest uses fixtures by matching their function names with the names of args in the test functins.

for example, the `test_yo` function takes a `client` argument.
    pytest matches that with the `client` fixture definition, calls it, and passes the returned value to the test functin.

"""
import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    """
    create and open a temp file, returning the file descrptor and path.
    database path is overridden to point to the temp path.
    test db tables are created, test data inserted.
    after testing, temp file closed and removed.

    TESTING indicates to the app that we are in test mode.
        - Flask uses this behind the scenes to do some optimiations for test.
    """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

        yield app

        os.close(db_fd)
        os.unlink(db_path)

@pytest.fixture
def client(app):
    """
        client fixture: calls app.test_client() with the app object created by the app fixture.
        tests will use the client to make reqs to the app without running the server.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    creates a runner that can call the Click commands registered with the application.
    """
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)