from flask import (
    Flask,render_template,request,redirect,jsonify,
    url_for,flash,session,g,abort
)
import hashlib, uuid
from werkzeug.exceptions import BadRequest,InternalServerError,NotAcceptable
from application.views.stocks_main import stocks_main_views
from application.misc.stocks_getter import get_data_historical,get_lastday_data,get_today_price,get_today_prices_several,get_historical_for_graph,get_data_for_plotting
from application.models.db_functions_plotting import get_data_for_plotting_wrap
from os import getenv,environ
import config
from json import dumps
from bokeh.embed import json_item
from application.models.database import db
from application.models import create_index
from datetime import date
from datetime import datetime, timedelta
from application.models.db_functions import filling_indexes_db,remove_indexes
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.plotting import figure
from users.users import User,users_list
import webbrowser
from application.views.stocks_main_views import stocks_main_app
from werkzeug.security import check_password_hash
from flask_login import (
    login_user,login_manager,
    logout_user,login_required,UserMixin,current_user,LoginManager
)
import random
app = Flask(__name__)
# print('==========',app.url_map)
app.register_blueprint(stocks_main_views)
app.register_blueprint(stocks_main_app)
from flask_migrate import Migrate
db.init_app(app)
migrate = Migrate(app, db)  # откуда он знает про db?


# app.config['SERVER_NAME'] = '0.0.0.0:5000'
environ["FLASK_ENV"] = "development"
environ["FLASK_DEBUG"] = "1"
workmode = getenv("FLASK_ENV", 'development')
if workmode == 'development':
    config_app = config.DevelopmentConfig
elif workmode == 'production':
    config_app = config.ProductionConfig
elif workmode == 'test':
    config_app = config.TestingConfig
else:
    raise EnvironmentError('Not right mode of initialization, aborting')
app.config.from_object(config_app)
# environ["FLASK_DEBUG"] = "1"
app.secret_key = 'super secret key'


from flask_apscheduler import APScheduler
from jobs import job1,job_pseupo_update,job_get_update_all_indexes


#
# scheduler = APScheduler()
#     # it is also possible to enable the API directly
#     # scheduler.api_enabled = True  # noqa: E800
# APScheduler.init_app(job1(),app=app)
# APScheduler.start()
# scheduler.init_app(app)
# scheduler.start()
# indexes_eft_list = [
#     'SPLG',
#     'QQQM',
#     'DIA',
#     'IWM'
# ]
# @app.before_request
# def before_request():
#     g.user = None
#     if 'user_id' in session:
#         user =  [user for user in users_list if user.id == session['user_id']][0]
#         print('Establishing session for user',user)
#         g.user = user
#     else:
#         g.user = None
#
from application.models.users import LoginForm,RegisterForm
from flask_bcrypt import Bcrypt
from application.misc.user_db_funct import create_user
from application.misc.user_db_funct import get_user
bcrypt = Bcrypt(app)
# app.config['SESSION_COOKIE_SECURE'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
from flask_wtf.csrf import CsrfProtect
import os
import pandas as pd
CsrfProtect(app)



def get_all_indexes():
    cwd = os.getcwd()
    path = os.path.join(cwd, "application", 'misc', 'iex')
    out = pd.read_csv(path + '/all_symbols.csv', sep='\t', encoding='utf-8') # read
    print('reading.....')
    return out['symbol'].to_list()

all_symbols_iex = get_all_indexes()


@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    user = get_user(id=user_id)
    print('loggined as',user.username)
    return user
