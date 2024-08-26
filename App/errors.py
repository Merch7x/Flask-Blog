from flask import render_template
from App import app, db


@app.errorhandler(404)
def not_found_error(error):
    """Not Found Error"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Server Error"""
    db.session.rollback()
    return render_template('500.html'), 500
