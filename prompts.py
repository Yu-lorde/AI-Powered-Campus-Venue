"""Prompt 模板与边界判断（P3）"""

from __future__ import annotations

import re

from sport_terms import (
    chunk_matches_sports,
    extract_sports_from_query,
    sport_match_score,
)

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
        "keywords": ["运动", "打球", "踢球", "跑步", "健身", "游泳", "体育"],
        "target_docs": ["体育馆", "操场", "球场", "游泳馆", "健身房", "田径", "气膜"],
        "exclude_docs": ["自习", "食堂", "餐厅", "餐吧"],
    },
    "会议/活动": {
        "keywords": ["开会", "会议", "活动", "讲座", "排练", "社团", "聚会", "团建"],
        "target_docs": ["会议室", "报告厅", "多功能", "活动中心", "路演"],
        "exclude_docs": [],
    },
}


# 主任务句式：识别「供我自习」「用来打球」等目的表达
_PURPOSE_PATTERNS = [
    re.compile(r"供(?:我|咱们|大家)?(.{0,12})?(自习|学习|看书|复习|备考|刷题)"),
    re.compile(r"(?:用于|用来|去做)(.{0,12})?(自习|学习|打球|吃饭|就餐|开会|会议|游泳|健身)"),
    re.compile(
        r"(?:想|要)(?:去|在)?(.{0,15})?(自习|学习|打球|踢球|踢足球|打篮球|打排球|打羽毛球|打乒乓球|打网球|跑步|健身|游泳|吃饭|就餐|早餐|午餐|晚餐|开会|会议)"
    ),
]

# 约束句式：识别「离食堂近」「方便吃饭」等地标/条件
_CONSTRAINT_PATTERNS = [
    re.compile(r"(?:离|靠近|邻近|临近|在旁边|近)(.{0,8}?)(食堂|餐厅|教学楼|图书馆|宿舍|体育馆|餐吧)"),
    re.compile(r"方便(.{0,6}?)(吃饭|就餐|用餐)"),
]

# 动作词 → 意图类别
_ACTION_TO_INTENT: dict[str, str] = {
    "自习": "自习",
    "学习": "自习",
    "看书": "自习",
    "复习": "自习",
    "备考": "自习",
    "刷题": "自习",
    "吃饭": "餐饮",
    "就餐": "餐饮",
    "早餐": "餐饮",
    "午餐": "餐饮",
    "晚餐": "餐饮",
    "打球": "运动",
    "踢球": "运动",
    "踢足球": "运动",
    "打篮球": "运动",
    "打排球": "运动",
    "打羽毛球": "运动",
    "打乒乓球": "运动",
    "打网球": "运动",
    "跑步": "运动",
    "健身": "运动",
    "游泳": "运动",
    "开会": "会议/活动",
    "会议": "会议/活动",
}


def _score_intents(query: str) -> list[tuple[int, str]]:
    q = query.lower()
    scored: list[tuple[int, str]] = []
    for category, cfg in INTENT_CATEGORIES.items():
        score = sum(1 for kw in cfg["keywords"] if kw in q)
        if score > 0:
            scored.append((score, category))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored


def _intent_from_action(action: str) -> str | None:
    return _ACTION_TO_INTENT.get(action)


def parse_query_roles(query: str) -> dict:
    """
    方案 C：分解为主任务 + 约束条件。
    返回 main_intent、constraint_labels、constraint_keywords。
    """
    q = query.strip()
    scored = _score_intents(q)
    hit_labels = [cat for _, cat in scored]

    main_intent: str | None = None
    for pat in _PURPOSE_PATTERNS:
        m = pat.search(q)
        if m:
            main_intent = _intent_from_action(m.group(2))
            if main_intent:
                break

    if not main_intent and hit_labels:
        main_intent = hit_labels[0]
    if not main_intent:
        main_intent = "通用"

    constraint_labels = [label for label in hit_labels if label != main_intent]

    constraint_keywords: list[str] = []
    for pat in _CONSTRAINT_PATTERNS:
        for m in pat.finditer(q):
            constraint_keywords.append(m.group(2))
    for label in constraint_labels:
        for kw in INTENT_CATEGORIES[label]["keywords"]:
            if kw in q and kw not in constraint_keywords:
                constraint_keywords.append(kw)
        for kw in INTENT_CATEGORIES[label]["target_docs"]:
            if kw not in constraint_keywords:
                constraint_keywords.append(kw)
    # 知识库字段常见写法
    if any(k in q for k in ("食堂", "吃饭", "就餐", "用餐")):
        for extra in ("距食堂", "大食堂"):
            if extra not in constraint_keywords:
                constraint_keywords.append(extra)

    return {
        "main_intent": main_intent,
        "constraint_labels": constraint_labels,
        "constraint_keywords": constraint_keywords,
        "sport_focus": extract_sports_from_query(q),
    }


