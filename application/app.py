from flask import (
    Flask, render_template, request, redirect, jsonify,
    url_for, flash, session, g, abort
)
import hashlib, uuid
from werkzeug.exceptions import BadRequest, InternalServerError, NotAcceptable
from application.views.stocks_main import stocks_main_views
from application.misc.stocks_getter import get_data_historical, get_lastday_data, get_today_price, \
    get_today_prices_several, get_historical_for_graph, get_data_for_plotting
from application.models.db_functions_plotting import get_data_for_plotting_wrap
from os import getenv, environ
import config
from json import dumps
from bokeh.embed import json_item
from application.models.database import db
from application.models import create_index
from datetime import date
from datetime import datetime, timedelta
from application.models.db_functions import filling_indexes_db, remove_indexes
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.plotting import figure
from users.users import User, users_list
import webbrowser
from application.views.stocks_main_views import stocks_main_app
from werkzeug.security import check_password_hash
from flask_login import (
    login_user, login_manager,
    logout_user, login_required, UserMixin, current_user, LoginManager
)
import random
from flask_apscheduler import APScheduler
from jobs import job1, job_pseupo_update, job_get_update_all_indexes
from application.models.users import LoginForm, RegisterForm
from flask_bcrypt import Bcrypt
from application.misc.user_db_funct import create_user
from application.misc.user_db_funct import get_user
from flask_migrate import Migrate
from flask_wtf.csrf import CsrfProtect
import os
import pandas as pd

app = Flask(__name__)

# app.config['SERVER_NAME'] = '0.0.0.0:5000'
environ["FLASK_ENV"] = "development"
environ["FLASK_DEBUG"] = "1"
workmode = getenv("FLASK_ENV", 'development')
if workmode == 'development':
    print('using developing config')
    config_app = config.DevelopmentConfig
elif workmode == 'production':
    config_app = config.ProductionConfig
elif workmode == 'test':
    config_app = config.TestingConfig
else:
    raise EnvironmentError('Not right mode of initialization, aborting')
app.config.from_object(config_app)
app.secret_key = 'super secret key_my'
print(config_app.ENV)
# print(app.root_path)

