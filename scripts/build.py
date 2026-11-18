#!/usr/bin/env python3
"""Build Justin's ArtVerse into _site/ for GitHub Pages.

Reads:
  site.json                 site name, tagline, bio, links, accent colour
  art/                      images placed directly here are "uncategorized"
  art/<Series name>/        every folder is one series (one planet)
  art/<Series>/_info.json   optional: series description, cover, order, per-work titles

Writes _site/ with index.html and web-sized images in _site/img/.
"""
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

try:  # lets iPhone/iPad .heic photos work too
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass

Image.MAX_IMAGE_PIXELS = 400_000_000  # big Procreate canvases are fine

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "art"
OUT = ROOT / "_site"
IMG = OUT / "img"
PICTURE = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff"}
GIF = {".gif"}
VIDEO = {".mp4", ".webm"}
SUPPORTED = PICTURE | GIF | VIDEO
FULL_SIZE = 2400   # longest edge of the image shown in the viewer
THUMB_SIZE = 900   # longest edge of the image shown in the grid
PREFIX = re.compile(r"^(\d+)[\s._-]+")
CAMERA = re.compile(r"^(img|image|dsc|photo|screenshot|untitled|artwork|procreate)?[\s_-]*\d*$", re.I)

warnings = []


def warn(msg):
    warnings.append(msg)
    print("WARNING:", msg)


