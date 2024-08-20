from flask import render_template
from App import app


@app.route("/")
@app.route("/index")
def index():
  user = { 'username': 'Timbo'}
  return render_template('index.html')