#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_docs: data/docs.json -> posts/docs-checklist.html (자금별 신청 서류 체크리스트).
원칙: 서류 항목과 원문 URL은 data/docs.json 에만 둔다. 생성기 실행 = id 중복·필수 필드·URL 형식 검증.
헤더·푸터·스크립트는 게시글 관례(상대 경로·비영리 저장)를 따른다. 수치는 넣지 않는다."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = json.loads((ROOT / 'data' / 'docs.json').read_text(encoding='utf-8'))
OUT = ROOT / 'posts' / 'docs-checklist.html'
VER = '20260929a'
CSS = '../style.css?v=' + VER


def validate():
    errs = []
    ids = [d['id'] for d in DOCS['items']]
    if len(ids) != len(set(ids)):
        errs.append('docs.id 중복')
    for d in DOCS['items']:
        for k in ('id', 'name', 'source', 'source_url', 'common', 'extra'):
            if not d.get(k):
                errs.append('%s 필드 누락: %s' % (d.get('id', '?'), k))
        if not re.match(r'^https://', d.get('source_url', '')):
            errs.append('%s source_url 형식 오류' % d.get('id'))
    if DOCS.get('verified_at') and not re.match(r'^\d{4}-\d{2}-\d{2}', str(DOCS['verified_at'])):
        errs.append('docs.verified_at 형식 오류')
    return errs


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;')


def docbox(d):
    labels = d['common'] + d['extra']
    rows = ''.join('<label class="ck"><input type="checkbox"><span>%s</span></label>' % esc(x) for x in labels)
    return ('<div class="docbox"><h3>%s</h3><p class="doc-src"><b>원문</b> '
            '<a href="%s" rel="nofollow noopener">%s</a></p>%s</div>'
            % (esc(d['name']), d['source_url'], esc(d['source']), rows))


def main():
    errs = validate()
    if errs:
        print('BUILD FAIL:')
        [print(' -', e) for e in errs]
        raise SystemExit(1)
    head = ('<!DOCTYPE html>\n<html lang="ko"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>정책자금 신청 서류 체크리스트 — 자금별 공통·추가 서류 | 자금레이더</title>\n'
            '<meta name="description" content="정책자금 신청에 필요한 공통·추가 서류를 자금별로 체크합니다. 체크 상태는 이 브라우저에만 저장되고, 각 자금의 공고 원문 링크를 함께 보여줍니다">\n'
            '<link rel="canonical" href="https://jaegeum.hub77a.com/posts/docs-checklist.html">\n'
            '<link rel="stylesheet" href="%s"></head>\n<body>\n' % CSS)
    head += ('<header class="hwrap"><div class="hrow">\n'
             '<a class="logo" href="../index.html">자금레이더</a>\n'
             '<nav><a href="../index.html?v=20260918#fundboard">정책자금</a><a href="eligibility-check.html">자격 자가진단</a>'
             '<a href="../index.html?v=20260918#guides">가이드</a><a href="../about.html?v=20260918">소개</a><a href="../contact.html?v=20260918">광고·문의</a></nav>\n'
             '</div></header>\n<main class="hwrap">\n')
    body = '<h1>정책자금 신청 서류 체크리스트</h1>\n'
    body += ('<p class="meta"><b>발행 2026-09-27 · 상태: 유효 · 분류: 정책자금 · %s그룹 서류</b></p>\n' % len(DOCS['items']))
    body += ('<p>직접대출이든 대리대출이든 신청 단계에서 공통으로 요구하는 서류는 사업자등록증명·소득금액증명·건강보험 가입자 확인 세 가지입니다. '
             '여기에 자금별 추가 서류가 얹힙니다. 카드마다 그 추가 서류를 넣어 두었습니다. 체크 표시는 이 브라우저에만 저장되고 서버로 전송되지 않습니다.</p>\n')
    body += ('<div class="ck-toolbar"><button class="btn sm" id="ck-reset" type="button">모두 해제</button>'
             '<button class="btn ghost sm" id="ck-print" type="button">인쇄</button>'
             '<span class="dim small">체크 상태는 브라우저에 저장됩니다.</span></div>\n')
    body += ''.join(docbox(d) for d in DOCS['items'])
    body += ('<div class="notice">본 체크리스트는 소진공·중소벤처기업부 공고의 공통 요구 서류를 정리한 준비용 목록이며, '
             '최종 구비 서류는 신청 시점의 공고 원문과 접수 창구 안내가 우선합니다. 각 자금 카드의 원문 링크로 교정하세요.</div>\n')
    body += ('<h2>같이 읽기</h2>\n<ul>\n'
             '<li><a href="policy-fund-map.html">소상공인 정책자금 2026 총정리 — 자금별 한도·금리·자격</a></li>\n'
             '<li><a href="eligibility-check.html">정책자금 자격 자가진단 — 7문항 30초</a></li>\n'
             '<li><a href="udaegumri-5types-2026.html">정책자금 신청 흐름 완전정복 — 직접·대리·보증서부 3단계</a></li>\n</ul>\n')
    body += ('</main>\n<footer>© 2026 자금레이더 · <a href="../about.html?v=20260918">소개</a> · '
             '<a href="../privacy.html?v=20260918">개인정보처리방침</a> · <a href="../terms.html?v=20260918">이용약관</a> · '
             '<a href="../contact.html?v=20260918">광고·문의</a><br>본 사이트는 소상공인 정책자금·공공조달 정보를 공식 공고 기준으로 정리하는 민간 정보 서비스입니다.\n'
             '<div class="sister" style="margin-top:10px">자매 사이트: <a href="https://sangsik.hub77a.com/">척척상식</a> · '
             '<a href="https://tech.hub77a.com/">테크한잔</a> · Perky Facts: '
             '<a href="https://www.instagram.com/perkyfacts/" rel="me">인스타그램</a> · '
             '<a href="https://www.threads.com/@perkyfacts" rel="me">스레드</a> · '
             '<a href="https://www.youtube.com/@Perky_Facts" rel="me">유튜브</a> · '
             '<a href="https://www.facebook.com/people/Perky-Facts/61594432972028" rel="me">페이스북</a></div></footer>\n<script>\n')
    body += ('(function(){var K="jageum-docs-2026";var b=document.querySelectorAll(".ck input");'
             'var s={};try{s=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}'
             'b.forEach(function(x,i){if(s[i])x.checked=true;x.addEventListener("change",function(){s[i]=x.checked;'
             'localStorage.setItem(K,JSON.stringify(s))})});'
             'document.getElementById("ck-reset").onclick=function(){s={};b.forEach(function(x){x.checked=false});localStorage.removeItem(K)};'
             'document.getElementById("ck-print").onclick=function(){window.print()};})();\n</script>\n</body></html>')
    OUT.write_text(head + body)
    print('docs-checklist.html built:', len(body), 'chars,', len(DOCS['items']), 'groups')


if __name__ == '__main__':
    main()
