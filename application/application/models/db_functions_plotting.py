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
        last = df.index[-1]
        before = last - 90
        df = df.truncate(before=before,after=last) #only - days!
        # print('last',last)
        # print('------------------------',df)
        df["date"] = pd.to_datetime(df["date"])
        inc = df.close > df.open
        dec = df.open > df.close
        w = 12 * 60 * 60 * 1000  # half day in ms
        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
        p = figure( tools=TOOLS, plot_height=300, plot_width=1400, title=ticker + " candlestick")

        # p.xaxis.major_label_orientation = pi / 4
        # p.grid.grid_line_alpha = 1
        print(pd.to_datetime(df["date"]))
        p.xaxis.major_label_overrides = {
            i: date.strftime('%b %d') for i, date in enumerate(pd.to_datetime(df["date"]),start=before)
        }
        p.xaxis.bounds = (before, last)
        p.x_range.range_padding = 0.05

        p.segment(df.index, df.high, df.index, df.low, color="black")
        p.vbar(df.index[inc], 0.5, df.open[inc], df.close[inc], fill_color="#00FF5E", line_color="black")
        p.vbar(df.index[dec], 0.5, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")
        # p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#00FF5E", line_color="black")
        # p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Price ($)'
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
