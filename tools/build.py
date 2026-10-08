from pathlib import Path
import json, html, csv, math, shutil, re
from collections import defaultdict
from xml.sax.saxutils import escape as xe

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
DOMAIN='https://fanqiangtizi.wiki'
DATE='2026-10-08'
E=lambda x:html.escape(str(x),quote=True)
original=json.loads((ROOT/'data/source-site-data.json').read_text(encoding='utf-8'))
source={b['id']:b for b in original['brands']}
aliases={'dalao':'dalaocloud','ladder':'laddercloud','wave':'wavenet','global':'globalcloud','guangnian':'guangnianti'}
brands=json.loads((ROOT/'data/brands.json').read_text(encoding='utf-8'))
for rank,b in enumerate(brands,1):
    old=source[aliases.get(b['id'],b['id'])]
    for k in ['plans','line','note','checkedAt','evidence','profile','source','sourceLabel','audience']:
        b[k]=old.get(k)
    b['sourcePage']='https://jichangnetwork.blog/brands/'+old['id']+'/'
    b['order']=rank
    b['status']='资料待复核' if b['id'] in ['firefly','jilian'] else '运营状态待确认' if b['id']=='kosing' else '参考资料已收录'
topics=list(csv.reader((ROOT/'data/topics.tsv').open(encoding='utf-8'),delimiter='\t'))
assert len(topics)==121 and len(brands)==29
(ROOT/'data/brand-catalog.json').write_text(json.dumps(brands,ensure_ascii=False,indent=2),encoding='utf-8')
OUT.mkdir(exist_ok=True)
(OUT/'assets').mkdir(exist_ok=True)
for name in ['style.css','app.js','favicon.svg']:
    shutil.copyfile(ROOT/'assets'/name,OUT/'assets'/name)
paths=[]
search=[]

def url(path): return DOMAIN+path
def button(label,href,secondary=False): return f'<a class="button {"secondary" if secondary else ""}" href="{E(href)}">{E(label)}</a>'
def note(text):return '<aside class="note">'+text+'</aside>'
def section_title(kicker,title,link='',label='查看全部'):
    return f'<div class="section-head"><div><p class="eyebrow">{E(kicker)}</p><h2>{E(title)}</h2></div>'+(f'<a class="text-link" href="{link}">{label}</a>' if link else '')+'</div>'
def page(path,title,description,body,kind='WebPage',article=False,category=''):
    dest=OUT/path.strip('/')/'index.html' if path!='/' else OUT/'index.html'
    dest.parent.mkdir(parents=True,exist_ok=True)
    schema={'@context':'https://schema.org','@type':kind,'name':title,'url':url(path),'description':description,'inLanguage':'zh-CN'}
    if article:
        schema.update({'headline':title,'datePublished':DATE,'dateModified':DATE,'author':{'@type':'Organization','name':'翻墙梯子编辑部'},'publisher':{'@type':'Organization','name':'翻墙梯子','url':DOMAIN},'mainEntityOfPage':url(path),'articleSection':category})
    active='brands' if path.startswith('/brands') else 'articles' if path.startswith('/articles') else 'topics' if path.startswith('/topics') else 'reviews' if path.startswith('/reviews') else 'home'
    nav=''.join(f'<a href="{p}"'+(' aria-current="page"' if active==key else '')+f'>{label}</a>' for key,label,p in [('home','首页','/'),('topics','严选专题','/topics/'),('brands','品牌库','/brands/'),('articles','博客文章','/articles/'),('reviews','机场测评','/reviews/')])
    data=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    markup=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} | 翻墙梯子</title><meta name="description" content="{E(description)}"><meta name="keywords" content="梯子推荐,机场推荐,{E(category or '机场套餐,机场严选,翻墙梯子')}"><meta name="robots" content="index,follow"><link rel="canonical" href="{url(path)}"><meta property="og:locale" content="zh_CN"><meta property="og:site_name" content="翻墙梯子"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{url(path)}"><meta property="og:type" content="{'article' if article else 'website'}"><meta name="theme-color" content="#080d18"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/style.css?v=20261008-tech"><link rel="alternate" type="application/rss+xml" title="翻墙梯子博客" href="/feed.xml"><script type="application/ld+json">{data}</script><script src="/assets/app.js?v=20261008-tech" defer></script></head><body><div class="ambient" aria-hidden="true"><div class="aurora a1"></div><div class="aurora a2"></div><div class="grid-bg"></div><canvas class="tech-canvas"></canvas><div class="light-ribbon r1"></div><div class="light-ribbon r2"></div><div class="stars"></div></div><a class="skip" href="#main">跳到正文</a><header><div class="shell header-inner"><a class="logo" href="/"><span class="logo-mark" aria-hidden="true">梯</span><span>翻墙梯子<small>FANQIANGTIZI.WIKI</small></span></a><button class="menu-toggle" aria-label="展开导航" aria-expanded="false" aria-controls="site-nav">菜单</button><nav id="site-nav" aria-label="主导航">{nav}</nav><button class="motion-toggle" aria-pressed="false">暂停动画</button></div></header><main id="main" class="shell">{body}</main><footer class="shell"><div class="footer-top"><a class="logo" href="/">翻墙梯子<small>FANQIANGTIZI.WIKI</small></a><p>从套餐、流量与证据出发，做有依据的选择。</p><div><a href="/methodology/">编辑与测评方法</a><a href="/disclosure/">推广说明</a><a href="/sitemap/">站点地图</a><a href="/feed.xml">RSS</a></div></div><div class="footer-bottom"><span>© 2026 翻墙梯子</span><span>推广链接可能产生佣金 · 历史套餐需在购买页复核</span></div></footer><div id="toast" role="status" aria-live="polite"></div></body></html>'''
    dest.write_text(markup,encoding='utf-8')
    paths.append(path)
    search.append({'title':title,'description':description,'path':path,'category':category or kind})

