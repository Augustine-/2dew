import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    """
    On POST with valid data, it should register a user in the DB and redirect to the login URL.
    Register view renders on GET.
    """
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == '/auth/login'

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'"
        ).fetchone() is not None

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered.')
))
def test_register_validate_input(client, username, password, message):
    """
    Invalid data should display appropriate error messages.
    """
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    """
    Valid login data shoud log you in and render the login page.
    """
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        assert client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    """
    Incorrect login data should show error messages.
    """
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    """
    Logout should remove the user_id from session.
    """
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