#https://stackoverflow.com/questions/21214270/how-to-schedule-a-function-to-run-every-hour-on-flask
@app.route('/login',methods = ['GET','POST'],endpoint='login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur_user = get_user(str(form.username.data))
        if cur_user is not None:
            if bcrypt.check_password_hash(cur_user.password,form.password.data):
                login_user(cur_user)
                flash('Logged in successfully.')
                return redirect(url_for('index'))
    return render_template('users/login.html',form=form)

@app.route('/logout',methods = ['GET','POST'],endpoint='logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register',methods = ['GET','POST'],endpoint='register')
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = create_user(username=form.username.data,
                               password=hashed_password)
        if new_user is None: #user exists
            return render_template('users/register.html',message='Such user is already exists')
        login_user(get_user(str(form.username.data)))
        flash('Logged in successfully.')
        return redirect(url_for('index'))
    return render_template('users/register.html',form=form)


@app.route("/",endpoint='index',methods=['GET','POST','DELETE'])
@login_required
def index_page():
    # print(all_symbols_iex)
    today =  date.today()
    current_data = datetime.now() + timedelta(days=0)
    indexes_to_add = []
    indexes_to_delete = []
    all_indexes = {}
    # error = None
    if request.method == 'POST' and request.form.get("delete_pressence") != 'delete': #why cant redirect?????????????????
        index_ticker = request.form.get("index_ticker")
        indexes_to_add.append(index_ticker) #add ticker
        full_data = filling_indexes_db(time0=current_data,
                                                    list_new_indexes=indexes_to_add)

        if full_data == 0: # error  - invalid symbol syntaxis
            error = 'Please enter a valid symbol'
            current_day_prices, last_day_prices, \
            count, data_historical = filling_indexes_db(time0=current_data,
                                                     list_new_indexes=[]) #dont add
            return render_template("index.html",
                                   current_day_prices=current_day_prices,
                                   last_day_prices=last_day_prices,
                                   length0=count,
                                   list_indexes=dumps(all_indexes), error=error,
                                   username = current_user.username)
        elif full_data == 1:# error - already added
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
                                   username = current_user.username)

        else: # no errors
            current_day_prices, last_day_prices, \
            count, data_historical = full_data#filling_indexes_db(time0=current_data,
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
                                   username = current_user.username)
    elif request.method == 'GET':
        # error = request.args['error']  # counterpart for url_for()
        # if request.args.get('error') is not None:
        #     error = request.args['error']  # counterpart for url_for()
        # else:
        #     error = None
        current_day_prices, last_day_prices, \
        count, data_historical = filling_indexes_db(time0=current_data,
                                                    list_new_indexes=indexes_to_add)
        for n, (ticker,_) in enumerate(last_day_prices.items()):
            all_indexes[n+1] = ticker
        return render_template("index.html",
                               current_day_prices=current_day_prices,
                               last_day_prices = last_day_prices,
                               length0 = count,
                               list_indexes=dumps(all_indexes),
                               username = current_user.username)


        # return render_template("index.html",
        #                        current_day_prices=current_day_prices,
        #                        last_day_prices=last_day_prices,
        #                        length0=count,
        #                        list_indexes=dumps(all_indexes),error=error)
    elif request.method == 'POST' and request.form.get("delete_pressence") == 'delete':
        index_ticker = request.form.get("index_ticker")

        if remove_indexes(index_ticker):
            # indexes_to_delete.append(index_ticker)
            # indexes_to_delete.clear()
            current_day_prices, last_day_prices, \
            count, data_historical = filling_indexes_db(time0=current_data,
                                                        list_new_indexes=indexes_to_add)
            for n, (ticker,_) in enumerate(last_day_prices.items()):
                all_indexes[n+1] = ticker
            return render_template("index.html",
                                   current_day_prices=current_day_prices,
                                   last_day_prices=last_day_prices,
                                   length0=count,
                                   list_indexes=dumps(all_indexes), error=None,
                                   username = current_user.username)
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
                                   username = current_user.username)

@app.route('/redirect0/<string:index_ticker>/',endpoint='redirect0')
def redirect0(index_ticker):
    sa = 'https://seekingalpha.com/symbol/' + str(index_ticker)
    return redirect(sa)
    # return webbrowser.open_new_tab(sa)

@app.route('/_add_numbers')
def add_numbers():
    # a = request.args.get('a', 0, type=int)
    # b = request.args.get('b', 0, type=int)
    # return jsonify(result=a + b)
    ticker = request.args.get('ticker')
    price = get_today_price(ticker)
    # return jsonify(
    #     ticker=ticker,
    #     price=price
    # )
    return jsonify(result=price)

@app.route('/add_random',methods = ['GET'],endpoint='add_random')
def add_random():
    if request.method == 'GET':
        index_ticker = []
        index_ticker.append(random.choice(all_symbols_iex))
        print('index ticker===============',index_ticker)
        full_data = filling_indexes_db(list_new_indexes=index_ticker)
        return redirect(url_for('index'))
        # else:
        #     flash('This stock is already added')
        #     return redirect(url_for('index'))

@app.route('/plot/<string:index_ticker>/',endpoint='plot')
def plot(index_ticker):
    # index_ticker = 'AAPL'
    p = get_data_for_plotting_wrap(index_ticker)
    # html = file_html(p,CDN,'plot')
    # return html
    return dumps(json_item(p, "myplot"))




# @app.route('/plot')
# def plot():
#     index_ticker = 'AAPL'
#     p = get_data_for_plotting_wrap(index_ticker)
#     # html = file_html(p,CDN,'plot')
#     # return html
#     return dumps(json_item(p, "myplot"))


    # return render_template('test.html')
#
# @app.cli.command(help="create all tables")
# def create_all_tables():
#     with app.app_context():
#         migrate.init_app()
#         migrate.upgrade()
# print('==========',app.url_map)

if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(use_reloader = True,debug=True, host="0.0.0.0", port="5000") #REQUIRED!

