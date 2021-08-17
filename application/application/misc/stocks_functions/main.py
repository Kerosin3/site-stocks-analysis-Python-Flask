from application.models.db_stocks import Stock_obj,Stock_data,Prices_tracking
from application.models.database import db
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker,load_only
engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')



def create_stock_obj(ticker:str,
                     Session=sessionmaker(engine)):
    checker = db.session.query(Stock_obj).filter(Stock_obj.ticker == ticker).one_or_none()
    id = None
    if checker is not None: # exists
        return 0
    with Session() as session:
        out = Stock_obj()
        out.ticker = ticker
        data = Stock_data()
        session.add(out)
        session.flush()
        session.refresh(out)
        id = out.id
        # session.commit()
        data.Stock_obj_id = out.id
        session.add(data)
        session.commit()
        print('creating................',id)
    return id

def create_track_price_object(ticker:str,id:int,Session=sessionmaker(engine)):
    with Session() as session:
        check = session.query(Prices_tracking). \
            filter(Prices_tracking.ticker == ticker).one_or_none()
        #already exists
        if check is not None:
            return None
        else:
            p0 = Prices_tracking()
            p0.ticker = ticker
            p0.user_related = id
            session.add(p0)
            session.flush()
            session.refresh(p0)
            id_out = p0.user_related
            session.commit()
            return id_out
