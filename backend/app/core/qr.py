"""Conteudo dos QR de retirada: prefixo do tipo + codigo (o leitor aceita o QR lido ou so o codigo digitado)."""


def qr_payload(prefix: str, code: str) -> str:
    return f"{prefix}{code}"


def code_from_scan(prefix: str, value: str) -> str:
    value = value.strip()
    return value[len(prefix):] if value.startswith(prefix) else value
