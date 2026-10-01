"""Rotulos em portugues usados nos avisos dos requisitos de conclusao."""

from app.models.completion import ReviewStatus

REVIEW_LABELS = {
    ReviewStatus.submitted: "em análise",
    ReviewStatus.approved: "aprovada",
    ReviewStatus.rejected: "não aprovada",
}
