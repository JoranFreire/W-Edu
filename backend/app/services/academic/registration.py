"""Formato do numero de matricula: ano de ingresso + codigo do programa + sequencial."""

import re


def registration_prefix(year: int, program_code: str) -> str:
    return f"{year}{re.sub(r'[^A-Z0-9]', '', program_code.upper())}"


def registration_number(prefix: str, sequence: int) -> str:
    return f"{prefix}{sequence:04d}"
