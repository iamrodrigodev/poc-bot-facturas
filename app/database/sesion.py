from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.ajustes import ajustes


motor = create_engine(
    ajustes.crear_url_sqlalchemy(),
    pool_pre_ping=True,
    use_setinputsizes=False,
)

crear_sesion = sessionmaker(
    bind=motor,
    autoflush=False,
    expire_on_commit=False,
)
