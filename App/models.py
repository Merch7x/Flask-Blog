from datetime import datetime, timezone
from hashlib import md5
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from App import db, login
import jwt  # type: ignore
from time import time
from App.search import add_to_index, remove_from_index, query_index


class SearchableMixin:
    @classmethod
    def search(cls, expression, page, per_page):
        """Queries Elasticsearch for a given expression 
            and maps the results back to SQLAlchemy objects in the database.
        """
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(*when, value=Post.id)), total

    @classmethod
    def before_commit(cls, session):
        """Captures changes (additions, updates, deletions)
        in the SQLAlchemy session before a commit."""
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        """Synchronizes changes made
        in the database with Elasticsearch after a commit."""
        try:
            for obj in session._changes['add']:
                if isinstance(obj, SearchableMixin):
                    add_to_index(obj.__tablename__, obj)
            for obj in session._changes['update']:
                if isinstance(obj, SearchableMixin):
                    add_to_index(obj.__tablename__, obj)
            for obj in session._changes['delete']:
                if isinstance(obj, SearchableMixin):
                    remove_from_index(obj.__tablename__, obj)
        except Exception as e:
            # Log the exception to avoid impacting the database functionality
            current_app.logger.error(f"Elasticsearch update failed: {e}")

        session._changes = None

    @classmethod
    def reindex(cls):
        """Rebuilds the Elasticsearch index
        for all records of the model."""
        for obj in cls.query:
            try:
                add_to_index(cls.__tablename__, obj)
            except Exception as e:
                current_app.logger.error(f"Failed to reindex {obj.id}: {e}")


# Auxiliary table used to instrument the many to many relationship
# between users. it doesn't represent any object.it is managed by sqlalchemy
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))


)


class User(UserMixin, db.Model):
    """A database model for users"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(250))
    # sql-alchemy construct 'posts' only exists in the model not db
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(
        db.DateTime, default=datetime.utcnow)  # revisit
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return f'<user> {self.username}'

    def set_password(self, password):
        """Transforms a users password into a hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks password hash against user password"""
        return check_password_hash(self.password_hash, password)

    # creates user avatars based on users' md5 hashed email
    # that is sent to the gravatar service and returns an image
    def avatar(self, size):
        """create a user's avatar"""
        digest = md5(self.email.lower().encode('utf-8 ')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def is_following(self, user):
        """Establish whether a user is following another user"""
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        """Follow a user"""
        if self == user:
            raise ValueError("Users cannot follow themselves.")
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """Unfollow a user"""
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        return followed.union(self.posts).order_by(
            Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            # payload contains user id and current time + 10min
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@ login.user_loader
def load_user(id):
    """Creates a user loader function that
        writess the login state to the user
        session
    """
    return User.query.get(int(id))


class Post(SearchableMixin, db.Model):
    """Model for posts"""
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<post {self.body}'


# class Message(db.Model):
#     """Model for user messages"""
#     id = db.Column(db.Integer, primary_key=True)
#     sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     body = db.Column(db.String(140))
#     timestamp = db.Column(db.DateTime, index=True,
#                           default=datetime.now(timezone.utc))

#     def __repr__(self):
#         return '<message {}>'.format(self.body)


# class Notifications(db.Model):
#     """Model for notis"""
#     id = db.Column(db.integer, primary_key=True)
#     name = db.Column(db.String(128), index=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     imestamp = db.Column(db.DateTime, index=True, default=time)
#     payload_json = db.Column(db.Text)

#     def get_data(self):
#         return json.loads(str(self.payload_json))


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


# def retry_es_operations():
#     """Retry failed Elasticsearch operations."""
#     global es_retry_queue
#     for action, instance in es_retry_queue[:]:  # Copy the list to iterate safely
#         try:
#             if action == 'add':
#                 add_to_index(instance.__tablename__, instance)
#             elif action == 'update':
#                 add_to_index(instance.__tablename__, instance)
#             elif action == 'delete':
#                 remove_from_index(instance.__tablename__, instance)
#             es_retry_queue.remove((action, instance))  # Remove successfully retried operation
#         except Exception as e:
#             current_app.logger.error(f"Retry failed for Elasticsearch operation: {e}")
