import os
from sqlalchemy import Table, create_engine, MetaData
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine(os.environ['DATATBASE_URL'])
metadata = MetaData(bind=engine)


class Addresses(Base):
    __table__ = Table('addresses', metadata, autoload=True)
