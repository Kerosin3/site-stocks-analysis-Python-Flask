# from application import a
# from application import app
from application.misc import get_data_historical, get_lastday_data, get_today_price
import pytest
from pandas._libs.tslibs.timestamps import Timestamp
from iexfinance.utils.exceptions import IEXQueryError
from application.misc import ServerExeption, SomethingBadHappened, NoSuchStock
from application.views.stocks_main import get_today_price_url
from app import app
import json


# https://stackoverflow.com/questions/56658481/how-to-parse-a-jsonify-object-in-python-and-display-in-html

@pytest.fixture
def app_context():
    with app.app_context():
        yield
# dont need due to required content
# https://stackoverflow.com/questions/51563867/how-to-read-python-flask-jsonify-response-object
# https://stackoverflow.com/questions/51563867/how-to-read-python-flask-jsonify-response-object
# def test_get_today_price_url(app_context):
#     ticker = 'TSLA'
#     json_data_price = get_today_price_url(ticker)
#     assert json_data_price.status_code == 200
#     data_dict = json.loads(json_data_price.get_data().decode("utf-8"))
#     assert ticker == data_dict['ticker']
