from flask import render_template, flash, redirect, url_for, request, g, \
    current_app
# from werkzeug.urls import url_parse
from datetime import datetime, timezone
from urllib.parse import urlparse
from flask_babel import _, get_locale  # type: ignore
from flask_login import current_user, login_required
from App import db
from App.main import bp
from App.main.forms import EditProfileForm, PostForm
from App.models import User, Post


# the app.before_request is ran before any request
# against any route is ran. it allows us to not convolute
# the codebase by adding the same lines of code to all the routes
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(
            timezone.utc
        )
        db.session.commit()
    g.locale = str(get_locale())


# note: order of decorators is important- routes first

@bp.route("/", methods=['GET', 'POST'])
@bp.route("/index", methods=['GET', 'POST'])
# protects routes from anonymous users
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Done!'))
        # redirect because if template is rendered on post request
        # were a refresh to happen the form would be resubmitted
        # standard response for a post is a redirect
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts(). \
        paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=posts.next_num)\
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num)\
        if posts.has_prev else None
    return render_template('index.html', form=form, title=_('Home'),
                           posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route("/explore", methods=['GET', 'POST'])
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).\
        paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=posts.next_num)\
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num)\
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@ login_required
def user(username):
    """Profile page route"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).\
        paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.user', username=current_user.username,
                       page=posts.next_num)\
        if posts.has_next else None
    prev_url = url_for('main.user', username=current_user.username,
                       page=posts.prev_num)\
        if posts.has_prev else None
    return render_template('user.html', user=user,
                           posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=["GET", "POST"])
@ login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Profile Updated Successfully!'))
        return redirect(url_for('main.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',
                           title=_('Edit Profile'), form=form)


@bp.route('/follow/<username>')
@ login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User%(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))

    current_user.follow(user)
    db.session.commit()
    flash(_('You are now following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %{username}s not found.', username=username))
        return redirect(url_for('main.index'))
    # if user == current_user:
    #     flash('You cannot follow yourself!')
    #     return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(_('You have stopped following {username}s!', username=username))
    return redirect(url_for('main.user', username=username))
