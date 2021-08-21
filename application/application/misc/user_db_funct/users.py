from application.models.users import Users
from sqlalchemy.orm import Session,sessionmaker,load_only
from sqlalchemy import create_engine
from application.models.database import engine
# engine = create_engine('postgresql://USER:PASSWORD@localhost:5432/APPLICATION_DB')

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
            print('Created user')
            return id
        else:
            return None

def get_user(username:str='some',id=None):
    Session = sessionmaker(engine)
    if id is not None:
        if type(id) is int:
            with Session() as session:
                User = session.query(Users). \
                    filter(Users.id == id).one_or_none()
                return User
        else:
            return None
    with Session() as session:
        User = session.query(Users). \
            filter(Users.username == username).one_or_none()
        return User