def format_query_roles_label(roles: dict) -> str:
    main = roles["main_intent"]
    if main == "通用":
        return "通用"
    constraints = roles["constraint_labels"]
    if not constraints:
        return f"主任务：{main}"
    return f"主任务：{main}；约束：{'、'.join(constraints)}"


def classify_intent(query: str) -> tuple[str, list[str], list[str]]:
    """兼容旧接口：按主任务返回 target / exclude（约束词会从 exclude 中剔除）。"""
    roles = parse_query_roles(query)
    main = roles["main_intent"]
    if main == "通用":
        return "通用", [], []

    cat = INTENT_CATEGORIES[main]
    excludes = _effective_excludes(roles)
    label = format_query_roles_label(roles)
    return label, cat["target_docs"], excludes


def _chunk_doc_fields(chunk: dict) -> tuple[str, str, str]:
    title = (chunk.get("title", "") or chunk.get("name", "")).lower()
    source = (chunk.get("source", "") or "").lower()
    text = (chunk.get("text", "") or chunk.get("content", "")).lower()
    return title, source, text


def _chunk_matches_keywords(chunk: dict, keywords: list[str]) -> bool:
    if not keywords:
        return False
    title, source, text = _chunk_doc_fields(chunk)
    haystack = f"{title} {source}"
    return any(kw in haystack or kw in text for kw in keywords)


def _effective_excludes(roles: dict) -> list[str]:
    """主任务 exclude 中，与约束条件冲突的项不再排除。"""
    main = roles["main_intent"]
    if main == "通用":
        return []
    excludes = list(INTENT_CATEGORIES[main].get("exclude_docs", []))
    if not roles["constraint_labels"]:
        return excludes

    constraint_tokens = set(roles["constraint_keywords"])
    for label in roles["constraint_labels"]:
        constraint_tokens.update(INTENT_CATEGORIES[label]["keywords"])
        constraint_tokens.update(INTENT_CATEGORIES[label]["target_docs"])

    return [
        ex
        for ex in excludes
        if not any(ex in tok or tok in ex for tok in constraint_tokens)
    ]


# query 重加权时只剥离泛化词，保留「羽毛球」「食堂」等具体检索词
_REWEIGHT_STRIP: dict[str, list[str]] = {
    "自习": ["学习", "看书", "复习", "备考", "刷题", "安静"],
    "餐饮": ["吃", "吃饭", "就餐", "用餐", "外卖", "美食", "餐饮", "饭堂"],
    "运动": ["运动", "体育", "打球", "跑步", "健身"],
    "会议/活动": ["活动", "聚会", "团建", "讲座", "排练", "社团"],
}


def _chunk_matches_main_task(chunk: dict, roles: dict, query: str) -> bool:
    """主任务匹配：运动类优先按具体项目词；其余按 target_docs。"""
    main = roles["main_intent"]
    if main == "通用":
        return True

    sports = roles.get("sport_focus") or extract_sports_from_query(query)
    if main == "运动" and sports:
        return chunk_matches_sports(chunk, sports)

    cat = INTENT_CATEGORIES[main]
    if _chunk_matches_keywords(chunk, cat["target_docs"]):
        return True
    for kw in cat["keywords"]:
        if len(kw) >= 2 and kw in query and _chunk_matches_keywords(chunk, [kw]):
            return True
    return False


def _sport_backup_chunks(roles: dict, query: str, excludes: list[str]) -> list[dict]:
    """从全库按具体运动项目补捞段落。"""
    sports = roles.get("sport_focus") or extract_sports_from_query(query)
    if not sports:
        return []
    try:
        from retriever import load_chunks

        index_pool = load_chunks()
    except ImportError:
        return []

    backup: list[dict] = []
    for c in index_pool:
        if excludes and _chunk_matches_keywords(c, excludes):
            continue
        if chunk_matches_sports(c, sports):
            backup.append(c)
    backup.sort(key=lambda c: sport_match_score(c, sports), reverse=True)
    max_n = getattr(config, "MAX_SECTIONS_IN_PROMPT", 12)
    return backup[:max_n]


