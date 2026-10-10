"""Build the three-column, offline Megumin naming and art reference table."""
from pathlib import Path
from html import escape as esc
from collections import Counter
import base64
import csv
import io
import json
import mimetypes

from build_lore_archetypes import SOURCES as EXISTING_SOURCES

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
DATA = json.loads((ROOT / 'docs/惠惠卡牌命名与配图素材.json').read_text(encoding='utf-8'))
ROWS = DATA['rows']
OUT = ROOT / '惠惠卡牌命名与配图素材表.html'
CSV_OUT = ROOT / '参考资料/惠惠卡牌命名与配图素材.csv'
SOURCES = {k: dict(v) for k, v in EXISTING_SOURCES.items()}
EXTRA = {
    'anime6': ('《爆焰》TV 第6话·爆裂尼特的求职', 'https://konosuba.com/bakuen/story/?mode=story6', '官方动画'),
    'anime11': ('《爆焰》TV 第11话·名物娘与森林恶魔', 'https://konosuba.com/bakuen/story/?mode=story11', '官方动画'),
    'b33': ('《爆焰》小说3·第3章', 'https://cgtranslations.me/2018/01/19/explosion-spinoff-3-chapter-3/', '非官方英译'),
    'b15full': ('《爆焰》小说1·第5章', 'https://cgtranslations.me/2018/01/12/explosion-1-chapter-5/', '非官方英译'),
    'b14full': ('《爆焰》小说1·第4章', 'https://cgtranslations.me/2018/01/12/explosion-spinoff-1-chapter-4/', '非官方英译'),
    'anime5wiki': ('《爆焰》TV 第5话·剧情定位', 'https://konosuba.fandom.com/wiki/Konosuba_Explosion_Episode_5', '二手剧情索引'),
    's202': ('本篇 TV 第二季第2话', 'https://konosuba.com/2nd/story/?id=02&mode=detail', '官方动画'),
    's202wiki': ('本篇 TV 第二季第2话·剧情定位', 'https://konosuba.fandom.com/wiki/Konosuba_Episode_12', '二手剧情索引'),
    'quartet1': ('《异世界四重奏》第一季故事页', 'https://isekai-quartet.com/story-s1.html', '官方动画'),
    'quartet2': ('《异世界四重奏》第二季故事页', 'https://isekai-quartet.com/story-s2.html', '官方动画'),
    'quartet7review': ('《四重奏》第一季第7话·画面与剧情定位', 'https://akananime.com/archives/15370', '二手分集记录'),
    'quartetfeats': ('《四重奏》动作索引·含躲避球片段', 'https://www.reddit.com/r/respectthreads/comments/sgp4uv/respect_the_isekai_quartet_isekai_quartet/', '二手片段索引'),
}
for key, (title, url, kind) in EXTRA.items():
    SOURCES[key] = dict(title=title, url=url, kind=kind)

ART = {}
still_dir = ROOT / '参考资料/卡牌命名配图素材'
for a in json.loads((still_dir / 'official_stills.json').read_text(encoding='utf-8')):
    ART[a['id']] = dict(label=a['label'], page_url=a['page_url'], image_url=a['image_url'], path=still_dir / a['file'])
quartet_dir = REPO / 'art/isekai-quartet-references-20261009'
for a in json.loads((quartet_dir / 'catalog.json').read_text(encoding='utf-8'))['items']:
    ART[a['id']] = dict(label='《四重奏》· ' + a['title'], page_url=a['source_page'], image_url=a['source_image'], path=quartet_dir / a['file'])

assert len({r['id'] for r in ROWS}) == len(ROWS)
for r in ROWS:
    assert all(s in SOURCES for s in r['sources']), r['id']
    if r['art']:
        assert ART[r['art']]['path'].is_file(), r['id']

USED_ART = {r['art']: ART[r['art']] for r in ROWS if r['art']}
URI = {k: 'data:' + (mimetypes.guess_type(str(a['path']))[0] or 'image/jpeg') + ';base64,' + base64.b64encode(a['path'].read_bytes()).decode('ascii') for k, a in USED_ART.items()}
GROUPS = list(dict.fromkeys(r['group'] for r in ROWS))
TAGS = list(dict.fromkeys(t for r in ROWS for t in r['tags']))


