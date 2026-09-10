import io
import re
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from fpdf import FPDF
from fpdf.fonts import FontFace

from memo_charts import chart_pngs

_MD_HEADING = re.compile(r"^(#{1,4})\s+(.*)$")
_MD_UL = re.compile(r"^[-*+]\s+(.*)$")
_MD_OL = re.compile(r"^(\d+)[.)]\s+(.*)$")
_MD_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_MD_TABLE_DIV = re.compile(r"^\s*\|?\s*:?-{3,}")
_MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_MD_HR = re.compile(r"^\s*-{3,}\s*$")
_FIELD_LINE = re.compile(r"^\*{0,2}[A-Za-z][^*:]{0,40}:\*{0,2}\s+\S")
_NUMERIC = re.compile(r"^(Rs\s*)?-?\d", re.I)
_COVER_HEAD = re.compile(r"^\d+[.)]?\s*cover\b", re.I)
_FINANCIAL_HEAD = re.compile(r"financial", re.I)
_REC_HEAD = re.compile(r"recommendation", re.I)

NAVY = (20, 35, 55)
INK = (28, 28, 28)
MUTED = (90, 96, 104)
LINE = (210, 214, 220)
RULE = (180, 186, 194)
PAPER = (255, 255, 255)
HEAD_FILL = (236, 239, 243)
ZEBRA = (248, 249, 251)
ADVANCE = (6, 95, 70)
CAUTION = (146, 86, 12)
DECLINE = (153, 27, 27)
ADVANCE_BG = (236, 247, 241)
CAUTION_BG = (255, 248, 235)
DECLINE_BG = (253, 242, 242)
QUOTE_BG = (245, 247, 250)
NEWS = (120, 90, 40)

_FONT_PACKS = [
    (
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold Italic.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
    ),
    (
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    ),
]


