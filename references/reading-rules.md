# Reading Rules & Edge Cases

Detailed guidance for deciding per-character readings. Load when preparing the
bracketed annotation file.

## Table of contents

1. [Splitting readings across kanji](#1-splitting-readings-across-kanji)
2. [Okurigana (送り仮名)](#2-okurigana)
3. [Iteration marks 々](#3-iteration-marks)
4. [ヶ / ヵ and counters](#4-ヶ--ヵ-and-counters)
5. [Non-dictionary readings (当て字・義訓)](#5-non-dictionary-readings)
6. [Katakana and loanwords](#6-katakana-and-loanwords)
7. [Numerals](#7-numerals)
8. [Voiced, semi-voiced and small kana](#8-voiced-semi-voiced-and-small-kana)
9. [Common homographs](#9-common-homographs)
10. [When genuinely ambiguous](#10-when-genuinely-ambiguous)

## 1. Splitting readings across kanji

The bracket applies to one character, so distribute a word's kana across its
kanji by meaning/etymology, not mechanically:

| Word | Split |
|---|---|
| 約束 (やくそく) | 約[やく]束[そく] |
| 音楽 (おんがく) | 音[おん]楽[がく] |
| 二人 (ふたり) | 二[ふた]人[り] |
| 今朝 (けさ) | 今[け]朝[さ] |
| 花火 (はなび) | 花[はな]火[び] |
| 手紙 (てがみ) | 手[て]紙[がみ] |
| 目覚める (めざめる) | 目[め]覚[ざ]める |
| 話し合う (はなしあう) | 話[はなし]合[あ]う |

When the natural split is unclear (e.g. 今日 → 今[きょ]日[う] feels odd), any
split whose characters recombine to the sung kana is acceptable; prefer the
split that matches the word's components.

## 2. Okurigana

Okurigana (the kana tail of a verb/adjective) is written as-is, not annotated:

- 咲く → 咲[さ]く
- 輝く → 輝[かがや]く
- 暖かい → 暖[あたた]かい
- 眠れない → 眠[ねむ]れない

## 3. Iteration marks

- 々 repeats the previous character's reading: 人々 → 人[ひと]々[びと],
  国々 → 国[くに]々[ぐに], 日々 → 日[ひ]々[び].
- 〆 (e.g. 〆切) → 〆[し]め ... read in context.

## 4. ヶ / ヵ and counters

- ヶ in 一ヶ月 → 一[いっ]ヶ[か]月[げつ]; in ヶ所 it is read かしょ.
- ヵ in 一ヵ月 likewise → ヵ[か].

## 5. Non-dictionary readings

Lyrics frequently read kanji against the dictionary:

- Kanji read as a katakana loanword: 世界 → セカイ, 愛 → ラブ, 光 → ライト.
- Kanji read as a different Japanese word: 未来 → あす, 空 → そら/から, 夕焼け → サンセット.
- Keep exactly what is sung. This is the main reason a dictionary/morphological
  analyzer alone is not enough.

## 6. Katakana and loanwords

By default katakana (サクラ, レモン, タクシー) is basic kana and gets no
annotation. Only annotate katakana if the user explicitly asks for learner
notes. Hiragana likewise never needs annotation.

## 7. Numerals

Read numerals by context or as sung:

- 二人 → 二[ふた]人[り]; 三人 → 三[みっ]人[たり] ... split so it recombines.
- 100万 → 1[ひゃく]0[まん] is awkward; prefer Arabic-digit forms read as words:
  100万[ひゃくまん] over the whole token is not supported per-character — spell
  per digit or keep Arabic digits unannotated when the reading cannot be split
  naturally. When in doubt, keep the digit and put the kana split on adjacent
  kanji only.

## 8. Voiced, semi-voiced and small kana

Readings freely use がぎぐげご, ぱぴぷぺぽ, ゃゅょ, っ, ー, etc.:

- 一階 → 一[いっ]階[かい]
- 学校 → 学[がっ]校[こう]
- 歌手 → 歌[か]手[しゅ]
- 東京 → 東[とう]京[きょう]

## 9. Common homographs

Choose the reading sung in the song:

| Kanji | Possible readings |
|---|---|
| 頭 | あたま / どう / ず / かしら / つむり |
| 人 | ひと / じん / にん |
| 世 | よ / せい |
| 今日 | きょう / こんにち / こんじつ |
| 心 | こころ / しん |
| 空 | そら / から / くう |
| 目 | め / もく / ま |
| 手 | て / しゅ / た |
| 一 | いち / いっ / ひと / はじめ |
| 行 | ゆ / い / こう / ぎょう |
| 思 | おも / おぼ / し |

## 10. When genuinely ambiguous

Pick the most likely reading for the lyric context, render it, and list the
uncertain spots in your final summary so the user can correct them. Do not stop
and ask for every homograph.