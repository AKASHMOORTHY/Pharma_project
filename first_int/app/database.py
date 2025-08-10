from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
 
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:12345@localhost:5432/pharma_db"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:12345@localhost:5432/new_pharma_db" 

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


"""  
# cd "C:\Program Files\PostgreSQL\17\bin"
# psql -U postgres -h localhost -p 5432 
# CREATE DATABASE pharma_db;    # after this we get the msg "CREATE DATABASE"
# \q   #to exit the psql
# alembic init alembic
# change the sqlalchemy.url in alembic.ini file to the new database name i.e(sqlalchemy.url = postgresql://postgres:12345@localhost:5432/new_pharma_db)
# alembic revision --autogenerate -m "create tables"
# alembic upgrade head
"""