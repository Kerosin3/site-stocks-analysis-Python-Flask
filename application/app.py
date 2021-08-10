from flask import Flask,render_template,request,redirect,jsonify
from werkzeug.exceptions import BadRequest,InternalServerError,NotAcceptable
from application.views.stocks_main import stocks_main_views
from application.misc.stocks_getter import get_data_historical,get_lastday_data,get_today_price,get_today_prices_several,get_historical_for_graph
from os import getenv,environ
import config
from json import dumps
from bokeh.embed import json_item
from application.models.database import db
from application.models import create_index
from datetime import date
from datetime import datetime, timedelta
from application.models.db_functions import filling_indexes_db

app = Flask(__name__)
app.register_blueprint(stocks_main_views)
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

indexes_eft_list = [
    'SPLG',
    'QQQM',
    'DIA',
    'IWM'
]

# @app.route("/",endpoint='index',methods=['GET','POST'])
# def index_page():
#     last_day_prices = {}
#     if request.method == 'GET':
#         current_prices = get_today_prices_several(indexes_eft_list)
#         for index in indexes_eft_list:
#             #utlize many requests
#             last_day_prices[index] = get_lastday_data(index)
#         # return current_prices
#         return render_template("index.html",
#                                current_day_prices=current_prices,
#                                last_day_prices = last_day_prices,
#                                length0 = len(indexes_eft_list))
#     elif request.method == 'POST':
#         index_ticker = request.form.get("index_ticker")
#         if get_lastday_data(index_ticker) is None:
#             raise NotAcceptable('There is no such ticker')
#         elif index_ticker not in indexes_eft_list:
#             indexes_eft_list.append(index_ticker)
#             for index in indexes_eft_list:
#                 data0[index] = get_lastday_data(index)
#             return redirect('/')
#             # return render_template("index.html", indexes=data0)
#         else:
#             raise BadRequest('This index has been already added')


@app.route("/",endpoint='index',methods=['GET','POST'])
def index_page():
    today =  date.today()
    current_data = datetime.now() + timedelta(days=0)
    indexes_to_add = []
    # index_ticker = None
    if request.method == 'GET':
        # indexes_to_add.append(str(index_ticker))
        print('=====================', indexes_to_add)
        current_day_prices, last_day_prices, \
        count, data_historical = filling_indexes_db(time0=current_data,
                                                    list_new_indexes=indexes_to_add)
        # for ind in last_day_prices:
        #     ind = xxx.history_data['close'].iloc[-1])
        # return current_prices
        print('count is =====================',count)
        return render_template("index.html",
                               current_day_prices=current_day_prices,
                               last_day_prices = last_day_prices,
                               length0 = count)
    elif request.method == 'POST': #why cant redirect?
        index_ticker = request.form.get("index_ticker")
        indexes_to_add.append(index_ticker)
        current_day_prices, last_day_prices, \
        count, data_historical = filling_indexes_db(time0=current_data,
                                                    list_new_indexes=indexes_to_add)
        indexes_to_add.clear()
        return render_template("index.html",
                               current_day_prices=current_day_prices,
                               last_day_prices=last_day_prices,
                               length0=count)
    #     if get_lastday_data(index_ticker) is None:
    #         raise NotAcceptable('There is no such ticker')
    #     elif index_ticker not in indexes_eft_list:
    #         indexes_eft_list.append(index_ticker)
    #         for index in indexes_eft_list:
    #             data0[index] = get_lastday_data(index)
    #         return redirect('/')
    #         # return render_template("index.html", indexes=data0)
    #     else:
    #         raise BadRequest('This index has been already added')




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

@app.route('/plot')
def plot():
    # p = make_plot('petal_width', 'petal_length')
    p = get_historical_for_graph('ADBE')
    return dumps(json_item(p, "myplot"))
#
# @app.cli.command(help="create all tables")
# def create_all_tables():
#     with app.app_context():
#         migrate.init_app()
#         migrate.upgrade()


if __name__ == '__main__':
    app.run(use_reloader = True,debug=True, host="0.0.0.0", port="5000") #REQUIRED!
