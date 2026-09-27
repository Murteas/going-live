"""Generate qr.png and qr-poster.html for the youth career night page.

Run after any change to the published URL:
    python make-qr.py
"""
from pathlib import Path
import base64
import io

import segno

URL = "https://murteas.github.io/going-live/"
HERE = Path(__file__).parent

qr = segno.make(URL, error="q")
qr.save(HERE / "qr.png", scale=12, border=2, dark="#1B1740", light="#FFFFFF")

buf = io.BytesIO()
qr.save(buf, kind="png", scale=12, border=2, dark="#1B1740", light="#FFFFFF")
data_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

poster = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Going Live poster</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@700;900&family=Manrope:wght@500;700&display=swap">
<style>
  @page {{ size: letter portrait; margin: 0.5in; }}
  html, body {{ height: 100%; }}
  body {{
    margin: 0; display: grid; place-items: center;
    background: #0B0820; color: #FFF9EC;
    font-family: "Manrope", "Segoe UI", system-ui, sans-serif;
  }}
  .sheet {{
    width: 7.5in; min-height: 10in; padding: .6in; box-sizing: border-box;
    display: grid; align-content: space-between; gap: .4in; text-align: center;
    background:
      radial-gradient(circle at 20% 15%, rgba(255,61,138,.55) 0, transparent 40%),
      radial-gradient(circle at 85% 80%, rgba(255,194,75,.55) 0, transparent 42%),
      #0B0820;
    border-radius: 24px;
  }}
  h1 {{ font-family: "Unbounded", sans-serif; font-weight: 900; font-size: 64px; line-height: 1; margin: 0; letter-spacing: -.02em; }}
  h1 span {{ display: block; font-size: 22px; font-weight: 700; color: #FFC24B; margin-top: 14px; letter-spacing: 0; }}
  .qr {{ justify-self: center; background: #fff; padding: 22px; border-radius: 20px; box-shadow: 0 20px 70px rgba(255,61,138,.35); }}
  .qr img {{ display: block; width: 4.2in; height: 4.2in; }}
  p {{ margin: 0; font-size: 20px; font-weight: 500; line-height: 1.4; }}
  .who {{ font-size: 16px; opacity: .8; }}
  .url {{ font-size: 13px; opacity: .6; word-break: break-all; }}
  @media print {{ body {{ background: #fff; }} .sheet {{ border-radius: 0; }} }}
</style>
</head>
<body>
<div class="sheet">
  <h1>Going Live<span>Software engineering, in one minute</span></h1>
  <div class="qr"><img src="{data_uri}" alt="QR code linking to the Going Live page"></div>
  <div>
    <p>Scan it. Play the song. Change the code.<br>Then find out what an engineer actually makes.</p>
    <p class="who" style="margin-top:14px">Dave Saetrum, Software Development Manager at FamilySearch</p>
  </div>
  <p class="url">{URL}</p>
</div>
</body>
</html>
"""
(HERE / "qr-poster.html").write_text(poster, encoding="utf-8")
print("wrote", HERE / "qr.png", "and", HERE / "qr-poster.html")