def head(title,description,kicker='THE EDITORIAL / 翻墙梯子',crumb=''):
    return (f'<div class="breadcrumbs"><a href="/">首页</a> / {crumb or E(title)}</div>' if crumb else '')+f'<div class="page-head"><p class="eyebrow">{E(kicker)}</p><h1>{E(title)}</h1><p class="lead">{E(description)}</p></div>'
def monthly(b):
    plans=[p for p in b['plans'] if p['cycle']=='月付' and p.get('gb') and p.get('quotaPeriod')=='month']
    return min(plans,key=lambda p:p['price']) if plans else None
def money(x):return f'{x:g}' if isinstance(x,(int,float)) else str(x)
def brand_card(b,compact=False):
    p=monthly(b)
    price=f'<strong>¥{money(p["price"])}<small> / 月付参考</small></strong><span>{p["gb"]} GB / 月</span>' if p and b['id'] not in ['firefly','jilian','kosing'] else '<strong>待复核<small> / 套餐资料</small></strong>'
    if b.get('referenceMonthlyPrice') is not None:
        price=f'<strong>¥{money(b["referenceMonthlyPrice"])}<small> / 月付参考</small></strong>'
    return f'''<article class="brand-card" data-search="{E(b['name'])}"><div class="brand-top"><span class="rank">{b['order']:02}</span><span class="badge">{'优惠码' if b.get('coupon') else '品牌档案'}</span></div><h3><a href="/brands/{b['id']}/">{E(b['name'])}</a></h3><p>{E(b['profile']['headline'])}</p><div class="brand-price">{price}</div><div class="brand-bottom"><span>{E(b['status'])}</span><a href="/brands/{b['id']}/">查看详情</a></div></article>'''
def plans_table(b):
    rows=[]
    for p in b['plans']:
        gb=p.get('gb')
        period=p.get('quotaPeriod')
        label={'month':'每月额度','30days':'每30天额度','year':'每年总额度','year-total':'每年总额度','total':'总额度'}.get(period,'周期待核实')
        if p.get('resetDays'):label=f'每{p["resetDays"]}天额度'
        amount=gb if gb is not None else p.get('quotedGb','—')
        quota=str(amount)+' GB · '+label
        if p.get('capacityConflict'):quota='/'.join(str(x) for x in p['capacityValues'])+' GB · 容量有分歧 · '+label
        rows.append(f'<tr><td>{E(p["name"])}</td><td>¥{money(p["price"])}</td><td>{E(p["cycle"])}</td><td>{E(quota)}</td><td>{E(p.get("sourceDate","未注明"))}</td></tr>')
    notes=''.join(f'<li><strong>{E(p["name"])}</strong>：{E(p["quotaNote"])}</li>' for p in b['plans'] if p.get('quotaNote'))
    return '<div class="table-wrap"><table><caption>历史参考套餐：金额为对应付款周期的总价，未扣优惠</caption><thead><tr><th>套餐</th><th>参考金额</th><th>付款周期</th><th>额度与重置窗口</th><th>资料日期</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'+('<div class="quota-notes"><strong>原资料中的额度说明</strong><ul>'+notes+'</ul></div>' if notes else '')
def coupon_block(b):
    c=b.get('coupon')
    return f'<div class="coupon"><div><span>站主提供优惠码 · 未结算验证</span><code>{E(c)}</code></div><button data-copy="{E(c)}" aria-label="复制{E(b["name"])}优惠码">复制优惠码</button></div><p class="muted">有效期、折扣、适用套餐与叠加条件，以最终结算页为准。</p>' if c else '<p>站主尚未提供该品牌优惠码。没有优惠码不代表没有活动，请在购买页核对。</p>'
def outbound(b): return f'<a class="button" href="{E(b["url"])}" target="_blank" rel="sponsored noopener noreferrer">前往官网入口</a>'
def sources(b):
    return f'<div class="source-box"><h2>资料来源与适用范围</h2><p>资料迁移自站主指定旧博客，读取日期为 {DATE}；原站资料核对日期为 {E(b["checkedAt"])}。读取成功不等于重新验证所有套餐。本站未登录付款，也未开展该品牌统一网络实测。</p><p><a href="{E(b["sourcePage"])}" target="_blank" rel="noopener">旧博客品牌资料</a> · <a href="{E(b["source"])}" target="_blank" rel="noopener">原记录来源</a></p><p>{E(b["note"])}</p></div>'
def review_status(b):
    return '<div class="metrics">'+''.join(f'<div><span>{k}</span><strong>待实测</strong></div>' for k in ['下载吞吐','高峰可用率','延迟与波动','丢包与恢复','平台可用性','设备兼容性'])+'</div><p class="muted">没有可复核样本，暂不发布分数、星级或性能排名。</p>'

