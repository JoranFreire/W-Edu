import json
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings
from app.core.ids import IdType


def _json_default(value):
    # Ids (UUID) dentro de colunas JSON (payload de avisos, detalhes de movimentacoes) viram texto.
    if isinstance(value, UUID):
        return str(value)
    raise TypeError(f"Tipo nao serializavel em JSON: {type(value).__name__}")


def json_serializer(value) -> str:
    return json.dumps(value, default=_json_default)


def _engine_options(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"json_serializer": json_serializer}
    return {
        "json_serializer": json_serializer,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT_SECONDS,
        "pool_recycle": settings.DB_POOL_RECYCLE_SECONDS,
        "pool_pre_ping": True,
    }


engine = create_engine(settings.DATABASE_URL, **_engine_options(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    # Toda coluna anotada como UUID (ids e chaves estrangeiras) usa o tipo que aceita o id tambem em texto.
    type_annotation_map = {UUID: IdType}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
