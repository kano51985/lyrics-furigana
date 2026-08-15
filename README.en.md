# Lyrics Furigana

Annotate Japanese song lyrics with **per-character kana readings (furigana/ruby) that match how each word is actually sung**, and render print-ready PDF/HTML lyrics sheets.

> 中文说明见 [README.md](README.md)。

## Features

- **Original text stays as-is, readings on top**: the lyrics keep their original size and font; each kanji gets a smaller kana reading centered directly above it, like Chinese pinyin (HTML `<ruby>` + headless Chrome/Edge rendering, zero extra dependencies).
- **Readings follow the actual sung pronunciation**, not the dictionary default: if 頭 is sung as 「あたま」, it is annotated あたま; if 未来 is sung as 「あす」, annotate 未[あ]来[す]; if 世界 is sung as 「セカイ」, annotate 世[セ]界[カイ].
- **No annotation for basic kana**: hiragana, katakana and punctuation stay untouched; okurigana (e.g. the く in 咲く) keeps its original text.
- **Built-in validation**: missing readings, readings attached to plain kana, or non-kana readings all produce warnings.


> The sample output is regenerated automatically by GitHub Actions on every change to the skill or the sample lyrics.


## Preview

![Sample output](examples/sample_output.png)

## Installation (Codex users)

Copy this folder to:

- Windows: `C:\Users\<you>\.codex\skills\lyrics-furigana`
- macOS/Linux: `~/.codex/skills/lyrics-furigana`

Codex discovers the skill automatically. Then just say:

> Use $lyrics-furigana to annotate these lyrics and render a PDF: <lyrics or song title>

## Manual usage

1. Prepare a UTF-8 text file and annotate each kanji with its reading in square brackets:

```
#title: 春の歌
#artist: サンプル

花[はな]が咲[さ]く　春[はる]の空[そら]
頭[あたま]の中[なか]
二[ふた]人[り]歩[ある]く
```

2. Render:

```
python scripts/render_ruby_pdf.py lyrics.txt
```

This creates a `.pdf` and an `.html` next to the input. Useful options:

| Option | Description | Default |
|---|---|---|
| `--font-size 30pt` | base text size | `26pt` |
| `--rt-scale 0.45` | reading size as a fraction of base text | `0.5` |
| `--preview out.png` | save a preview PNG for QA | - |
| `--html-only` | generate HTML only | - |
| `--browser <path>` | specify Chrome/Edge executable | auto-detected |
| `--margin "18mm 16mm"` | page margins | `20mm 18mm` |

Options can also be set per-file with directives such as `#font-size:`, `#rt-scale:`, `#letter-spacing:`, `#page-size:` and `#margin:`.

## Reading rules (highlights)

- **Use the actual sung pronunciation**; homographs depend on the song (頭 → あたま/どう/ず/…).
- **Split multi-kanji words per character**: 約束 → 約[やく]束[そく]; 二人 → 二[ふた]人[り]; 音楽 → 音[おん]楽[がく].
- **Okurigana stays as text**: 咲く → 咲[さ]く; 輝く → 輝[かがや]く.
- **々 repeats the previous reading**: 人々 → 人[ひと]々[びと].
- **ヶ/ヵ read in context**: 一ヶ月 → 一[いっ]ヶ[か]月[げつ].
- **Non-dictionary readings (当て字/義訓) follow the song**: 世界 sung as セカイ → 世[セ]界[カイ].
- Full rules: [`references/reading-rules.md`](references/reading-rules.md).

## Requirements

- Python 3 (standard library only; no pip packages required)
- Chrome or Edge on the machine for PDF rendering (auto-detected; override with the `LYRICS_BROWSER` environment variable or `--browser`)
- In sandboxed environments the headless-browser step may need user approval once; `--html-only` always works

## License

[MIT](LICENSE)