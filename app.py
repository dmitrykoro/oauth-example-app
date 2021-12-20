import datetime
import os
import random
import threading
import time

from flask import Flask, render_template, redirect, url_for, request
from flask_dance.contrib.github import make_github_blueprint, github
from turbo_flask import Turbo

app = Flask(__name__)
turbo = Turbo(app)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "password")

# heroku
app.config['SERVER_NAME'] = 'number-generator-oauth.herokuapp.com'
app.config["GITHUB_OAUTH_CLIENT_ID"] = 'Iv1.eceeaee96e9f56c7'
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = '2cabbf3cb6a709256364d1b93e5ce1eb14c9a79d'

github_bp = make_github_blueprint()
app.register_blueprint(github_bp, url_prefix="/number")

TIMEDELTA = 5
current_number = 0.0
previous_time = datetime.datetime.now()


@app.before_first_request
def before_first_request():
    thread = threading.Thread(target=print_random_number)
    thread.start()


def print_random_number():
    with app.app_context():
        while True:
            turbo.push(turbo.replace(render_template('index/index.html'), 'rand_num'))

            global previous_time
            previous_time = datetime.datetime.now()

            time.sleep(TIMEDELTA)


@app.context_processor
def generate_random_number():
    actual_timedelta = (datetime.datetime.now() - previous_time).total_seconds()

    if actual_timedelta >= TIMEDELTA:
        global current_number
        current_number = random.random()

    return {'current_number': current_number}


@app.route('/')
def index():
    if not github.authorized:
        return render_template('login/login.html')

    return redirect(url_for('number'))


@app.route('/logout')
def logout():
    try:
        del app.blueprints['github'].token
    except KeyError:
        pass

    return redirect("https://number-generator-oauth.herokuapp.com")


@app.route('/number')
def number():
    if github.authorized:
        return render_template('base.html')

    else:
        return render_template('login/login.html')


if __name__ == '__main__':
    app.run()
