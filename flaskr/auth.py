import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# creating the blueprint 'auth', __name__ says where it is defined
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST': # starting validation after submitting the form
        username = request.form['username'] # request.form is a special type of dict mapping
        password = request.form['password']

        db = get_db()
        error = None

        # validating that username and password are not empty
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        if error is None:
            # after successful validation, insert the new user data into db
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password),)
                )
                db.commit()
            except db.IntegrityError: # will occur if the username already exists
                error = f"User {username} is already registered."
            else: # after storing the user, redirecting to login page
                return redirect(url_for("auth.login"))
            
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone() # returns one row from the query

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data across requests
            # data is stored in a cookie that is sent to the browser, 
            # and the browser then sends it back for subsequent requests
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request # registers a function that runs before the view function, no matter what URL is requested
def load_loggen_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


def login_required(view): # returns a new view function that wraps the original view
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None: # checks if a user is loaded and redirects to the login page otherwise
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view