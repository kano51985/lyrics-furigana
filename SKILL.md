---
name: lyrics-furigana
description: Annotate Japanese song lyrics with per-character kana readings (furigana/ruby) matching how each word is actually sung, and render print-ready PDF/HTML lyrics sheets with the readings in small type above the original kanji. Use when the user wants Japanese lyrics with pronunciation guides (furigana/ルビ), pinyin-style kana above kanji, lyrics sheets showing song-specific readings (e.g. 頭 sung as あたま rather than どう), or lyrics converted to PDF/HTML with readings.
---

# Lyrics Furigana

Turn Japanese lyrics into a print-ready sheet: the original text at full size, with the actual sung reading of every kanji in small kana above it (like Chinese pinyin). Output is PDF (+HTML); input is a simple bracketed text format.

## Workflow

1. **Get the lyrics.** Accept a file path or pasted text; note the song title/artist when known.
2. **Decide readings.** Determine the reading of every kanji **as it is actually sung**, not the dictionary default. This is the core step — see "Reading decisions".
3. **Write the annotated input file** in the bracket format below.
4. **Render** to PDF/HTML with `scripts/render_ruby_pdf.py`.
5. **Verify** the output and fix all warnings before delivering.

## Bracket input format

Plain UTF-8 text. `[reading]` directly after a character gives that character's kana reading.

```
#title: 春の歌
#artist: サンプル

花[はな]が咲[さ]く
二[ふた]人[り]歩[ある]く
頭[あたま]の中[なか]　溢[あふ]れる音[おん]楽[がく]
```

- One bracket per character. For a multi-kanji word, split the reading across its characters, e.g. 約束 → 約[やく]束[そく], 二人 → 二[ふた]人[り], 音楽 → 音[おん]楽[がく].
- Blank lines separate stanzas (extra vertical space).
- Hiragana, katakana, and punctuation are written as-is with no bracket.
- Optional `#key: value` directives: `title`, `artist`, `font`, `font-size`, `rt-scale`, `letter-spacing`, `font-weight`, `page-size`, `margin`, `stanza-gap`, `line-height`.

## Reading decisions (the core step)

- The reading must be the pronunciation **actually sung in the song**. Homographs depend on the song: 頭 can be あたま/どう/ず/かしら — use the sung one; 人 can be ひと/じん/にん; 世 can be よ/せい.
- Songs often use non-dictionary readings (当て字/義訓): kanji read as a katakana loanword (世界 sung as セカイ), or kanji read as a different word (未来 sung as あす). Keep the sung reading, even if it is unusual.
- 送り仮名 (okurigana) stays as text: 咲く → 咲[さ]く, 輝く → 輝[かがや]く.
- 々 repeats the previous character's reading: 人々 → 人[ひと]々[びと], 国々 → 国[くに]々[ぐに].
- ヶ/ヵ get their context reading: 一ヶ月 → 一[いっ]ヶ[か]月[げつ].
- Numerals get the sung reading: 二人 → 二[ふた]人[り]; 1→いち, 2→に, 3→さん, ... (or whatever is actually sung).
- Use only basic kana (hiragana/katakana) for readings.
- If a reading is genuinely ambiguous, choose the most likely reading for the context and flag it in your final summary so the user can correct it.
- Optional aid: a Japanese morphological analyzer (MeCab/Sudachi/pykakasi) can suggest default readings, but always override to the sung pronunciation.

## Rendering

```
python <skill>/scripts/render_ruby_pdf.py lyrics.txt [out.pdf] [--preview preview.png] [--font-size 26pt] [--rt-scale 0.5]
```

- Writes `out.pdf` and a matching `out.html` next to the input (or at `out.pdf`).
- The PDF is rendered by headless Chrome/Edge (auto-detected; override with `LYRICS_BROWSER` or `--browser`). In sandboxed environments the browser step may require approval/escalation.
- Defaults: A4, 26pt text, readings at 50% size, centered, Noto Sans JP → Yu Gothic → Meiryo fallback. Override per song with `#` directives or CLI flags.
- `--html-only` skips the PDF. `--preview` saves a viewport PNG for visual QA.

## Verification

- Re-run until there are **zero** `no reading given for 'X'` warnings — every kanji must be annotated. Warnings also flag readings on plain kana and non-kana readings.
- Visually inspect the HTML (or preview PNG): readings must sit above and be centered on their kanji, and long lines must wrap cleanly.
- Spot-check known homographs and special readings in the rendered output.

## Examples

| Original | Annotated |
|---|---|
| 花が咲く | 花[はな]が咲[さ]く |
| 二人歩く | 二[ふた]人[り]歩[ある]く |
| 頭の中 | 頭[あたま]の中[なか] |
| 人々の笑顔 | 人[ひと]々[びと]の笑[え]顔[がお] |
| 一ヶ月後 | 一[いっ]ヶ[か]月[げつ]後[ご] |
| 世界の果て (sung as セカイ) | 世[セ]界[カイ]の果[は]て |
| 未来 (sung as あす) | 未[あ]来[す] |

See `references/reading-rules.md` for detailed splitting rules and edge cases.