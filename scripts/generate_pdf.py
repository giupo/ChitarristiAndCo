#!/usr/bin/env python3
"""Genera il PDF della scaletta a partire da songs.csv e config.json."""

import csv
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "songs.csv"
CONFIG_PATH = ROOT / "config.json"

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
SIDE_MARGIN = 5 * mm  # mezzo centimetro

# titolo/autore/toni prendono il 34% della larghezza, i 3 giri accordi il 66%
TABLE_WIDTH = PAGE_SIZE[0] - 2 * SIDE_MARGIN
COL_WIDTHS = [
    TABLE_WIDTH * 0.135,  # titolo
    TABLE_WIDTH * 0.085,  # autore
    TABLE_WIDTH * 0.060,  # ton. orig.
    TABLE_WIDTH * 0.060,  # ton. live
    TABLE_WIDTH * 0.240,  # giro accordi 1
    TABLE_WIDTH * 0.240,  # giro accordi 2
    TABLE_WIDTH * 0.180,  # giro / special
]

TITLE_FONT_SIZE = 18
TITLE_LEADING = 21
SUBTITLE_FONT_SIZE = 11
SUBTITLE_LEADING = 14
HEADER_TOP_PADDING = 10 * mm
HEADER_BOTTOM_GAP = 6 * mm

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


def load_songs_db():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return {row["id"]: row for row in csv.DictReader(f)}


def select_songs(songs_db, song_ids):
    selected = []
    for song_id in song_ids:
        row = songs_db.get(str(song_id))
        if row is None:
            raise SystemExit(f"ID canzone {song_id} non trovato in songs.csv")
        selected.append(row)
    return selected


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


def compute_title_lines(title):
    max_width = PAGE_SIZE[0] - 2 * SIDE_MARGIN
    return simpleSplit(title, "Helvetica-Bold", TITLE_FONT_SIZE, max_width)


def compute_header_height(title_lines):
    return (
        HEADER_TOP_PADDING
        + len(title_lines) * TITLE_LEADING
        + SUBTITLE_LEADING
        + HEADER_BOTTOM_GAP
    )


def make_canvas_factory(config, title_lines):
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
            y = height - HEADER_TOP_PADDING
            self.setFont("Helvetica-Bold", TITLE_FONT_SIZE)
            for line in title_lines:
                self.drawCentredString(width / 2, y, line)
                y -= TITLE_LEADING

            self.setFont("Helvetica", SUBTITLE_FONT_SIZE)
            page_info = f"Pagina {self._pageNumber}/{total_pages}"
            subtitle = config.get("subtitle") or ""
            line = f"{subtitle}   |   {page_info}" if subtitle else page_info
            self.drawCentredString(width / 2, y, line)

    return HeaderCanvas


def main():
    config = load_config()
    songs_db = load_songs_db()
    song_ids = config.get("song_ids") or []
    if not song_ids:
        raise SystemExit("config.json: 'song_ids' e' vuoto")
    songs = select_songs(songs_db, song_ids)

    title_lines = compute_title_lines(config["title"])

    doc = SimpleDocTemplate(
        str(ROOT / config["output_pdf"]),
        pagesize=PAGE_SIZE,
        topMargin=compute_header_height(title_lines),
        bottomMargin=15 * mm,
        leftMargin=SIDE_MARGIN,
        rightMargin=SIDE_MARGIN,
    )

    table_data = build_table_data(songs)
    table = Table(table_data, colWidths=COL_WIDTHS, repeatRows=1)
    table.setStyle(build_table_style(len(table_data)))

    doc.build([table], canvasmaker=make_canvas_factory(config, title_lines))
    print(f"PDF generato: {ROOT / config['output_pdf']}")


if __name__ == "__main__":
    main()
