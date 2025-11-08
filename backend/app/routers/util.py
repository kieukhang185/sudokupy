# api/app/routers/util.py
from app.database import Base
from sqlalchemy.orm import Session


def ensure_tables(db: Session):
    # call this once at startup in dev, or use Alembic in prod
    engine = db.get_bind()
    Base.metadata.create_all(engine)
