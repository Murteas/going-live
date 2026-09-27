# Youth career night

A 10-minute software engineering session for a church youth career night, run three times as kids ages 11 to 18 rotate between career tables. Everything the kids see is on one published web page reached by QR code; the one-minute original song "Going Live" (Suno, 1:09, used whole) opens each round.

## The page

- **Lyric video with a song picker.** Buttons under the video pick one of three original songs, each labeled with its style and length: Going Live (K-pop, 1:09, the default and the one played at the table), Carry It Home (Country, 1:51), and the mashup of the two (K-pop × Country, 2:46). Every song gets the same effects (word-by-word karaoke, canvas code rain, countdown numerals, chorus bursts, deploy bar) in its own color palette. Switching songs stops playback and returns to that song's start screen.
- **Light on phone data.** Only the chosen song's mp3 is fetched, and only when it is played. If it takes more than a moment to start or stalls, a "Loading the song…" pill shows on the video. If the mp3 cannot load at all, the lyrics run over a synthesized beat and a note says so.
- **Below the video:** the presenter's story, day-in-the-life, pay ladder, four education paths plus the Christmas MasterMind "built for fun" card, a live code editor, an AI prompt, and find-the-bug puzzles.
- Tab icon is an inline SVG (gold play triangle), so there is no favicon file to host.

## Files

| File | What it is | Regenerate? |
|---|---|---|
| `going-live.html` | The page behind the QR code. Source of truth. The songs, their cues, palettes, and labels live in the `SONGS` list in its script | Edit, run `build-site.py`, commit and push |
| `going-live-lyrics.md` | Original lyrics for every song, the Suno style lines, and the steps to generate a track | Stable |
| `going-live.mp3`, `carry-it-home.mp3`, `going-live-mashup.mp3` | The Suno tracks, used at full length. Served as separate files next to the page in `docs/`, not embedded | From Suno |
| `time-lyrics.py` | Times a song's lyrics to its mp3: faster-whisper word timestamps aligned to the official lyrics in `going-live-lyrics.md`, printed as a `cues` array for `going-live.html`. `python time-lyrics.py carry-it-home.mp3 3` (the number is the song's heading number in the lyrics file) | Run for each new song |
| `build-site.py` | Wraps `going-live.html` in a full HTML skeleton (with the tab icon) and copies every `*.mp3` in the project root into `docs/` | Run after any edit to `going-live.html` or a new song |
| `docs/` | The published site: GitHub Pages serves `main` branch, `/docs` folder. Build output only; edit `going-live.html`, never `docs/index.html` | From `build-site.py` |
| `talk-plan.md` | Minute-by-minute run of the 10-minute session and answers to expected questions | Stable |
| `talk-plan.html` | Phone-friendly render of the run sheet. Pandoc with `phone.css` | `pandoc talk-plan.md --standalone --embed-resources --css phone.css --metadata pagetitle="Going Live: the 10-minute run sheet" -o talk-plan.html` |
| `phone.css` | Stylesheet for `talk-plan.html` only | Stable |
| `qr-poster.html` | Printable table poster with the QR code. Hand-built, not a pandoc render | From `make-qr.py` |
| `qr.png` | The QR code alone | From `make-qr.py` |
| `make-qr.py` | Generates `qr.png` and `qr-poster.html` from the published URL | Run after any URL change |

The whole folder is the public GitHub repo `Murteas/going-live`. Only `docs/` is served on the site; everything else, including the talk plan, is visible on github.com.

## Published URL

**https://murteas.github.io/going-live/** is the QR target (GitHub Pages, public, no sign-in, source `main` /docs). The URL is printed on the poster, so it must not change. It is recorded in `make-qr.py`; if it ever does change, rerun `make-qr.py` and reprint the poster.

An older copy exists as a Claude artifact at https://claude.ai/artifact/PMCoH8gaWxysoq5XDA5YUJ. It can only be shared inside its workspace, so it is not the QR target and is not kept in sync.

## Updating the live page

1. Edit `going-live.html`.
2. `python build-site.py`
3. From the project root: `git add -A`, commit, `git push`. Pages redeploys in about a minute.

To preview locally, serve the project root and open `/docs/index.html`. `python -m http.server` works for looking at the page, but it cannot serve part of a file, so seeking in a song does not work there. Browser dev tools that emulate a phone or throttle the network also make songs slow to start; the live site does not have either problem.

## Adding a song

"Lights Come Back On" has lyrics in `going-live-lyrics.md` but no track yet. For it or any other song:

1. Put its lyrics in `going-live-lyrics.md` under a numbered `## N.` heading, and save its mp3 in the project root with a kebab-case name.
2. `python time-lyrics.py <song>.mp3 N` and paste the output as the `cues` of a new entry in the `SONGS` list in `going-live.html`. Copy an existing entry for the other fields: button label, genre, palette, title card, caption, start-screen text, BPM, and duration measured with PyAV.
3. Spot-check a few lines by ear, then build and push as above.

## Guards

- The pay figures on the page carry their sources in the footer. Two ranges (first job $65k to $80k, engineering manager $150k to $250k) are the presenter's own observation and are labeled that way on the page. Do not present them as statistics.
- The lyrics are original. Do not add lines from any other published song; the page is public.
- The page is dark-first in the hero by design and follows the viewer's theme below it.
