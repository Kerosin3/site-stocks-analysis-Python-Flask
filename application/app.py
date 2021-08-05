from flask import Flask,render_template,request,redirect,jsonify
from werkzeug.exceptions import BadRequest,InternalServerError,NotAcceptable
app = Flask(__name__)
test = '1'
from application.views.stocks_main import stocks_main_views
from application.misc.stocks_getter import get_data_historical,get_lastday_data,get_today_price
from os import getenv,environ
import config

app.register_blueprint(stocks_main_views)

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

@app.route("/",endpoint='index',methods=['GET','POST'])
def index_page():
    data0 = {}
    today_prices = {}
    if request.method == 'GET':
        for index in indexes_eft_list:
            data0[index] = get_lastday_data(index),get_today_price(index)
            # today_prices[index] = get_today_price(index)
        print('today prices are', today_prices)
        return render_template("index.html",indexes=data0)
    elif request.method == 'POST':
        index_ticker = request.form.get("index_ticker")
        if get_lastday_data(index_ticker) is None:
            raise NotAcceptable('There is no such ticker')
        elif index_ticker not in indexes_eft_list:
            indexes_eft_list.append(index_ticker)
            for index in indexes_eft_list:
                data0[index] = get_lastday_data(index)
            return render_template("index.html", indexes=data0)
        else:
            raise BadRequest('This index has been already added')

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




if __name__ == '__main__':
    app.run(use_reloader = True,debug=True, host="0.0.0.0", port="5000") #REQUIRED!
