#!/usr/bin/env python3
"""Checks links between the pages of the site.

    python3 scripts/check_links.py              # internal links only
    python3 scripts/check_links.py --external   # also request external URLs

Checks: every href/src/srcset (and og:image/og:url, and url() in CSS) resolves to a file in the repo (directory links must
end with "/"), every #fragment exists on its target page, canonical URLs match
the page, EN/RU alternates and the language switcher point at each other, and
every page is reachable from the home page. Exits with 1 on any error.
"""
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://hexvale.dev"
HOST = urlsplit(SITE).netloc
SKIP_DIRS = {".git", "scripts", "node_modules"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.lang = None
        self.has_title = False
        self.canonical = None
        self.og_url = None
        self.alternates = {}
        self.lang_switch = {}
        self._nav_depth = 0
        self._lang_nav_depth = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self.has_title = True
        elif tag == "nav":
            self._nav_depth += 1
            if "lang" in a.get("class", "").split():
                self._lang_nav_depth = self._nav_depth
        elif tag == "link":
            rel = a.get("rel", "").split()
            if "canonical" in rel:
                self.canonical = a.get("href")
            if "alternate" in rel and a.get("hreflang"):
                self.alternates[a["hreflang"]] = a.get("href")
        elif tag == "meta" and a.get("property") in ("og:image", "og:url"):
            self.links.append((tag, a["property"], a.get("content", "")))
            if a["property"] == "og:url":
                self.og_url = a.get("content")
        elif tag == "a" and self._lang_nav_depth is not None and "href" in a:
            self.lang_switch[a.get("lang")] = a["href"]
        for attr in ("href", "src"):
            if attr in a:
                self.links.append((tag, a.get("rel", ""), a[attr]))
        for candidate in a.get("srcset", "").split(","):
            if candidate.strip():
                self.links.append((tag, "srcset", candidate.split()[0]))

    def handle_endtag(self, tag):
        if tag == "nav":
            if self._lang_nav_depth == self._nav_depth:
                self._lang_nav_depth = None
            self._nav_depth -= 1


def url_of(path):
    rel = path.relative_to(ROOT).as_posix()
    return "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)


def file_of(url_path):
    target = ROOT / unquote(url_path).lstrip("/")
    if url_path.endswith("/"):
        target = target / "index.html"
    return target


def main():
    check_external = "--external" in sys.argv[1:]
    files = sorted(
        p for p in ROOT.rglob("*.html")
        if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts)
    )
    pages = {}
    for f in files:
        parser = Page()
        parser.feed(f.read_text(encoding="utf-8"))
        pages[url_of(f)] = parser

    errors, external, graph = [], set(), {}
    checked = 0

    for url, page in pages.items():
        here = SITE + url
        graph[url] = set()

        if not page.lang:
            errors.append(f"{url}: <html> has no lang")
        if not page.has_title:
            errors.append(f"{url}: no <title>")
        if page.canonical != here:
            errors.append(f"{url}: canonical is {page.canonical!r}, expected {here!r}")
        if page.og_url != here:
            errors.append(f"{url}: og:url is {page.og_url!r}, expected {here!r}")

        for tag, rel, href in page.links:
            full = urljoin(here, href)
            parts = urlsplit(full)
            if parts.scheme in ("mailto", "tel"):
                continue
            if parts.netloc != HOST:
                external.add(full)
                continue
            checked += 1
            if parts.scheme != "https":
                errors.append(f"{url}: {href} should use https")
            path = parts.path or "/"
            target = file_of(path)
            if not target.is_file():
                hint = " (add a trailing /)" if (ROOT / path.lstrip("/")).is_dir() else ""
                errors.append(f"{url}: <{tag}> {href} -> missing {path}{hint}")
                continue
            if parts.fragment:
                target_url = url_of(target) if target.suffix == ".html" else None
                if target_url in pages and parts.fragment not in pages[target_url].ids:
                    errors.append(f"{url}: {href} -> no id={parts.fragment!r} on {target_url}")
            if tag == "a" and target.suffix == ".html":
                graph[url].add(url_of(target))

        for code, href in page.alternates.items():
            alt_url = urlsplit(href).path
            if code == "x-default":
                continue
            if alt_url not in pages:
                errors.append(f"{url}: hreflang={code} -> missing page {alt_url}")
                continue
            back = pages[alt_url].alternates.get(page.lang)
            if back != here:
                errors.append(f"{url}: {alt_url} does not link back with hreflang={page.lang}")
            if pages[alt_url].lang != code:
                errors.append(f"{url}: hreflang={code} points to a page with lang={pages[alt_url].lang}")
        if page.alternates.get(page.lang) != here:
            errors.append(f"{url}: no hreflang={page.lang} alternate pointing at itself")

        if not page.lang_switch:
            errors.append(f"{url}: no language switcher")
        for code, href in page.lang_switch.items():
            if SITE + href != page.alternates.get(code):
                errors.append(f"{url}: language switch {code} -> {href} differs from hreflang alternate")

    for css in sorted(ROOT.glob("assets/**/*.css")):
        css_url = url_of(css)
        for ref in re.findall(r'url\(\s*["\']?(/[^"\')]+)', css.read_text(encoding="utf-8")):
            checked += 1
            if not file_of(ref).is_file():
                errors.append(f"{css_url}: url({ref}) -> missing file")

    reachable, queue = {"/"}, ["/"]
    while queue:
        for nxt in graph.get(queue.pop(), ()):
            if nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)
    for url in sorted(set(pages) - reachable):
        errors.append(f"{url}: not reachable by links from /")

    if check_external:
        for link in sorted(external):
            try:
                req = urllib.request.Request(link, method="HEAD", headers={"User-Agent": "link-check"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    status = resp.status
            except Exception as exc:  # noqa: BLE001
                status = getattr(exc, "code", None) or exc
            ok = isinstance(status, int) and status < 400
            print(f"  external {'ok ' if ok else 'ERR'} {status}  {link}")
            if not ok:
                errors.append(f"external link failed: {link} ({status})")

    print(f"{len(pages)} pages, {checked} internal links, {len(external)} external links")
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