def worked_example(cat,b,index):
    if b['id'] in ['firefly','jilian','kosing']:b=brands[index%4]
    p=monthly(b)
    base=f'以{b["name"]}的历史资料为例，{p["name"]}记录为{money(p["price"])}元月付、{p["gb"]}GB月额度，来源日期为{p.get("sourceDate","未注明")}。' if p else ''
    if cat=='预算选择':
        usage=max(1,round(p['gb']*.4))
        detail=f'假设一个月实际使用{usage}GB，按实用量分摊的费用约为{p["price"]/usage:.3f}元/GB；按全部标称容量计算则约为{p["price"]/p["gb"]:.3f}元/GB。前者帮助复盘支出，后者描述容量标价，二者不能混用。示例没有计入优惠、倍率或其他费用。'
    elif cat=='流量知识':
        usage=round(p['gb']*.6)
        detail=f'若一个统计窗口内显示已用{usage}GB，只有确认后台单位、统计周期与节点倍率一致后，才能将它与{p["gb"]}GB额度比较。这里的用量是演算假设，没有读取任何读者账户，也不代表该服务实际扣费记录。'
    elif cat=='稳定性':detail='这份套餐记录说明了费用和容量，没有证明高峰表现。真正的观察表还需要记录你所在地区、运营商、常用节点与连续任务结果。即使某次任务完成，也要保留之后的失败和恢复记录，才能判断结论是否适用于持续使用。'
    elif cat=='测评方法':detail='测试时应写出实际购买的套餐版本，不以目录中的参考档位替代账号权益。选择固定目标和时间窗口，保存原始样本，再计算典型水平与异常范围。没有购买记录或任务日志时，报告只能停留在资料分析层面。'
    elif cat=='线路知识':detail=f'原记录的线路描述为“{b["line"]}”。这属于资料标签，不是本站对路由、出口或容量做出的测量结果。若要进一步比较，先确定具体节点，再核对实际任务与出口信息，不能从宣传名称推导所有地区表现。'
    elif cat=='客户端':detail='品牌档案提供的官网入口不含你的私人配置。实际导入前需要从已确认后台取得个人订阅，并核对格式和客户端版本。本文没有该品牌所有系统的兼容性样本，不能把目录收录误读为支持全部设备。'
    elif cat=='故障排查':detail='如果账号面板显示额度仍有剩余，而客户端无法完成任务，应分别核对配置更新时间、实际节点连接与目标应用。套餐余额只是其中一项信息；它既不能证明线路正常，也不意味着必须再次购买套餐。'
    elif cat=='安全隐私':detail='这份公开档案只保存推广入口与历史套餐，不保存个人订阅或支付凭据。排查同类问题时，可以引用套餐名称与日期，但个人令牌、账号密码和付款验证码应从公开材料中移除。'
    elif cat=='优惠活动':
        detail=(f'站主提供的代码为“{b["coupon"]}”，当前未完成结算验证。输入代码后，需要同时检查原订单金额、折扣项目与最终实付；不能从代码名称推断折扣百分比。' if b.get('coupon') else '站主没有为该品牌提供优惠码，因此资料表保持空缺。其他品牌的活动不能用于推算它的折后价格，也不能把没有代码解释为完全没有促销。')
    elif cat=='使用场景':detail='将这个参考档位放回自己的任务清单：需要哪些地区、每月预计使用多少、是否包含上传、能否接受任务中断。容量满足只是一个筛选条件，会议、文件传输或移动网络体验仍需要在实际环境验证。'
    else:detail='比较时把这组金额、容量和资料日期放在同一行，避免从另一个来源挑选更低价格或更大额度拼接。未确认的设备限制、倍率与当前在售状态继续保持未知；只有对应字段一致，计算结果才有可解释的基础。'
    return '<h2>用一份品牌资料练习核对</h2><p>'+E(base+detail)+f'</p><p class="source-reference"><a href="/brands/{b["id"]}/">查看{E(b["name"])}完整档案与来源</a>。以上是参考资料与明确假设的分析，未形成当前订单或性能验证。</p>'

