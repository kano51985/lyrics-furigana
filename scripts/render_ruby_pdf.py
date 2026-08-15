#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_ruby_pdf.py - Render Japanese lyrics with furigana to HTML + PDF.

INPUT FORMAT (UTF-8 text)
-------------------------
  #title: 花
  #artist: 中島みゆき

  花[はな]が咲[さ]く
  君[きみ]と頭[あたま]を撫[な]でる

* `[reading]` directly after a character attaches that kana reading to that
  single character (per-character ruby, like pinyin). Keep readings in basic
  kana (hiragana / katakana).
* Blank lines separate stanzas (extra vertical space).
* `#key: value` lines set options: title, artist, font, font-size, rt-scale,
  letter-spacing, font-weight, page-size, margin, stanza-gap, line-height.

USAGE
-----
  python render_ruby_pdf.py lyrics.txt [out.pdf]
  python render_ruby_pdf.py lyrics.txt --html-only
  python render_ruby_pdf.py lyrics.txt --font-size 30pt --rt-scale 0.45
  python render_ruby_pdf.py lyrics.txt --preview preview.png   # QA image

The PDF is rendered with headless Chrome/Edge so ruby positioning is exact.
Set LYRICS_BROWSER (env) or --browser to override browser auto-detection.
"""

import argparse
import html
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------- char sets
HIRAGANA = set(
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
    "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ"
    "ぁぃぅぇぉゃゅょっゎゝゞ")
KATAKANA = set(
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
    "ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ"
    "ァィゥェォャュョッヮヽヾ")
GOJUON = HIRAGANA | KATAKANA          # basic kana: no ruby by default
ANNOTATABLE_EXTRA = set("々〆ヶヵゐゑヰヱヷヸヹヺ")  # rare chars that take ruby
READING_EXTRA = set("・、ー")          # allowed inside a reading


def is_kanji(ch):
    o = ord(ch)
    return (0x4E00 <= o <= 0x9FFF) or (0x3400 <= o <= 0x4DBF) or (0xF900 <= o <= 0xFAFF)


def needs_ruby(ch):
    return is_kanji(ch) or ch in ANNOTATABLE_EXTRA or ch.isdigit()


def is_kana_reading(s):
    return bool(s) and all(c in GOJUON or c in READING_EXTRA for c in s)


# ---------------------------------------------------------------- options
DEFAULT_FONT = ('"Noto Sans JP", "Noto Sans CJK JP", "Yu Gothic UI", "Yu Gothic", "Meiryo", '
                '"MS Gothic", "BIZ UDGothic", sans-serif')


class Options:
    def __init__(self):
        self.title = ""
        self.artist = ""
        self.font = DEFAULT_FONT
        self.font_size = "26pt"
        self.rt_scale = 0.5
        self.letter_spacing = "0.05em"
        self.font_weight = "400"
        self.page_size = "A4"
        self.margin = "20mm 18mm"
        self.stanza_gap = "7mm"
        self.line_height = 1.95
        self.header_gap = "5mm"

    DIRECTIVES = {
        "title": "title", "artist": "artist", "font": "font",
        "font-size": "font_size", "rt-scale": "rt_scale",
        "letter-spacing": "letter_spacing", "font-weight": "font_weight",
        "page-size": "page_size", "margin": "margin",
        "stanza-gap": "stanza_gap", "line-height": "line_height",
        "header-gap": "header_gap",
    }

    def apply_directive(self, key, value, warn):
        target = self.DIRECTIVES.get(key)
        if target is None:
            warn(f"unknown directive '#{key}' (ignored)")
            return
        if target in ("rt_scale", "line_height"):
            try:
                setattr(self, target, float(value))
            except ValueError:
                warn(f"bad numeric value for '#{key}': {value!r}")
        else:
            setattr(self, target, value)


# ---------------------------------------------------------------- parsing
def parse_line(line, warn):
    """Return list of (char, reading|None). `[reading]` applies to the
    immediately preceding character."""
    tokens = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "[":
            end = line.find("]", i + 1)
            if end == -1:
                warn(f"unterminated '[' in line: {line!r}")
                tokens.append(("[", None))
                i += 1
                continue
            reading = line[i + 1:end]
            if not tokens:
                warn(f"reading {reading!r} has no preceding character in: {line!r}")
            else:
                prev_ch, prev_reading = tokens[-1]
                if prev_reading is not None:
                    warn(f"double annotation on '{prev_ch}' in: {line!r}")
                else:
                    tokens[-1] = (prev_ch, reading)
            i = end + 1
        else:
            tokens.append((ch, None))
            i += 1
    return tokens


def parse_input(text, warn):
    opts = Options()
    stanzas = []
    cur = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if cur:
                stanzas.append(cur)
                cur = []
            continue
        if line.startswith("#"):
            key, _, val = line[1:].partition(":")
            opts.apply_directive(key.strip().lower(), val.strip(), warn)
            continue
        cur.append(parse_line(line, warn))
    if cur:
        stanzas.append(cur)
    return opts, stanzas


def validate(opts, stanzas, warn):
    n_annot = 0
    n_missing = 0
    for si, stanza in enumerate(stanzas, 1):
        for li, line in enumerate(stanza, 1):
            for ch, reading in line:
                if reading is not None:
                    n_annot += 1
                    if ch in GOJUON and ch not in ANNOTATABLE_EXTRA:
                        warn(f"annotation on plain kana '{ch}' (stanza {si} line {li}); "
                             "remove unless intentional")
                    if not is_kana_reading(reading):
                        warn(f"reading {reading!r} for '{ch}' contains non-kana "
                             f"(stanza {si} line {li})")
                else:
                    if needs_ruby(ch):
                        n_missing += 1
                        warn(f"no reading given for '{ch}' (stanza {si} line {li})")
    return n_annot, n_missing


# ---------------------------------------------------------------- HTML
def build_html(opts, stanzas):
    def esc(s):
        return html.escape(s, quote=False)

    lines_html = []
    for stanza in stanzas:
        inner = []
        for line in stanza:
            parts = []
            for ch, reading in line:
                if reading is not None:
                    parts.append(f"<ruby>{esc(ch)}<rt>{esc(reading)}</rt></ruby>")
                else:
                    parts.append(esc(ch))
            inner.append(f'<div class="line">{"".join(parts)}</div>')
        lines_html.append(f'<div class="stanza">{"".join(inner)}</div>')

    header = ""
    if opts.title or opts.artist:
        title = f'<div class="title">{esc(opts.title)}</div>' if opts.title else ""
        artist = f'<div class="artist">{esc(opts.artist)}</div>' if opts.artist else ""
        header = f'<div class="header">{title}{artist}</div>'

    rt_em = f"{opts.rt_scale}em"
    css = f"""
