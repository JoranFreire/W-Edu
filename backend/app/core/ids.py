"""Identificadores das entidades: UUID versao 7 (RFC 9562).

Os primeiros 48 bits sao o instante em milissegundos, entao os ids crescem com o tempo:
indexam bem (sem a fragmentacao do UUID aleatorio) e ordenar por id ainda segue a criacao.
Os 12 bits seguintes sao um contador (metodo 1 da RFC): ids gerados no mesmo milissegundo
tambem saem em ordem crescente, como um id sequencial. O restante e aleatorio, entao o id
nao revela volume nem permite adivinhar o vizinho.
"""

import os
import threading
import time
import uuid

from sqlalchemy import Uuid
from sqlalchemy.types import TypeDecorator

_COUNTER_BITS = 12
_RANDOM_BITS = 62
_MILLIS_MASK = (1 << 48) - 1

_lock = threading.Lock()
_last_millis = 0
_counter = 0


def _next_slot() -> tuple[int, int]:
    """Instante e contador do proximo id: mesmo milissegundo incrementa o contador; se esgotar, avanca 1 ms."""
    global _last_millis, _counter
    with _lock:
        millis = time.time_ns() // 1_000_000
        if millis > _last_millis:
            _last_millis = millis
            # Comeca na metade inferior para sobrar espaco ao incrementar no mesmo milissegundo.
            _counter = int.from_bytes(os.urandom(2), "big") & ((1 << (_COUNTER_BITS - 1)) - 1)
        else:
            _counter += 1
            if _counter >= 1 << _COUNTER_BITS:
                _last_millis += 1
                _counter = 0
        return _last_millis & _MILLIS_MASK, _counter


def new_id() -> uuid.UUID:
    millis, counter = _next_slot()
    rand_b = int.from_bytes(os.urandom(8), "big") & ((1 << _RANDOM_BITS) - 1)
    value = millis << 80 | 0x7 << 76 | counter << 64 | 0b10 << 62 | rand_b
    return uuid.UUID(int=value)


def parse_id(value: str | uuid.UUID | None) -> uuid.UUID | None:
    """Id vindo de texto (token, cabecalho, consulta); valor que nao e UUID vira None."""
    if value is None or isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


class IdType(TypeDecorator):
    """Coluna de id (UUID nativo no PostgreSQL); aceita o id tambem em texto, como chega da API ou de JSON."""

    impl = Uuid
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None or isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
