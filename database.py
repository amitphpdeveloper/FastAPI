from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



#SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
#engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
#engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/sampledb')
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:password123@localhost:5432/TodoApplicationDatabase'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()