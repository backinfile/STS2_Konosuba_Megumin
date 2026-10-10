"""Cache public official episode stills for the card-material research table.

Images are kept intact. This is an offline research cache, not game assets.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from html import escape
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / '参考资料' / '卡牌命名配图素材'

GROUPS = {
    'B01': ('《爆焰》第1话', 'https://konosuba.com/bakuen/story/?mode=story1', 'https://konosuba.com/bakuen/story/img/story1/{:02}.jpg'),
    'B05': ('《爆焰》第5话', 'https://konosuba.com/bakuen/story/?mode=story5', 'https://konosuba.com/bakuen/story/img/udsmga5/{:02}.jpg'),
    'B06': ('《爆焰》第6话', 'https://konosuba.com/bakuen/story/?mode=story6', 'https://konosuba.com/bakuen/story/img/story6/{:02}.jpg'),
    'S104': ('本篇第一季第4话', 'https://konosuba.com/1st/story/?id=04&mode=detail', 'https://konosuba.com/1st/story/img/04/{}.jpg'),
    'S202': ('本篇第二季第2话', 'https://konosuba.com/2nd/story/?id=02&mode=detail', 'https://konosuba.com/2nd/story/img/02/{}.jpg'),
}


def fetch(item):
    path = ART / item['file']
    if path.exists():
        return item, None
    request = urllib.request.Request(item['image_url'], headers={'User-Agent': 'Mozilla/5.0', 'Referer': item['page_url']})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if not response.headers.get('Content-Type', '').startswith('image/'):
                    raise ValueError(item['image_url'])
                return item, response.read()
        except Exception as error:
            if attempt == 2:
                item['fetch_error'] = type(error).__name__
                return item, None


def main():
    (ART / 'originals').mkdir(parents=True, exist_ok=True)
    items = []
    for key, (label, page, pattern) in GROUPS.items():
        for number in range(1, 7):
            items.append(dict(id=f'{key}-{number}', label=f'{label} · 官网图{number}',
                              page_url=page, image_url=pattern.format(number),
                              file=f'originals/{key}-{number}.jpg'))
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(fetch, items))
    for item, data in results:
        if data:
            (ART / item['file']).write_bytes(data)
    (ART / 'official_stills.json').write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf8')
    figures = ''.join(f'<figure><img src="{escape(i["file"])}"><figcaption>{i["id"]} · {escape(i["label"])}</figcaption></figure>' for i in items)
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>官方配图核对</title><style>body{margin:20px;background:#f5f0e7;font-family:Microsoft YaHei}main{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}figure{margin:0}img{width:100%;display:block}figcaption{font-size:12px;padding:5px}</style><h1>官方公开剧照 · 内容核对</h1><main>' + figures + '</main></html>'
    (ART / '核图.html').write_text(page, encoding='utf8')
    print(json.dumps({'images': len(items), 'cached': sum((ART / i['file']).exists() for i in items), 'failed': [i['id'] for i in items if i.get('fetch_error')], 'contact_sheet': str(ART / '核图.html')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
