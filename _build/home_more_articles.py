# -*- coding: utf-8 -*-
"""build_home 영구 안전망: tpl 치환 후 posts/ 전 편을 index.html의
'더 찾아보기' 섹션에 멱등 연결한다 (2026-10-20 — 07:40 재빌드가 backfill
섹션을 통째로 지운 사고의 재발 방지). home_link_backfill과 같은 마커 사용."""
import glob
import os
import re
import html as H

MARK_S = "<!-- more-articles:begin -->"
MARK_E = "<!-- more-articles:end -->"


def title_of(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r"<title>(.*?)</title>", txt, re.S)
    t = (m.group(1) if m else "")
    t = re.split(r"\s*[|–—]\s*", t)[0].strip()
    return t or os.path.basename(path)[:-5]


def ensure_more_articles(html, root):
    """html 문자열에 posts/ 전 편 링크 섹션을 멱등 보장. (html, 추가편수) 반환."""
    files = sorted(glob.glob(os.path.join(root, "posts", "*.html")))
    head = html.split(MARK_S)[0]
    linked = set(re.findall(r"posts/([a-z0-9_-]+)\.html", head))
    todo = []
    for p in files:
        slug = os.path.basename(p)[:-5]
        if slug in ("404", "eligibility-check") or slug in linked:
            continue
        todo.append((slug, title_of(p)))
    if not todo and MARK_S in html:
        return html, 0
    lines = ['<li><a href="posts/%s.html">%s</a></li>' % (s, H.escape(t)) for s, t in todo]
    block = (MARK_S + "\n<section class=\"more-articles\">\n"
             "<h2>더 찾아보기</h2>\n<ul>\n" + "\n".join(lines) + "\n</ul>\n</section>\n" + MARK_E)
    if MARK_S in html:
        html = re.sub(re.escape(MARK_S) + r".*?" + re.escape(MARK_E), block, html, flags=re.S)
    else:
        if "</main>" in html:
            html = html.replace("</main>", block + "\n</main>", 1)
        else:
            html = html.replace("</body>", block + "\n</body>", 1)
    return html, len(todo)
