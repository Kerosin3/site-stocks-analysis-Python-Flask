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

@stocks_main_views.route("/get_index_price/", methods=["GET"],endpoint='get_index_price')
def get_today_price_url(ticker:str):
    price = application.misc.stocks_getter.get_today_price(ticker)
    return jsonify(
        ticker=ticker,
        price=price
    )
