from flask import Flask,render_template

app = Flask(__name__)

from application.views.stocks_main import stocks_main_views
app.register_blueprint(stocks_main_views)

@app.route("/")
def hello_world():
    return render_template("index.html")
