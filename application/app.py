from flask import Flask,render_template

app = Flask(__name__)

from application.views.stocks_main import stocks_main_views
from application.misc.stocks_getter import get_data_historical

app.register_blueprint(stocks_main_views)


indexes_eft_list = [
    'SPGL',
    'QQQM',
    'DIA',
    'IWM'
]

@app.route("/",endpoint='index')
def index_page():
    # for index in indexes_eft_list:

    return render_template("index.html",indexes=indexes_eft_list)
