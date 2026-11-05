# sahannonis.github.io

The home of the books of S. Nonis: a page for every book, a page for every pin, and the daily Pinterest feeds.

- `data/pins.json` holds every pin and the day it goes out. `data/drip.json` holds the start date.
- Every morning `.github/workflows/drip.yml` runs `tools/build_feeds.py`, which puts that day's pins into
  `feeds/<book>.xml`, then publishes the site. Pinterest reads each feed and pins the new items to its board.
- To pause the pins, disable the "Daily pins" workflow in the Actions tab. To restart later, set a new `start` date.
- `data/books.json` holds the Amazon links. Empty means the buttons search Amazon for the title.
