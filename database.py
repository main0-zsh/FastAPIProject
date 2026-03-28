import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

engine = sa.create_engine("sqlite:///./feedback.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)