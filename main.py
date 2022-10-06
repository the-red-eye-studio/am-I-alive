import requests, time
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from config import github_account, account_string, days_to_consider_dead


def the_app():
    the_application = Flask(__name__)
    the_application.debug = False
    the_application.config['MAX_CONTENT_LENGTH'] = 256
    the_application.jinja_env.trim_blocks = True
    the_application.jinja_env.lstrip_blocks = True
    the_application.jinja_env.enable_async = True
    the_application.wsgi_app = ProxyFix(the_application.wsgi_app, x_proto=1, x_host=1)
    return the_application


app = the_app()
app.app_context().push()


@app.route("/")
def index():
    try:
        latest_commit_get = requests.get(f"https://api.github.com/users/{github_account}/events/public").json()
        latest_commit_time = latest_commit_get[0]["created_at"]
    except Exception:
        the_text = f"I couldn't connect to Github to check when {github_account} last committed."
        return render_template('index.html',
                               the_text=the_text,
                               request_complete=False,
                               alive=False), 404
    else:
        current_time = time.time()
        time_since_last_commit_in_seconds = current_time - latest_commit_time
        time_since_last_commit_in_days = time_since_last_commit_in_seconds / 86400
        if time_since_last_commit_in_days > days_to_consider_dead:
            the_text = f"{account_string} is dead. They haven't committed in {time_since_last_commit_in_days} days."
            return render_template('index.html',
                                   the_text=the_text,
                                   request_complete=True,
                                   alive=False), 404
        else:
            the_text = f"{account_string} is alive. They last committed {time_since_last_commit_in_days} days ago."
            return render_template('index.html',
                                   the_text=the_text,
                                   request_complete=True,
                                   alive=True), 200
