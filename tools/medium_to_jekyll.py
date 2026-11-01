#!/usr/bin/env python3
"""Convert a Medium export into Jekyll posts, downloading images locally.

How to get the export: https://medium.com/me/export (Medium emails you a zip).

Usage:
    pip install -r tools/requirements.txt
    python tools/medium_to_jekyll.py ~/Downloads/medium-export.zip --site .

The input can be the .zip, the unzipped folder, or its posts/ subfolder.
Re-running is safe: existing posts are skipped unless --overwrite is given.

What it does for each post:
  * writes _posts/YYYY-MM-DD-slug.md with front matter (title, subtitle,
    date, categories, cover, description, medium_url)
  * downloads every image to assets/images/<category>/<slug>/ and rewrites
    the links, so the site no longer depends on Medium's CDN
  * guesses a section (category) from keywords; check the report afterwards
  * writes tools/migration_report.csv so you can review and fix categories
"""
import argparse
import csv
import json
import re
import sys
import tempfile
import time
import zipfile
from datetime import date as _date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    from bs4 import BeautifulSoup
    from markdownify import markdownify as to_markdown
except ImportError:
    sys.exit("Missing dependencies. Run: pip install -r tools/requirements.txt")

USER_AGENT = "Mozilla/5.0 (compatible; medium-to-jekyll/1.0)"
SECTIONS = ["hiking", "travel", "data-science", "coding", "linux",
            "raspberry-pi", "thoughts", "journals"]

# Keyword hints used to guess a section. Edit freely; the report lets you
# check every guess afterwards.
CATEGORY_RULES = {
    "hiking": ["hike", "hiking", "trek", "trail", "summit", "peak", "camp", "mountain", "ridge"],
    "travel": ["travel", "trip", "itinerary", "flight", "journey", "visa", "hostel", "tour", "backpack"],
    "data-science": ["data science", "machine learning", "dataset", "pandas", "regression",
                     "model", "neural", "analysis", "kaggle", "statistic"],
    "coding": ["python", "javascript", "code", "programming", "function", "api", "github", "algorithm"],
    "linux": ["linux", "ubuntu", "terminal", "bash", "shell", "kernel", "debian", "arch linux"],
    "raspberry-pi": ["raspberry", "raspberry pi", "gpio", "arduino", "sensor", "pi zero"],
    "journals": ["dear diary", "today i", "this week", "journal"],
}

EXT_BY_TYPE = {
    "image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif",
    "image/webp": ".webp", "image/svg+xml": ".svg",
}


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:70].strip("-") or "untitled"


def guess_category(title, text):
    haystack = (title + " " + title + " " + text[:2500]).lower()
    best, best_score = None, 0
    for cat, words in CATEGORY_RULES.items():
        score = sum(haystack.count(w) for w in words)
        if score > best_score:
            best, best_score = cat, score
    return best


def bigger(url):
    """Ask Medium's CDN for a larger rendition than the one in the export."""
    url = re.sub(r"/max/\d+/", "/max/1600/", url)
    return re.sub(r"resize:fit:\d+", "resize:fit:1600", url)


def download(url, dest_dir, stem):
    """Download an image; return the saved Path or None."""
    candidates = [bigger(url)]
    if candidates[0] != url:
        candidates.append(url)
    for candidate in candidates:
        try:
            req = Request(candidate, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=30) as resp:
                data = resp.read()
                ctype = resp.headers.get("Content-Type", "").split(";")[0].strip()
        except (HTTPError, URLError, TimeoutError, OSError):
            continue
        if not data:
            continue
        ext = EXT_BY_TYPE.get(ctype) or Path(urlparse(candidate).path).suffix or ".jpg"
        if len(ext) > 5:
            ext = ".jpg"
        dest_dir.mkdir(parents=True, exist_ok=True)
        path = dest_dir / f"{stem}{ext}"
        path.write_bytes(data)
        time.sleep(0.2)
        return path
    return None


def find_posts_dir(root):
    root = Path(root)
    if (root / "posts").is_dir():
        return root / "posts"
    if any(root.glob("*.html")):
        return root
    # zip extracted into a nested folder
    for sub in root.rglob("posts"):
        if sub.is_dir() and any(sub.glob("*.html")):
            return sub
    return None


def first_paragraph(body):
    for p in body.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) >= 40:
            return text
    return ""


def yaml_str(value):
    # JSON strings are valid YAML double-quoted scalars.
    return json.dumps(value, ensure_ascii=False)


