from flask import render_template, flash, redirect, url_for, request
# from werkzeug.urls import url_parse
from urllib.parse import urlparse
from flask_login import login_user, current_user, logout_user, login_required
from App import app, db
from App.forms import LoginForm, SignUpForm
from App.models import User


# note: order of decorators is important- routes first
@app.route("/")
@app.route("/index")
# protects routes from anonymous users
@login_required
def index():
    posts = [
        {
            'author': {'username': 'john'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Movie was really good'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Defines a login route"""
    # prevents logged in users from coming to login again
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # first used instead of all since atleast one result is expected
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        # enhance user experience by redirecting users back
        # to the login required pages once authenticated
        next_page = request.args.get('next')  # parse the query string
        # check query string is a relative url...just a path
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route("/logout")
def logout():
    """Defines a logout route"""
    # clears the user session
    logout_user()
    return redirect(url_for('index'))


@app.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
    """New user signup route"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats you are now registered!')
        return redirect(url_for('login'))
    return render_template('sign_up.html', title=SignUp, form=form)
