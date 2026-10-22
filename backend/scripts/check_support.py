"""Apoio comum dos scripts de verificacao."""

from __future__ import annotations

import os
import re
from typing import Any

import httpx
from fastapi.encoders import jsonable_encoder
from sqlalchemy.engine import make_url

# Os scripts apagam e recriam todas as tabelas: so rodam em banco descartavel. SQLite (o padrao,
# arquivo temporario) ou PostgreSQL cujo nome deixe claro que e de teste.
_DISPOSABLE = re.compile(r"(check|test|e2e|tmp|scratch)", re.IGNORECASE)


def ensure_disposable_database(url: str | None = None) -> None:
    """Recusa rodar contra um banco de verdade (ex.: o do Docker, `wedu`): os dados seriam apagados.

    Para forcar num banco especifico, `CHECK_ALLOW_DATABASE=<nome do banco>`.
    """
    parsed = make_url(url or os.environ.get("DATABASE_URL", "sqlite://"))
    if parsed.get_backend_name() == "sqlite":
        return
    name = parsed.database or ""
    if _DISPOSABLE.search(name) or os.environ.get("CHECK_ALLOW_DATABASE") == name:
        return
    raise SystemExit(
        f"Recusado: os scripts de verificacao apagam o banco '{name}'. Use um banco de teste "
        f"(nome com check, test, e2e, tmp ou scratch) ou CHECK_ALLOW_DATABASE={name} se ele for descartavel."
    )


ensure_disposable_database()


class ApiClient(httpx.AsyncClient):
    """Cliente de teste que aceita ids UUID (e datas) no corpo JSON, como o frontend os envia em texto."""

    async def request(self, method: str, url: Any, *args: Any, json: Any = None, **kwargs: Any) -> httpx.Response:
        if json is not None:
            json = jsonable_encoder(json)
        return await super().request(method, url, *args, json=json, **kwargs)

# Id valido (UUID versao 7) que nao existe em nenhuma tabela: testa respostas 404.
MISSING_ID = "00000000-0000-7000-8000-000000000000"
