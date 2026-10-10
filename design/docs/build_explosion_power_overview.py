"""Render the current Power-based design without the retired chant calculator."""
from html import escape
from pathlib import Path
import re


def build(data, root):
    e = escape
    out = root / '惠惠当前设计总览.html'
    previous_ids = re.findall(r'\bid="([^"]+)"', out.read_text(encoding='utf-8')) if out.exists() else []
    core = data['core']
    system_ids = [s['destination'] for s in data['systems']]

    def ul(items):
        return '<ul>' + ''.join('<li>' + e(x) + '</li>' for x in items) + '</ul>'

    rows = ''.join('<tr><th scope="row"><a href="#' + e(s['destination']) + '">' + e(s['name']) +
                   '</a></th><td>' + e(s['size_suggestion']) + '</td><td>' + e(s['ports']) + '</td><td>' +
                   e(s['status']) + '</td></tr>' for s in data['systems'])
    cards = ''.join('<tr><th scope="row">' + e(c['name']) + '</th><td>' + str(c['cost']) + '费 · ' + e(c['type']) +
                    '</td><td>' + e(c['text']) + '</td><td>' + e(c['role']) + '</td></tr>' for c in data['sample_cards'])
    sections = []
    for system in data['systems']:
        key = system['id']
        body = '<p>' + e(system['loop']) + '</p><p>' + e(system['connection']) + '</p>'
        if key == 'explosion':
            body = '<blockquote>' + e(core['keyword']) + '</blockquote><p>' + e(core['formula']) + '</p>' + body
            body += '<h3>关键判断</h3>' + ul(core['design_findings'])
            body += '<h3>第一轮样例</h3><p class="muted">费用与数值为建议，尚未验证。</p><div class="scroll"><table><thead><tr><th>卡牌</th><th>费用／类型</th><th>卡面草案</th><th>用途</th></tr></thead><tbody>' + cards + '</tbody></table></div>'
            body += '<details><summary>建议细则（尚待确认）</summary>' + ul(core['recommended_rulings']) + '</details>'
        elif key == 'declaration':
            body = '<blockquote>' + e(data['declaration']['keyword']) + '</blockquote>' + body
        elif key == 'storage':
            body += '<p class="muted">关键词原文：</p><blockquote>' + e(data['storage_system']['keyword']) + '</blockquote>'
        elif key == 'skill_points':
            body += '<blockquote>' + e(data['skill_points']['user_text']) + '</blockquote>'
        body += '<h3>待设计</h3>' + ul(system['gaps'])
        sections.append('<section id="' + e(system['destination']) + '"><h2>' + e(system['name']) + '</h2><p class="muted">' + e(system['role']) + '</p>' + body + '</section>')
    # Keep old incoming fragment links usable, directing them to the history notice.
    aliases = ''.join('<span id="' + e(x, quote=True) + '"></span>' for x in dict.fromkeys(previous_ids)
                      if x not in system_ids + ['overview', 'history'])
    style = '''
:root{color-scheme:light;--bg:#f7f3ec;--ink:#302b26;--line:#d9d0c4;--accent:#96352e}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.85 'Segoe UI','Microsoft YaHei',sans-serif}
main{max-width:1160px;margin:auto;padding:40px 32px 70px}h1{font-size:36px;line-height:1.4}h2{font-size:27px}h3{font-size:18px}
a{color:var(--accent);text-underline-offset:4px}section{padding:28px 0;border-top:1px solid var(--line);scroll-margin-top:18px}.muted,footer{color:#726a61;font-size:14px}
blockquote{margin:18px 0;padding:16px 22px;border-left:3px solid var(--accent);background:#f0e9df;font-weight:600}
nav{display:flex;flex-wrap:wrap;gap:12px 24px;margin:25px 0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;min-width:760px;font-size:14px}th,td{padding:12px 16px 12px 0;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--accent)}li{margin:7px 0}summary{cursor:pointer}details{margin:20px 0}footer{margin-top:30px}
@media(max-width:700px){main{padding:22px 18px 50px}h1{font-size:29px}}
'''
    page = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>惠惠当前设计 · 爆裂Power</title><style>' + style + '</style></head><body><main><header><p class="muted">' + e(data['date']) + '</p><h1>惠惠当前设计 · 爆裂Power</h1><p><b>出牌蓄积，停手引爆。</b></p><p><a href="惠惠角色体系设计.md">完整体系分析与样例牌（Markdown）</a> · <a href="原版五职业与华恋及惠惠体系表.html">职业体系对照</a></p></header><nav>' + ''.join('<a href="#' + e(s['destination']) + '">' + e(s['name']) + '</a>' for s in data['systems']) + '</nav><section id="overview"><h2>体系分工</h2><p class="muted">规模为工作建议；旧卡不计作新版成品卡池。</p><div class="scroll"><table><thead><tr><th>体系</th><th>规模建议</th><th>端口</th><th>状态</th></tr></thead><tbody>' + rows + '</tbody></table></div></section>' + ''.join(sections) + '<section id="history">' + aliases + '<h2>上一版已归档</h2><p>旧吟唱、爆裂牌生成与减费、下一次增伤及其资源账，不作为当前规则。</p><p><a href="docs/历史/吟唱版设计_2026-10-09.json">查看完整旧数据与文档原文</a></p></section><footer>' + e(data['status']) + '<p><a href="docs/当前设计总览.json">结构化设计</a> · <a href="README.md">设计资料导航</a></p></footer></main></body></html>'
    out.write_text(page, encoding='utf-8')
    portable = page
    for href in re.findall(r'href="([^"]+)"', page):
        if not href.startswith(('#', 'http:', 'https:', 'file:')):
            filename, separator, fragment = href.partition('#')
            absolute = (root / filename).resolve().as_uri() + separator + fragment
            portable = portable.replace('href="' + href + '"', 'href="' + absolute + '"')
    target = Path.home() / '.agent' / 'diagrams'
    target.mkdir(exist_ok=True, parents=True)
    (target / 'megumin-current-design.html').write_text(portable, encoding='utf-8')
    print('Built current Power overview:', out)
