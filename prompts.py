"""Prompt 模板与边界判断（P3）"""

from __future__ import annotations

import re

try:
    import config
except ImportError:

    class config:  # type: ignore
        MAX_VENUES_IN_PROMPT = 3


SYSTEM_PROMPT = """你是「校园智能场馆匹配助手」，回答与本校各类校园空间相关的问题，包括但不限于：
- 体育场馆（羽毛球、篮球、游泳等）及预约方式
- 食堂、餐厅、餐吧等餐饮场所及供餐时间
- 自习室、图书馆阅览室等学习空间
- 会议室、报告厅等活动场地

【必须遵守】
1. 仅根据用户消息中「参考资料」部分作答；不得编造场馆名称、开放时间、电话、费用等未在参考资料中出现的信息。
2. 若标注为「知识库无相关条目」，须明确说明资料中未记载，可建议用户联系浙大后勤、体育部或场馆管理中心核实；不要假装检索到了内容。
3. 若用户问题与上述校园空间完全无关（如教务、成绩、选课、转专业、宿舍管理等），礼貌说明本助手只做校园空间匹配，并建议咨询相应部门。餐饮、自习、运动、活动场地类问题均属服务范围，不得拒答。
4. 多轮对话时，结合上文理解指代（如「第二个」「它」），仍须遵守第 1–3 条。
5. 语气简洁、有条理；推荐时说明理由（容量、位置、设备等）。
6. 【引用标注】回答中每个具体信息（如时间、地点、电话、价格）后面，必须用 [来源: 文件名:起始行-结束行] 标注。示例：休闲餐厅晚餐 16:30-19:00 [来源: 东区大食堂.md:13-24]。行号以参考资料中标注的为准，不得写 ?-?。
7. 【合并来源】如果连续多条信息来自同一文件的同一段落，只在段落末尾合并标注一次。"""

OUT_OF_SCOPE_REPLY = """您的问题似乎不属于「校园空间」范围，本助手无法根据知识库准确回答。

我主要负责：体育场馆、食堂餐饮、自习学习空间、会议活动场地等的推荐与开放信息。

教务、成绩、选课、转专业等问题请咨询教务处；如需校园空间帮助，请直接描述需求（如运动类型、用餐时段、自习环境等）。"""


NO_CONTEXT_USER_WRAPPER = """用户需求：{query}

【知识库检索结果】未找到与问题足够相关的参考资料（请勿编造任何场馆信息）。

请按系统要求：说明资料未记载，列出可向用户确认的关键信息（人数、室内/室外、时间段），并建议通过学校官方场馆预约渠道查询。"""


# 明显非场馆领域的关键词（可按本校情况增删）
_OUT_OF_SCOPE_PATTERNS = [
    r"转专业|绩点|gpa|学分|选课|退课|补考|挂科|期末考试安排",
    r"教务处|教务系统|成绩单|学位证|毕业要求",
    r"宿舍分配|换宿舍|学费|奖学金",
    r"数学题|编程作业|写代码|bug",
]


def is_out_of_scope(query: str) -> bool:
    """规则预判：明显非场馆话题时直接拒答，节省 API 并强化边界。"""
    q = query.strip().lower()
    if not q:
        return False
    for pat in _OUT_OF_SCOPE_PATTERNS:
        if re.search(pat, q, re.IGNORECASE):
            return True
    return False


def build_retrieval_query(current: str, raw_history: list[tuple[str, str]]) -> str:
    """多轮时把上一轮摘要拼进检索 query，便于理解「第二个」「那个馆」。"""
    current = current.strip()
    if not raw_history:
        return current
    last_user, _ = raw_history[-1]
    return (
        f"上一轮用户问题：{last_user}\n"
        f"本轮追问：{current}"
    )


# ========== 两阶段检索增强 ==========

INTENT_CATEGORIES: dict[str, dict] = {
    "自习": {
        "keywords": ["自习", "学习", "看书", "复习", "备考", "刷题", "安静"],
        "target_docs": ["自习", "图书馆", "教室", "阅览室"],
        "exclude_docs": ["食堂", "餐厅", "体育馆", "操场"],
    },
    "餐饮": {
        "keywords": ["吃", "吃饭", "食堂", "餐厅", "饭堂", "餐饮", "美食", "就餐", "用餐", "外卖", "晚餐", "午餐", "早餐"],
        "target_docs": ["食堂", "餐厅", "餐吧", "咖啡厅", "便利店"],
        "exclude_docs": ["自习", "体育馆", "操场", "球场", "游泳馆"],
    },
    "运动": {
        "keywords": ["运动", "打球", "跑步", "健身", "游泳", "篮球", "足球", "羽毛球", "乒乓球", "体育"],
        "target_docs": ["体育馆", "操场", "球场", "游泳馆", "健身房", "田径", "气膜"],
        "exclude_docs": ["自习", "食堂", "餐厅", "餐吧"],
    },
    "会议/活动": {
        "keywords": ["开会", "会议", "活动", "讲座", "排练", "社团", "聚会", "团建"],
        "target_docs": ["会议室", "报告厅", "多功能", "活动中心", "路演"],
        "exclude_docs": [],
    },
}


