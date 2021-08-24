from flask import request, Blueprint, render_template, jsonify, g, redirect, flash, url_for
from application.misc.user_db_funct.users import create_user
from sqlalchemy import create_engine
from datetime import date
from datetime import datetime, timedelta
from application.misc.stocks_functions import create_stock_obj
from application.models.users import Users
from sqlalchemy.orm import Session, sessionmaker, load_only, session
from flask import current_app
from flask_login import (
    login_user, login_manager,
    logout_user, login_required, UserMixin, current_user, LoginManager
)

stocks_main_app = Blueprint("stocks_main_app",
                            __name__,
                            url_prefix="/stocks_tracking"
                            )


@stocks_main_app.route("/index_stocks/", methods=["GET", 'POST'], endpoint='index_stocks')
@login_required
def index_stocks():
    return render_template('stocks/stocks_index.html', username=current_user.username)
    # cur_username =  str(g.user.username)
    # user = create_user(cur_username, '12345')
    # if user is None: #user exists
    #     with Session() as session:
    #         user_id = session.query(Users). \
    #             filter(Users.username == cur_username).one_or_none()
    #         assert  user_id is not None
    #         user_id = user_id.id
    #     print(f'current user is {cur_username},id:{user_id} ')
    #     if request.method == 'GET':
    #         pass
    #     #add
    #     elif request.method == 'POST' and request.form.get("delete_pressence") != 'delete':
    #         ticker = request.form.get("index_ticker")
    #         print('here we are',ticker)
    #         stock = create_stock_obj(ticker)
    #         if stock is None:
    #             error = 'This stock has been already added'
    #             flash(error)
    #
    # else:
    #     return  redirect(url_for('login'))


@stocks_main_app.route("/crypto_dynamics/", methods=["GET", 'POST'], endpoint='crypto_dynamics')
@login_required
def crypto_dynamics():
    return render_template('stocks/stocks_index.html', username=current_user.username)


@stocks_main_app.route("/news/", methods=["GET", 'POST'], endpoint='news')
@login_required
def news():
    return render_template('stocks/stocks_index.html', username=current_user.username)
