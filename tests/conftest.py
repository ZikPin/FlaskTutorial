import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db


with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


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
def app():
    db_fd, db_path = tempfile.mkstemp() # creates and opens a temporary file 

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path # overriding the database
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql) # inserting test data

    yield app

    os.close(db_fd) # temprory file is closed and removed after test completion
    os.unlink(db_path)


# we are using client to make fake requests to application without running the server
@pytest.fixture
def client(app):
    return app.test_client()


# runner that can call the Click commands
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    return AuthActions(client)