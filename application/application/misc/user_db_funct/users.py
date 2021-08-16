from application.models.users import Users
from sqlalchemy.orm import Session,sessionmaker,load_only
from sqlalchemy import create_engine

engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')

def create_user(username:str,
                password:str='somepassword'):
    Session = sessionmaker(engine)
    with Session() as session:
        id = None
        user_to_create = session.query(Users). \
            filter(Users.username == username).one_or_none()
        if user_to_create == None:
            user0 = Users()
            user0.username = username
            user0.password = password
            session.add(user0)
            session.flush()
            session.refresh(user0)
            id = user0.id
            session.commit()
            return id
        else:
            return None

