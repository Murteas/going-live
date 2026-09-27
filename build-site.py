"""Build the GitHub Pages site from going-live.html.

going-live.html is written in Claude-artifact form (no doctype/head/body; the artifact host wraps it).
GitHub Pages serves docs/ as-is, so this script adds the skeleton and copies the songs.

    python build-site.py
Then commit and push from the project root.
"""
from pathlib import Path
import shutil

HERE = Path(__file__).parent
SITE = HERE / "docs"
SITE.mkdir(exist_ok=True)

body = (HERE / "going-live.html").read_text(encoding="utf-8")

page = f"""<!doctype html>
<!-- served from docs/ -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="A one-minute original anthem and a one-page guide to a software engineering career for youth ages 11 to 18.">
<meta name="color-scheme" content="light dark">
<style>
  :root {{ padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }}
  img {{ max-width: 100%; }}
  [hidden] {{ display: none !important; }}
</style>
{body}
</head>
<body>
</body>
</html>
"""
# The artifact form puts <title>, <style>, <main> and <script> in one stream; browsers move body content out of
# <head> automatically, but keep the document valid by splitting at the first <main>.
head_part, main_part = page.split("<main>", 1)
page = head_part + "</head>\n<body>\n<main>" + main_part.replace("</head>\n<body>\n</body>\n</html>\n", "</body>\n</html>\n")

(SITE / "index.html").write_text(page, encoding="utf-8")
songs = sorted(HERE.glob("*.mp3"))
for song in songs:
    shutil.copyfile(song, SITE / song.name)
(SITE / ".nojekyll").write_text("", encoding="utf-8")
print("built", SITE / "index.html", "and copied", ", ".join(s.name for s in songs))
