#!/usr/bin/env python3
"""
Regenerate PortMelbournePSNewsletter_T1_2026.pdf using reportlab.

Header layout (fixed):
  Blue bar (68 pt tall):
    LEFT  – "South Port Melbourne Primary School"  (22 pt, white bold)
              "TERM 1 NEWSLETTER"                   (12 pt, gold bold, below school name)
              "Beacon Street, Port Melbourne VIC 3207"  (8 pt, white, bottom of bar)
              "www… | (03)…"                            (8 pt, white)
    RIGHT – "Edition 9 — Final Edition"   (10 pt, gold, right-aligned, vertically centred)
              "Friday 28 March 2026"        (10 pt, gold, right-aligned)
  Gold bar (24 pt):
    Motto + "Last week of Term 1 2026"
"""

import os
import fitz
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import Color

W, H = A4  # 595.28 x 841.89

SOURCE = os.path.join(os.path.dirname(__file__), 'PortMelbournePSNewsletter_T1_2026.pdf')

# ---------------------------------------------------------------------------
# Extract images from source PDF (run once)
# ---------------------------------------------------------------------------
_src = fitz.open(SOURCE)
IMG = {}   # xref -> local file path
for pg in range(len(_src)):
    for info in _src[pg].get_images(full=True):
        xref = info[0]
        if xref not in IMG:
            raw = _src.extract_image(xref)
            path = f'/tmp/nl_img_{xref}.{raw["ext"]}'
            with open(path, 'wb') as f:
                f.write(raw['image'])
            IMG[xref] = path

# Known image placements per page (bbox in fitz coords: x0,y0,x1,y1)
PAGE_IMGS = {
    0: [(306.1, 145.9, 538.6, 247.9),
        (306.1, 272.4, 538.6, 374.5)],
    1: [(306.1, 272.5, 538.6, 428.4)],
    2: [],
    3: [],
}
# Map page->image xrefs in order
PAGE_XREFS = {
    0: [5, 7],
    1: [9],
    2: [],
    3: [],
}

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
NAVY  = Color(26/255,  58/255,  92/255)
GOLD  = Color(232/255, 160/255, 32/255)
WHITE = Color(1, 1, 1)

def fitz_color(color_int):
    return Color(((color_int >> 16) & 255) / 255,
                 ((color_int >>  8) & 255) / 255,
                 ( color_int        & 255) / 255)

def rl_font(fitz_font):
    if fitz_font == 'Symbol':
        return 'Symbol'
    return 'Helvetica-Bold' if 'Bold' in fitz_font else 'Helvetica'

# ---------------------------------------------------------------------------
# Header — redesigned layout
# ---------------------------------------------------------------------------
def draw_header(c):
    BOX_TOP  = H - 39.69   # 802.2  (rl, from bottom)
    BOX_BOT  = H - 107.69  # 734.2
    GOLD_BOT = H - 131.69  # 710.2
    BOX_H    = BOX_TOP - BOX_BOT   # 68 pt
    LEFT_X   = 70.7
    RIGHT_X  = 526.6   # right-align all right-column text here

    # ── Backgrounds ──────────────────────────────────────────────────────────
    c.setFillColor(NAVY)
    c.rect(56.7, BOX_BOT,  481.9, BOX_H,              fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(56.7, GOLD_BOT, 481.9, BOX_BOT - GOLD_BOT, fill=1, stroke=0)

    # ── LEFT column ──────────────────────────────────────────────────────────
    # Layout from top of blue bar, top-to-bottom:
    #   [5 pt margin]
    #   School name   22 pt white bold
    #   [3 pt gap]
    #   TERM 1 NEWSLETTER  12 pt gold bold
    #   [auto gap fills middle]
    #   Address       8 pt white  }  grouped at bottom of box
    #   [2 pt gap]                }
    #   Website       8 pt white  }
    #   [5 pt margin]

    # School name
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 22)
    school_asc  = 22 * 0.728          # ≈ 16.0 pt
    school_desc = 22 * 0.21           # ≈  4.6 pt
    school_y    = BOX_TOP - 5 - school_asc          # baseline
    school_bot  = school_y - school_desc             # bottom of descenders
    c.drawString(LEFT_X, school_y, 'South Port Melbourne Primary School')

    # TERM 1 NEWSLETTER subtitle
    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 12)
    nl_asc  = 12 * 0.728      # ≈ 8.7 pt
    nl_desc = 12 * 0.21       # ≈ 2.5 pt
    nl_y    = school_bot - 3 - nl_asc               # baseline (3 pt below school)
    nl_bot  = nl_y - nl_desc
    c.drawString(LEFT_X, nl_y, 'TERM 1 NEWSLETTER')

    # Address + contact grouped at bottom of bar (8 pt, white)
    c.setFillColor(WHITE)
    c.setFont('Helvetica', 8)
    a8_asc  = 8 * 0.728       # ≈ 5.8 pt
    a8_desc = 8 * 0.21        # ≈ 1.7 pt
    a8_lh   = a8_asc + a8_desc   # ≈ 7.5 pt  (full line height)

    web_y   = BOX_BOT + 5 + a8_desc                 # baseline, 5 pt from box bottom
    addr_y  = web_y + a8_lh + 2                     # address line above website

    c.drawString(LEFT_X, web_y,  'www.southportmelbourneps.vic.edu.au  |  (03) 9646 0000')
    c.drawString(LEFT_X, addr_y, 'Beacon Street, Port Melbourne VIC 3207')

    # ── RIGHT column (gold, right-aligned) ───────────────────────────────────
    # Two lines: Edition and Date, vertically centred in the UPPER portion of
    # the blue bar (above where address/contact live).
    # "Upper portion" = from box top down to where subtitle ends + a bit of gap.
    upper_bot = nl_bot - 4          # 4 pt below the subtitle bottom
    upper_h   = BOX_TOP - upper_bot # height of upper portion

    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 10)
    r10_asc  = 10 * 0.728
    r10_desc = 10 * 0.21
    r10_lh   = r10_asc + r10_desc   # ≈ 9.4 pt

    right_lines = [
        'Edition 9 \u2014 Final Edition',
        'Friday 28 March 2026',
    ]
    gap_r    = 6
    total_r  = len(right_lines) * r10_lh + (len(right_lines) - 1) * gap_r
    top_pad_r = (upper_h - total_r) / 2

    for i, text in enumerate(right_lines):
        ry = BOX_TOP - top_pad_r - i * (r10_lh + gap_r) - r10_asc
        tw = c.stringWidth(text, 'Helvetica-Bold', 10)
        c.drawString(RIGHT_X - tw, ry, text)

    # ── Gold bar: motto + term note ───────────────────────────────────────────
    c.setFillColor(NAVY)
    c.setFont('Helvetica-Bold', 9)
    gold_h   = BOX_BOT - GOLD_BOT      # 24 pt
    g9_asc   = 9 * 0.728
    text_y   = GOLD_BOT + (gold_h + g9_asc) / 2 - g9_asc   # visually centred

    tagline  = '\u2665  Celebrating community, curiosity and connection  \u2665'
    lw_text  = 'Last week of Term 1 2026'
    c.drawString(123.3, text_y, tagline)
    lw_w = c.stringWidth(lw_text, 'Helvetica-Bold', 9)
    c.drawString(RIGHT_X - lw_w, text_y, lw_text)


