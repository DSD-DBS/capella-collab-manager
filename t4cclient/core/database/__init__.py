import pathlib

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from t4cclient import config
from t4cclient.core.database import users
from t4cclient.schemas.repositories.users import Role

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_db():
    root_dir = pathlib.Path(__file__).parents[2]

    # Get current revision of Database. If no revision is available, initialize the database.
    alembic_cfg = Config(root_dir / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(root_dir / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", config.DATABASE_URL)
    alembic_cfg.attributes["configure_logger"] = False

    engine = create_engine(config.DATABASE_URL)
    conn = engine.connect()

    context = MigrationContext.configure(conn)
    current_rev = context.get_current_revision()

    if current_rev:
        command.upgrade(alembic_cfg, "head")
    else:
        Base.metadata.create_all(bind=engine)
        command.stamp(alembic_cfg, "head")
        initialize_admin_user()


def initialize_admin_user():
    with SessionLocal() as db:
        users.create_user(db=db, username=config.INITIAL_ADMIN_USER, role=Role.ADMIN)
