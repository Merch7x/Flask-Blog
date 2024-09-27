from flask import render_template, flash, redirect, url_for, request, g
# from werkzeug.urls import url_parse
from datetime import datetime, timezone
from urllib.parse import urlparse
from flask_babel import _  # type: ignore
from flask_login import login_user, current_user, logout_user, login_required
from App import db
from App.auth import bp
from App.auth.forms import LoginForm, SignUpForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from App.models import User
from App.auth.email import send_password_reset_email


@bp.route("/login", methods=['GET', 'POST'])
def login():
    """Defines a login route"""
    # prevents logged in users from coming to login again
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # first used instead of all since atleast one result is expected
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        # enhance user experience by redirecting users back
        # to the login required pages once authenticated
        next_page = request.args.get('next')  # parse the query string
        # check query string is a relative url...just a path
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
            return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@bp.route("/logout")
def logout():
    """Defines a logout route"""
    # clears the user session
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
    """New user signup route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congrats you are now registered!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/sign_up.html', title=_(SignUp), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)

    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your passsword has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
