from flask import Blueprint

bp = Blueprint('auth', __name__)


from App.auth import routes