# The first usable slice is the homepage, with the final visual direction and core links.
hero=f'''<section class="hero"><div class="hero-copy"><p class="eyebrow"><span class="tiny-line"></span> 连接之前，先读懂选择</p><h1>梯子推荐，<br>从<span>严选</span>开始。</h1><p>机场推荐、套餐分析与使用指南。<br>看清价格与流量，也看清每一个结论的依据。</p><div class="hero-actions">{button('查看机场推荐','/topics/recommended/')}{button('浏览品牌库','/brands/',True)}</div><div class="hero-stats"><div><strong>29</strong><span>品牌档案</span></div><div><strong>150</strong><span>博客文章</span></div><div><strong>3</strong><span>严选专题</span></div></div></div><aside class="hero-picks"><div class="picks-header"><span>站主推荐 · TOP 10</span><a href="/topics/recommended/">完整榜单</a></div>'''+''.join(f'<a class="pick-row" href="/brands/{b["id"]}/"><span>{b["order"]:02}</span><div><strong>{E(b["name"])}</strong><small>{E(b["profile"]["headline"])}</small></div><span class="pick-label">品牌详情</span></a>' for b in brands[:3])+'''<div class="picks-note">推荐顺序由站主指定，性能结论见测评记录。</div></aside></section>'''
topic_cards='''<div class="topic-grid"><a class="topic-card" href="/topics/recommended/"><span class="topic-no">01 / EDITOR’S ORDER</span><h3>机场推荐排行 1–10</h3><p>按站主指定顺序，了解十个推荐品牌。</p><span>浏览推荐榜</span></a><a class="topic-card" href="/topics/budget/"><span class="topic-no">02 / BUDGET SELECTION</span><h3>便宜机场严选 1–10</h3><p>以历史月付参考价比较，注明容量与条件。</p><span>查看低价参考榜</span></a><a class="topic-card" href="/topics/stable/"><span class="topic-no">03 / STABILITY RESEARCH</span><h3>稳定机场严选 1–10</h3><p>十个待测候选，按统一方法验证持续体验。</p><span>查看候选与标准</span></a></div>'''
home=hero+section_title('CURATED COLLECTIONS / 专题','围绕需求，逐项严选','/topics/')+topic_cards+section_title('BRAND LIBRARY / 品牌库','从一个品牌，读懂一套方案','/brands/','全部29个品牌')+'<div class="brand-grid">'+''.join(brand_card(b) for b in brands[:6])+'</div>'
home+=section_title('THE JOURNAL / 博客','用知识，让选择更清楚','/articles/','全部150篇文章')+'<div class="article-grid">'+''.join(f'<a class="article-card" href="/articles/guide-{i+1:03}/"><span>{E(row[0])} / GUIDE {i+1:03}</span><h3>{E(row[1])}</h3><p>{E(row[2])}</p><small>翻墙梯子编辑部 · {DATE}</small></a>' for i,row in list(enumerate(topics))[:6])+'</div>'
page('/','梯子推荐与机场推荐：品牌库、严选排行与博客指南','翻墙梯子围绕梯子推荐、机场推荐整理29个品牌、150篇博客文章和三类严选专题，提供参考套餐、流量周期、优惠码及测评方法。',home)

