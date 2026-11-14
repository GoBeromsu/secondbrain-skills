#!/usr/bin/env python3
"""Print the preview image each page declares, one JSON line per page.

Usage: thumbnail.py <url> [<url> ...]

Output per page: {page, image, content_type}. `image` is the page's og:image (or twitter:image)
and is null when the page declares none; `content_type` is what the image URL answers with.
"""
import json, re, sys, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
META = re.compile(r"<meta\b[^>]*>", re.I)
ATTR = re.compile(r'([\w:-]+)\s*=\s*["\']([^"\']*)["\']')
KEYS = ("og:image", "og:image:url", "og:image:secure_url", "twitter:image")


def declared(html):
    found = {}
    for tag in META.findall(html):
        attrs = {k.lower(): v for k, v in ATTR.findall(tag)}
        key = (attrs.get("property") or attrs.get("name") or "").lower()
        if key in KEYS and attrs.get("content"):
            found.setdefault(key, attrs["content"])
    return next((found[k] for k in KEYS if k in found), None)


def fetch(url, limit=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read(limit) if limit else r.read(), r.headers.get("Content-Type", "")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for page in sys.argv[1:]:
        row = {"page": page, "image": None, "content_type": None}
        try:
            html, _ = fetch(page, 400_000)
            found = declared(html.decode("utf-8", "replace"))
            if found:
                row["image"] = urllib.parse.urljoin(page, found.replace("&amp;", "&"))
                _, row["content_type"] = fetch(row["image"], 64)
        except Exception as e:
            row["error"] = str(e)
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
