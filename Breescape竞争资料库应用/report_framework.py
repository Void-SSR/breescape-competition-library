"""User-approved V1.0 research contract; revised item 6 has two questions."""
VERSION = 'V1.0-20261105-approved'
QUESTIONS = {
 1: [('background','成立时间与发展背景'),('business','主营业务'),('position','品牌定位与核心宣称'),('target','目标消费者'),('difference','品牌差异化：希望消费者记住它什么？')],
 2: [('scale','品牌销售规模及增长情况'),('channels','各渠道销售额及占比'),('main','核心销售渠道'),('growth','增长最快的渠道')],
 3: [('matrix','各品类布局及价格带'),('contribution','核心产品销量及销售贡献'),('structure','依靠单一爆款，还是多品类发展？')],
 4: [('identity','产品名称、规格、价格及商品链接'),('performance','销量、销售额、评分及评论数量'),('concept','商家给消费者设计的核心购买理由是什么？'),('difference','与同类产品相比，有什么差异？')],
 5: [('positive','消费者认可哪些方面？'),('negative','消费者不认可哪些方面？'),('purchase','消费者真实的购买理由是什么？'),('unmet','消费者还有哪些未满足的需求？')],
 6: [('drivers','产品销量背后的主要驱动因素是什么？'),('advantage','相比同类产品，真正领先的地方是什么？')],
 7: [('accounts','渠道账号、粉丝量、账号数量与发布频率'),('affiliate','达人带货与品牌自营情况'),('format','直播与短视频销售占比')],
 8: [('samples','TOP5内容：视频、截图与播放及互动数据'),('message','视频表达什么卖点，为什么能够吸引消费者？'),('conversion','是否形成实际销售转化？')],
 9: [('strategy','主要内容方向及传播策略是什么？'),('perception','品牌正在建立什么消费者认知？'),('learn','哪些内容形式值得模仿？')],
 10: [('timeline','关键发展历程')],
 11: [('actions','哪些动作推动了品牌快速增长？'),('change','品牌从早期到现在，增长方式发生了什么变化？')],
 12: [('perception','目前消费者对这个品牌最核心的认知是什么？'),('value','相比其他品牌，它提供了什么独特价值？'),('pay','消费者为什么愿意购买它，甚至支付更高的价格？'),('mind','这种选择理由是否已经形成品牌心智？')],
 13: [('factor','品牌成功最关键的因素是什么？'),('capability','背后依靠什么能力？'),('barrier','哪些优势是竞争对手难以复制的？'),('sustain','这些能力能否支撑品牌持续增长？')],
 14: [('innovation','值得学习的产品创新')],
 15: [('marketing','值得模仿的营销及渠道动作')],
 16: [('weakness','品牌目前的主要短板')],
 17: [('opportunity','潜在市场机会')],
 18: [('implication','对我们的战略启示')]
}
SIXTH = ['产品创新','营销与渠道借鉴','竞争短板','潜在市场机会','对我方的战略启示']

def topic_number(topic):
    return SIXTH.index(topic) + 14 if topic in SIXTH else int(topic.split('.')[0])

def question_id(bid, pid, number, key):
    return f'{bid}-{pid or "brand"}-{number}-{key}'

def empty_questions(bid, pid, topic):
    n = topic_number(topic)
    return [{'id':question_id(bid,pid,n,key), 'framework_key':key,
             'title':title, 'answer':'尚未取得足够资料，暂不能回答。',
             'record_ids':[], 'answer_status':'资料不足', 'presentation':'pending'}
            for key,title in QUESTIONS[n]]

def validate_document(doc, product_ids=None):
    """Validate semantic slots, ordering, and reference ownership before publication."""
    if doc.get('framework_version') != VERSION:
        raise ValueError('报告未按本轮已确认框架校验')
    if [s['number'] for s in doc['sections']] != list(range(1,7)):
        raise ValueError('请保留六大板块顺序')
    chapter_topics = {1:[1,2,3],3:[7,8,9],4:[10,11],5:[12,13],6:[14,15,16,17,18]}
    product_topics = doc['sections'][1]['topics']
    found_products = list(dict.fromkeys(t.get('product_id') for t in product_topics))
    if None in found_products or (product_ids is not None and set(found_products) != set(product_ids)):
        raise ValueError('请为本品牌每个产品保留独立研究')
    expected_product_topics = [(pid,n) for pid in found_products for n in [4,5,6]]
    if [(t.get('product_id'),topic_number(t['topic'])) for t in product_topics] != expected_product_topics:
        raise ValueError('每个产品须按顺序完整保留第4—6项')
    seen = set()
    for s in doc['sections']:
        if s['number'] != 2 and [topic_number(t['topic']) for t in s['topics']] != chapter_topics[s['number']]:
            raise ValueError('请保留本板块全部研究项及原定顺序')
        for t in s['topics']:
            if t.get('scope_product_id') and t['scope_product_id'] not in found_products:
                raise ValueError('研究内容对应的产品不属于本品牌')
            n = topic_number(t['topic']); expected = QUESTIONS[n]
            qs = [q for q in t.get('questions',[]) if q.get('framework_key')]
            if [(q['framework_key'],q['title']) for q in qs] != expected:
                raise ValueError(f'{t["topic"]}：问题缺失、顺序或标题与已确认框架不符')
            for q in t['questions']:
                if not q.get('framework_key') and not (q.get('type') == 'feedback-summary' and q.get('presentation') == 'plain'):
                    raise ValueError('补充内容不能代替或新增未确认的研究问题')
                if q['id'] in seen:
                    raise ValueError('问题标识重复')
                seen.add(q['id'])
                if not set(q.get('record_ids',[])).issubset(set(t['record_ids'])):
                    raise ValueError('问题来源未纳入所属研究项')
                if q.get('answer_status') == '已回答' and not q.get('record_ids'):
                    raise ValueError('已回答的问题缺少来源')
                if not (q.get('answer') or q.get('points') or q.get('tables') or q.get('type')):
                    raise ValueError('每个问题须有回答或明确的资料缺口')
    return True
