# Youth career night

Dave's 10-minute software engineering session for a church youth career night in early October 2026, run three times as kids ages 11 to 18 rotate between career tables. Everything the kids see is on one published web page reached by QR code; the one-minute original song "Going Live" (Suno, 1:09, used whole) opens each round.

## Files

| File | What it is | Regenerate? |
|---|---|---|
| `going-live.html` | The page behind the QR code: animated lyric video with a song picker (Going Live, Carry It Home, the mashup; each song has its own palette and loads its mp3 only when played; word-by-word karaoke timed from a faster-whisper transcription, canvas code rain, countdown numerals, chorus bursts, deploy bar), Dave's story, day-in-the-life, pay ladder, four education paths plus the Christmas MasterMind "built for fun" card, live code editor, AI prompt, find-the-bug. Source of truth. | Edit, run `build-site.py`, commit and push |
| `going-live-lyrics.md` | Original lyrics for every song, the Suno style lines, and the steps to generate a track | Stable |
| `going-live.mp3` | The Suno track, downloaded by Dave. Used at full length and served as a separate file next to the page (`docs/going-live.mp3`), not embedded. Lyric cues timed with faster-whisper | From Suno |
| `carry-it-home.mp3`, `going-live-mashup.mp3` | The other two Suno songs, copied into `docs/` the same way | From Suno |
| `time-lyrics.py` | Times a song's lyrics to its mp3: faster-whisper word timestamps aligned to the official lyrics in `going-live-lyrics.md`, printed as a `cues` array for `going-live.html`. `python time-lyrics.py carry-it-home.mp3 3` (the number is the song's heading number in the lyrics file) | Run for each new song |
| `talk-plan.md` | Minute-by-minute run of the 10-minute session and answers to expected questions | Stable |
| `talk-plan.html` | Phone-friendly render of the run sheet for Dave's Google Drive. Pandoc with `phone.css`, deliberately not the FS stylesheet since this is a personal doc | `pandoc talk-plan.md --standalone --embed-resources --css phone.css --metadata pagetitle="Going Live: the 10-minute run sheet" -o talk-plan.html` |
| `phone.css` | Stylesheet for `talk-plan.html` only | Stable |
| `qr-poster.html` | Printable table poster with the QR code. Hand-built, not a pandoc render, so the fs-html-gen rule does not apply | From `make-qr.py` |
| `qr.png` | The QR code alone | From `make-qr.py` |
| `make-qr.py` | Generates `qr.png` and `qr-poster.html` from the published URL | Run after any URL change |
| `build-site.py` | Wraps `going-live.html` in a full HTML skeleton and copies every `*.mp3` in the project root into `docs/` | Run after any edit to `going-live.html` or a new song |
| `docs/` | The published site: GitHub Pages serves `main` branch, `/docs` folder. Build output only; edit `going-live.html`, never `docs/index.html` | From `build-site.py` |

The whole folder is the public GitHub repo `Murteas/going-live`. Only `docs/` is served on the site; everything else, including the talk plan, is visible on github.com.

## Published URL

**https://murteas.github.io/going-live/** is the QR target (GitHub Pages, public, no sign-in, source `main` /docs). The URL is recorded in `make-qr.py` and on the poster; if it ever changes, rerun `make-qr.py` and reprint the poster.

A copy also exists as a Claude artifact at https://claude.ai/artifact/PMCoH8gaWxysoq5XDA5YUJ, but the Church Claude workspace only allows sharing with Church accounts, so it is not the QR target and is not kept in sync.

## Updating the live page

1. Edit `going-live.html`.
2. `python build-site.py`
3. From the project root: `git add -A`, commit, `git push`. Pages redeploys in about a minute.

## Adding a song

1. Put its lyrics in `going-live-lyrics.md` under a numbered `## N.` heading, and save its mp3 in the project root with a kebab-case name.
2. `python time-lyrics.py <song>.mp3 N` and paste the output as the `cues` of a new entry in the `SONGS` list in `going-live.html` (copy an existing entry for the other fields: title, palette, card, caption, BPM, duration measured with PyAV).
3. Spot-check a few lines by ear, then build and push as above.

## Guards

- The pay figures on the page carry their sources in the footer. Two ranges (first job $65k to $80k, engineering manager $150k to $250k) are Dave's own observation and are labeled that way on the page. Do not present them as statistics.
- The lyrics are original. Do not add lines from the real "Golden" or any other published song; the page is public.
- The page is dark-first in the hero by design and follows the viewer's theme below it.
