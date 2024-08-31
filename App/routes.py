from flask import render_template, flash, redirect, url_for, request
# from werkzeug.urls import url_parse
from datetime import datetime
from urllib.parse import urlparse
from flask_login import login_user, current_user, logout_user, login_required
from App import app, db
from App.forms import LoginForm, SignUpForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from App.models import User, Post
from App.email import send_password_reset_email


# the app.before_request is ran before any request
# against any route is ran. it allows us to not convolute
# the codebase by adding the same lines of code to all the routes
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()


# note: order of decorators is important- routes first

@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
# protects routes from anonymous users
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Done!')
        # redirect because if template is rendered on post request
        # were a refresh to happen the form would be resubmitted
        # standard response for a post is a redirect
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts(). \
        paginate(
            page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', form=form, title='Home',
                           posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route("/explore", methods=['GET', 'POST'])
def Explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()). \
        paginate(
            page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


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
    return redirect(url_for('login'))


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


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)

    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your passsword has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    """Profile page route"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()). \
        paginate(
            page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('user', username=current_user.username,
                       page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=current_user.username,
                       page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user,
                           posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Profile Updated Successfully!')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',
                           title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))

    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}')
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found')
        return redirect(url_for('index'))
    # if user == current_user:
    #     flash('You cannot follow yourself!')
    #     return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(f'You have stopped following {username}')
    return redirect(url_for('user', username=username))