def convert(path, site, args, report):
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    is_draft = path.name.startswith("draft_")

    title_el = soup.select_one("h1.p-name") or soup.find("h1")
    title = title_el.get_text(" ", strip=True) if title_el else path.stem
    body = soup.select_one('section[data-field="body"]') or soup.select_one(".e-content")
    if body is None:
        print(f"  ! skipped (no body found): {path.name}")
        return

    # Date: published time, else filename prefix, else today.
    post_date = None
    time_el = soup.select_one("time.dt-published")
    if time_el and time_el.get("datetime"):
        post_date = time_el["datetime"][:10]
    if not post_date:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
        post_date = m.group(1) if m else _date.today().isoformat()

    subtitle_el = soup.select_one('section[data-field="subtitle"]')
    subtitle = subtitle_el.get_text(" ", strip=True) if subtitle_el else ""
    canonical = soup.select_one("a.p-canonical")
    medium_url = canonical["href"] if canonical and canonical.get("href") else ""

    # Medium repeats the title/subtitle at the top of the body.
    for el in body.select(".graf--title, .graf--subtitle"):
        el.decompose()

    # Medium uses h3/h4 for headings; on this site the post title is the h1,
    # so shift them up one level (h3 -> h2, h4 -> h3).
    for h in body.find_all(["h3", "h4"]):
        h.name = "h2" if h.name == "h3" else "h3"

    description = subtitle or first_paragraph(body)
    plain_text = body.get_text(" ", strip=True)
    category = args.category or guess_category(title, plain_text) or args.default_category
    guessed = not args.category

    slug = slugify(title)
    post_file = site / "_posts" / f"{post_date}-{slug}.md"
    if post_file.exists() and not args.overwrite:
        print(f"  = exists, skipped: {post_file.name}")
        return

    # Images -> local files; figures -> image + italic caption.
    img_dir = site / "assets" / "images" / category / slug
    cover = ""
    ok = failed = 0
    counter = 0
    for fig in body.find_all("figure"):
        img = fig.find("img")
        cap_el = fig.find("figcaption")
        caption = cap_el.get_text(" ", strip=True) if cap_el else ""
        new_nodes = []
        if img is not None and img.get("src"):
            counter += 1
            src = img["src"]
            if not args.no_images:
                saved = download(src, img_dir, f"image-{counter:02d}")
                if saved:
                    src = "/" + saved.relative_to(site).as_posix()
                    ok += 1
                else:
                    failed += 1
                    print(f"  ! image download failed: {src}")
            if not cover and src.startswith("/assets/"):
                cover = src
            p = soup.new_tag("p")
            p.append(soup.new_tag("img", src=src, alt=img.get("alt") or caption))
            new_nodes.append(p)
        if caption:
            p = soup.new_tag("p")
            em = soup.new_tag("em")
            em.string = caption
            p.append(em)
            new_nodes.append(p)
        for node in new_nodes:
            fig.insert_before(node)
        fig.decompose()

    markdown = to_markdown(str(body), heading_style="ATX", bullets="-")
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip() + "\n"

    front = ["---", f"title: {yaml_str(title)}"]
    if subtitle:
        front.append(f"subtitle: {yaml_str(subtitle)}")
    if description:
        front.append(f"description: {yaml_str(description[:200])}")
    front.append(f"date: {post_date}")
    front.append(f"categories: [{category}]")
    if cover:
        front.append(f"cover: {cover}")
    if medium_url:
        front.append(f"medium_url: {yaml_str(medium_url)}")
    if is_draft:
        front.append("published: false")
    front.append("---")

    post_file.parent.mkdir(parents=True, exist_ok=True)
    post_file.write_text("\n".join(front) + "\n\n" + markdown, encoding="utf-8")
    print(f"  + {post_file.name}  [{category}{'?' if guessed else ''}]  images ok={ok} failed={failed}")
    report.append({
        "post": post_file.name, "title": title, "date": post_date,
        "category": category, "category_was_guessed": "yes" if guessed else "no",
        "draft": "yes" if is_draft else "no",
        "images_downloaded": ok, "images_failed": failed,
    })


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", help="Medium export: .zip, folder, or its posts/ folder")
    ap.add_argument("--site", default=".", help="Root of the Jekyll site (default: current folder)")
    ap.add_argument("--category", choices=SECTIONS, help="Force every post into this section instead of guessing")
    ap.add_argument("--default-category", choices=SECTIONS, default="thoughts",
                    help="Section used when no keywords match (default: thoughts)")
    ap.add_argument("--include-drafts", action="store_true", help="Also convert drafts (written with published: false)")
    ap.add_argument("--no-images", action="store_true", help="Leave image links pointing at Medium instead of downloading")
    ap.add_argument("--overwrite", action="store_true", help="Replace posts that already exist")
    args = ap.parse_args()

    site = Path(args.site).resolve()
    export = Path(args.export).expanduser()
    if not export.exists():
        sys.exit(f"Not found: {export}")

    tmp = None
    if export.suffix.lower() == ".zip":
        tmp = tempfile.TemporaryDirectory(prefix="medium-export-")
        with zipfile.ZipFile(export) as zf:
            zf.extractall(tmp.name)
        export = Path(tmp.name)

    posts_dir = find_posts_dir(export)
    if posts_dir is None:
        sys.exit("Could not find a posts/ folder with .html files in the export.")

    files = sorted(posts_dir.glob("*.html"))
    if not args.include_drafts:
        files = [f for f in files if not f.name.startswith("draft_")]
    print(f"Converting {len(files)} post(s) from {posts_dir} into {site}\n")

    report = []
    for f in files:
        convert(f, site, args, report)

    if report:
        report_path = site / "tools" / "migration_report.csv"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(report[0].keys()))
            writer.writeheader()
            writer.writerows(report)
        failed = sum(r["images_failed"] for r in report)
        print(f"\nDone: {len(report)} post(s) written. Report: {report_path}")
        if failed:
            print(f"{failed} image(s) failed to download; those still point at Medium. Re-run with --overwrite to retry.")
        print("Next: open the report, fix any wrong categories (edit `categories:` in each post), then preview the site.")
    else:
        print("\nNothing written.")

    if tmp:
        tmp.cleanup()


if __name__ == "__main__":
    main()