def build_remaining():
    groups=defaultdict(list)
    article_records=[]
    for b in brands:
        profile=b['profile']
        desc=profile['deck']
        body=head(b['name']+'：套餐、优惠码与测评档案',desc,'BRAND ARCHIVE / 品牌档案',f'<a href="/brands/">品牌库</a> / {E(b["name"])}')
        body+=f'<div class="brand-overview"><div><span class="badge">目录顺序 {b["order"]:02}</span><h2>{E(profile["headline"])}</h2><p>{E(b["audience"])}</p></div><div>{outbound(b)}</div></div>'+note(f'{E(b["status"])}。官网入口由站主提供，含推广参数；参考套餐尚未完成当前订单验证。')
        body+=section_title('PLANS / 套餐','价格、流量与付款周期')+plans_table(b)
        if b.get('referenceMonthlyPrice') is not None:
            body=body.replace(section_title('PLANS / 套餐','价格、流量与付款周期'),section_title('PLANS / 套餐','价格、流量与付款周期')+f'<div class="panel"><h2>¥{money(b["referenceMonthlyPrice"])} / 月付参考</h2><p>{E(b["referencePriceSource"])} · {E(b["referencePriceDate"])}。对应流量与套餐权益待补充；下表保留旧资料日期的历史套餐。</p></div>')
        body+='<details class="panel"><summary>线路与原资料宣传：尚未实测验证</summary><p>原记录线路描述：'+E(b['line'])+'。以下是资料来源的描述，不是本站实测结论。</p>'+''.join('<h3>'+E(p['name'])+'</h3><ul>'+''.join('<li>'+E(f)+'</li>' for f in p['features'])+'</ul>' for p in b['plans'] if p.get('features'))+'</details>'
        body+='<div class="two-col"><section class="panel"><h2>月付档位解读</h2><p>'+E(profile['monthlyInsight'])+'</p></section><section class="panel"><h2>周期与按量的区别</h2><p>'+E(profile['cycleInsight'])+'</p></section></div>'
        body+='<section class="panel"><h2>需要认真权衡的条件</h2><p>'+E(profile['tradeoff'])+'</p><p>'+E(profile['verifyInsight'])+'</p></section>'+section_title('COUPON / 优惠','优惠码与使用条件')+coupon_block(b)
        body+=section_title('REVIEW / 测评','实测记录状态')+review_status(b)+sources(b)+f'<p>{button("阅读该品牌资料评析","/articles/brand-"+b["id"]+"/",True)}</p>'
        page('/brands/'+b['id']+'/',b['name']+'套餐价格、流量与优惠码',desc,body,category='品牌详情')
        title=b['name']+'资料评析：套餐结构、购买核对与测评边界'
        intro=profile['deck']
        body=head(title,intro,'BRAND RESEARCH / 品牌研究',f'<a href="/articles/">博客文章</a> / 品牌研究')
        body+=f'<div class="article-layout"><article class="prose"><p class="byline">翻墙梯子编辑部 · {DATE} · 资料评析</p><p class="article-intro">{E(intro)}</p><h2 id="structure">套餐结构怎样读</h2><p>{E(profile["monthlyInsight"])}</p>{plans_table(b)}<h2 id="cycle">付款周期与容量窗口</h2><p>{E(profile["cycleInsight"])}</p><p>{E(profile["tradeoff"])}</p><h2 id="check">购买前的核对重点</h2><p>{E(profile["verifyInsight"])}</p><p>先确认这份资料对应当前面板中的哪一个套餐。对照套餐名称、总价、流量单位、重置日期和有效期，不把来源中的不同版本拼接成一个实际不存在的优惠方案。设备限制、节点倍率、退款与续费条件尚需从当前服务条款确认。</p><h2 id="evidence">哪些结论可以成立</h2><p>{E(b["note"])}</p><p>本文提供套餐资料分析，没有完成统一环境的测速或长期可用性观察。因此不能据此认定该品牌比其他服务更快、更稳定或适合所有地区。下载速度、延迟、丢包和平台功能，需要记录具体日期、套餐、网络与测试任务后另行评价。</p><h2 id="coupon">优惠与入口</h2>{coupon_block(b)}<p>{outbound(b)}</p>{sources(b)}<h2>下一步怎样核对</h2><ol><li>在当前购买页确认套餐、费用与额度周期，保存脱敏记录。</li><li>核对你所用设备与客户端的配置支持，确认必要地区是否可用。</li><li>用真实任务做小范围观察，再决定是否使用更长付款周期。</li></ol><p><a href="/brands/{b["id"]}/">查看完整品牌档案</a> · <a href="/methodology/">阅读编辑与测评方法</a></p></article><aside class="article-aside"><span class="eyebrow">阅读目录</span><a href="#structure">套餐结构</a><a href="#cycle">容量与周期</a><a href="#check">购买核对</a><a href="#evidence">证据边界</a><a href="#coupon">优惠与入口</a></aside></div>'
        path='/articles/brand-'+b['id']+'/'
        page(path,title,'资料评析：'+intro,body,'BlogPosting',True,'品牌研究')
        article_records.append({'title':title,'description':intro,'path':path,'category':'品牌研究'})

    contexts={
      '预算选择':('费用表','原价、实付、付款周期、预计使用月份','只比较满足必要需求的套餐，避免把未使用的容量当成已经获得的价值。'),
      '流量知识':('用量记录','起止时间、前后余额、计量单位、任务类型','先统一统计窗口与额度周期，再判断用量是否超出预期。'),
      '稳定性':('观察日志','接入网络、节点、时段、成功或失败、恢复耗时','将实际任务与连续样本放在一起，结论只覆盖观察过的条件。'),
      '测评方法':('测试记录','设备、客户端版本、目标、样本数、失败情况','公开方法和限制，比没有来源的漂亮分数更有助于复核。'),
      '线路知识':('线路核对表','节点标签、实际出口、配置版本、官方说明','宣传名称与实际结果分别保存，不根据标签推断未经证实的能力。'),
      '客户端':('配置记录','系统版本、客户端来源、配置格式、更新时间','版本与格式需要匹配，操作步骤以对应版本的官方文档为准。'),
      '故障排查':('复现记录','错误时间、任务、环境、每次改动、结果','一次只改变一个条件，保留原配置和脱敏日志，才容易确认有效措施。'),
      '安全隐私':('安全核对表','资料来源、访问域名、权限、敏感字段','只提供必要信息，密码、验证码与订阅密钥不进入公开记录。'),
      '优惠活动':('结算记录','优惠码、资格、套餐范围、实付、有效期','优惠码文本与生效结果属于不同证据，结算页才决定这笔订单的金额。'),
      '使用场景':('需求清单','真实任务、频率、关键地区、设备、可接受中断','将真实需求作为筛选起点，容量与速度都需要放在任务中判断。'),
      '比较决策':('比较表','字段来源、资料日期、计算假设、缺失项','未知值不补成零，排名的口径和适用范围应当在结论之前明确。')}
    cat_slugs={cat:f'collection-{i+1:02}' for i,cat in enumerate(contexts)}
    for i,row in enumerate(topics,1):
        cat,title,p1,p2,p3=row
        record_name,fields,principle=contexts[cat]
        path=f'/articles/guide-{i:03}/'
        related=brands[(i-1)%len(brands)]
        body=head(title,p1,'FIELD GUIDE / 使用与选购指南',f'<a href="/articles/">博客文章</a> / {E(cat)}')
        body+=f'<div class="article-layout"><article class="prose"><p class="byline">翻墙梯子编辑部 · {DATE} · {E(cat)}</p><h2 id="question">先把问题界定清楚</h2><p>{E(p1)}</p><h2 id="compare">比较或验证的第一步</h2><p>{E(p2)}</p><h2 id="action">把结论放回真实需求</h2><p>{E(p3)}</p><h2 id="record">保留一份可复核的{E(record_name)}</h2><p>建议记录：{E(fields)}。把事实、计算和推测分开；缺少依据的字段标记为待核实，不因为需要填写比较表就补上一个看似合理的数值。涉及账户的记录先脱敏，再决定是否可以公开。</p><div class="takeaway"><strong>阅读要点</strong><p>{E(principle)}</p></div><h2 id="checklist">实际使用时的核对顺序</h2><ol><li>明确当前问题涉及的任务、套餐或配置，确认对应版本与日期。</li><li>按上述方法收集一组有上下文的记录，同时保留未成功的情况。</li><li>核对费用、额度及具体任务的结果；没有证据的结论继续保持未知。</li></ol><h2>常见追问：能直接据此判断某个品牌好吗？</h2><p>这是一篇方法指南，没有对某个品牌做性能背书。价格与套餐资料可以在品牌档案中核对，当前售价需要查看购买页；速度与稳定性则需要同条件实测。推荐顺序、优惠码和线路名称，都不能代替实际观察。</p><p><a href="/topics/{cat_slugs[cat]}/">继续阅读{E(cat)}专题</a> · <a href="/brands/">核对品牌套餐</a> · <a href="/methodology/">查看测评记录标准</a></p>'
        body=body.replace('<h2>常见追问：能直接据此判断某个品牌好吗？</h2>',worked_example(cat,related,i)+'<h2>常见追问：能直接据此判断某个品牌好吗？</h2>')
        if 'sing-box' in title:
            body+='<p class="source-reference">技术依据：<a href="https://sing-box.sagernet.org/configuration/" target="_blank" rel="noopener">sing-box 官方配置文档</a>，具体字段需按使用版本核对。</p>'
        elif 'Mihomo' in title or '客户端关闭' in title:
            body+='<p class="source-reference">参考：<a href="https://mihomo.party/docs/issues/common" target="_blank" rel="noopener">Mihomo Party 常见问题文档</a>，其他客户端以各自文档为准。</p>'
        body+='</article><aside class="article-aside"><span class="eyebrow">阅读目录</span><a href="#question">问题与范围</a><a href="#compare">验证第一步</a><a href="#action">真实需求</a><a href="#record">保留记录</a><a href="#checklist">核对顺序</a></aside></div>'
        page(path,title,p1,body,'BlogPosting',True,cat)
        rec={'title':title,'description':p1,'path':path,'category':cat}
        article_records.append(rec)
        groups[cat].append(rec)

    body=head('品牌库：29个机场品牌档案','按站主给出的顺序完整收录。查看参考套餐、优惠码、入口及资料来源。','BRAND LIBRARY / 品牌库')
    body+='<div class="search-control"><label for="brand-search">查找品牌</label><input id="brand-search" data-filter=".brand-card" type="search" placeholder="输入中文名称或英文名"><span class="filter-status" role="status"></span></div><div class="brand-grid">'+''.join(brand_card(b) for b in brands)+'</div><p class="muted">品牌序号是目录顺序。所有历史参考价格均保留原资料日期，运营状态与性能需进一步核实。</p>'
    page('/brands/','机场推荐品牌库：29个品牌价格、流量与官网入口','完整收录29个机场品牌，按站主指定顺序展示套餐参考价、流量、官网入口与11个优惠码。',body)
    body=head('博客文章','150篇资料研究与方法指南，围绕预算、流量、稳定性和真实使用展开。','THE JOURNAL / 博客')
    body+='<div class="search-control"><label for="article-search">查找文章</label><input id="article-search" data-filter=".article-list-item" type="search" placeholder="搜索标题或分类"><span class="filter-status" role="status"></span></div><div class="category-links">'+''.join(f'<a href="/topics/{cat_slugs[c]}/">{E(c)}</a>' for c in groups)+'</div><div class="article-list">'+''.join(f'<a class="article-list-item" data-search="{E(r["title"]+r["category"])}" href="{r["path"]}"><span>{E(r["category"])}</span><div><h2>{E(r["title"])}</h2><p>{E(r["description"])}</p></div><small>阅读全文</small></a>' for r in article_records)+'</div>'
    page('/articles/','机场推荐博客：150篇套餐分析、测评方法与使用指南','阅读29篇品牌资料评析和121篇主题指南，覆盖梯子推荐、机场推荐、流量、客户端、故障排查与优惠条件。',body)
    page('/topics/','机场推荐专题：推荐、便宜与稳定机场严选', '三类严选专题与11个知识合集，按需求比较品牌资料、套餐费用和稳定性证据。',head('严选专题','从明确的选择标准开始，找到值得继续核对的品牌。','CURATED COLLECTIONS / 专题')+topic_cards+section_title('READING COLLECTIONS / 知识合集','按问题深入阅读')+'<div class="collection-grid">'+''.join(f'<a href="/topics/{cat_slugs[c]}/"><span>11篇指南</span><h2>{E(c)}</h2><p>{E(contexts[c][2])}</p></a>' for c in groups)+'</div>')
    for c,records in groups.items():
        page('/topics/'+cat_slugs[c]+'/',c+'专题：11篇机场选购与使用指南',contexts[c][2],head(c+'专题',contexts[c][2],'READING COLLECTION / 知识合集')+'<div class="article-grid">'+''.join(f'<a class="article-card" href="{r["path"]}"><span>{E(c)}</span><h3>{E(r["title"])}</h3><p>{E(r["description"])}</p><small>阅读全文</small></a>' for r in records)+'</div>')
    recommended=head('机场推荐排行 1–10','微风网络至二猫云，顺序完全按站主指定。推荐榜不代表实测性能排序。','EDITOR’S ORDER / 机场推荐')+note('榜单来源：站主提供的推荐顺序。套餐信息来自旧博客历史资料，未进行统一实测。')+'<div class="rank-list">'+''.join(rank_row(b,i) for i,b in enumerate(brands[:10],1))+'</div>'
    page('/topics/recommended/','机场推荐排行1–10：站主推荐品牌与套餐资料','按站主指定顺序收录微风网络、飞猫云、暮光网络、大佬云、Firefly、灵猫、闪跃、无忧链接、跨界云和二猫云。',recommended)
    candidates=[b for b in brands if b['id'] not in ['firefly','jilian','kosing'] and monthly(b)]
    cheap=sorted(candidates,key=lambda b:(monthly(b)['price'],b['order']))[:10]
    body=head('便宜机场严选排行 1–10','按历史资料中的最低月付金额排序。容量、版本与资料日期同步展示，方便进一步核对。','BUDGET SELECTION / 便宜机场严选')+note('口径：仅比较明确按月付费、月流量已知的最低档，不折算年付、不扣未验证优惠、不混入按量包。容量不同，因此这是入门月支出参考榜，不能直接代表性价比或当前在售排名。Firefly、极连云及可信云因原资料争议暂不参与。')+'<div class="rank-list">'+''.join(rank_row(b,i,True) for i,b in enumerate(cheap,1))+'</div>'+sources(cheap[0])
    page('/topics/budget/','便宜机场严选排行1–10：历史月付入门价参考','按历史月付参考价展示10个低价候选，注明金额、容量、付款周期与资料日期，不将未经验证的优惠计入价格。',body)
    body=head('稳定机场严选：1–10候选与实测标准','稳定需要持续观察。这十个席位按站主推荐顺序作为候选，等待同条件测试后再形成性能排名。','STABILITY RESEARCH / 稳定机场严选')+note('目前为待测候选表，序号是候选席位，不能解读为稳定性名次。本站尚无统一长期实测数据。')+'<div class="rank-list">'+''.join(rank_row(b,i,stable=True) for i,b in enumerate(brands[:10],1))+'</div>'+section_title('EVIDENCE FIRST / 评选标准','实测后怎样形成稳定榜')+'<div class="panel"><p>建议在常用网络中连续观察至少7天，覆盖高峰与非高峰。固定客户端、节点与目标任务，记录成功样本、断线、恢复耗时以及配置变化。观察周期是本站拟采用的方法，不代表已经完成测试。</p><p>按运营商与地区分组，公开可用率、失败次数和最长连续中断。缺少同口径资料的品牌不补分，最终榜单同时给出样本数量与限制。</p><a href="/methodology/">完整测评与编辑方法</a></div>'
    page('/topics/stable/','稳定机场严选1–10：待测候选、稳定性方法与证据','提供10个稳定机场待测候选及统一观察标准；尚未开展长期实测，不发布虚构的速度、稳定性分数或排名。',body)
    body=head('机场测评：先有证据，再有结论','套餐资料已收录；网络性能尚待统一实测。逐品牌保留测评字段与原始数据位置。','REVIEW DESK / 机场测评')+review_status(brands[0])+section_title('BRAND RECORDS / 品牌记录','29个品牌的测评档案')+'<div class="review-grid">'+''.join(f'<a href="/reviews/{b["id"]}/"><strong>{E(b["name"])}</strong><span>实测待补充 · 查看资料状态</span></a>' for b in brands)+'</div>'+button('查看测试方法','/methodology/',True)
    page('/reviews/','机场测评中心：29个品牌实测档案与数据标准','机场测评中心展示29个品牌的测评状态、资料来源与统一测试标准，未完成实测项目保持待补充。',body)
    for b in brands:
        body=head(b['name']+'测评档案','套餐分析与性能测试分别记录。以下指标尚未取得可复核样本。','REVIEW FILE / 测评档案')+review_status(b)+note(E(b['note']))+section_title('BEFORE TESTING / 测试准备','需要记录的环境与条件')+'<div class="panel"><ul><li>测试日期、时间与时区，所在地区及接入运营商。</li><li>设备、客户端版本、代理模式、套餐和被测节点。</li><li>目标任务、采样间隔、成功条件及原始日志。</li><li>优惠结算、平台可用性及客服体验分别保留证据。</li></ul><p>这些是待执行的记录要求，没有实际结果。官网宣传或历史套餐不能替代测试日志。</p></div>'+sources(b)+button('查看套餐档案','/brands/'+b['id']+'/',True)
        page('/reviews/'+b['id']+'/',b['name']+'机场测评：资料状态与待测指标','查看'+b['name']+'测评资料及待测指标。当前没有统一网络实测，不提供未经证实的速度、延迟或平台功能结论。',body)
    method=head('编辑与测评方法','让价格有来源，让比较有口径，让性能有样本。','OUR METHODOLOGY / 编辑方法')+'''<article class="prose"><h2>资料分为三种状态</h2><p>站主提供：品牌顺序、推广入口与优惠码。历史参考：从指定旧博客迁移的套餐及原记录说明。实测结果：需要具体环境与原始日志，目前尚未取得。三个层级不相互代替。</p><h2>价格如何展示</h2><p>金额按对应付款周期显示总价，年付总额不伪装成月付价格。月额度、年额度与按量总额度分别标注；未知重置规则保持未知。套餐资料采用原日期，资料读取日期另行记录。</p><h2>推荐与低价榜如何排序</h2><p>品牌库与机场推荐前十使用站主顺序。便宜榜比较无归属争议且额度明确的最低月付金额，排序并列时沿用品牌目录顺序；不叠加未经结算验证的优惠。不将不同容量的低月费写成绝对性价比。</p><h2>稳定性测试怎样开展</h2><p>计划在固定环境中连续观察至少7天，覆盖高峰与非高峰，记录目标任务成功率、延迟波动、断线次数及恢复耗时。测试失败样本保留，不仅发布最佳结果。建议周期是方法设计，实际完成时间与样本数必须在报告中另行说明。</p><h2>未知与争议如何处理</h2><p>未知字段不填零、不借用其他品牌数值。Firefly与极连云保留旧站资料归属争议，可信云保留运营状态及客户端支持疑点。出现新证据时更新原始数据、品牌页、相关文章及专题，保留更正原因。</p><h2>文章内容的定位</h2><p>29篇品牌资料评析使用站主授权的旧博客资料；121篇知识指南围绕独立问题编写。没有虚构使用经历、购买记录、用户评价或服务性能。方法指南不能代替对应客户端的官方操作文档。</p><h2>更正与更新</h2><p>更正时保留资料日期、来源链接、具体字段和修改说明。订单与订阅链接等敏感信息必须先脱敏。本站目前不收集账户、订阅密钥或支付资料。</p></article>'''
    page('/methodology/','机场推荐编辑方法与测评标准','公开品牌资料层级、历史价格口径、榜单排序规则、稳定性测试计划及缺失数据处理方法。',method)
    disclosure=head('推广与资料说明','知道信息从哪里来，也知道推荐链接可能带来的利益关系。','EDITORIAL DISCLOSURE / 推广说明')+'''<article class="prose"><h2>推广关系</h2><p>品牌库中的入口由站主提供，链接包含推广参数。读者通过这些入口注册或购买，站主可能获得佣金。推广关系不构成质量、性能或隐私保证。</p><h2>排名来源</h2><p>机场推荐榜由站主指定顺序；品牌目录也遵循提供顺序。便宜榜使用历史月付参考价格，稳定榜目前是待测候选。不同榜单依据在各专题页面公开。</p><h2>优惠码</h2><p>优惠码由站主提供，未完成当前订单验证。本站不承诺有效期、折扣力度或适用范围，订单最终金额需要在购买页确认。</p><h2>隐私与数据</h2><p>本站为静态博客，无登录、付款或订阅收集功能。复制代码与本地筛选在浏览器中执行；动画偏好保存在当前浏览器。访问外部服务后，其数据处理适用对应服务的条款。</p></article>'''
    page('/disclosure/','推广关系、优惠码与资料披露','了解翻墙梯子的推广链接、排名来源、优惠码验证状态和浏览器本地偏好说明。',disclosure)
    sitepaths=list(paths)+['/sitemap/']
    page('/sitemap/','站点地图：博客、品牌与专题索引','翻墙梯子全部文章、品牌档案、测评记录及专题页面的HTML索引。',head('站点地图','全部页面的阅读入口。','SITEMAP / 全站索引')+'<div class="sitemap-list">'+''.join(f'<a href="{r["path"]}">{E(r["title"])}</a>' for r in search)+'</div>')
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{xe(url(p))}</loc><lastmod>{DATE}</lastmod></url>' for p in paths)+'</urlset>',encoding='utf-8')
    (OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n',encoding='utf-8')
    (OUT/'CNAME').write_text('fanqiangtizi.wiki\n',encoding='utf-8')
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    rss='<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>翻墙梯子博客</title><link>'+DOMAIN+'</link><description>梯子推荐、机场推荐与选购研究</description><language>zh-CN</language>'+''.join(f'<item><title>{xe(r["title"])}</title><link>{url(r["path"])}</link><guid>{url(r["path"])}</guid><description>{xe(r["description"])}</description></item>' for r in article_records)+'</channel></rss>'
    (OUT/'feed.xml').write_text(rss,encoding='utf-8')
    (ROOT/'data/articles.json').write_text(json.dumps(article_records,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'data/reviews.json').write_text(json.dumps([{'brandId':b['id'],'status':'pending','environment':None,'samples':[],'throughputMbps':None,'latencyMs':None,'packetLossPercent':None,'uptimePercent':None,'platformResults':[],'note':'没有实际测试数据，不能发布为测评结果'} for b in brands],ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'404.html').write_text((OUT/'index.html').read_text(encoding='utf-8').replace('<meta name="robots" content="index,follow">','<meta name="robots" content="noindex,follow">').replace('<main id="main" class="shell">','<main id="main" class="shell"><div class="page-head"><h1>这个页面暂时不存在</h1><p>请通过下方品牌库、专题或文章入口继续阅读。</p></div>'),encoding='utf-8')
    print(json.dumps({'articles':len(article_records),'brands':len(brands),'coupons':sum(bool(b.get('coupon')) for b in brands),'pages':len(paths),'topics':14},ensure_ascii=False))

def rank_row(b,i,cheap=False,stable=False):
    p=monthly(b)
    detail='待实测候选 · 不代表稳定性名次' if stable else f'¥{money(p["price"])} / 月付参考 · {p["gb"]} GB/月 · {p.get("sourceDate","未注明")}' if cheap else b['profile']['headline']
    return f'<article class="rank-row"><span class="rank-number">{i:02}</span><div><h2><a href="/brands/{b["id"]}/">{E(b["name"])}</a></h2><p>{E(detail)}</p><small>{E(b["profile"]["tradeoff"])}</small></div><a class="button secondary" href="/brands/{b["id"]}/">品牌详情</a></article>'

if __name__=='__main__':
    import sys
    if '--slice' not in sys.argv: build_remaining()
