# from .stocks import Indexes
# from sqlalchemy.orm import Session,sessionmaker,load_only
# from sqlalchemy import create_engine
# from .db_functions import engine
# engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')
import pandas as pd
from bokeh.plotting import figure, output_file, show
from .stocks import Indexes
from math import pi
from bokeh.models import Circle, ColumnDataSource, LinearAxis, Plot, Range1d, Title
from sqlalchemy.orm import Session, sessionmaker, load_only
from sqlalchemy import create_engine
from bokeh.models import LinearAxis, Range1d, Segment, Legend
from os import getenv
from sqlalchemy import create_engine


def top_func(func):
    def wrapper(ticker: str):
        df = func(ticker)

        last = df.shape[0]
        duration = 120  # sessions
        before = last - duration
        # before = df.index[s]
        df = df.truncate(before=before, )  # only - days!
        w = 12 * 60 * 60 * 1000  # half day in ms
        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
        p = figure(tools=TOOLS, plot_height=350, sizing_mode="stretch_width",
                   title=ticker + " candlestick" + ' throught ' + str(duration) + ' sessions ')

        p.add_layout(Legend(click_policy="hide", orientation='horizontal', spacing=20), 'below')
        p.yaxis.axis_label = 'Price'
        # df.reset_index(inplace=True)
        # df.rename(columns={'index': 'date'}, inplace=True)
        low, high = df[['open', 'close']].min().min(), df[['open', 'close']].max().max()
        diff = high - low
        p.y_range = Range1d(low - 0.1 * diff, high + 0.1 * diff)
        inc = df.close > df.open
        dec = df.open > df.close
        # print(df)
        # print(pd.to_datetime(df["date"]))
        p.x_range.range_padding = 0.05

        p.xaxis.major_label_overrides = {
            i: date.strftime('%b %d') for i, date in enumerate((df["date"]), start=before)
        }
        # print(df)
        # print('============', inc)
        p.xaxis.bounds = (before, last)
        p.segment(df.index, df.high, df.index, df.low, color="black", legend_label='Candlestick')
        p.vbar(df.index[inc], 0.5, df.open[inc], df.close[inc],
               fill_color="#00FF5E", line_color="black", legend_label='Candlestick')
        p.vbar(df.index[dec], 0.5, df.open[dec], df.close[dec],
               fill_color="#F2583E", line_color="black", legend_label='Candlestick')
        # right y axis
        p.extra_y_ranges.update({'two': Range1d(0, 1.1 * df.volume.max())})
        p.add_layout(LinearAxis(y_range_name='two', axis_label='Volume'), 'right')
        p.vbar(df.index, 0.5, df.volume, [0] * df.shape[0], alpha=0.5, level='underlay',
               legend_label='Volume', y_range_name='two')
        return p
        # last = df.index[-1]
        # duration = 90 #sessions
        # before = last - duration
        # df = df.truncate(before=before,after=last) #only - days!
        # df["date"] = pd.to_datetime(df["date"])
        # inc = df.close > df.open
        # dec = df.open > df.close
        # w = 12 * 60 * 60 * 1000  # half day in ms
        # TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
        # p = figure( tools=TOOLS, plot_height=350,sizing_mode="stretch_width", title=ticker + " candlestick"+' throught ' + str(duration) +' sessions ')
        # print(pd.to_datetime(df["date"]))
        # p.add_layout(LinearAxis(), 'right')
        # print('before',before,last)
        # p.xaxis.major_label_overrides = {
        #     i: date.strftime('%b %d') for i, date in enumerate(pd.to_datetime(df["date"]),start=before)
        # }
        # p.xaxis.bounds = (before, last)
        # p.x_range.range_padding = 0.05
        # p.segment(df.index, df.high, df.index, df.low, color="black")
        # p.vbar(df.index[inc], 0.5, df.open[inc], df.close[inc], fill_color="#00FF5E", line_color="black")
        # p.vbar(df.index[dec], 0.5, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")
        # p.extra_y_ranges.update({'two': Range1d(0, 1.1 * df.volume.max())})
        # p.xaxis.axis_label = 'Date'
        # p.yaxis.axis_label = 'Price ($)'
        # return p

    return wrapper


@top_func
def get_data_for_plotting_wrap(ticker: str):
    engine = create_engine(getenv("SQLALCHEMY_DATABASE_URI"))
    if type(ticker) is str:
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
