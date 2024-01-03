import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

#associate the /register URL with the `register()` view func 
@bp.route('/register', methods=('GET', 'POST'))
# the view func, when the URL is hit, this code is run, and then the view is returned and rendered
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                #this handles escaping the input, no sql injection here
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                #this saves the change to the db
                db.commit()
            except db.IntegrityError:
                errr =f"User {username} is already registered."
            else:
                #url_for is more maintainable than hardcoding the url
                return redirect(url_for("auth.login"))
        # flash stores messages that can be retrieved when rendering the template
        flash(error)

    return render_template('auth/register.html')