def link(url, title, css=''):
    return f'<a class="{css}" href="{esc(url, quote=True)}" target="_blank" rel="noopener noreferrer">{esc(title)} ↗</a>'


def refs(r):
    return '<details class="refs"><summary>词句来源 · ' + str(len(r['sources'])) + '</summary>' + ''.join(
        '<div>' + link(SOURCES[s]['url'], SOURCES[s]['title']) + '<small>' + esc(SOURCES[s]['kind']) + '</small></div>' for s in r['sources']) + '</details>'


def art_cell(r):
    art = ART.get(r['art'])
    kind = 'exact' if r['art_relation'] == '同场景' else ('pending' if not art else 'related')
    status = f'<span class="relation {kind}">{esc(r["art_relation"])}</span>'
    image_html = ''
    image_links = ''
    if art:
        image_html = f'<button class="preview" data-art="{r["art"]}" data-row="{r["id"]}" aria-label="放大{r["id"]}配图：{esc(r["name"], quote=True)}"><img src="{URI[r["art"]]}" alt="{esc(art["label"], quote=True)}" loading="lazy" decoding="async"><span>点击放大</span></button>'
        image_links = '<div class="art-links">' + link(art['page_url'], '官方剧照页') + link(art['image_url'], '原图') + '</div>'
    else:
        image_html = '<div class="pending-note">画面尚未取得 · 已保留定位建议</div>'
    extra = '<div class="art-links">' + link(r['art_extra_url'], r['art_extra']) + '</div>' if r.get('art_extra_url') else ''
    return status + image_html + f'<p class="art-note">{esc(r["art_note"])}</p>' + image_links + extra


def row_html(r):
    tags = ''.join(f'<button class="tag" data-tag="{esc(t, quote=True)}" aria-label="筛选用途：{esc(t, quote=True)}">{esc(t)}</button>' for t in r['tags'])
    return f'''<tr id="{r['id']}" data-id="{r['id']}">
<th scope="row" data-label="原本词语或句子"><div class="row-id"><a href="#{r['id']}">{r['id']}</a><span>{esc(r['form'])}</span></div><div class="original">{esc(r['original'])}</div><p class="working-name">中文索引：{esc(r['name'])}</p><button class="copy" data-copy="{r['id']}">复制原词句</button>{refs(r)}</th>
<td data-label="简要意思"><p class="meaning">{esc(r['meaning'])}</p><div class="tags">{tags}</div><small class="group-note">{esc(r['group'])}</small></td>
<td data-label="推荐配图">{art_cell(r)}</td></tr>'''


def csv_values(r):
    src = '\n'.join(SOURCES[s]['title'] + '：' + SOURCES[s]['url'] for s in r['sources'])
    art = ART.get(r['art'])
    artwork = r['art_relation'] + '。' + r['art_note']
    if art:
        artwork += '\n' + art['label'] + '\n官方页：' + art['page_url'] + '\n原图：' + art['image_url']
    if r.get('art_extra_url'):
        artwork += '\n' + r['art_extra'] + '：' + r['art_extra_url']
    return [f"{r['id']} | {r['original']}\n中文索引：{r['name']}\n{r['form']}\n{src}", r['meaning'], artwork]


csv_stream = io.StringIO(newline='')
writer = csv.writer(csv_stream)
writer.writerow(['原本词语或句子（含来源）', '简要意思', '推荐配图（含定位与链接）'])
writer.writerows(csv_values(r) for r in ROWS)
CSV_OUT.write_text(csv_stream.getvalue(), encoding='utf-8-sig', newline='')

art_metadata = {k: {key: value for key, value in a.items() if key != 'path'} for k, a in USED_ART.items()}
bundle = dict(**DATA, sources={k: SOURCES[k] for k in dict.fromkeys(s for r in ROWS for s in r['sources'])}, artwork=art_metadata, csv_rows={r['id']: csv_values(r) for r in ROWS})
bundle_json = json.dumps(bundle, ensure_ascii=False).replace('<', '\\u003c')
groups_html = ''.join(f'<option value="{esc(g, quote=True)}">{esc(g)}</option>' for g in GROUPS)
tags_html = ''.join(f'<option value="{esc(t, quote=True)}">{esc(t)}</option>' for t in TAGS)
counts = Counter(bool(r['art']) for r in ROWS)