def filter_chunks_by_intent(
    chunks: list[dict],
    intent_label: str,
    target_keywords: list[str],
    exclude_keywords: list[str],
) -> list[dict]:
    """单意图过滤（保留兼容）。"""
    if intent_label == "通用" or not chunks:
        return chunks

    filtered: list[dict] = []
    for c in chunks:
        if exclude_keywords and _chunk_matches_keywords(c, exclude_keywords):
            continue
        if target_keywords and not _chunk_matches_keywords(c, target_keywords):
            continue
        filtered.append(c)
    return filtered


def _constraint_match_score(chunk: dict, constraint_keywords: list[str]) -> int:
    if not constraint_keywords:
        return 0
    title, source, text = _chunk_doc_fields(chunk)
    haystack = f"{title} {source} {text}"
    return sum(1 for kw in constraint_keywords if kw in haystack)


def filter_chunks_by_roles(chunks: list[dict], roles: dict, query: str = "") -> list[dict]:
    """
    方案 C：按主任务筛 target，约束条件下放宽 exclude，并按约束词重排。
    另附少量约束地标文档（如食堂概况）供选址参考。
    """
    main = roles["main_intent"]
    if main == "通用":
        return chunks

    excludes = _effective_excludes(roles)
    pool = list(chunks)
    if not pool and query:
        try:
            from retriever import load_chunks

            pool = load_chunks()
        except ImportError:
            pool = []

    filtered: list[dict] = []
    for c in pool:
        if excludes and _chunk_matches_keywords(c, excludes):
            continue
        if not _chunk_matches_main_task(c, roles, query):
            continue
        filtered.append(c)

    sports = roles.get("sport_focus") or extract_sports_from_query(query)
    sport_matched = sports and any(chunk_matches_sports(c, sports) for c in filtered)
    if sports and not sport_matched:
        filtered = _sport_backup_chunks(roles, query, excludes)
    elif not filtered and query and main == "运动":
        filtered = _sport_backup_chunks(roles, query, excludes)
    elif not filtered and query:
        try:
            from retriever import load_chunks

            index_pool = load_chunks()
        except ImportError:
            index_pool = []
        backup: list[dict] = []
        for c in index_pool:
            if excludes and _chunk_matches_keywords(c, excludes):
                continue
            if _chunk_matches_main_task(c, roles, query):
                backup.append(c)
        max_n = getattr(config, "MAX_SECTIONS_IN_PROMPT", 12)
        filtered = backup[:max_n]

    if sports:
        filtered.sort(key=lambda c: sport_match_score(c, sports), reverse=True)
    elif roles["constraint_keywords"]:
        filtered.sort(
            key=lambda c: _constraint_match_score(c, roles["constraint_keywords"]),
            reverse=True,
        )

    if roles["constraint_labels"]:
        seen = {c.get("id") for c in filtered}
        landmark_targets: list[str] = []
        for label in roles["constraint_labels"]:
            landmark_targets.extend(INTENT_CATEGORIES[label]["target_docs"])
        landmarks: list[dict] = []
        for c in chunks:
            cid = c.get("id")
            if cid in seen:
                continue
            if _chunk_matches_keywords(c, landmark_targets):
                landmarks.append(c)
                seen.add(cid)
            if len(landmarks) >= 2:
                break
        filtered = filtered + landmarks

    return filtered


def reweight_query(query: str, roles: dict) -> str:
    """有约束时保留完整 query；单主任务时仅弱化泛化词，保留羽毛球/食堂等具体词。"""
    main = roles["main_intent"]
    if main == "通用":
        return query
    if roles["constraint_labels"]:
        return query

    cleaned = query
    for kw in _REWEIGHT_STRIP.get(main, []):
        cleaned = cleaned.replace(kw, "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or query


def build_enhanced_retrieval_query(current: str, raw_history: list[tuple[str, str]]) -> str:
    """两阶段增强（方案 C）：主任务/约束分解 + query 重加权。"""
    current = current.strip()
    roles = parse_query_roles(current)
    weighted = reweight_query(current, roles)
    if not raw_history:
        return weighted
    last_user, _ = raw_history[-1]
    return f"上一轮用户问题：{last_user}\n本轮追问：{weighted}"


def build_enhanced_rag_user_message(query: str, chunks: list[dict]) -> str:
    """两阶段增强（方案 C）：主任务过滤 + 约束重排；无命中时不塞入无关段落。"""
    roles = parse_query_roles(query)
    filtered = filter_chunks_by_roles(chunks, roles, query)
    msg = build_rag_user_message(query, filtered)
    label = format_query_roles_label(roles)
    if label != "通用":
        msg = f"【意图分类】{label}\n\n{msg}"
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