def classify_intent(query: str) -> tuple[str, list[str], list[str]]:
    """识别用户意图，返回 (意图标签, 目标文档关键词, 排除文档关键词)。"""
    q = query.lower()
    best_category = None
    best_score = 0
    for category, cfg in INTENT_CATEGORIES.items():
        score = sum(1 for kw in cfg["keywords"] if kw in q)
        if score > best_score:
            best_score = score
            best_category = category
    if best_category and best_score > 0:
        cat = INTENT_CATEGORIES[best_category]
        return best_category, cat["target_docs"], cat["exclude_docs"]
    return "通用", [], []


def _chunk_doc_fields(chunk: dict) -> tuple[str, str, str]:
    title = (chunk.get("title", "") or chunk.get("name", "")).lower()
    source = (chunk.get("source", "") or "").lower()
    text = (chunk.get("text", "") or chunk.get("content", "")).lower()
    return title, source, text


def filter_chunks_by_intent(
    chunks: list[dict],
    intent_label: str,
    target_keywords: list[str],
    exclude_keywords: list[str],
) -> list[dict]:
    """根据意图对检索结果进行第一轮过滤。"""
    if intent_label == "通用" or not chunks:
        return chunks

    filtered: list[dict] = []
    for c in chunks:
        title, source, text = _chunk_doc_fields(c)
        haystack = f"{title} {source}"

        if exclude_keywords and any(kw in haystack or kw in text for kw in exclude_keywords):
            continue
        if target_keywords and not any(kw in haystack or kw in text for kw in target_keywords):
            continue
        filtered.append(c)
    return filtered


def reweight_query(query: str, intent_label: str) -> str:
    """弱化 query 中的意图关键词，让向量检索更关注具体描述（人数、地点等）。"""
    if intent_label == "通用":
        return query

    cleaned = query
    for kw in INTENT_CATEGORIES[intent_label]["keywords"]:
        cleaned = cleaned.replace(kw, "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or query


def build_enhanced_retrieval_query(current: str, raw_history: list[tuple[str, str]]) -> str:
    """两阶段增强：意图识别 + query 重加权，再拼多轮上下文。"""
    current = current.strip()
    intent_label, _, _ = classify_intent(current)
    weighted = reweight_query(current, intent_label)
    if not raw_history:
        return weighted
    last_user, _ = raw_history[-1]
    return f"上一轮用户问题：{last_user}\n本轮追问：{weighted}"


def build_enhanced_rag_user_message(query: str, chunks: list[dict]) -> str:
    """两阶段增强：意图过滤 chunks 后再拼 Prompt；过滤为空时回退原始结果。"""
    intent_label, target_kws, exclude_kws = classify_intent(query)
    filtered = filter_chunks_by_intent(chunks, intent_label, target_kws, exclude_kws)
    if not filtered and chunks:
        filtered = chunks
    msg = build_rag_user_message(query, filtered)
    if intent_label != "通用":
        msg = f"【意图分类】{intent_label}\n\n{msg}"
    return msg


def build_rag_user_message(query: str, chunks: list[dict]) -> str:
    """将检索结果拼入本轮 user 消息（写入对话 history）。"""
    if not chunks:
        return NO_CONTEXT_USER_WRAPPER.format(query=query)

    max_sections = getattr(config, "MAX_SECTIONS_IN_PROMPT", 12)

    blocks = []
    for i, c in enumerate(chunks[:max_sections], 1):
        src = c.get("source", "未知文件")
        start = c.get("start_line", "?")
        end = c.get("end_line", "?")
        title = c.get("title", c.get("name", ""))
        if title.startswith("自习-"):
            title = title[len("自习-") :]
        score = c.get("score")
        extra = f"（相似度 {score}）" if score is not None else ""
        text = c.get("text", c.get("content", ""))
        blocks.append(
            f"### 参考资料 [{i}] {title} {extra}\n"
            f"（来源: {src}:{start}-{end}）\n{text}"
        )

    refs = "\n\n".join(blocks)
    return (
        f"用户需求: {query}\n\n【知识库参考资料】\n{refs}\n\n"
        f"请根据以上参考资料回答，并在每个具体信息后标注 [来源: 文件名:行号-行号]。"
    )