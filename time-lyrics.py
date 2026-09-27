"""Time a song's lyrics to its mp3, for the lyric video in going-live.html.

Transcribes the mp3 with faster-whisper (word timestamps), aligns the recognized words to the official
lyrics in going-live-lyrics.md, and prints a CUES array: the official wording with whisper's times.

    python time-lyrics.py carry-it-home.mp3 3
    python time-lyrics.py going-live-mashup.mp3 4

The second argument is the song's number in going-live-lyrics.md ("## 3. ..."). Paste the output into
that song's `cues` in going-live.html.
"""
from difflib import SequenceMatcher
from pathlib import Path
import json
import re
import sys

HERE = Path(__file__).parent
LYRICS = HERE / "going-live-lyrics.md"
LEAD = 0.15  # a cue appears this long before its first word, as in the original Going Live cues
TITLE_AFTER = 0.5  # the title card follows the last sung word by this much
MAX_WORD = 0.5  # a word lights up at most this long before whisper says it ends
MAX_STEP = 0.6  # an unrecognized word is placed at most this far after the recognized word before it

# Section tags to cue kinds. Duet tags ([singer A], [singer B]) take the kind the same line has in its
# source song, so a mashup keeps each song's verse/pre/chorus shape.
TAG_KINDS = {"verse": "verse", "pre-chorus": "pre", "bridge": "pre", "chorus": "chorus"}
# Line-level overrides, checked first.
LINE_KINDS = [("three, two, one", "countdown"), ("we're gonna run it", "run")]


def song_lyrics(number):
    """[(tag, line)] from the lyrics code block of '## <number>.' in going-live-lyrics.md."""
    text = LYRICS.read_text(encoding="utf-8")
    section = re.search(rf"^## {number}\. .*?(?=^## |\Z)", text, re.M | re.S)
    if not section:
        sys.exit(f"no song {number} in {LYRICS.name}")
    block = re.search(r"### Lyrics.*?```\n(.*?)```", section.group(0), re.S).group(1)
    lines, tag = [], ""
    for raw in block.splitlines():
        raw = raw.strip()
        if raw.startswith("["):
            tag = raw.strip("[]").split(":")[0].strip().lower()
        elif raw:
            lines.append((tag, raw))
    return lines


def all_line_kinds():
    """Kind of every line in every song that uses plain section tags, for duet lines to borrow."""
    kinds = {}
    for number in re.findall(r"^## (\d+)\.", LYRICS.read_text(encoding="utf-8"), re.M):
        for tag, line in song_lyrics(number):
            if tag in TAG_KINDS:
                kinds.setdefault(norm_line(line), TAG_KINDS[tag])
    return kinds


def norm_line(line):
    return " ".join(norm(w) for w in line.split())


def norm(word):
    return re.sub(r"[^a-z0-9']", "", word.lower().replace("’", "'"))


def kind_of(tag, line, borrowed):
    low = line.lower()
    for start, kind in LINE_KINDS:
        if low.startswith(start):
            return kind
    if tag in TAG_KINDS:
        return TAG_KINDS[tag]
    if norm_line(line) in borrowed:
        return borrowed[norm_line(line)]
    sys.exit(f"no cue kind for [{tag}] {line!r}")


def transcribe(mp3):
    from faster_whisper import WhisperModel

    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(mp3), word_timestamps=True, language="en")
    return [(norm(w.word), w.start, w.end) for s in segments for w in s.words if norm(w.word)]


def unglue(words):
    """Whisper often starts a word where the previous one ended or where a pause began, so a word it hears
    as long is really sung near its end. This rule matched the original Going Live cues best."""
    return [(w, max(start, end - MAX_WORD), end) for w, start, end in words]


def similar(a, b):
    return a == b or SequenceMatcher(None, a, b).ratio() >= 0.75


