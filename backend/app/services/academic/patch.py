from pydantic import BaseModel


def apply_patch(entity: object, data: BaseModel, clearable: frozenset[str] = frozenset()) -> None:
    """Aplica so os campos enviados; ``null`` limpa apenas os campos opcionais listados."""
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None and field not in clearable:
            continue
        setattr(entity, field, value)
