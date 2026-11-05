"""Writes one RSS feed per Pinterest board into feeds/, holding only the pins whose day has come.

data/pins.json   every pin, with "day" = days after the start date it goes out
data/drip.json   {"start": "YYYY-MM-DD", "window_days": 14}
Pinterest reads each feed about once a day and makes a pin from every new item it finds.
Run by .github/workflows/drip.yml every morning. Standard library only.
"""
import datetime as dt
import json
import os
import sys
from email.utils import format_datetime
from xml.sax.saxutils import escape

SITE = "https://sahannonis.github.io"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(today=None):
    drip = json.load(open(os.path.join(HERE, "data/drip.json")))
    pins = json.load(open(os.path.join(HERE, "data/pins.json")))
    start = dt.date.fromisoformat(drip["start"])
    today = today or dt.datetime.now(dt.timezone.utc).date()
    n = (today - start).days
    window = drip.get("window_days", 14)
    os.makedirs(os.path.join(HERE, "feeds"), exist_ok=True)
    books = sorted({p["book"] for p in pins})
    live_total = 0
    for book in books:
        mine = [p for p in pins if p["book"] == book]
        live = [p for p in mine if n - window < p["day"] <= n]
        live_total += len(live)
        live.sort(key=lambda p: p["day"], reverse=True)
        board = mine[0]["board"]
        items = []
        for p in live:
            when = dt.datetime.combine(start + dt.timedelta(days=p["day"]), dt.time(6, 0), dt.timezone.utc)
            img = f"{SITE}/{p['image']}"
            size = os.path.getsize(os.path.join(HERE, p["image"])) if os.path.exists(os.path.join(HERE, p["image"])) else 0
            desc = f'<img src="{img}" alt="{p["title"]}"/><p>{p["description"]}</p>'
            items.append(f"""  <item>
   <title>{escape(p['title'][:100])}</title>
   <link>{escape(p['link'])}</link>
   <guid isPermaLink="false">{escape(p['book'] + '/' + p['slug'])}</guid>
   <pubDate>{format_datetime(when)}</pubDate>
   <description>{escape(desc)}</description>
   <category>{escape(p.get('keywords', ''))}</category>
   <enclosure url="{escape(img)}" length="{size}" type="image/jpeg"/>
   <media:content url="{escape(img)}" medium="image" type="image/jpeg" width="1000" height="1500"/>
  </item>""")
        latest = format_datetime(dt.datetime.combine(today, dt.time(6, 0), dt.timezone.utc))
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">
 <channel>
  <title>{escape(board)} · Books by S. Nonis</title>
  <link>{SITE}/books/{book}/</link>
  <atom:link href="{SITE}/feeds/{book}.xml" rel="self" type="application/rss+xml"/>
  <description>{escape(board)}, from the books of S. Nonis.</description>
  <language>en</language>
  <lastBuildDate>{latest}</lastBuildDate>
{chr(10).join(items)}
 </channel>
</rss>
"""
        open(os.path.join(HERE, "feeds", book + ".xml"), "w").write(xml)
    print(f"day {n}: {live_total} pins live across {len(books)} feeds")


if __name__ == "__main__":
    main(dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else None)
