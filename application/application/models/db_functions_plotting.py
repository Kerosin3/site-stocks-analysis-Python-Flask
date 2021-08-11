# from .stocks import Indexes
# from sqlalchemy.orm import Session,sessionmaker,load_only
# from sqlalchemy import create_engine
# from .db_functions import engine
# engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
import pandas as pd
from bokeh.plotting import figure, output_file, show
from .stocks import Indexes
from math import pi
from sqlalchemy.orm import Session,sessionmaker,load_only
from sqlalchemy import create_engine

def top_func(func):
    def wrapper(ticker:str):
        # ticker = 'AAPL'
        df = func(ticker)
        # print('------------------------',df)
        df["date"] = pd.to_datetime(df["date"])
        inc = df.close > df.open
        dec = df.open > df.close
        w = 12 * 60 * 60 * 1000  # half day in ms
        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
        p = figure(x_axis_type="datetime", tools=TOOLS, plot_height=300, plot_width=1400, title=ticker + " candlestick")
        p.xaxis.major_label_orientation = pi / 4
        p.grid.grid_line_alpha = 0.3
        p.segment(df.date, df.high, df.date, df.low, color="black")
        p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
        p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")
        # output_file("candlestick.html", title="candlestick.py example")
        return p
    return wrapper

@top_func
def get_data_for_plotting_wrap(ticker:str):
    if type(ticker) is str:
        engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
        Session = sessionmaker(engine)
        with Session() as session:
            index_to_plot = session.query(Indexes). \
                filter(Indexes.ticker == ticker).one_or_none()
            if index_to_plot is not None:
                return index_to_plot.history_data
            else:
                return None
    else:
        return None
