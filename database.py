from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

DATABASE_URL = "sqlite:///database.db"

# engine = create_engine(DATABASE_URL)
# Base.metadata.create_all(engine)

# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://rupesh:fyndtest123@rupesh.mysql.pythonanywhere-services.com/rupesh$fynd'
SQLALCHEMY_DATABASE_URI_LOCAL = 'mysql+pymysql://root:@localhost/ecommerce'

engine=create_engine(SQLALCHEMY_DATABASE_URI_LOCAL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)
session = Session()