def h8(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def split_prefix(name):
    """'03 Moonlit Fox' -> ('Moonlit Fox', 3)."""
    m = PREFIX.match(name)
    num = int(m.group(1)) if m else None
    return PREFIX.sub("", name).strip(), num


def load_json(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        warn(f"{path.relative_to(ROOT)} is not valid JSON and was ignored ({e})")
        return {}


def added_date(path):
    """Date the file was first committed, falling back to its modified time."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%cs", "--", str(path.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        ).stdout.split()
        if out:
            return out[-1]
    except Exception:
        pass
    return datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()


def title_from(stem):
    base, num = split_prefix(stem)
    base = re.sub(r"[_-]+", " ", base).strip()
    if not base or CAMERA.match(base):
        base = "Untitled"
    return base, num


def save_webp(im, size, dest, quality):
    copy = im.copy()
    copy.thumbnail((size, size), Image.LANCZOS)
    copy.save(dest, "WEBP", quality=quality, method=5)
    return copy.size


def process(f, meta, series_id, medium):
    rel = f.relative_to(ART).as_posix()
    wid = "w" + h8(rel)
    ext = f.suffix.lower()
    title, num = title_from(f.stem)
    date = added_date(f)
    work = {
        "id": wid,
        "title": str(meta.get("title") or title),
        "series": series_id or "",
        "year": str(meta.get("year") or date[:4]),
        "medium": str(meta.get("medium", medium)),
        "desc": str(meta.get("description", "")),
        "_num": num, "_date": date, "_file": f.name,
    }
    try:
        if ext in VIDEO:
            shutil.copy2(f, IMG / (wid + ext))
            work.update(kind="video", src=f"img/{wid}{ext}")
        elif ext in GIF:
            shutil.copy2(f, IMG / (wid + ".gif"))
            with Image.open(f) as im:
                work["w"], work["h"] = im.size
            work["src"] = f"img/{wid}.gif"
        else:
            with Image.open(f) as im:
                im = ImageOps.exif_transpose(im)
                alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
                im = im.convert("RGBA" if alpha else "RGB")
                work["w"], work["h"] = save_webp(im, FULL_SIZE, IMG / f"{wid}.webp", 86)
                save_webp(im, THUMB_SIZE, IMG / f"{wid}-t.webp", 80)
            work["src"] = f"img/{wid}.webp"
            work["thumb"] = f"img/{wid}-t.webp"
    except Exception as e:
        warn(f"could not read art/{rel} ({e}); it was skipped")
        return None
    print(f"  ok  {rel}")
    return work


def collect(folder, info, series_id, medium):
    files = []
    for p in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        if not p.is_file() or p.name.startswith((".", "_")):
            continue
        if p.suffix.lower() in SUPPORTED:
            files.append(p)
        elif p.suffix.lower() not in {".md", ".json", ".txt"}:
            warn(f"art/{p.relative_to(ART).as_posix()} is not a supported image or video and was skipped")
    per_work = info.get("works") or {}
    items = [w for w in (process(p, per_work.get(p.name, {}), series_id, medium) for p in files) if w]
    # Inside a series: numbered files (01-, 02-) first in number order, then newest first.
    items.sort(key=lambda w: w["_file"].lower())
    items.sort(key=lambda w: w["_date"], reverse=True)
    items.sort(key=lambda w: (w["_num"] is None, w["_num"] or 0))
    for i, w in enumerate(items):
        w["rank"] = i
    return items


def main():
    site = load_json(ROOT / "site.json")
    medium = site.get("defaultMedium", "Procreate")
    if OUT.exists():
        shutil.rmtree(OUT)
    IMG.mkdir(parents=True)

    series, works = [], []
    if ART.exists():
        print("art/ (uncategorized)")
        works += collect(ART, load_json(ART / "_info.json"), None, medium)
        folders = sorted((d for d in ART.iterdir() if d.is_dir() and not d.name.startswith((".", "_"))),
                         key=lambda d: d.name.lower())
        for d in folders:
            info = load_json(d / "_info.json")
            name, num = split_prefix(d.name)
            sid = "s" + h8(d.name)
            print(f"art/{d.name}/")
            items = collect(d, info, sid, medium)
            entry = {
                "id": sid,
                "name": str(info.get("name") or name or d.name),
                "desc": str(info.get("description", "")),
                "_order": info.get("order", num if num is not None else 10_000),
            }
            cover = info.get("cover")
            if cover:
                match = next((w for w in items if w["_file"] == cover), None)
                if match:
                    entry["cover"] = match["id"]
                else:
                    warn(f'cover "{cover}" in art/{d.name}/_info.json was not found in that folder')
            series.append(entry)
            works += items

    series.sort(key=lambda s: s["name"].lower())
    series.sort(key=lambda s: s["_order"] if isinstance(s["_order"], (int, float)) else 10_000)
    # "All" view: newest first.
    works.sort(key=lambda w: w["_file"].lower())
    works.sort(key=lambda w: w["_date"], reverse=True)

    featured = []
    for ref in site.get("featured", []) or []:
        ref = str(ref).strip().lstrip("/")
        ref = ref[4:] if ref.startswith("art/") else ref
        fid = "w" + h8(ref)
        if any(w["id"] == fid for w in works):
            featured.append(fid)
        else:
            warn(f'featured image "{ref}" in site.json was not found under art/')

    def clean(d):
        return {k: v for k, v in d.items() if not k.startswith("_")}

    public_site = {k: site[k] for k in ("name", "tagline", "bio", "email", "links", "accent") if k in site}
    data = {"site": public_site, "series": [clean(s) for s in series],
            "works": [clean(w) for w in works], "featured": featured}

    template = (ROOT / "index.html").read_text(encoding="utf-8")
    marker = '<script id="app-data" type="application/json">{}</script>'
    if marker not in template:
        sys.exit("index.html is missing the app-data block; restore it from the original template.")
    blob = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    page = template.replace(marker, f'<script id="app-data" type="application/json">{blob}</script>')

    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    name = site.get("name", "Justin’s ArtVerse")
    page = re.sub(r"<title>.*?</title>", lambda m: f"<title>{esc(name)}</title>", page, count=1, flags=re.S)
    if site.get("description"):
        page = re.sub(r'<meta name="description" content="[^"]*">',
                      lambda m: f'<meta name="description" content="{esc(site["description"])}">', page, count=1)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / ".nojekyll").write_text("")

    print(f"\nBuilt {len(works)} works in {len(series)} series into _site/")
    if warnings:
        print(f"{len(warnings)} warning(s); see above.")


if __name__ == "__main__":
    main()
