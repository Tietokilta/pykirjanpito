import logging
from configuration import configuration
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db = create_engine(configuration['database'], echo=False)
Base = declarative_base()
db.session = sessionmaker(bind=db)()

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)