def memo_filename(company_name: str, fmt: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", company_name or "").strip("-")
    if not slug:
        slug = "credit-memo"
    return f"{slug}-credit-memo.{fmt}"


def _split_identity(company_name: str) -> tuple[str, str]:
    raw = (company_name or "Credit memo").strip()
    match = re.search(r"^(.*?)\s*\(\s*CIN\s*([^)]+)\)\s*$", raw, re.I)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return raw, ""


def _pdf_safe(text: str, unicode_ok: bool) -> str:
    converted = (text or "").replace("₹", "Rs ")
    if unicode_ok:
        return converted
    return (
        converted.replace("–", "-")
        .replace("—", "-")
        .replace("•", "-")
        .replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def _plain(text: str) -> str:
    converted = _MD_LINK.sub(r"\1", text or "")
    converted = re.sub(r"^>\s*", "", converted)
    return re.sub(r"[*_`]", "", converted)


def _keep_md(text: str) -> str:
    """Keep bold/italic/links for fpdf2 markdown; drop raw asterisk noise."""
    converted = text or ""
    converted = re.sub(r"^>\s*", "", converted)
    converted = converted.replace("`", "")
    return converted


def _soft_wrap(text: str, every: int = 88) -> str:
    parts = []
    for token in (text or "").split(" "):
        if len(token) <= every:
            parts.append(token)
            continue
        parts.append(" ".join(token[i : i + every] for i in range(0, len(token), every)))
    return " ".join(parts)


def _clean_heading(text: str) -> str:
    cleaned = _plain(text)
    cleaned = re.sub(r"^\d+[.)]\s+", "", cleaned)
    cleaned = re.sub(r"\s*\(\d+\s*[–-]\s*\d+\s*lines?\)", "", cleaned, flags=re.I)
    return cleaned.strip(" -—")


def _iter_blocks(markdown: str):
    lines = (markdown or "").replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if _MD_HR.match(stripped):
            yield ("hr",)
            i += 1
            continue
        heading = _MD_HEADING.match(line)
        if heading:
            yield ("h", len(heading.group(1)), heading.group(2).strip())
            i += 1
            continue
        if stripped.startswith(">"):
            quotes = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quotes.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            yield ("quote", " ".join(quotes))
            continue
        if _MD_TABLE_ROW.match(line):
            rows = []
            while i < len(lines) and _MD_TABLE_ROW.match(lines[i]):
                raw = _MD_TABLE_ROW.match(lines[i]).group(1)
                cells = [cell.strip() for cell in raw.split("|")]
                if not _MD_TABLE_DIV.match(lines[i]):
                    rows.append(cells)
                i += 1
            if rows:
                yield ("table", rows)
            continue
        ul = _MD_UL.match(line)
        if ul:
            items = []
            while i < len(lines):
                match = _MD_UL.match(lines[i])
                if not match:
                    break
                items.append(match.group(1).strip())
                i += 1
            yield ("ul", items)
            continue
        ol = _MD_OL.match(line)
        if ol:
            items = []
            while i < len(lines):
                match = _MD_OL.match(lines[i])
                if not match:
                    break
                items.append(match.group(2).strip())
                i += 1
            yield ("ol", items)
            continue
        if _FIELD_LINE.match(stripped):
            yield ("p", stripped)
            i += 1
            continue
        para = [stripped]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not _MD_HEADING.match(lines[i])
            and not _MD_UL.match(lines[i])
            and not _MD_OL.match(lines[i])
            and not _MD_TABLE_ROW.match(lines[i])
            and not lines[i].strip().startswith(">")
            and not _MD_HR.match(lines[i].strip())
        ):
            para.append(lines[i].strip())
            i += 1
        yield ("p", " ".join(para))


def _font_pack():
    for paths in _FONT_PACKS:
        if all(Path(path).exists() for path in paths[:6]):
            resolved = []
            for path in paths:
                resolved.append(path if Path(path).exists() else None)
            for idx, fallback in ((3, 1), (2, 0), (7, 5), (6, 4)):
                if resolved[idx] is None:
                    resolved[idx] = resolved[fallback]
            return tuple(resolved)
    return None


def _looks_numeric(text: str) -> bool:
    return bool(_NUMERIC.match(_plain(text).replace(",", "").strip()))


def _section_tone(text: str, previous: str | None = None) -> str | None:
    label = _clean_heading(text).lower()
    if "strength" in label and "red flag" in label:
        return None
    if any(key in label for key in ("red flag", "watch item")):
        return "risk"
    if re.search(r"\brisks?\b", label) and "financial" not in label:
        return "risk"
    if "strength" in label:
        return "strength"
    if "recommend" in label:
        return "rec"
    if any(key in label for key in ("legal", "nclt", "litigation", "insolvency")):
        return "risk"
    if "news" in label:
        return "news"
    if label in {"cover", "executive summary", "financial position", "figures"}:
        return None
    return previous


def _tone_accent(tone: str | None) -> tuple[int, int, int]:
    if tone == "risk":
        return DECLINE
    if tone == "strength":
        return ADVANCE
    if tone == "rec":
        return ADVANCE
    if tone == "news":
        return NEWS
    return NAVY


def _tone_colors(label: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    upper = (label or "").upper()
    if "DECLINE" in upper or "REJECT" in upper:
        return DECLINE, DECLINE_BG
    if "CAUTION" in upper or "WATCH" in upper:
        return CAUTION, CAUTION_BG
    return ADVANCE, ADVANCE_BG
    upper = (label or "").upper()
    if "DECLINE" in upper or "REJECT" in upper:
        return DECLINE, DECLINE_BG
    if "CAUTION" in upper or "WATCH" in upper:
        return CAUTION, CAUTION_BG
    return ADVANCE, ADVANCE_BG


class _MemoPdf(FPDF):
    def __init__(self, company_name: str):
        super().__init__(format="A4")
        self.company_name, self.cin = _split_identity(company_name)
        self.short_name = self.company_name[:48]
        now = datetime.now(timezone.utc)
        self.as_of = now.date().isoformat()
        self.as_of_long = now.strftime("%d %B %Y").lstrip("0")
        self.unicode_ok = False
        self.serif = "Times"
        self.sans = "Helvetica"
        pack = _font_pack()
        if pack:
            self.unicode_ok = True
            self.serif = "KuberSerif"
            self.sans = "KuberSans"
            self.add_font("KuberSerif", "", pack[0])
            self.add_font("KuberSerif", "B", pack[1])
            self.add_font("KuberSerif", "I", pack[2])
            self.add_font("KuberSerif", "BI", pack[3])
            self.add_font("KuberSans", "", pack[4])
            self.add_font("KuberSans", "B", pack[5])
            self.add_font("KuberSans", "I", pack[6])
            self.add_font("KuberSans", "BI", pack[7])
        self.set_margins(18, 18, 18)
        self.set_auto_page_break(auto=True, margin=16)

    def header(self):
        self.set_fill_color(*PAPER)
        self.rect(0, 0, self.w, self.h, "F")
        self.set_fill_color(*NAVY)
        self.rect(0, 0, self.w, 2.6, "F")
        self.set_xy(18, 6)
        self.set_font(self.sans, "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(110, 5, "KUBER  |  CREDIT COMMITTEE MEMORANDUM")
        self.set_font(self.sans, "B", 7.5)
        self.set_text_color(*NAVY)
        self.cell(0, 5, "CONFIDENTIAL", align="R")
        self.set_draw_color(*LINE)
        self.set_line_width(0.25)
        self.line(18, 13, self.w - 18, 13)
        self.set_fill_color(*PAPER)
        self.set_text_color(*INK)
        self.set_draw_color(*RULE)
        self.set_line_width(0.25)
        self.set_y(16)

    def footer(self):
        self.set_draw_color(*LINE)
        self.set_line_width(0.25)
        self.line(self.l_margin, self.h - 12, self.w - self.r_margin, self.h - 12)
        self.set_y(-10)
        self.set_x(self.l_margin)
        self.set_font(self.sans, "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(self.epw / 2, 5, _pdf_safe(self.short_name, self.unicode_ok))
        self.cell(self.epw / 2, 5, f"{self.as_of_long}   |   {self.page_no()}", align="R")


def _safe(pdf: _MemoPdf, text: str) -> str:
    return _pdf_safe(text, pdf.unicode_ok)


def _reset_style(pdf: _MemoPdf):
    pdf.set_fill_color(*PAPER)
    pdf.set_text_color(*INK)
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.25)


def _write(pdf: _MemoPdf, text: str, *, size=10.5, leading=6.3, color=INK, style=""):
    pdf.set_x(pdf.l_margin)
    pdf.set_font(pdf.serif, style, size)
    pdf.set_text_color(*color)
    body = _soft_wrap(_safe(pdf, _keep_md(text)))
    if not body:
        return
    pdf.multi_cell(pdf.epw, leading, body, markdown=True)
    pdf.set_x(pdf.l_margin)


def _heading(pdf: _MemoPdf, level: int, text: str, tone: str | None = None):
    label = _clean_heading(text)
    if not label:
        return
    accent = _tone_accent(tone)
    pdf.ln(7 if level <= 2 else 4.5)
    if pdf.get_y() > pdf.page_break_trigger - 20:
        pdf.add_page()
    if level <= 2:
        y = pdf.get_y()
        pdf.set_fill_color(*accent)
        pdf.rect(pdf.l_margin, y + 0.6, 2.1, 7.4, "F")
        pdf.set_xy(pdf.l_margin + 4.5, y)
        pdf.set_font(pdf.sans, "B", 12)
        pdf.set_text_color(*accent)
        pdf.multi_cell(pdf.epw - 4.5, 7.4, _safe(pdf, label))
        pdf.set_draw_color(*accent)
        pdf.set_line_width(0.45)
        rule_y = pdf.get_y() + 0.4
        pdf.line(pdf.l_margin + 4.5, rule_y, pdf.l_margin + 44, rule_y)
        pdf.ln(4)
    else:
        pdf.set_font(pdf.serif, "B", 11.5)
        pdf.set_text_color(*accent)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 6.2, _safe(pdf, label))
        pdf.ln(1.8)
    _reset_style(pdf)


def _compact_cell(text: str, money: bool) -> str:
    plain = _plain(text)
    if not money:
        return plain
    stripped = re.sub(r"^Rs\s+", "", plain)
    stripped = re.sub(r"\s*crore\s*$", "", stripped, flags=re.I)
    return stripped


def _write_table(pdf: _MemoPdf, rows: list[list[str]]):
    if not rows:
        return
    pdf.ln(1.5)
    pdf.set_x(pdf.l_margin)
    cols = max(len(row) for row in rows)
    numeric_cols = set()
    if len(rows) > 1:
        for cidx in range(cols):
            sample = [row[cidx] for row in rows[1:] if cidx < len(row) and row[cidx]]
            if sample and sum(_looks_numeric(cell) for cell in sample) >= max(1, len(sample) * 0.55):
                numeric_cols.add(cidx)
    money = False
    body_cells = [
        _plain(row[cidx])
        for row in rows[1:]
        for cidx in numeric_cols
        if cidx < len(row) and row[cidx]
    ]
    if body_cells:
        money = sum("crore" in cell.lower() or cell.lower().startswith("rs ") for cell in body_cells) >= len(body_cells) * 0.5
    if cols == 1:
        widths = (1,)
    else:
        first = 2.2 if cols >= 5 else 1.6
        widths = (first,) + (1,) * (cols - 1)
    font_size = 8 if cols <= 6 else 7
    _reset_style(pdf)
    pdf.set_font(pdf.sans, "", font_size)
    headings_style = FontFace(emphasis="BOLD", color=NAVY, fill_color=HEAD_FILL)
    with pdf.table(
        width=pdf.epw,
        col_widths=widths,
        first_row_as_headings=True,
        line_height=4.8,
        v_align="MIDDLE",
        align="LEFT",
        borders_layout="SINGLE_TOP_LINE",
        cell_fill_color=ZEBRA,
        cell_fill_mode="EVEN_ROWS",
        headings_style=headings_style,
        padding=(1.2, 1.6, 1.2, 1.6),
    ) as table:
        for row in rows:
            padded = row + [""] * (cols - len(row))
            table_row = table.row()
            for cidx, cell in enumerate(padded):
                align = "RIGHT" if cidx in numeric_cols else "LEFT"
                style = None
                display = _safe(pdf, _compact_cell(cell, money and cidx in numeric_cols))
                stripped = display.replace(",", "").replace(" ", "")
                if cidx in numeric_cols and stripped.startswith("-") and any(ch.isdigit() for ch in stripped):
                    style = FontFace(color=DECLINE)
                table_row.cell(display, align=align, style=style)
    _reset_style(pdf)
    pdf.ln(2.5)
    pdf.set_x(pdf.l_margin)


def _list_item(pdf: _MemoPdf, marker: str, text: str, tone: str | None = None):
    if pdf.get_y() > pdf.page_break_trigger - 12:
        pdf.add_page()
    x = pdf.l_margin
    pdf.set_x(x)
    pdf.set_font(pdf.serif, "B", 10.5)
    pdf.set_text_color(*_tone_accent(tone))
    pdf.cell(8, 6.1, marker)
    pdf.set_font(pdf.serif, "", 10.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(pdf.epw - 8, 6.1, _soft_wrap(_safe(pdf, _keep_md(text))), markdown=True)
    pdf.ln(1.1)
    pdf.set_x(x)


def _quote(pdf: _MemoPdf, text: str):
    pdf.ln(2)
    y0 = pdf.get_y()
    note = _plain(text).lower().lstrip().startswith("note")
    fill = CAUTION_BG if note else QUOTE_BG
    bar = CAUTION if note else NAVY
    pdf.set_fill_color(*fill)
    pdf.set_x(pdf.l_margin)
    pdf.set_font(pdf.serif, "I", 9.5)
    pdf.set_text_color(*MUTED)
    pdf.set_x(pdf.l_margin + 6)
    pdf.multi_cell(pdf.epw - 6, 5.4, _soft_wrap(_safe(pdf, _keep_md(text))), markdown=True, fill=True)
    y1 = max(pdf.get_y(), y0 + 5)
    pdf.set_fill_color(*fill)
    pdf.rect(pdf.l_margin, y0, 6, max(5, y1 - y0), "F")
    pdf.set_fill_color(*bar)
    pdf.rect(pdf.l_margin, y0, 1.4, max(5, y1 - y0), "F")
    _reset_style(pdf)
    pdf.ln(3)
    pdf.set_x(pdf.l_margin)


def _banner(pdf: _MemoPdf, title: str, body: str):
    bar, fill = _tone_colors(title)
    pdf.ln(1)
    y0 = pdf.get_y()
    inset = 5
    pdf.set_fill_color(*fill)
    pdf.set_font(pdf.sans, "B", 8)
    pdf.set_text_color(*bar)
    pdf.set_x(pdf.l_margin + inset)
    pdf.multi_cell(pdf.epw - inset, 5.4, _safe(pdf, title.upper()), fill=True)
    if body:
        pdf.set_fill_color(*fill)
        pdf.set_x(pdf.l_margin + inset)
        pdf.set_font(pdf.serif, "", 10)
        pdf.set_text_color(*INK)
        pdf.multi_cell(
            pdf.epw - inset,
            5.3,
            _soft_wrap(_safe(pdf, _keep_md(body))),
            markdown=True,
            fill=True,
        )
    y1 = pdf.get_y()
    pdf.set_fill_color(*fill)
    pdf.rect(pdf.l_margin, y0, inset, max(6, y1 - y0), "F")
    pdf.set_fill_color(*bar)
    pdf.rect(pdf.l_margin, y0, 1.8, max(6, y1 - y0), "F")
    _reset_style(pdf)
    pdf.ln(4)
    pdf.set_x(pdf.l_margin)


def _facts_table(pdf: _MemoPdf, facts: list[tuple[str, str]]):
    if not facts:
        return
    _reset_style(pdf)
    pdf.set_font(pdf.sans, "", 9)
    headings_style = FontFace(emphasis="BOLD", color=NAVY, fill_color=HEAD_FILL)
    with pdf.table(
        width=pdf.epw,
        col_widths=(0.32, 0.68),
        first_row_as_headings=False,
        num_heading_rows=0,
        line_height=5.2,
        v_align="MIDDLE",
        borders_layout="MINIMAL",
        cell_fill_color=ZEBRA,
        cell_fill_mode="EVEN_ROWS",
        headings_style=headings_style,
        padding=(1.2, 2.0, 1.2, 2.0),
    ) as table:
        for key, value in facts:
            row = table.row()
            row.cell(_safe(pdf, key), style=FontFace(emphasis="BOLD", color=NAVY))
            row.cell(_safe(pdf, value))
    _reset_style(pdf)
    pdf.ln(3)


def _parse_cover(blocks):
    facts = []
    recommendation = ""
    rationale = ""
    cover_blocks = []
    body = []
    in_cover = False
    for kind, *rest in blocks:
        if kind == "h":
            level, text = rest[0], rest[1]
            cleaned = _clean_heading(text)
            is_cover = level <= 2 and (
                bool(_COVER_HEAD.match(text)) or cleaned.lower() == "cover"
            )
            if is_cover:
                in_cover = True
                continue
            if in_cover and level <= 2:
                in_cover = False
        if in_cover:
            cover_blocks.append((kind, *rest))
        else:
            body.append((kind, *rest))

    for kind, *rest in cover_blocks:
        if kind != "p":
            continue
        plain = _plain(rest[0])
        if _REC_HEAD.match(plain) or plain.lower().startswith("recommendation"):
            recommendation = re.sub(r"^[^:]+:\s*", "", plain, count=1).strip()
            continue
        if plain.lower().startswith("rationale"):
            rationale = re.sub(r"^[^:]+:\s*", "", plain, count=1).strip()
            continue
        if ":" in plain:
            key, value = plain.split(":", 1)
            if 1 < len(key) <= 42:
                facts.append((key.strip(), value.strip()))
                continue
        if plain:
            facts.append(("Note", plain))
    return facts, recommendation, rationale, body


def _title_block(pdf: _MemoPdf):
    pdf.set_font(pdf.serif, "B", 20)
    pdf.set_text_color(*NAVY)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(pdf.epw, 8.5, _safe(pdf, pdf.company_name))
    if pdf.cin:
        pdf.set_font(pdf.sans, "", 9)
        pdf.set_text_color(*MUTED)
        pdf.set_x(pdf.l_margin)
        pdf.cell(pdf.epw, 5, f"CIN  {pdf.cin}")
        pdf.ln(6)
    else:
        pdf.ln(3)
    pdf.set_font(pdf.sans, "", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.set_x(pdf.l_margin)
    pdf.cell(pdf.epw / 2, 5, f"Prepared  {pdf.as_of_long}")
    pdf.cell(pdf.epw / 2, 5, "Internal credit use only", align="R")
    pdf.ln(8)
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.6)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 36, pdf.get_y())
    pdf.ln(5)


def _draw_figures(pdf: _MemoPdf, chart_sets: list[dict]):
    images = []
    for charts in chart_sets or []:
        for caption, png in chart_pngs(charts):
            images.append((caption, png))
    if not images:
        return
    _heading(pdf, 2, "Figures")
    _write(
        pdf,
        "Standalone filings. Values in Rs crore unless the axis says otherwise.",
        size=9,
        leading=5,
        color=MUTED,
        style="I",
    )
    pdf.ln(2)
    gap = 4
    width = (pdf.epw - gap) / 2
    height = width * 0.48
    idx = 0
    while idx < len(images):
        needed = height + 14
        if pdf.get_y() + needed > pdf.page_break_trigger:
            pdf.add_page()
        y = pdf.get_y()
        for col in range(2):
            if idx >= len(images):
                break
            caption, png = images[idx]
            x = pdf.l_margin + col * (width + gap)
            pdf.set_xy(x, y)
            pdf.set_font(pdf.sans, "B", 8)
            pdf.set_text_color(*NAVY)
            pdf.cell(width, 4.5, _safe(pdf, caption))
            pdf.image(io.BytesIO(png), x=x, y=y + 5.5, w=width, h=height)
            idx += 1
        pdf.set_xy(pdf.l_margin, y + height + 10)


def render_pdf(markdown: str, chart_sets: list[dict], company_name: str) -> bytes:
    pdf = _MemoPdf(company_name)
    pdf.add_page()
    _title_block(pdf)

    blocks = list(_iter_blocks(markdown))
    facts, recommendation, rationale, body = _parse_cover(blocks)
    if facts:
        _facts_table(pdf, facts[:8])
    if recommendation:
        _banner(pdf, f"Recommendation  —  {recommendation.split('(')[0].strip()}", rationale or recommendation)

    first_title = True
    pending_figures = False
    figures_drawn = False
    tone = None
    for kind, *rest in body:
        if kind == "h":
            level, text = rest[0], rest[1]
            cleaned = _clean_heading(text)
            if first_title and level == 1 and (
                cleaned.lower() == "cover"
                or cleaned.lower() in pdf.company_name.lower()
            ):
                first_title = False
                continue
            first_title = False
            if pending_figures and level <= 2 and not figures_drawn:
                _draw_figures(pdf, chart_sets)
                figures_drawn = True
                pending_figures = False
            tone = _section_tone(text, None if level <= 2 else tone)
            _heading(pdf, level, text, tone)
            if level <= 2 and _FINANCIAL_HEAD.search(cleaned):
                pending_figures = True
        elif kind == "p":
            _write(pdf, rest[0])
            pdf.ln(3.4)
        elif kind == "quote":
            _quote(pdf, rest[0])
        elif kind == "hr":
            pdf.ln(2)
            pdf.set_draw_color(*LINE)
            pdf.set_line_width(0.2)
            y = pdf.get_y()
            pdf.line(pdf.l_margin, y, pdf.l_margin + pdf.epw, y)
            pdf.ln(4)
        elif kind == "ul":
            for item in rest[0]:
                _list_item(pdf, "•" if pdf.unicode_ok else "-", item, tone)
            pdf.ln(2.8)
        elif kind == "ol":
            for idx, item in enumerate(rest[0], start=1):
                _list_item(pdf, f"{idx}.", item, tone)
            pdf.ln(2.8)
        elif kind == "table":
            if rest[0]:
                _write_table(pdf, rest[0])

    if not figures_drawn:
        _draw_figures(pdf, chart_sets)

    return bytes(pdf.output())


def _shade_cell(cell, hex_color: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    for child in list(tc_pr):
        if child.tag == qn("w:shd"):
            tc_pr.remove(child)
    fill = OxmlElement("w:shd")
    fill.set(qn("w:val"), "clear")
    fill.set(qn("w:color"), "auto")
    fill.set(qn("w:fill"), hex_color)
    tc_pr.append(fill)


def render_docx(markdown: str, chart_sets: list[dict], company_name: str) -> bytes:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.font.color.rgb = RGBColor(28, 28, 28)

    name, cin = _split_identity(company_name)
    heading = doc.add_heading(name or "Credit memo", level=0)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    meta_bits = ["Kuber credit committee memorandum", datetime.now(timezone.utc).strftime("%d %B %Y").lstrip("0")]
    if cin:
        meta_bits.insert(1, f"CIN {cin}")
    meta = doc.add_paragraph("  |  ".join(meta_bits) + "  |  Confidential")
    meta.runs[0].italic = True
    meta.runs[0].font.size = Pt(10)
    meta.runs[0].font.color.rgb = RGBColor(90, 96, 104)

    for kind, *rest in _iter_blocks(markdown):
        if kind == "h":
            level, text = rest[0], rest[1]
            doc.add_heading(_clean_heading(text), level=min(level, 3))
        elif kind == "p":
            doc.add_paragraph(_plain(rest[0]))
        elif kind == "quote":
            para = doc.add_paragraph(_plain(rest[0]))
            if para.runs:
                para.runs[0].italic = True
        elif kind == "hr":
            continue
        elif kind == "ul":
            for item in rest[0]:
                doc.add_paragraph(_plain(item), style="List Bullet")
        elif kind == "ol":
            for item in rest[0]:
                doc.add_paragraph(_plain(item), style="List Number")
        elif kind == "table":
            rows = rest[0]
            if not rows:
                continue
            cols = max(len(row) for row in rows)
            table = doc.add_table(rows=len(rows), cols=cols)
            table.style = "Table Grid"
            for ridx, row in enumerate(rows):
                padded = row + [""] * (cols - len(row))
                for cidx, cell in enumerate(padded):
                    table.rows[ridx].cells[cidx].text = _plain(cell)
                    if ridx == 0:
                        _shade_cell(table.rows[ridx].cells[cidx], "ECEFF3")
                        for para in table.rows[ridx].cells[cidx].paragraphs:
                            for run in para.runs:
                                run.bold = True
                                run.font.color.rgb = RGBColor(20, 35, 55)

    for charts in chart_sets or []:
        doc.add_heading("Figures", level=1)
        for caption, png in chart_pngs(charts):
            doc.add_paragraph(caption)
            paragraph = doc.add_paragraph()
            run = paragraph.add_run()
            run.add_picture(io.BytesIO(png), width=Inches(6.3))

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
