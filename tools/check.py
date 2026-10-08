from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; DIST=ROOT/'dist'
errors=[]; titles=[]; descriptions=[]; pages=list(DIST.rglob('index.html'))
class Audit(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set();self.h1=0;self.canonical=[];self.descriptions=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag in ['link','script'] and (a.get('href') or a.get('src')):self.links.append(a.get('href') or a['src'])
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
        if tag=='meta' and a.get('name')=='description':self.descriptions.append(a.get('content'))
audits={}
for file in pages:
    text=file.read_text(encoding='utf-8');audit=Audit();audit.feed(text);audits[file]=audit
    title=re.search(r'<title>(.*?)</title>',text).group(1);titles.append(title)
    descriptions.extend(audit.descriptions)
    if audit.h1!=1:errors.append(f'{file}: H1数量{audit.h1}')
    if len(audit.canonical)!=1 or not audit.canonical[0].startswith('https://fanqiangtizi.wiki/'):errors.append(f'{file}: canonical错误')
    if len(audit.descriptions)!=1 or not audit.descriptions[0]:errors.append(f'{file}: description缺失')
    if '<meta name="keywords"' not in text:errors.append(f'{file}: keywords缺失')
    for match in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text):json.loads(match)
for file,audit in audits.items():
    for link in audit.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        target=DIST/unquote(u.path).lstrip('/') if u.path.startswith('/') else file.parent/unquote(u.path) if u.path else file
        if target.is_dir():target=target/'index.html'
        if not target.exists():errors.append(f'{file.relative_to(DIST)}: 链接缺失{link}')
        elif u.fragment and target in audits and u.fragment not in audits[target].ids:errors.append(f'{file}: 锚点缺失{link}')
brands=json.loads((ROOT/'data/brand-catalog.json').read_text(encoding='utf-8'))
input_brands=json.loads((ROOT/'data/brands.json').read_text(encoding='utf-8'))
assert [b['name'] for b in brands]==[b['name'] for b in input_brands]
assert [b['url'] for b in brands]==[b['url'] for b in input_brands]
assert len(brands)==29 and sum(bool(b.get('coupon')) for b in brands)==11
assert len(list((DIST/'articles').glob('*/index.html')))==150
assert len(titles)==len(set(titles)) and len(descriptions)==len(set(descriptions))
xml=ET.parse(DIST/'sitemap.xml');locs=[node.text for node in xml.findall('.//{*}loc')]
assert len(locs)==len(pages) and len(locs)==len(set(locs))
ET.parse(DIST/'feed.xml')
for name in ['recommended','budget','stable']:
    content=(DIST/'topics'/name/'index.html').read_text(encoding='utf-8')
    assert content.count('class="rank-row"')==10
pending=json.loads((ROOT/'data/reviews.json').read_text(encoding='utf-8'))
assert len(pending)==29 and all(r['throughputMbps'] is None for r in pending)
report={'status':'pass' if not errors else 'fail','pages':len(pages),'articles':150,'brands':29,'coupons':11,'sitemapUrls':len(locs),'errors':errors,'checks':['全部内部链接与锚点','标题与描述唯一','逐页TDK与canonical','JSON-LD有效','XML sitemap与RSS有效','品牌顺序与原始入口一致','三榜各10个条目','实测缺失值保留为空']}
(ROOT/'validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