# ---------------------------------------------------------------------------
# Page body — reproduced from fitz extraction
# ---------------------------------------------------------------------------
def draw_body(c, fitz_page, page_idx):
    # 1. Filled rectangles (below header)
    for d in fitz_page.get_drawings():
        fill  = d.get('fill')
        rect  = d.get('rect')
        color = d.get('color')
        items = d.get('items', [])

        if not rect or rect[1] <= 131:
            continue   # skip header area

        x0, y0f, x1, y1f = rect
        rw, rh = x1 - x0, y1f - y0f
        y_bot  = H - y1f

        if fill:
            c.setFillColor(Color(fill[0], fill[1], fill[2]))
            c.rect(x0, y_bot, rw, rh, fill=1, stroke=0)
        elif color and len(items) == 1 and items[0][0] == 'l':
            p1, p2 = items[0][1], items[0][2]
            c.setStrokeColor(Color(color[0], color[1], color[2]))
            c.setLineWidth(d.get('width', 0.75))
            c.line(p1.x, H - p1.y, p2.x, H - p2.y)

    # 2. Text (below header, including footer)
    for b in fitz_page.get_text('dict')['blocks']:
        if b.get('type') != 0:
            continue
        for line in b.get('lines', []):
            yf = line['bbox'][1]
            if yf <= 131:       # header + gold bar — skip (redrawn above)
                continue
            for span in line.get('spans', []):
                c.setFillColor(fitz_color(span['color']))
                c.setFont(rl_font(span['font']), span['size'])
                c.drawString(span['origin'][0], H - span['origin'][1], span['text'])

    # 3. Footer separator line (reproduced from drawings, y≈788)
    c.setStrokeColor(Color(0, 0, 0))
    c.setLineWidth(1.0)
    c.line(56.7, H - 788.2, 538.6, H - 788.2)

    # 4. Images
    bboxes = PAGE_IMGS.get(page_idx, [])
    xrefs  = PAGE_XREFS.get(page_idx, [])
    for bbox, xref in zip(bboxes, xrefs):
        path = IMG.get(xref, '')
        if path and os.path.exists(path):
            x0, y0f, x1, y1f = bbox
            c.drawImage(path, x0, H - y1f,
                        width=x1 - x0, height=y1f - y0f,
                        preserveAspectRatio=True, anchor='sw')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    out = os.path.join(os.path.dirname(__file__), 'PortMelbournePSNewsletter_T1_2026.pdf')
    c = rl_canvas.Canvas(out, pagesize=A4)

    for pg_idx in range(len(_src)):
        draw_header(c)
        draw_body(c, _src[pg_idx], pg_idx)
        c.showPage()

    c.save()
    _src.close()
    print(f'Saved: {out}')

if __name__ == '__main__':
    main()
