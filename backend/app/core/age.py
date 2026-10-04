"""Idade a partir da data de nascimento (regra pura, sem banco)."""

from datetime import date

ADULT_AGE = 18
# Relativamente incapaz (Codigo Civil, art. 4o): a partir dos 16 a pessoa decide sozinha o uso do
# proprio rosto para login e catraca; abaixo disso, quem decide e o responsavel.
SELF_CONSENT_AGE = 16


def age_on(birth_date: date, day: date) -> int:
    had_birthday = (day.month, day.day) >= (birth_date.month, birth_date.day)
    return day.year - birth_date.year - (0 if had_birthday else 1)


def is_adult(birth_date: date | None, today: date | None = None) -> bool:
    """Sem data de nascimento, a pessoa nao e tida como adulta (o reconhecimento facial
    para presenca exige maioridade comprovada)."""
    if birth_date is None:
        return False
    return age_on(birth_date, today or date.today()) >= ADULT_AGE


def is_16_or_older(birth_date: date | None, today: date | None = None) -> bool:
    """Sem data de nascimento, a pessoa e tratada como menor de 16 (o responsavel decide)."""
    if birth_date is None:
        return False
    return age_on(birth_date, today or date.today()) >= SELF_CONSENT_AGE
