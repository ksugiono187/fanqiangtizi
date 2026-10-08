"""Editorial components for the brand research, topic and guide editions."""
import json, re, math
from pathlib import Path

def setup(env):
    for key in ['E','head','monthly','money','plans_table','coupon_block','outbound','sources','review_status','brands','DATE','ROOT']:
        globals()[key]=env[key]
    global CASES
    CASES={int(r[0]):r[1:] for r in [line.split('\t') for line in (ROOT/'data/guide-cases.tsv').read_text(encoding='utf-8').splitlines()]}
    assert len(CASES)==121

def para(text):return '<p>'+E(text)+'</p>'
def ul(items):return '<ul>'+''.join('<li>'+E(x)+'</li>' for x in items)+'</ul>'
def table(caption,headers,rows):
    return '<div class="table-wrap editorial-table"><table><caption>'+E(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+E(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def toc(items):return '<nav class="section-nav" aria-label="本页目录">'+''.join(f'<a href="#{key}">{E(label)}</a>' for key,label in items)+'</nav>'
def section(key,title,content):return f'<section class="editorial-section" id="{key}"><h2>{E(title)}</h2>{content}</section>'
def meta(category,minutes=''):
    return f'<div class="editorial-meta"><span>翻墙梯子编辑部</span><span>{E(category)}</span><time datetime="{DATE}">更新 {DATE}</time>'+('<span>约 '+E(minutes)+' 分钟阅读</span>' if minutes else '')+'</div>'
def valid_months(b):
    if b['id'] in ['firefly','jilian','kosing','flyv']:return []
    return sorted([p for p in b['plans'] if p['cycle']=='月付' and p.get('gb') and p.get('quotaPeriod')=='month' and not p.get('capacityConflict')],key=lambda p:p['gb'])
def price_info(b):
    if b.get('referenceMonthlyPrice') is not None:return '¥'+money(b['referenceMonthlyPrice']),'月付参考 · 站主提供','对应流量待补充'
    ps=valid_months(b)
    if ps:return '¥'+money(ps[0]['price']),'月付参考起',str(ps[0]['gb'])+' GB / 月'
    return '待核对','当前套餐身份或状态','见原始资料说明'
def facts(b):
    price,period,quota=price_info(b)
    return '<div class="fact-grid">'+''.join(f'<div><span>{E(label)}</span><strong>{E(value)}</strong><small>{E(sub)}</small></div>' for label,value,sub in [('入门支出',price,period),('额度周期',quota,'按套餐分别标注'),('套餐记录',str(len(b['plans']))+' 项','历史价目与周期'),('优惠代码',b.get('coupon') or '未提供','适用范围以结算为准')])+'</div>'
def economics(b):
    ps=valid_months(b)
    if not ps:
        return '<div class="editorial-callout"><strong>费用分析的适用条件</strong>'+para(b['profile']['monthlyInsight'])+para('当前资料不足以将全部历史套餐与正在销售的版本对应，因此暂不生成每GB成本或容量匹配结果。取得一致的套餐名、金额、额度与周期后，才适合进行这些计算。')+'</div>'
    rows=[]
    previous=None
    for p in ps:
        increase='入门档'
        if previous and p['gb']>previous['gb']:
            dp=p['price']-previous['price'];dq=p['gb']-previous['gb']
            increase=f'多付{money(dp)}元 / 增加{money(dq)}GB'
        rows.append([p['name'],f'¥{money(p["price"])}',f'{p["gb"]}GB / 月',f'{p["price"]/p["gb"]:.3f}元 / GB',increase])
        previous=p
    content=table('月付档位的名义容量成本：未计倍率、优惠和附加费用',['档位','月支出','月额度','标称单位价','与前一档的差异'],rows)
    content+=para(b['profile']['monthlyInsight'])
    content+=para('单位价按参考月费÷标称月额度计算，只用于理解容量定价，不衡量网络质量。实际用量少于额度时，按实际消耗分摊的成本会更高；若节点有倍率，还需单独核对有效传输量。')
    return content
def scenarios(b):
    ps=valid_months(b)
    if not ps:return para(b['profile']['verifyInsight'])+table('当前可采取的核对动作',['目标','先取得什么','判断依据'],[['确认套餐归属','带品牌名称的当前套餐页','套餐名称、金额、周期一致'],['比较使用成本','明确的有效流量和重置规则','按同一计量窗口计算'],['评估实际体验','你的网络与任务记录','可用性、持续任务和恢复表现']])
    needs=sorted(set([max(1,round(ps[0]['gb']*.6)),round(ps[0]['gb']*1.2),round(ps[-1]['gb']*.8)]))
    rows=[]
    for need in needs:
        chosen=next((p for p in ps if p['gb']>=need),None)
        if chosen:
            rows.append([f'假设{need}GB / 月',chosen['name'],f'¥{money(chosen["price"])} / 月',f'额度余量{chosen["gb"]-need}GB；另查倍率与必要功能'])
        else:rows.append([f'假设{need}GB / 月','无直接对应档','需查看当前套餐','不要默认通过加购满足需求'])
    return table('容量选择演算：是假设需求，不是实际用户测评',['月度需求','容量可覆盖的参考档','参考支出','仍需确认'],rows)+para('表中以标称容量为边界，尚未计入节点倍率、超额处理或设备限制。实际选择应先排除无法满足必要地区和客户端需求的档位，再决定是否为峰值月份保留余量。')
def purchase_checks(b):
    return table('购买前核对单',['核对项目','需要看到的内容','为什么影响选择'],[['套餐版本',b['profile']['verifyInsight'],'避免把不同版本的价格与容量拼接'],['流量计量','重置日、时区、上下行计费与节点倍率','决定有效可用量及月度规划'],['设备与配置','允许的客户端格式、同时在线和共享规则','设备数不等于多人使用授权'],['付款与续费','最终实付、退款规则、续费价和自动续费','首次优惠不能代替持续成本'],['真实任务','常用时段、必要地区、任务完成与恢复','线路名称不能替代实际体验']])
def faqs(b):
    price,period,quota=price_info(b)
    questions=[('这个品牌的参考入门支出是多少？',f'{price}，{period}；{quota}。完整价目需要同时查看付款周期与资料日期。当前订单应以购买页显示为准。'),('月付、年付与按量如何选择？',b['profile']['cycleInsight']),('有哪些特别需要注意的条件？',b['profile']['tradeoff']),('优惠码是否已经核实有效？',('站主提供的代码为'+b['coupon']+'。本文没有当前结算验证记录，需核对适用套餐、资格、有效期与最终实付。' if b.get('coupon') else '站主没有提供该品牌优惠码。请查看当前活动，不采用其他品牌的代码推算折后价。'))]
    return '<div class="faq-list">'+''.join('<details><summary>'+E(q)+'</summary>'+para(a)+'</details>' for q,a in questions)+'</div>'
def rail(b):
    return '<aside class="research-rail"><span class="eyebrow">品牌入口</span><h3>'+E(b['name'])+'</h3>'+outbound(b)+'<p class="muted">入口由站主提供，含推广参数。</p><dl><dt>目录位置</dt><dd>'+f'{b["order"]:02}'+'</dd><dt>资料状态</dt><dd>'+E(b['status'])+'</dd><dt>原资料核对</dt><dd>'+E(b['checkedAt'])+'</dd></dl><a href="/reviews/'+b['id']+'/">查看测评档案 →</a></aside>'
def brand_detail(b):
    p=b['profile'];price,period,quota=price_info(b)
    body=head(b['name']+'：价格、套餐与选购分析',p['deck'],'品牌研究 / BRAND DOSSIER',f'<a href="/brands/">品牌库</a> / {E(b["name"])}')+meta('品牌档案')+facts(b)+'<div class="dossier-actions">'+outbound(b)+'<a class="button secondary" href="#plans">查看完整价目</a></div>'
    items=[('summary','选购摘要'),('plans','完整价目'),('economics','档位分析'),('scenarios','适用场景'),('network','线路与体验'),('coupon','优惠与购买'),('faq','常见问题'),('sources','来源与更新')]
    body+=toc(items)+'<div class="research-layout"><article class="research-body">'
    body+=section('summary','先看结论：'+p['headline'],'<div class="verdict-grid"><div><h3>值得比较的部分</h3>'+ul(p['strengths'])+'</div><div><h3>选择前的关键条件</h3>'+para(p['tradeoff'])+'</div></div>'+para('需求定位：'+b['audience'])+para(p['verifyInsight']))
    reference=''
    if b.get('referenceMonthlyPrice') is not None:reference='<div class="editorial-callout"><h3>¥'+money(b['referenceMonthlyPrice'])+' / 月付参考</h3>'+para('该价格由站主于'+b['referencePriceDate']+'提供，对应流量和具体权益待补充。下表单独保存旧资料中的历史套餐，不能将两个版本混合。')+'</div>'
    body+=section('plans','完整套餐价目与额度规则',reference+plans_table(b))
    body+=section('economics',p['monthlyTitle'],economics(b))
    body+=section('scenarios','按实际用量与使用频率选择',scenarios(b)+para(p['cycleInsight']))
    network=para('原资料线路描述：'+b['line']+'。这一描述属于资料记录，尚未取得当前节点配置与统一测试日志。')
    network+=table('线路与体验分别判断',['比较维度','已有信息','应如何验证'],[['线路描述',b['line'],'核对具体套餐、节点和资料版本'],['高峰任务','未取得统一样本','固定网络与任务，记录失败和恢复'],['地区与平台','未取得对应功能测试','逐地区逐功能记录日期和结果'],['客户端与并发','当前条款待核对','确认格式、版本与账号规则']])
    body+=section('network','线路标签之外，怎样判断体验',network+f'<a class="text-link" href="/reviews/{b["id"]}/">查看测评记录与待测项目 →</a>')
    body+=section('coupon','优惠码与购买核对',coupon_block(b)+purchase_checks(b)+outbound(b))
    body+=section('faq','关于'+b['name']+'的常见问题',faqs(b))
    body+=section('sources','资料来源与更新记录',sources(b)+table('本档案的数据层级',['资料','来源或日期','使用范围'],[['品牌顺序、入口和优惠码','站主提供','目录和访问入口'],['套餐及线路记录',b['checkedAt'],'历史参考与结构分析'],['本文整理',DATE,'计算、选择路径和待核对字段'],['性能测评','尚未取得统一日志','不作为速度或稳定性排名依据']]))
    body+='</article>'+rail(b)+'</div><div class="next-reading"><span>继续研究</span><a href="/articles/brand-'+b['id']+'/">'+E(b['name'])+'套餐研究报告 →</a><a href="/topics/recommended/">回到机场推荐专题 →</a></div>'
    return body
def brand_article(b,title):
    p=b['profile']
    body=head(title,p['deck'],'套餐研究 / RESEARCH NOTE',f'<a href="/articles/">博客文章</a> / 品牌研究')+meta('品牌研究','6')
    items=[('structure','结构与定位'),('economics','容量成本'),('cycle','周期取舍'),('decision','选择案例'),('check','购买核对'),('sources','资料依据')]
    body+=toc(items)+'<div class="reading-layout"><article class="prose longform">'
    body+='<div class="article-abstract"><span>内容摘要</span>'+para(p['deck'])+ul([p['headline'],p['monthlyInsight'],p['tradeoff']])+'</div>'
    body+=section('structure','从套餐结构理解'+b['name'],para('本文围绕'+b['name']+'的费用与容量展开。'+p['deck'])+para('适用需求：'+b['audience'])+ul(p['strengths'])+para(p['verifyInsight']))
    body+=section('economics',p['monthlyTitle'],economics(b))
    body+=section('cycle','长期付款与跨周期额度的取舍',para(p['cycleInsight'])+table('付款周期需要分别解释',['类型','现金支出','容量窗口','决策重点'],[['月付','每次支付一个月费用','只采用已明确的月额度','是否足够覆盖稳定月需求'],['年付','一次支付年费','以原条款标注为准','预计活跃月份、重置规则与退款'],['按量或单次','购买一份总额度','需要单独确认有效期','消耗节奏、账号有效和未用余额']])+para(p['tradeoff']))
    body+=section('decision','把参考价目放进三种用量情形',scenarios(b)+para(p['monthlyInsight']))
    body+=section('check',p['evidenceTitle'],para(p['verifyInsight'])+purchase_checks(b)+coupon_block(b))
    body+=section('sources','分析结论与资料依据',para('本文能够解释历史档位之间的费用差异和容量边界；不能从这些数据推导当前网络性能。'+b['note'])+sources(b))
    body+='<div class="article-conclusion"><h2>本文结论</h2>'+para(p['monthlyInsight'])+para(p['cycleInsight'])+'<a href="/brands/'+b['id']+'/">完整档案、入口与优惠码 →</a></div></article>'+rail(b)+'</div>'
    return body

HEADINGS={
 '预算选择':['费用口径与购买目标','把费用放在同一窗口计算','选择周期与容量的依据'],
 '流量知识':['先确认计量与额度规则','怎样记录任务产生的流量','将样本换算成规划需求'],
 '稳定性':['指标定义与观察范围','建立可重复的对照','如何解释失败与恢复'],
 '测评方法':['报告要回答的具体问题','采样和记录的基本要求','结论能够覆盖的范围'],
 '线路知识':['标签、配置与实际路径','从任务结果核对线路描述','比较时保留的环境差异'],
 '客户端':['配置与版本的对应关系','导入或修改前的核对','验证任务与恢复原配置'],
 '故障排查':['先定位失败发生的阶段','按单变量顺序做对照','如何判断恢复与下一步'],
 '安全隐私':['需要保护的数据与暴露范围','核对来源和处理方式','采取措施后的确认'],
 '优惠活动':['优惠资格和费用边界','以结算结果核对活动','把优惠放回购买需求'],
 '使用场景':['将真实任务变成选择条件','在常用环境验证任务','预算、余量与备用安排'],
 '比较决策':['比较口径与资料来源','把条件放进同一张表','形成有适用范围的结论']}

FIELD_HINTS={
 '预算选择':['保留同一订单的实付与附加项目','按实际预计使用时间计算','先排除不满足必要需求的方案'],
 '流量知识':['记录起止时间和同一计量单位','把重置窗口和任务时长对齐','用固定任务核对前后余额'],
 '稳定性':['同时保留成功与失败的时间戳','每次对照尽量固定任务与环境','统计时注明样本与适用范围'],
 '测评方法':['关联原始样本，不只保存截图','提前定义成功、失败与异常处理','让结论能追溯到测试过程'],
 '线路知识':['区分标签、官方描述与实际结果','注明节点、目标、时间与版本','未确认的路径信息不作推断'],
 '客户端':['记录实际应用和内核版本','保留私有配置副本及脱敏日志','逐个确认常用任务，保留恢复方法'],
 '故障排查':['写明首次失败时间和具体错误','一次只改变一个条件并记录结果','无法确定原因时保持未知'],
 '安全隐私':['先判断字段是否能够识别或授权账号','只保留和提供必要的信息','需要撤销的权限或令牌在服务端处理'],
 '优惠活动':['保存活动原文与核对日期','写出对应套餐、周期和资格','以最终订单结果确认，而非代码外观'],
 '使用场景':['明确必要任务与无法妥协的条件','覆盖真实设备、网络和使用时段','记录完成情况与中断恢复方式'],
 '比较决策':['每项数据带来源与时间','未知与零值分开处理','改变需求后重新计算和筛选']}

def guide_article(row,i,cat_slug,records):
    cat,title,p1,p2,p3=row
    case,*fields=CASES[i]
    headings=HEADINGS[cat]
    paragraphs=[p1,p2,p3,case]
    minutes=str(max(4,math.ceil(sum(len(p) for p in paragraphs)/240)+2))
    body=head(title,p1,'深度指南 / FIELD GUIDE',f'<a href="/articles/">博客文章</a> / {E(cat)}')+meta(cat,minutes)
    items=[('answer','阅读摘要'),('scope',headings[0]),('method',headings[1]),('example','情形与演算'),('worksheet','核对表'),('decision','行动与结论'),('related','延伸阅读')]
    body+=toc(items)+'<div class="reading-layout"><article class="prose longform">'
    body+='<section class="article-abstract" id="answer"><span>本文回答的问题</span><h2>'+E(title)+'</h2>'+para(p1)+'<div class="abstract-topics">'+''.join('<span>'+E(f)+'</span>' for f in fields)+'</div></section>'
    body+=section('scope',headings[0],para('围绕这项问题，首先需要取得'+fields[0]+'的记录，并确认'+fields[1]+'是否与当前任务对应。'+FIELD_HINTS[cat][0]+'。这里需要区分记录本身和由记录推导的判断；'+fields[2]+'则用于确认最终选择或处理结果。'))
    body+=section('method',headings[1],para(p2)+table('本文的判断路径',['阶段','对应问题','应保留什么'],[['确认条件',fields[0],FIELD_HINTS[cat][0]],['执行对照',fields[1],FIELD_HINTS[cat][1]],['解释结果',fields[2],FIELD_HINTS[cat][2]]]))
    body+=section('example','具体情形：怎样推导而不跳过条件','<div class="worked-case"><span>说明性案例 · 不代表任何品牌的实测结果</span>'+para(case)+'</div>'+para('这个情形的重点是'+fields[0]+'、'+fields[1]+'与'+fields[2]+'之间的对应关系。条件发生变化时，需要重新核对结果；不能只保留案例中的数字，而省略它成立的前提。'))
    body+=guide_supplement(i)
    body+=section('worksheet','可直接使用的核对表',table(title+'：记录字段',['核对字段','建议记录方式','完成后的用途'],[[f,FIELD_HINTS[cat][n],['确认起点与边界','进行同条件比较','判断结论是否成立'][n]] for n,f in enumerate(fields)])+para('同一次记录应使用一致的时间窗口，并保留对应来源、版本或原始样本。出现相互矛盾的数字时，先查明差异，不用平均值或其他品牌资料填补。'))
    body+=section('decision',headings[2],'<ol class="action-steps">'+''.join('<li><strong>'+E(label)+'</strong>'+para(text)+'</li>' for label,text in [('先核对 '+fields[0],FIELD_HINTS[cat][0]+'，将可确认的条件写入表格；未取得的信息单独标记。'),('再检查 '+fields[1],FIELD_HINTS[cat][1]+'，使用与本文问题相对应的记录，避免无关数据影响判断。'),('最后判断 '+fields[2],FIELD_HINTS[cat][2]+'，如必要条件仍缺失，先完成核对，再执行依赖它的选择或修改。')])+'</ol>')
    body+='<section class="article-conclusion"><h2>结论与适用边界</h2>'+para(p3)+para('本文提供的是'+cat+'的判断方法，案例采用明确的假设条件。涉及具体品牌时，需要引用当前档案中的套餐版本与资料日期；涉及实际体验时，还需要你所使用网络和任务的记录。')+'</section>'
    if cat in ['客户端','线路知识','故障排查']:
        body+='<div class="source-box"><h2>技术参考</h2><p>配置字段与版本兼容性请分别核对 <a href="https://sing-box.sagernet.org/configuration/" target="_blank" rel="noopener">sing-box 官方配置文档</a> 与 <a href="https://wiki.metacubex.one/config/" target="_blank" rel="noopener">Mihomo 官方配置文档</a>。本文不把某个客户端的操作步骤泛化到全部应用。</p></div>'
    elif cat in ['流量知识','测评方法']:
        body+='<p class="source-reference">计算依据：本文列明的单位换算、费用或样本公式；情形数据为说明性假设。品牌价目另见带来源日期的品牌档案。</p>'
    peers=[n for n,r in enumerate(records,1) if r[0]==cat and n!=i]
    nearest=sorted(peers,key=lambda n:abs(n-i))[:3]
    body+=section('related','沿着这个问题继续阅读','<div class="related-reading">'+''.join(f'<a href="/articles/guide-{n:03}/"><span>{E(cat)}</span><strong>{E(records[n-1][1])}</strong></a>' for n in nearest)+'</div><p><a href="/topics/'+cat_slug+'/">'+E(cat)+'全部指南 →</a></p>')
    body+='</article><aside class="research-rail"><span class="eyebrow">阅读路径</span><h3>'+E(cat)+'</h3>'+ul(fields)+'<a href="/brands/">品牌资料库 →</a><a href="/methodology/">编辑与测评方法 →</a></aside></div>'
    return body

def guide_supplement(i):
    if i in [1,112,116]:
        selected=[b for b in brands[:10] if valid_months(b)][:6]
        rows=[]
        for b in selected:
            p=valid_months(b)[0]
            rows.append([b['name'],p['name'],f'¥{money(p["price"])}',f'{p["gb"]}GB / 月',f'{p["price"]/p["gb"]:.3f}元 / GB'])
        return section('brand-comparison','用历史价目理解两种费用口径',table('真实资料演算：只比较参考月付金额与标称容量',['品牌','参考档位','月支出','容量','标称单位价'],rows)+para('这张表使用品牌档案中的历史月付资料，金额未扣优惠、未计倍率。月支出排序与单位价排序会不同：预算有限时先看满足自己用量所需的总费用，不能直接把容量较小的起价与容量较大的档位比较。')+'<p><a href="/topics/budget/">查看完整价格口径及资料日期 →</a></p>')
    if i==2:
        return section('break-even','怎样找到年付与月付的费用分界',table('假设月付25元、年付240元：仅比较相同权益的购买支出',['预计活跃月份','按需月付合计','年付合计','费用判断'],[['6个月','150元','240元','月付少支出90元'],['8个月','200元','240元','月付少支出40元'],['10个月','250元','240元','年付少支出10元'],['12个月','300元','240元','年付少支出60元']])+para('数学分界为240÷25=9.6个月。只有相同权益、年内确实持续使用且其他费用一致时，这个分界才有意义。若年包和月包容量不同，或年包存在单独限制，需要先按必要需求重新匹配，不能只用两个标价相除。')+para('付款周期也改变选择的灵活性。可退款范围、服务变更、项目结束时间与账号闲置规则，不适合凭空换算成一个确定风险分数；应作为独立条款核对，再决定是否承担较大的首次支出。'))
    if i==14:
        return section('multiplier','混合倍率怎样计算有效流量',table('假设传输总量100GB，分配到不同倍率节点',['倍率1传输','倍率2传输','基础扣减演算','结果'],[['100GB','0GB','100×1','100GB'],['70GB','30GB','70×1 + 30×2','130GB'],['50GB','50GB','50×1 + 50×2','150GB'],['0GB','100GB','100×2','200GB']])+para('分段加总比用一个统一倍率更准确。若不同任务采用不同节点，先记录各段传输量，再按对应计费规则演算。表中没有加入双向计费、单位差异与后台重传；真实余额仍需与服务条款和实际记录对照。'))
    if i in [23,113]:
        return section('observation','建立一份覆盖真实时段的观察计划',table('建议观察安排：是方法设计，不是本站已完成测试',['观察任务','固定条件','记录结果','解释范围'],[['常用网页与资料访问','同一目标、同一客户端与网络','完成、超时、错误阶段','基础任务可用性'],['会议或持续连接','实际时长、摄像头和共享设置','卡顿、重连、任务中断','实时任务体验'],['高峰与非高峰对照','同一节点、同规模任务','耗时、失败、恢复方式','时段差异'],['故障与备用切换','故障时刻与替代方案','恢复耗时和完成情况','恢复能力']])+para('可以连续观察至少7天作为初步记录，覆盖工作日和周末，但时间更长不自动代表全国适用。需要按地区和接入网络分组，发布样本量、失败次数和最长连续中断；更换客户端、节点或套餐后，应标记新阶段。'))
    if i in [57,63,68]:
        return section('stages','把下载失败与解析失败分成两条路径',table('导入问题的分阶段诊断',['可观察现象','优先核对','下一步'],[['无法取得响应','URL有效期、令牌、接入网络与错误时间','通过可信后台确认地址，并保留脱敏下载错误'],['返回登录页或错误页','响应内容是否真的是配置','确认登录或订阅入口，不将网页当配置导入'],['取得配置但报字段错误','实际客户端和内核版本、格式与日志位置','对照对应官方文档，保留原文件再修改'],['导入成功但任务失败','节点、规则匹配和实际接管范围','按任务日志定位连接或应用阶段']])+para('同样表现为导入失败，原因可能出现在不同阶段。修改字段只能处理配置解析问题，不能修复失效的订阅地址；重置地址也不能自动解决当前客户端不支持的格式。每次更改后只验证与该阶段对应的结果。'))
    if i==100:
        return section('office','把办公需求拆成三组验证任务',table('远程办公验证表：由真实工作任务定义标准',['任务组','先测试什么','主要观察','备用安排'],[['会议沟通','常用会议时长、屏幕共享和摄像头','卡顿、断线、重连与上传表现','准备可实际启用的替代接入'],['文档协作','检索、下载、上传和保存结果','任务完成、首响应和同步冲突','保留工作文件与未提交变更'],['文件交付','有权访问的代表性文件','持续传输、续传和最终文件可读取','确认时间窗口和备用传输方式']])+para('关键任务需要明确失败后的恢复步骤。流量足够、客户端下载成功或单次测速很快，都不能代替会议和交付的完成记录。先验证必要任务，再在能满足这些任务的候选中比较费用，避免高分指标掩盖硬条件缺失。'))
    return ''

def review_file(b):
    p=b['profile']
    body=head(b['name']+'评测研究：资料分析与测试计划',p['deck'],'评测研究 / REVIEW FILE',f'<a href="/reviews/">机场测评</a> / {E(b["name"])}')+meta('资料分析 · 性能待测')
    body+=toc([('position','研究重点'),('data','套餐资料'),('protocol','测试方案'),('evidence','报告字段'),('sources','资料来源')])+'<div class="research-layout"><article class="research-body">'
    body+=section('position','这份报告需要回答什么',para(p['headline'])+para(p['monthlyInsight'])+para(p['verifyInsight'])+'<div class="editorial-callout"><strong>当前进度：已整理套餐资料，尚未取得统一性能样本</strong>'+para('本文提供数据分析与可执行测试方案。速度、延迟、可用率和平台功能将在有环境信息与原始记录后分别发布。')+'</div>')
    body+=section('data','套餐结构能够说明的部分',economics(b)+para(p['cycleInsight']))
    body+=section('protocol','怎样安排这个品牌的测试',table('测试计划：尚未执行，不是结果',['项目','固定条件','记录内容','判断边界'],[['基础访问','常用网络、同节点与目标','成功或错误、耗时、时间戳','只覆盖被测目标'],['持续传输','代表性文件、相同任务规模','完整耗时、失败和续传','不以瞬时峰值代替'],['晚高峰对照','相同时段重复任务','分组样本与异常事件','注明地区和运营商'],['故障恢复','明确首次失败和恢复标准','中断时长、切换步骤','无法确认的起点保持未知'],['地区功能','具体账号、出口与目标功能','日期、功能通过或失败','不保证持续解锁']])+para('对于'+b['name']+'，测试前优先完成以下套餐核对：'+p['verifyInsight']))
    body+=section('evidence','一份可复核报告应保留什么',table('报告记录字段',['记录组','必要字段','发布方式'],[['环境','地区、运营商、设备、客户端和模式','按环境分组，避免全国化结论'],['套餐','实际版本、购买日期、额度和倍率','与历史参考档位区分'],['样本','任务、目标、时间、成功条件和失败','保留全部样本与异常处理依据'],['指标','数量、单位、计算口径与观察窗口','公开典型值、范围与限制'],['结论','适用任务、日期和未覆盖项目','不填补未知值，不添加虚构评分']])+para(p['tradeoff']))
    body+=section('sources','资料来源与后续更新',sources(b)+'<p><a href="/articles/guide-034/">如何写一份完整测评报告 →</a></p>')
    return body+'</article>'+rail(b)+'</div>'

def article_front(records):
    selected=[(2,'费用研究'),(23,'稳定性观察'),(63,'配置排查')]
    return '<div class="journal-feature-grid">'+''.join(f'<a href="/articles/guide-{i:03}/"><span>{label} / FEATURE</span><strong>{E(records[i-1][1])}</strong><p>{E(records[i-1][2])}</p><small>阅读案例与核对表 →</small></a>' for i,label in selected)+'</div>'

def collection_front(category,records):
    fields=HEADINGS[category]
    return '<section class="topic-brief"><span class="eyebrow">专题阅读路径</span><h2>从概念到记录，再到实际选择</h2><div class="topic-criteria">'+''.join('<div><strong>'+f'{i:02} / '+E(text)+'</strong><p>'+E(FIELD_HINTS[category][i-1])+'</p></div>' for i,text in enumerate(fields,1))+'</div></section>'

def rank_card(b,i,cheap=False,stable=False):
    p=b['profile'];price,period,quota=price_info(b)
    label='候选' if stable else '严选' if cheap else '推荐'
    body=f'<article class="ranking-dossier" id="rank-{i}"><div class="ranking-heading"><span class="rank-medallion">{i:02}</span><div><span class="eyebrow">{label}席位 · {E(period)}</span><h2><a href="/brands/{b["id"]}/">{E(b["name"])}</a></h2></div><div class="ranking-price"><strong>{E(price)}</strong><span>{E(quota)}</span></div></div>'
    body+='<p class="ranking-deck">'+E(p['deck'])+'</p><div class="ranking-analysis"><section><h3>'+('为什么纳入候选' if stable else '套餐结构与比较价值')+'</h3>'+ul(p['strengths'])+para(p['monthlyInsight'])+'</section><section><h3>适用需求与选择条件</h3>'+para(b['audience'])+para(p['cycleInsight'])+'</section></div>'
    if stable:body+='<div class="editorial-callout"><strong>稳定性验证重点</strong>'+para('这一个席位需要固定常用网络、具体套餐与节点，连续记录任务成功、断线和恢复情况。'+p['verifyInsight'])+'</div>'
    else:body+='<div class="editorial-callout"><strong>购买前最值得确认的事项</strong>'+para(p['tradeoff'])+para(p['verifyInsight'])+'</div>'
    body+='<div class="dossier-footer"><span>资料核对 '+E(b['checkedAt'])+' · '+E(b['status'])+'</span><div><a href="/brands/'+b['id']+'/">完整品牌分析 →</a><a href="/articles/brand-'+b['id']+'/">套餐研究 →</a></div></div></article>'
    return body
def topic_intro(selected,mode):
    rows=[]
    for i,b in enumerate(selected,1):
        price,period,quota=price_info(b)
        rows.append([f'{i:02} '+b['name'],price,quota,b['profile']['headline'],b['checkedAt']])
    names={'recommended':('按指定推荐顺序，逐个比较套餐与使用条件','推荐顺序由站主指定。每个席位包含费用结构、适用需求与核对重点，读者可以依据自己的条件重新筛选。'), 'budget':('低月支出与低单位价，是两种比较','本专题按可确认月额度的历史最低月付金额排序。小额度档可能月费更低，大额度档可能单位价更低；实际需求决定应比较哪一档。'), 'stable':('候选目录与性能排名分开呈现','以下十个席位用于安排后续稳定性测试。缺少同条件连续样本，因此不提供星级、分数或稳定性高低结论。')}
    title,intro=names[mode]
    body='<section class="topic-brief"><span class="eyebrow">专题阅读说明</span><h2>'+title+'</h2>'+para(intro)+'<div class="topic-criteria">'+''.join('<div><strong>'+label+'</strong><p>'+text+'</p></div>' for label,text in [('01 / 先确认需求','预算、必要地区、设备和真实任务。'),('02 / 再统一口径','月付、年度与按量额度分别计算。'),('03 / 最后验证体验','以常用网络的任务样本确认可用性。')])+'</div></section>'
    body+=table('十个候选快速对照：价格为有日期的参考记录',['席位与品牌','入门支出','额度说明','比较重点','资料核对'],rows)
    body+=toc([('rank-'+str(i),f'{i:02} '+b['name']) for i,b in enumerate(selected,1)])
    return body
def home_upgrade(body):
    body=body.replace('连接之前，先读懂选择','套餐研究 · 选购专题 · 实用指南').replace('梯子推荐，<br>从<span>严选</span>开始。','机场推荐，<br>从<span>需求</span>到选择。').replace('机场推荐、套餐分析与使用指南。<br>看清价格与流量，也看清每一个结论的依据。','29个品牌的套餐档案、150篇问题指南。<br>比较费用结构、流量周期与实际使用条件，<br>找到适合自己的选择路径。')
    end=body.index('</section>')+len('</section>')
    intro='<section class="editorial-entry"><div><span class="eyebrow">本期研究 / RESEARCH DESK</span><h2>把每一个选择，拆成可以比较的问题。</h2><p>看榜单确定候选，读档案理解套餐，再用指南验证自己的需求。</p></div><a href="/topics/recommended/"><span>01 / 品牌比较</span><strong>十个推荐席位的完整分析</strong><small>套餐定位、费用与购买条件 →</small></a><a href="/articles/guide-002/"><span>02 / 费用研究</span><strong>月付与年付的真实取舍</strong><small>按活跃月份计算，而非只看折扣 →</small></a></section>'
    return body[:end]+intro+body[end:]
