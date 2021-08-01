from flask import request, Blueprint,render_template
from werkzeug.exceptions import BadRequest, InternalServerError

stocks_main_views = Blueprint("stocks_main_views",
                       __name__,
                       url_prefix="/stocks"
                       )

@stocks_main_views.route("/indexes/", methods=["GET"],endpoint='indexes')
def indexes_dynamics():
    return render_template('indexes.html')
