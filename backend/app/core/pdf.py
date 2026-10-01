"""PDF de texto (A4, Helvetica), sem dependencias externas: uma pagina ou texto corrido paginado."""

import textwrap
import unicodedata


def render_text_pdf(title: str, lines: list[str], *, title_size: int = 26, body_size: int = 13, leading: int = 32) -> bytes:
    stream_lines = ["BT", f"/F1 {title_size} Tf", "72 750 Td", f"({pdf_text(title)}) Tj", f"/F1 {body_size} Tf", "0 -54 Td"]
    for line in lines:
        stream_lines.append(f"({pdf_text(line)}) Tj")
        stream_lines.append(f"0 -{leading} Td")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("ascii")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    return _assemble(objects)


def pdf_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return normalized.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def render_paged_pdf(title: str, paragraphs: list[str], footer: list[str], *, width: int = 88) -> bytes:
    """PDF de texto corrido em varias paginas (A4, Helvetica 11): titulo na primeira, quebra de linha por palavras."""
    lines: list[str] = []
    for paragraph in paragraphs:
        lines.extend(textwrap.wrap(paragraph, width=width) or [""])
        lines.append("")
    lines.extend(footer)
    first_page, other_pages = 44, 48
    pages = [lines[:first_page]]
    rest = lines[first_page:]
    while rest:
        pages.append(rest[:other_pages])
        rest = rest[other_pages:]

    streams = []
    for index, page_lines in enumerate(pages):
        ops = ["BT", "/F1 11 Tf", "72 770 Td"]
        if index == 0:
            ops[1:3] = ["/F1 16 Tf", "72 770 Td"]
            ops += [f"({pdf_text(title)}) Tj", "/F1 11 Tf", "0 -30 Td"]
        for line in page_lines:
            ops += [f"({pdf_text(line)}) Tj", "0 -15 Td"]
        ops += ["/F1 9 Tf", "0 -15 Td", f"(Pagina {index + 1} de {len(pages)}) Tj", "ET"]
        streams.append("\n".join(ops).encode("ascii"))

    # Objetos: 1 catalogo, 2 paginas, 3 fonte, depois (pagina, conteudo) para cada pagina.
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(len(pages)))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("ascii"),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    for i, stream in enumerate(streams):
        content_ref = 5 + 2 * i
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_ref} 0 R >>".encode("ascii")
        )
        objects.append(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
    return _assemble(objects)


def _assemble(objects: list[bytes]) -> bytes:
    body = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{index} 0 obj\n".encode("ascii"))
        body.extend(obj)
        body.extend(b"\nendobj\n")
    xref_offset = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    body.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        body.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    body.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    return bytes(body)