PAGE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>惠惠 · 卡牌命名与配图素材表</title>
<style>
:root{--bg:#f5f2eb;--surface:#fffdf8;--border:#d8d0c4;--text:#28231e;--text-dim:#6c6156;--red:#98372e;--gold:#916319;--sage:#4c6855;--tint:#f2e8dc;--focus:#ac4637}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font-family:"Microsoft YaHei","Noto Sans SC",sans-serif;font-size:14px;line-height:1.7}button,input,select{font:inherit}a{color:var(--red);text-underline-offset:3px}button,a,input,select,summary{outline-offset:4px}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid var(--focus)}main{width:min(1440px,calc(100% - 64px));margin:0 auto 60px}header{padding:44px 0 25px;border-top:5px solid var(--red)}.eyebrow{color:var(--red);font:12px/1.5 Consolas,monospace;letter-spacing:2px}.heading{display:flex;gap:24px;align-items:end;justify-content:space-between}.heading>*{min-width:0}h1{font-family:"Noto Serif SC","SimSun",serif;font-size:clamp(30px,3.5vw,46px);font-weight:700;line-height:1.3;margin:10px 0 12px}.intro{margin:0;color:var(--text-dim);max-width:850px;font-size:15px}.stats{text-align:right;white-space:nowrap;line-height:1.9;color:var(--text-dim);font-size:12px}.stats strong{font:30px/1.2 Georgia,serif;color:var(--red)}.notes{margin-top:22px;padding:10px 15px;background:#eee8dd;border-left:3px solid var(--gold)}.notes summary{cursor:pointer;color:var(--text-dim)}.notes ul{margin:12px 0 2px;padding-left:21px}.notes li+li{margin-top:7px}.controls{display:grid;grid-template-columns:minmax(220px,2.2fr) repeat(3,minmax(120px,1fr));gap:12px;padding:18px 0 15px}.control{display:flex;flex-direction:column;gap:5px;font-size:12px;color:var(--text-dim);min-width:0}.control input,.control select{min-width:0;width:100%;height:40px;border:1px solid var(--border);background:var(--surface);border-radius:3px;color:var(--text);padding:0 11px}.table-tools{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:14px}.table-tools .actions{display:flex;gap:15px;flex-wrap:wrap;align-items:center}#result{font-size:13px;color:var(--text-dim)}.secondary,.copy{border:1px solid var(--border);background:transparent;padding:5px 10px;border-radius:3px;color:var(--text-dim);font-size:12px}.secondary:hover,.copy:hover{border-color:var(--red);color:var(--red)}.compact-label{font-size:12px;color:var(--text-dim);cursor:pointer}.table-wrap{border:1px solid var(--border);background:var(--surface);border-radius:3px}table{border-collapse:collapse;width:100%;table-layout:fixed}caption{text-align:left;padding:12px 18px;background:#eee7dc;border-bottom:1px solid var(--border);color:var(--text-dim);font-size:12px}col.words{width:29%}col.meaning-col{width:30%}col.art-col{width:41%}thead th{background:#e8dfd2;color:#554639;text-align:left;font-size:13px;padding:13px 18px;letter-spacing:.5px}tbody th,tbody td{text-align:left;vertical-align:top;padding:22px 18px;font-weight:400;border-top:1px solid var(--border);overflow-wrap:anywhere}tbody tr:hover{background:#faf5ec}tbody tr:target{background:#fff2dc;box-shadow:inset 4px 0 var(--gold)}tr[hidden]{display:none!important}.row-id{display:flex;gap:9px;align-items:baseline;color:var(--text-dim);font-size:11px;margin-bottom:9px}.row-id a{font:12px Consolas,monospace;color:var(--red);text-decoration:none;flex:none}.original{font-family:"Noto Serif SC","SimSun",serif;font-size:21px;font-weight:700;line-height:1.5}.working-name{font-size:12px;color:var(--text-dim);margin:10px 0}.meaning{margin:0 0 16px;line-height:1.85}.tags{display:flex;flex-wrap:wrap;gap:6px}.tag{color:var(--red);font-size:11px;border:1px solid #dec4b9;background:#fbf1e9;border-radius:3px;padding:2px 7px}.tag:hover{background:#f2dccc}.group-note{display:block;margin-top:13px;color:var(--text-dim);font-size:11px}.refs{margin-top:14px;font-size:11px;color:var(--text-dim)}.refs summary{cursor:pointer}.refs>div{padding:9px 0 0}.refs a{display:block;line-height:1.6}.refs small{font-size:10px;color:var(--text-dim)}.relation{display:inline-block;margin-bottom:9px;font-size:11px;border-radius:3px;padding:2px 7px;border:1px solid var(--border)}.relation.exact{color:var(--sage);border-color:#bed0ba;background:#edf4e9}.relation.related{color:var(--gold);background:#faf0d8;border-color:#dfcd9d}.relation.pending{color:var(--text-dim);background:#f0ece4}.preview{display:block;padding:0;position:relative;border:1px solid var(--border);border-radius:3px;overflow:hidden;line-height:0;background:#ece6db;width:min(100%,350px)}.preview img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:contain}.preview span{position:absolute;right:6px;bottom:6px;line-height:1.5;background:#2c241ed9;color:#fff;font-size:10px;padding:3px 6px;border-radius:2px}.preview:hover{border-color:var(--red)}.art-note{margin:10px 0 8px;color:var(--text-dim);font-size:12px;line-height:1.8}.art-links{display:flex;gap:14px;flex-wrap:wrap;margin-top:4px;font-size:11px}.pending-note{font-size:12px;color:var(--text-dim);padding:15px 0 6px;border-top:1px dashed var(--border)}.compact .preview{display:none}.compact .art-note{margin-top:4px}.compact tbody th,.compact tbody td{padding-top:16px;padding-bottom:16px}#empty{text-align:center;padding:50px 20px;color:var(--text-dim)}footer{padding:22px 0;color:var(--text-dim);font-size:12px;line-height:1.9}.notice{position:fixed;bottom:25px;left:50%;transform:translateX(-50%);padding:9px 18px;background:#30261e;color:#fff;border-radius:3px;z-index:10;max-width:90%;font-size:13px}.notice[hidden]{display:none}dialog{width:min(1100px,calc(100vw - 32px));border:1px solid var(--border);border-radius:4px;padding:20px;background:var(--surface);color:var(--text);max-height:90dvh;overflow:auto}dialog::backdrop{background:#211912cc}.dialog-head{display:flex;gap:15px;justify-content:space-between;align-items:center;margin-bottom:15px}.dialog-head h2{font-size:18px;line-height:1.5;margin:0}.dialog-image{display:block;max-height:65dvh;max-width:100%;height:auto;margin:auto;object-fit:contain}.dialog-caption{font-size:13px;color:var(--text-dim)}.dialog-links{display:flex;gap:20px;font-size:12px}body.dialog-open{overflow:hidden}
@media(min-width:1100px){thead{position:sticky;top:0;z-index:2}}
@media(max-width:900px){main{width:calc(100% - 32px)}.heading{display:block}.stats{text-align:left;margin-top:14px}.stats br{display:none}.stats span{margin-left:15px}.controls{grid-template-columns:1fr 1fr}.original{font-size:18px}tbody th,tbody td{padding:18px 13px}}
@media(max-width:650px){header{padding-top:26px}.intro{font-size:13px}.controls{gap:10px}.control:first-child{grid-column:1/-1}.table-tools{align-items:start}.table-tools .actions{gap:10px}table,tbody{display:block}colgroup,thead{display:none}tbody tr{display:block;border-top:1px solid var(--border)}tbody th,tbody td{display:block;width:100%;border:0;padding:15px 17px}tbody td+td{padding-top:0}tbody th::before,tbody td::before{content:attr(data-label);display:block;color:var(--text-dim);font-size:11px;margin-bottom:9px;letter-spacing:1px}.preview{width:min(100%,400px)}.original{font-size:22px}.working-name{margin-bottom:7px}.meaning{margin-bottom:10px}.group-note{display:none}.notes{font-size:12px}.table-tools .secondary{font-size:11px}caption{display:block}dialog{padding:12px}.dialog-head h2{font-size:15px}}
@media print{body{background:white;font-size:11px}main{width:100%;margin:0}header{padding:15px 0}.controls,.table-tools,.copy,.tag,.preview span,.notes,dialog{display:none}thead{position:static}tbody th,tbody td{padding:10px;border-top:1px solid #bbb}.original{font-size:15px}.preview{width:220px}.refs{display:block}tr{break-inside:avoid}footer{font-size:10px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style></head><body><main>
<header><div class="eyebrow">MEGUMIN / NAMING & ART REFERENCE</div><div class="heading"><div><h1>惠惠 · 卡牌素材表</h1><p class="intro">从原词、原句找到名字，从具体情节找到画面。以惠惠本人为中心，供以后写攻击、技能与能力牌时查阅。</p></div><div class="stats"><strong>__COUNT__</strong> 条素材<br><span>__PREVIEW__ 条有图 · __PENDING__ 条待找图</span></div></div>
<details class="notes"><summary>阅读说明：原句与中文索引、名称性质、配图对应程度</summary><ul>__NOTES__</ul></details></header>
<section aria-label="素材筛选"><div class="controls"><label class="control">搜索素材<input id="query" type="search" placeholder="原词、中文索引、动作、物件…" autocomplete="off"></label><label class="control">素材分类<select id="group"><option value="">全部分类</option>__GROUPS__</select></label><label class="control">用途标签<select id="tag"><option value="">全部用途</option>__TAGS__</select></label><label class="control">配图状态<select id="art-state"><option value="">全部配图</option><option value="available">已有图片预览</option><option value="exact">同场景图片</option><option value="pending">待找图／待截取</option></select></label></div>
<div class="table-tools"><output id="result" aria-live="polite">显示 __COUNT__ / __COUNT__ 条</output><div class="actions"><label class="compact-label"><input type="checkbox" id="compact"> 简洁模式（收起图片）</label><button class="secondary" id="reset">重置筛选</button><button class="secondary" id="export">导出当前筛选 CSV</button></div></div></section>
<div class="table-wrap"><table><caption>日文与英译片段保留所读文字；“中文索引”是方便查找的工作译名。点击用途标签可筛选，点击图片可放大。</caption><colgroup><col class="words"><col class="meaning-col"><col class="art-col"></colgroup><thead><tr><th scope="col">原作／相关内容的原本词语或句子</th><th scope="col">这个词语表达的简要意思</th><th scope="col">推荐使用的配图与出处</th></tr></thead><tbody id="materials">__ROWS__</tbody></table><p id="empty" hidden>没有匹配的素材。可清空关键词或重置筛选。</p></div>
<footer>整理日期 __DATE__ · 首批 __COUNT__ 条，后续可按卷章与动作继续补充。图片保留官方公开剧照原貌，小说图尚未取得的条目给出定位建议。<br>原词出处和配图出处分别链接，方便核对两者是否属于同一场景。</footer>
</main><div class="notice" id="notice" role="status" hidden></div>
<dialog id="art-dialog" aria-labelledby="dialog-title"><div class="dialog-head"><h2 id="dialog-title">配图预览</h2><button class="secondary" id="close-dialog">关闭</button></div><img class="dialog-image" id="dialog-image" alt=""><p id="dialog-caption" class="dialog-caption"></p><div class="dialog-links"><a id="dialog-source" target="_blank" rel="noopener noreferrer">官方剧照页 ↗</a><a id="dialog-original" target="_blank" rel="noopener noreferrer">原图 ↗</a></div></dialog>
<script type="application/json" id="reference-data">__DATA__</script><script>
const data=JSON.parse(document.getElementById('reference-data').textContent);
const byId=new Map(data.rows.map(r=>[r.id,r]));
const elements=new Map([...document.querySelectorAll('#materials tr')].map(e=>[e.dataset.id,e]));
const controls=['query','group','tag','art-state'].map(id=>document.getElementById(id));
const [query,group,tag,artState]=controls;
const searchable=new Map(data.rows.map(r=>[r.id,[r.id,r.name,r.original,r.form,r.group,r.meaning,r.art_note,...r.tags,...r.sources.map(s=>data.sources[s].title)].join(' ').toLocaleLowerCase()]));
let shown=data.rows;let noticeTimer;
function filter(){const q=query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);shown=data.rows.filter(r=>q.every(term=>searchable.get(r.id).includes(term))&&(!group.value||r.group===group.value)&&(!tag.value||r.tags.includes(tag.value))&&(!artState.value||(artState.value==='available'?!!r.art:artState.value==='exact'?(!!r.art&&r.art_relation==='同场景'):!r.art)));const ids=new Set(shown.map(r=>r.id));elements.forEach((el,id)=>el.hidden=!ids.has(id));document.getElementById('result').textContent=`显示 ${shown.length} / ${data.rows.length} 条 · ${shown.filter(r=>r.art).length} 条有图`;document.getElementById('empty').hidden=shown.length>0;}
controls.forEach(el=>el.addEventListener(el===query?'input':'change',filter));
document.getElementById('reset').addEventListener('click',()=>{controls.forEach(el=>el.value='');filter();});
document.querySelectorAll('[data-tag]').forEach(el=>el.addEventListener('click',()=>{tag.value=el.dataset.tag;filter();}));
document.getElementById('compact').addEventListener('change',e=>document.body.classList.toggle('compact',e.target.checked));
function notify(message){const el=document.getElementById('notice');el.textContent=message;el.hidden=false;clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>el.hidden=true,2200);}
document.querySelectorAll('[data-copy]').forEach(el=>el.addEventListener('click',async()=>{const r=byId.get(el.dataset.copy);try{await navigator.clipboard.writeText(r.original);notify('已复制原词句');}catch{const selection=window.getSelection();const range=document.createRange();range.selectNodeContents(elements.get(r.id).querySelector('.original'));selection.removeAllRanges();selection.addRange(range);notify('原词句已选中，可按 Ctrl+C 复制');}}));
const dialog=document.getElementById('art-dialog');
function closeDialog(){dialog.close();document.body.classList.remove('dialog-open');}
document.querySelectorAll('[data-art]').forEach(el=>el.addEventListener('click',()=>{const r=byId.get(el.dataset.row),art=data.artwork[el.dataset.art],img=document.getElementById('dialog-image');img.src=el.querySelector('img').src;img.alt=art.label;document.getElementById('dialog-title').textContent=`${r.id} · ${r.name} · ${r.art_relation}`;document.getElementById('dialog-caption').textContent=art.label+'。'+r.art_note;document.getElementById('dialog-source').href=art.page_url;document.getElementById('dialog-original').href=art.image_url;dialog.showModal();document.body.classList.add('dialog-open');}));
document.getElementById('close-dialog').addEventListener('click',closeDialog);
dialog.addEventListener('cancel',()=>document.body.classList.remove('dialog-open'));
dialog.addEventListener('click',e=>{if(e.target===dialog){const rect=dialog.getBoundingClientRect();if(e.clientX<rect.left||e.clientX>rect.right||e.clientY<rect.top||e.clientY>rect.bottom)closeDialog();}});
function csvCell(value){return '"'+String(value).replaceAll('"','""')+'"';}
document.getElementById('export').addEventListener('click',()=>{const header=['原本词语或句子（含来源）','简要意思','推荐配图（含定位与链接）'];const lines=[header,...shown.map(r=>data.csv_rows[r.id])].map(row=>row.map(csvCell).join(',')).join('\r\n');const blob=new Blob(['\ufeff'+lines],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob);const anchor=document.createElement('a');anchor.href=url;anchor.download=`惠惠卡牌素材_${shown.length}条.csv`;anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1000);notify(`已导出 ${shown.length} 条素材`);});
function revealHash(){const id=location.hash.slice(1);if(byId.has(id)&&elements.get(id).hidden){controls.forEach(el=>el.value='');filter();elements.get(id).scrollIntoView({block:'start'});}}
window.addEventListener('hashchange',revealHash);filter();revealHash();
</script></body></html>'''

replace = {
    '__COUNT__': str(len(ROWS)), '__PREVIEW__': str(counts[True]), '__PENDING__': str(counts[False]),
    '__NOTES__': ''.join('<li>' + esc(n) + '</li>' for n in DATA['notes']), '__GROUPS__': groups_html,
    '__TAGS__': tags_html, '__ROWS__': ''.join(row_html(r) for r in ROWS), '__DATE__': DATA['date'], '__DATA__': bundle_json,
}
for key, value in replace.items():
    PAGE = PAGE.replace(key, value)
assert not any(key in PAGE for key in replace)
OUT.write_text(PAGE, encoding='utf-8')
portable = Path.home() / '.agent/diagrams' / OUT.name
portable.parent.mkdir(parents=True, exist_ok=True)
portable.write_text(PAGE, encoding='utf-8')
print(json.dumps(dict(html=str(OUT), csv=str(CSV_OUT), portable=str(portable), rows=len(ROWS), with_preview=counts[True], pending=counts[False], unique_images=len(USED_ART), html_bytes=OUT.stat().st_size), ensure_ascii=False))
