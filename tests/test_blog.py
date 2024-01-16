import pytest
from flaskr.db import get_db


def test_index(client, auth):
    """
    Index should display login/register.

    Logged-in users should see the logout link, and a test post.
    """
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    """
    User must be logged in to view create/update/delete.
    """
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"

def test_author_required(test_app, client, auth):
    """
    User may only CUD their own posts.
    """
    # change author to another user
    with test_app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # can't see edit link
    assert b'href="/1/update"' not in client.get('/').data

@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    """
    POSTing to other user's endpoints is not allowed.
    """
    auth.login()
    assert client.post(path).status_code == 404

def test_create(client, auth, test_app):
    """
    Create view renders.
    POSTing to the database works.
    """
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with test_app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2

def test_update(client, auth, test_app):
    """
    Update view renders.
    UPDATEing a post in the database works.
    """
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with test_app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    """
    Invalid post/updates render errors.
    """
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

def test_delete(client, auth, test_app):
    """
    Delete view redirects to index.
    DELETE removes post from DB.
    """
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with test_app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None