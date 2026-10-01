"""O responsavel so acessa dados dos alunos vinculados a ele."""

from fastapi import HTTPException, status

from app.models.guardians import StudentGuardian


def ensure_linked(link: StudentGuardian | None) -> StudentGuardian:
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não vinculado a este responsável")
    return link


def ensure_financial(link: StudentGuardian) -> None:
    if not link.is_financial:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o responsável financeiro vê as cobranças")
