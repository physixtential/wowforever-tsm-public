"""Save TSM's public WoW Forever pricing files, run every 5 minutes by GitHub Actions.

TradeSkillMaster publishes the latest snapshot of each auction house and
region as a CSV (https://tradeskillmaster.com/public-data); nothing keeps the
older ones. This saves every new snapshot, gzipped and named by TSM's own
snapshot time (updatedAt), under <folder>/<epoch>.csv.gz, and keeps 30 days.
The Market Watch collector on the user's PC pulls them to fill the hours its
own TSM app downloads missed (WoWForeverTSMHistory/public.py).

Usage: python fetch.py <data dir>. Prints changed=1 if it added or removed a file.
"""

import csv
import gzip
import io
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://public-data.tradeskillmaster.com/forever/us"
SOURCES = {  # folder in the data branch -> file
    "realm/normal-alliance": f"{BASE}/realm/normal-alliance/items.csv",
    "region/us": f"{BASE}/region/items.csv",
}
KEEP_DAYS = 30


def snapshot_time(text):
    stamps = [r["updatedAt"] for r in csv.DictReader(io.StringIO(text)) if r.get("updatedAt")]
    if not stamps:
        raise ValueError("no updatedAt column or rows")
    return int(datetime.strptime(max(stamps), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp())


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main(data_dir):
    data_dir = Path(data_dir)
    changed = False
    for folder, url in SOURCES.items():
        try:
            data = fetch(url)
            t = snapshot_time(data.decode("utf-8"))
        except Exception as e:  # one file failing shouldn't lose the other
            print(f"{folder}: {type(e).__name__}: {e}")
            continue
        target = data_dir / folder / f"{t}.csv.gz"
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(gzip.compress(data, mtime=0))
            print(f"{folder}: saved {target.name} ({len(data)} bytes)")
            changed = True
        else:
            print(f"{folder}: {target.name} already saved")
    cutoff = time.time() - KEEP_DAYS * 86400
    for path in data_dir.glob("*/*/*.csv.gz"):
        if int(path.name.split(".")[0]) < cutoff:
            path.unlink()
            print(f"pruned {path}")
            changed = True
    flag = f"changed={1 if changed else 0}"
    print(flag)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as out:
            out.write(flag + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
