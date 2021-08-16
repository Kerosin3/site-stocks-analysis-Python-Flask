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
        return None
    with Session() as session:
        out = Stock_obj()
        out.ticker = ticker
        data = Stock_data()
        # db.session.flush()
        # db.session.refresh(out)
        id = out.id
        session.add(out)
        session.commit()
        data.Stock_obj_id = out.id
        session.add(data)
        session.commit()
    return id
