from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///sheets.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database table creation (only run once)
#from models import Base
#Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
