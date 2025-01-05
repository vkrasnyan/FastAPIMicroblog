from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from blogapp.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine('postgresql+psycopg2://vickie:newpassword@localhost/microblog', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
