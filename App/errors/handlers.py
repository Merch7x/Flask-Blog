from flask import render_template
from App import db
from App.errors import bp


@bp.errorhandler(404)
def not_found_error(error):
    """Not Found Error"""
    return render_template('errors/404.html'), 404


@bp.errorhandler(500)
def internal_error(error):
    """Server Error"""
    db.session.rollback()
    return render_template('errors/500.html'), 500
