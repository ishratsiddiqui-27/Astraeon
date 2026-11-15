"""Build data/timeline.csv, data/images.csv and assets/images/ from NASA PSI.

Run from the project root (needs internet):
    python build_psi_extras.py

For every experiment in data/investigations.csv it reads the PSI investigation record
(through the same data service the PSI website uses, psi.nasa.gov/geode-py/ws) and writes:
- data/timeline.csv: the investigation start and end dates PSI lists (the project period,
  not the flight dates), plus the flight platform.
- data/images.csv + assets/images/: the "Representative Image(s)" PSI publishes, downloaded
  into the repo. Logos are skipped, and an image is kept only when its PSI record states a
  license. The largest image per experiment is marked is_primary = yes (use it on the card).
"""
import csv
import http.client
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime

API = "https://psi.nasa.gov/geode-py/ws"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
INV = os.path.join("data", "investigations.csv")
TIMELINE = os.path.join("data", "timeline.csv")
IMAGES = os.path.join("data", "images.csv")
IMAGE_DIR = os.path.join("assets", "images")

TIMELINE_COLUMNS = ["id", "psi_id", "investigation_start", "investigation_end", "flight_platform", "source_page"]
IMAGE_COLUMNS = ["id", "psi_id", "image_path", "original_file", "is_primary", "license", "credit", "source_page"]
MAGIC = {b"\xff\xd8\xff": "jpg", b"\x89PNG": "png"}


def get(url, binary=False, tries=4):
    """Fetch a URL. PSI sometimes drops connections, so retry with growing pauses."""
    for attempt in range(1, tries + 1):
        try:
            time.sleep(0.5)  # be gentle with PSI's server
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
            return data if binary else data.decode("utf-8", "replace")
        except (OSError, http.client.HTTPException):   # dropped or cut-off connections
            if attempt == tries:
                raise
            time.sleep(3 * attempt)


def iso_date(text):
    """PSI writes dates as MM-DD-YYYY. Returns YYYY-MM-DD, or '' if blank or unreadable."""
    try:
        return datetime.strptime((text or "").strip(), "%m-%d-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""


def download_file(psi_id, entry):
    query = urllib.parse.urlencode({"file": entry["file_name"], "version": entry.get("version", 1), "redirect": "false"})
    signed_url = get(f"{API}/studies/{psi_id}/download?{query}").strip().strip('"')
    return get(signed_url, binary=True)


def main():
    with open(INV, encoding="utf-8", newline="") as f:
        experiments = [(r["id"], r["source_link"].rstrip("/").rsplit("/", 1)[-1]) for r in csv.DictReader(f)]

    # Clear old images file by file. Deleting and re-creating the folder fails on Windows/OneDrive.
    os.makedirs(IMAGE_DIR, exist_ok=True)
    for old in os.listdir(IMAGE_DIR):
        if os.path.isfile(os.path.join(IMAGE_DIR, old)):
            os.remove(os.path.join(IMAGE_DIR, old))

    timeline, images, skipped = [], [], []
    for rid, psi_id in experiments:
        rec = json.loads(get(f"{API}/repo/investigations/{psi_id}"))
        page = f"https://psi.nasa.gov/physci/repo/data/investigations/{psi_id}"
        timeline.append({
            "id": rid, "psi_id": psi_id,
            "investigation_start": iso_date(rec.get("investigationStartDate")),
            "investigation_end": iso_date(rec.get("investigationEndDate")),
            "flight_platform": (rec.get("flightProgram") or "").strip(),
            "source_page": page,
        })

        candidates = [i for i in rec.get("images") or []
                      if "logo" not in i.get("file_name", "").lower() and not i.get("restricted")]
        license_id = (rec.get("licenseIdentifier") or "").strip()
        if candidates and not license_id:
            skipped.append(f"{rid} ({psi_id}): {len(candidates)} image(s), but no license stated in the PSI record")
            continue
        kept = []
        for entry in sorted(candidates, key=lambda i: -int(i.get("file_size") or 0)):
            data = download_file(psi_id, entry)
            ext = next((e for m, e in MAGIC.items() if data.startswith(m)), None)
            if not ext:
                skipped.append(f"{rid} ({psi_id}): {entry['file_name']} is not a JPEG or PNG")
                continue
            path = f"{IMAGE_DIR}/{rid}_{len(kept) + 1}.{ext}".replace(os.sep, "/")
            with open(path, "wb") as out:
                out.write(data)
            kept.append({
                "id": rid, "psi_id": psi_id, "image_path": path, "original_file": entry["file_name"],
                "is_primary": "yes" if not kept else "no", "license": license_id,
                "credit": f"NASA Physical Sciences Informatics ({psi_id})", "source_page": page,
            })
        images.extend(kept)

    for path, columns, rows in ((TIMELINE, TIMELINE_COLUMNS, timeline), (IMAGES, IMAGE_COLUMNS, images)):
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=columns, lineterminator="\r\n")
            w.writeheader()
            w.writerows(rows)

    dated = sum(1 for t in timeline if t["investigation_start"])
    print(f"Wrote {TIMELINE}: {len(timeline)} experiments, {dated} with a start date")
    print(f"Wrote {IMAGES}: {len(images)} images for {len({i['id'] for i in images})} experiments, saved in {IMAGE_DIR}/")
    for s in skipped:
        print(f"  skipped: {s}")


if __name__ == "__main__":
    try:
        main()
    except PermissionError as e:
        sys.exit(f"Couldn't write a file ({e}). Close anything that has assets/images open, wait for OneDrive to finish syncing, then run it again.")
    except (OSError, http.client.HTTPException) as e:
        sys.exit(f"Download failed ({e!r}). PSI may be busy; wait a minute and run it again.")
