from pathlib import Path
import re
import shutil
import uuid

from fastapi import UploadFile

from app.core.config import settings


def documents_storage_dir() -> Path:
    path = Path(settings.DOCUMENTS_STORAGE_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def certificates_storage_dir() -> Path:
    path = Path(settings.CERTIFICATES_STORAGE_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def assignments_storage_dir() -> Path:
    path = Path(settings.ASSIGNMENTS_STORAGE_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _sanitize_filename(filename: str) -> str:
    stem = Path(filename).stem
    suffix = Path(filename).suffix.lower()
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-") or "document"
    return f"{safe_stem}{suffix}"


def store_uploaded_document(document_id: int, version_number: int, upload: UploadFile) -> tuple[str, int]:
    base_dir = documents_storage_dir() / str(document_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _sanitize_filename(upload.filename or "document")
    unique_name = f"v{version_number}_{uuid.uuid4().hex}_{safe_name}"
    target_path = base_dir / unique_name
    with target_path.open("wb") as handle:
        shutil.copyfileobj(upload.file, handle)
    size = target_path.stat().st_size
    return str(target_path), size


def store_generated_document(document_id: int, version_number: int, filename: str, content: bytes) -> tuple[str, int]:
    """Grava no GED um arquivo gerado pelo sistema (ex.: PDF de contrato)."""
    base_dir = documents_storage_dir() / str(document_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    target_path = base_dir / f"v{version_number}_{uuid.uuid4().hex}_{_sanitize_filename(filename)}"
    target_path.write_bytes(content)
    return str(target_path), len(content)


ADMISSION_DOCUMENT_TYPES = {".pdf", ".jpg", ".jpeg", ".png"}
ADMISSION_DOCUMENT_MAX_BYTES = 10 * 1024 * 1024


def store_admission_document(application_id: int, upload: UploadFile) -> tuple[str, str, int]:
    """Comprovante do candidato (PDF ou imagem, ate 10 MB) em documents/admissions/<inscricao>."""
    safe_name = _sanitize_filename(upload.filename or "comprovante")
    if Path(safe_name).suffix.lower() not in ADMISSION_DOCUMENT_TYPES:
        raise ValueError("Envie PDF, JPG ou PNG")
    base_dir = documents_storage_dir() / "admissions" / str(application_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    target_path = base_dir / f"{uuid.uuid4().hex}_{safe_name}"
    with target_path.open("wb") as handle:
        shutil.copyfileobj(upload.file, handle)
    size = target_path.stat().st_size
    if size > ADMISSION_DOCUMENT_MAX_BYTES:
        target_path.unlink()
        raise ValueError("Arquivo maior que 10 MB")
    return str(target_path), safe_name, size


def store_assignment_file(submission_id: int, upload: UploadFile) -> tuple[str, str, int]:
    base_dir = assignments_storage_dir() / str(submission_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _sanitize_filename(upload.filename or "submission")
    target_path = base_dir / f"{uuid.uuid4().hex}_{safe_name}"
    with target_path.open("wb") as handle:
        shutil.copyfileobj(upload.file, handle)
    return str(target_path), safe_name, target_path.stat().st_size
