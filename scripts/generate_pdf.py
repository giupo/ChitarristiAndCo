#!/usr/bin/env python3
"""Genera il PDF della scaletta a partire da songs.csv e config.json."""

import csv
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "songs.csv"
CONFIG_PATH = ROOT / "config.json"

CSV_FIELDS = [
    "titolo",
    "autore",
    "tono_originale",
    "tono_live",
    "giro_accordi_1",
    "giro_accordi_2",
    "giro_special",
]
HEADER_LABELS = [
    "TITOLO",
    "AUTORE",
    "TON.<br/>ORIG.",
    "TON.<br/>LIVE",
    "GIRO ACCORDI 1",
    "GIRO ACCORDI 2",
    "GIRO / SPECIAL",
]
PAGE_SIZE = landscape(A4)
COL_WIDTHS = [60 * mm, 38 * mm, 18 * mm, 18 * mm, 55 * mm, 55 * mm, 43 * mm]

TOP_MARGIN = 28 * mm
SIDE_MARGIN = 5 * mm  # mezzo centimetro

HEADER_STYLE = ParagraphStyle(
    "header", fontName="Helvetica-Bold", fontSize=11, leading=13,
    textColor=colors.white, alignment=1,
)
CELL_STYLE = ParagraphStyle("cell", fontName="Helvetica", fontSize=11, leading=13)
TITLE_CELL_STYLE = ParagraphStyle("titleCell", parent=CELL_STYLE, fontName="Helvetica-Bold")
TONE_CELL_STYLE = ParagraphStyle("toneCell", parent=CELL_STYLE, fontName="Helvetica-Bold", alignment=1)


def load_config():
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_songs():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def build_table_data(songs):
    header_row = [Paragraph(label, HEADER_STYLE) for label in HEADER_LABELS]
    rows = [header_row]
    for song in songs:
        row = [
            Paragraph(song["titolo"], TITLE_CELL_STYLE),
            Paragraph(song["autore"], CELL_STYLE),
            Paragraph(song["tono_originale"], TONE_CELL_STYLE),
            Paragraph(song["tono_live"], TONE_CELL_STYLE),
            Paragraph(song["giro_accordi_1"] or "-", CELL_STYLE),
            Paragraph(song["giro_accordi_2"] or "-", CELL_STYLE),
            Paragraph(song["giro_special"] or "-", CELL_STYLE),
        ]
        rows.append(row)
    return rows


def build_table_style(num_rows):
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbbb")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, num_rows):
        bg = colors.HexColor("#e6e6e6") if i % 2 == 0 else colors.white
        style.append(("BACKGROUND", (0, i), (-1, i), bg))
    return TableStyle(style)


def make_canvas_factory(config):
    class HeaderCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self._draw_header(total_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def _draw_header(self, total_pages):
            width, height = PAGE_SIZE
            self.setFont("Helvetica-Bold", 18)
            self.drawCentredString(width / 2, height - 15 * mm, config["title"])
            self.setFont("Helvetica", 11)
            page_info = f"Pagina {self._pageNumber}/{total_pages}"
            subtitle = config.get("subtitle") or ""
            line = f"{subtitle}   |   {page_info}" if subtitle else page_info
            self.drawCentredString(width / 2, height - 21 * mm, line)

    return HeaderCanvas


def main():
    config = load_config()
    songs = load_songs()
    if not songs:
        raise SystemExit("songs.csv non contiene brani")

    doc = SimpleDocTemplate(
        str(ROOT / config["output_pdf"]),
        pagesize=PAGE_SIZE,
        topMargin=TOP_MARGIN,
        bottomMargin=15 * mm,
        leftMargin=SIDE_MARGIN,
        rightMargin=SIDE_MARGIN,
    )

    table_data = build_table_data(songs)
    table = Table(table_data, colWidths=COL_WIDTHS, repeatRows=1)
    table.setStyle(build_table_style(len(table_data)))

    doc.build([table], canvasmaker=make_canvas_factory(config))
    print(f"PDF generato: {ROOT / config['output_pdf']}")


if __name__ == "__main__":
    main()