app.register_blueprint(stocks_main_views)
app.register_blueprint(stocks_main_app)
db.init_app(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
# app.config['SESSION_COOKIE_SECURE'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
CsrfProtect(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


def get_all_indexes():
    cwd = os.getcwd()
    path = os.path.join(app.root_path, "application", 'misc', 'iex')
    out = pd.read_csv(path + '/all_symbols.csv', sep='\t', encoding='utf-8')  # read
    print('reading.....')
    return out['symbol'].to_list()


all_symbols_iex = get_all_indexes()


@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    user = get_user(id=user_id)
    print('loggined as', user.username)
    return user


@app.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur_user = get_user(str(form.username.data))
        if cur_user is not None:
            if bcrypt.check_password_hash(cur_user.password, form.password.data):
                login_user(cur_user)
                flash('Logged in successfully.')
                return redirect(url_for('index'))
    return render_template('users/login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'], endpoint='logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = create_user(username=form.username.data,
                               password=hashed_password)
        if new_user is None:  # user exists
            return render_template('users/register.html', message='Such user is already exists')
        login_user(get_user(str(form.username.data)))
        flash('Logged in successfully.')
        return redirect(url_for('index'))
    return render_template('users/register.html', form=form)


@app.route("/", endpoint='index', methods=['GET', 'POST', 'DELETE'])
@login_required
def index_page():
    today = date.today()
    current_data = datetime.now() + timedelta(days=0)
    indexes_to_add = []
    indexes_to_delete = []
    all_indexes = {}
    # error = None
    if request.method == 'POST' and request.form.get(
            "delete_pressence") != 'delete':  # why cant redirect?????????????????
        index_ticker = request.form.get("index_ticker")
        indexes_to_add.append(index_ticker)  # add ticker
        full_data = filling_indexes_db(time0=current_data,
                                       list_new_indexes=indexes_to_add)

        if full_data == 0:  # error  - invalid symbol syntaxis
            error = 'Please enter a valid symbol'
            current_day_prices, last_day_prices, \
            count, data_historical = filling_indexes_db(time0=current_data,
                                                        list_new_indexes=[])  # dont add
            return render_template("index.html",
                                   current_day_prices=current_day_prices,
                                   last_day_prices=last_day_prices,
                                   length0=count,
                                   list_indexes=dumps(all_indexes), error=error,
                                   username=current_user.username)
        elif full_data == 1:  # error - already added
            error = 'This stock has been already added'
            # flash(error)
            current_day_prices, last_day_prices, \
            count, data_historical = filling_indexes_db(time0=current_data,
                                                        list_new_indexes=[])  # dont add
            return render_template("index.html",
                                   current_day_prices=current_day_prices,
                                   last_day_prices=last_day_prices,
                                   length0=count,
                                   list_indexes=dumps(all_indexes), error=error,
                                   username=current_user.username)

        else:  # no errors
            current_day_prices, last_day_prices, \
            count, data_historical = full_data  # filling_indexes_db(time0=current_data,
            #                   list_new_indexes=indexes_to_add)  # dont add
            indexes_to_add.clear()
            for n, (ticker, _) in enumerate(last_day_prices.items()):
                all_indexes[n + 1] = ticker
            error = None
            flash('Successfully added')
            return render_template("index.html",
                                   current_day_prices=current_day_prices,
                                   last_day_prices=last_day_prices,
                                   length0=count,
                                   list_indexes=dumps(all_indexes), error=error,
                                   username=current_user.username)
    elif request.method == 'GET':
        current_day_prices, last_day_prices, \
        count, data_historical = filling_indexes_db(time0=current_data,
                                                    list_new_indexes=indexes_to_add)
        for n, (ticker, _) in enumerate(last_day_prices.items()):
            all_indexes[n + 1] = ticker
        return render_template("index.html",
                               current_day_prices=current_day_prices,
                               last_day_prices=last_day_prices,
                               length0=count,
                               list_indexes=dumps(all_indexes),
                               username=current_user.username)
    elif request.method == 'POST' and request.form.get("delete_pressence") == 'delete':
        index_ticker = request.form.get("index_ticker")

        if remove_indexes(index_ticker):
            current_day_prices, last_day_prices, \
            count, data_historical = filling_indexes_db(time0=current_data,
                                                        list_new_indexes=indexes_to_add)
            for n, (ticker, _) in enumerate(last_day_prices.items()):
                all_indexes[n + 1] = ticker
            return render_template("index.html",
                                   current_day_prices=current_day_prices,
                                   last_day_prices=last_day_prices,
                                   length0=count,
                                   list_indexes=dumps(all_indexes), error=None,
                                   username=current_user.username)
        else:
            error = 'There is not such stock in database'
            flash(error)
            current_day_prices, last_day_prices, \
            count, data_historical = filling_indexes_db(time0=current_data,
                                                        list_new_indexes=indexes_to_add)
            for n, (ticker, _) in enumerate(last_day_prices.items()):
                all_indexes[n + 1] = ticker
            return render_template("index.html",
                                   current_day_prices=current_day_prices,
                                   last_day_prices=last_day_prices,
                                   length0=count,
                                   list_indexes=dumps(all_indexes), error=error,
                                   username=current_user.username)


@app.route('/redirect0/<string:index_ticker>/', endpoint='redirect0')
@login_required
def redirect0(index_ticker):
    sa = 'https://seekingalpha.com/symbol/' + str(index_ticker)
    return redirect(sa)


@app.route('/add_random', methods=['GET'], endpoint='add_random')
@login_required
def add_random():
    if request.method == 'GET':
        index_ticker = []
        index_ticker.append(random.choice(all_symbols_iex))
        print('index ticker===============', index_ticker)
        full_data = filling_indexes_db(list_new_indexes=index_ticker)
        return redirect(url_for('index'))
        # else:
        #     flash('This stock is already added')
        #     return redirect(url_for('index'))


@app.route('/plot/<string:index_ticker>/', endpoint='plot')
@login_required
def plot(index_ticker):
    p = get_data_for_plotting_wrap(index_ticker)
    return dumps(json_item(p, "myplot"))


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host="0.0.0.0", port="5000")  # REQUIRED!
