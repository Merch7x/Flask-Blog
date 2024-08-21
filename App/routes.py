from flask import render_template, flash, redirect, url_for
from App import app
from App.forms import LoginForm


@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'Timbo'}
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
    return render_template('index.html', user=user, title='Home', posts=posts)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Defines a login routes"""
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
