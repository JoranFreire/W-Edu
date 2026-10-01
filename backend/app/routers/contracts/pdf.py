from fastapi.responses import Response

from app.models.contracts import EnrollmentContract


def pdf_response(contract: EnrollmentContract, content: bytes) -> Response:
    filename = f"contrato_{contract.validation_code}.pdf"
    return Response(content, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}"'})