def align(official, heard):
    """Global alignment of official words to heard words (edit distance, fuzzy match).
    Returns, per official word, the index of the heard word it matched, or None."""
    n, m = len(official), len(heard)
    INF = float("inf")
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0] = [0.0] * (m + 1)  # heard words before the first lyric (ad-libs, hallucinations) are free
    for i in range(1, n + 1):
        cost[i][0] = cost[i - 1][0] + 1
        back[i][0] = "up"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = cost[i - 1][j - 1] + (0 if similar(official[i - 1], heard[j - 1][0]) else 1.5)
            skip_official = cost[i - 1][j] + 1
            skip_heard = cost[i][j - 1] + 0.6  # extra heard words (repeats, ad-libs) are cheap
            cost[i][j], back[i][j] = min((match, "diag"), (skip_official, "up"), (skip_heard, "left"))
    j = min(range(m + 1), key=lambda k: cost[n][k])  # trailing heard words are free too
    i, pairs = n, [None] * n
    while i > 0:
        step = back[i][j]
        if step == "diag":
            if similar(official[i - 1], heard[j - 1][0]):
                pairs[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif step == "up":
            i -= 1
        else:
            j -= 1
    return pairs


def fill(times):
    """Matched words keep whisper's start; unmatched ones are spread evenly between their matched neighbors."""
    known = [k for k, t in enumerate(times) if t is not None]
    if not known:
        return None
    for k in range(len(times)):
        if times[k] is None:
            before = max((x for x in known if x < k), default=None)
            after = min((x for x in known if x > k), default=None)
            if before is None:
                times[k] = times[after] - 0.3 * (after - k)
            elif after is None:
                times[k] = times[before] + 0.3 * (k - before)
            else:
                # Spread evenly, but a word misheard just before an instrumental break stays near its line.
                spread = times[before] + (times[after] - times[before]) * (k - before) / (after - before)
                times[k] = min(spread, times[before] + MAX_STEP * (k - before))
    return times


def repeats(lines, heard, used):
    """Lines sung more often than written: runs of heard words the alignment left over that match a lyric line.
    Returns [(line index, [time per word])]."""
    found, run = [], []
    for j in range(len(heard) + 1):
        if j < len(heard) and j not in used:
            run.append(j)
            continue
        if len(run) >= 4:
            gap = [heard[x][0] for x in run]
            best = max(range(len(lines)), key=lambda li: SequenceMatcher(None, gap, [norm(w) for w in lines[li][1].split()]).ratio())
            want = [norm(w) for w in lines[best][1].split()]
            sm = SequenceMatcher(None, want, gap)
            if sm.ratio() >= 0.6:
                times = [None] * len(want)
                for a, b, size in sm.get_matching_blocks():
                    for d in range(size):
                        times[a + d] = heard[run[b + d]][1]
                found.append((best, fill(times)))
        run = []
    return found


def cues_for(mp3, number):
    lines = song_lyrics(number)
    borrowed = all_line_kinds()
    words = [(li, w) for li, (_, line) in enumerate(lines) for w in line.split()]
    heard = unglue(transcribe(mp3))
    pairs = align([norm(w) for _, w in words], heard)
    times = fill([heard[p][1] if p is not None else None for p in pairs])
    if times is None:
        sys.exit("no lyric words recognized")

    def cue(li, ts):
        tag, line = lines[li]
        ws = [[w, round(t, 2)] for w, t in zip(line.split(), ts)]
        return {"t": round(max(0, ws[0][1] - LEAD), 2), "kind": kind_of(tag, line, borrowed), "words": ws}

    cues = [cue(li, [times[k] for k, (l, _) in enumerate(words) if l == li]) for li in range(len(lines))]
    extra = repeats(lines, heard, {p for p in pairs if p is not None})
    cues += [cue(li, ts) for li, ts in extra]
    cues.sort(key=lambda c: c["t"])
    cues.append({"t": round(max(c["words"][-1][1] for c in cues) + TITLE_AFTER, 2), "kind": "title", "words": []})
    matched = sum(p is not None for p in pairs)
    print(f"// {matched}/{len(pairs)} lyric words matched to whisper, the rest interpolated;"
          f" {len(extra)} repeated line(s) found: {[lines[li][1][:30] for li, _ in extra]}", file=sys.stderr)
    return cues


def js(cues):
    rows = []
    for c in cues:
        words = ", ".join(f"[{json.dumps(w)}, {t}]" for w, t in c["words"])
        rows.append(f'    {{ t: {c["t"]}, kind: "{c["kind"]}", words: [{words}] }}')
    return "[\n" + ",\n".join(rows) + "\n  ]"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(js(cues_for(HERE / sys.argv[1], sys.argv[2])))
