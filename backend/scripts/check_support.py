"""Apoio comum dos scripts de verificacao."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi.encoders import jsonable_encoder


class ApiClient(httpx.AsyncClient):
    """Cliente de teste que aceita ids UUID (e datas) no corpo JSON, como o frontend os envia em texto."""

    async def request(self, method: str, url: Any, *args: Any, json: Any = None, **kwargs: Any) -> httpx.Response:
        if json is not None:
            json = jsonable_encoder(json)
        return await super().request(method, url, *args, json=json, **kwargs)

# Id valido (UUID versao 7) que nao existe em nenhuma tabela: testa respostas 404.
MISSING_ID = "00000000-0000-7000-8000-000000000000"