@page {{ size: {opts.page_size}; margin: {opts.margin}; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  font-family: {opts.font};
  font-weight: {opts.font_weight};
  color: #111;
}}
.header {{ text-align: center; margin-bottom: {opts.header_gap}; }}
.title {{ font-size: 20pt; font-weight: 700; }}
.artist {{ font-size: 11pt; color: #666; margin-top: 1mm; }}
.stanza {{ margin-bottom: {opts.stanza_gap}; }}
.line {{
  font-size: {opts.font_size};
  line-height: {opts.line_height};
  letter-spacing: {opts.letter_spacing};
  text-align: center;
  margin: 0 0 0.15em 0;
}}
ruby {{
  ruby-position: over;
  ruby-align: center;
  white-space: nowrap;
}}
ruby rt {{
  font-size: {rt_em};
  line-height: 1.0;
  font-weight: 400;
  color: #333;
  letter-spacing: 0;
  ruby-align: center;
}}
"""
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{esc(opts.title or "Lyrics")}</title>
<style>{css}</style>
</head>
<body>
{header}
{''.join(lines_html)}
</body>
</html>
"""


# ---------------------------------------------------------------- PDF via browser
BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
BROWSER_NAMES = ("google-chrome", "chrome", "chromium", "chromium-browser",
                 "msedge", "microsoft-edge")


def find_browser(explicit=None):
    if explicit:
        if os.path.isfile(explicit):
            return explicit
        return shutil.which(explicit) or explicit
    env = os.environ.get("LYRICS_BROWSER")
    if env and os.path.isfile(env):
        return env
    for c in BROWSER_CANDIDATES:
        if os.path.isfile(c):
            return c
    for name in BROWSER_NAMES:
        p = shutil.which(name)
        if p:
            return p
    return None


def _extra_flags():
    """Extra Chrome flags for CI/container environments (Linux)."""
    return ["--no-sandbox"] if os.name == "posix" else []


def run_browser(browser, html_path, pdf_path, preview=None):
    url = html_path.resolve().as_uri()
    attempts = [
        ["--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--virtual-time-budget=2000"],
        ["--headless", "--disable-gpu", "--print-to-pdf-no-header",
         "--virtual-time-budget=2000"],
    ]
    for flags in attempts:
        cmd = [browser, *_extra_flags(), *flags, f"--print-to-pdf={pdf_path}", url]
        try:
            subprocess.run(cmd, timeout=240, capture_output=True)
        except Exception:
            continue
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            if preview:
                shot(browser, url, preview)
            return True
    return False


def shot(browser, url, preview):
    """Best-effort viewport screenshot of the HTML for visual QA."""
    try:
        cmd = [browser, *_extra_flags(), "--headless=new", "--disable-gpu",
               f"--screenshot={preview}", "--window-size=1000,1600",
               "--virtual-time-budget=2000", url]
        subprocess.run(cmd, timeout=120, capture_output=True)
    except Exception:
        pass


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Render Japanese lyrics with bracketed furigana to PDF/HTML.")
    ap.add_argument("input", help="UTF-8 lyrics file with [reading] annotations")
    ap.add_argument("output", nargs="?", help="output PDF path (default: next to input)")
    ap.add_argument("--html-only", action="store_true",
                    help="write HTML only, skip PDF")
    ap.add_argument("--preview", metavar="PNG",
                    help="also save a viewport PNG of the HTML for QA")
    ap.add_argument("--browser", help="path or name of Chrome/Edge executable")
    ap.add_argument("--title", "--artist", "--font", "--font-size",
                    "--rt-scale", "--letter-spacing", "--font-weight",
                    "--page-size", "--margin", "--stanza-gap", "--line-height",
                    dest=None, default=argparse.SUPPRESS,
                    help="override options (same keys as #directives)")
    args = ap.parse_args(argv)

    warnings = []

    def warn(msg):
        warnings.append(msg)

    try:
        text = Path(args.input).read_text(encoding="utf-8")
    except OSError as e:
        print(f"error: cannot read {args.input}: {e}", file=sys.stderr)
        return 1

    opts, stanzas = parse_input(text, warn)
    # CLI overrides
    for key in ("title", "artist", "font", "font-size", "rt-scale",
                "letter-spacing", "font-weight", "page-size", "margin",
                "stanza-gap", "line-height"):
        val = getattr(args, key.replace("-", "_"), None)
        if val is not None:
            opts.apply_directive(key, val, warn)

    if not stanzas:
        print("error: no lyric lines found in input", file=sys.stderr)
        return 1

    n_annot, n_missing = validate(opts, stanzas, warn)

    inp = Path(args.input)
    out_pdf = Path(args.output) if args.output else inp.with_suffix(".pdf")
    out_html = out_pdf.with_suffix(".html")

    html_str = build_html(opts, stanzas)
    out_html.write_text(html_str, encoding="utf-8")

    status = "ok"
    if not args.html_only:
        browser = find_browser(args.browser)
        if browser is None:
            print("error: no Chrome/Edge found; set LYRICS_BROWSER or --browser",
                  file=sys.stderr)
            status = "no-browser"
        elif run_browser(browser, out_html, out_pdf, args.preview):
            print(f"pdf:  {out_pdf}")
        else:
            print("error: browser ran but produced no PDF (see HTML)",
                  file=sys.stderr)
            status = "pdf-failed"

    print(f"html: {out_html}")
    if args.preview:
        p = Path(args.preview)
        if p.exists():
            print(f"preview: {p}")
        else:
            print("warning: preview PNG was not created", file=sys.stderr)

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(f"summary: {len(stanzas)} stanza(s), {n_annot} annotated, "
          f"{n_missing} kanji missing readings, {len(warnings)} warning(s)")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
