"""Regras do almoxarifado (funcoes puras): saldo, pendencias de devolucao e situacao da requisicao."""

from app.models.warehouse import MaterialKind, MaterialRequestLine


def outstanding(line: MaterialRequestLine) -> int:
    """Permanentes ainda fora do almoxarifado (entregues, nao devolvidos nem baixados)."""
    if line.item.kind != MaterialKind.durable:
        return 0
    return line.quantity_delivered - line.quantity_returned - line.quantity_lost


def available(received: int, delivered: int, returned: int) -> int:
    """Saldo no almoxarifado: o que entrou menos o que saiu, mais o que voltou (perdas nao voltam)."""
    return received - delivered + returned


def validate_return(line: MaterialRequestLine, returned: int, lost: int) -> str | None:
    if line.item.kind != MaterialKind.durable and (returned or lost):
        return f"{line.item.name} é material de consumo e não tem devolução"
    if returned + lost > outstanding(line):
        return f"{line.item.name}: devolução acima do que está emprestado ({outstanding(line)})"
    return None
