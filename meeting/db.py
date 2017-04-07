from sqlalchemy import create_engine
from meeting import config
from sqlalchemy.orm import sessionmaker


from sqlalchemy_utils.functions import create_database, database_exists
if not database_exists(config.sqlalchemy_url):
    create_database(config.sqlalchemy_url)


engine = create_engine(config.sqlalchemy_url, echo=False)

Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    chat_id = Column(Integer)
    username = Column(String(50))
    first_name = Column(String(30))
    last_name = Column(String(30))
    mobile = Column(String(16))
    province = Column(String(32))
    city = Column(String(32))
    register_date = Column(Integer)
    last_update = Column(Integer)
    comment = Column(String(1024))
    gender = Column(String(6))
    state = Column(String(10))


Base.metadata.create_all(engine)

