from flask import request, Blueprint,render_template,jsonify
from werkzeug.exceptions import BadRequest, InternalServerError
import application.misc.stocks_getter

stocks_main_views = Blueprint("stocks_main_views",
                       __name__,
                       url_prefix="/stocks"
                       )

@stocks_main_views.route("/indexes/", methods=["GET"],endpoint='indexes')
def indexes_dynamics():
    return render_template('indexes.html')


@stocks_main_views.route("/add_stock/", methods=["GET","POST"],endpoint='add_stock')
def add_stock():

    return render_template('indexes.html')

# @stocks_main_views.route("/get_index_price/<string:stock_ticker>/",methods=["GET"])
# def get_index(stock_ticker):
#     ticker = 'TSLA'
#     price = application.misc.stocks_getter.get_today_price(ticker)
#     return jsonify(
#         ticker=ticker,
#         price=price
#     )
#endpoint='get_index_price
#https://www.tutorialsteacher.com/jquery/jquery-ajax-method
@stocks_main_views.route("/get_index_price/", methods=["GET"])
def get_today_price_url():
    ticker = request.args.get('ticker')
    price = application.misc.stocks_getter.get_today_price(ticker)
    return jsonify(
        ticker=ticker,
        price=price
    )
    # return jsonify(result=price)
@stocks_main_views.route("/get_indexes_prices/", methods=["GET"])
def get_today_price_several_url():
    # tickers = request.args.get('several_tickers')
    tickers = request.args.getlist("several_tickers")
    # print('==============',tickers)
    # print('==============',statuses)
    prices = application.misc.stocks_getter.get_today_prices_several(tickers)
    return jsonify(prices)
