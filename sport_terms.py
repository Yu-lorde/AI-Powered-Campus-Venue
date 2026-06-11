"""体育运动词表：查询归一化、场馆匹配（prompts / retriever 共用）。"""

from __future__ import annotations

# 规范运动名 → 查询别名 + 知识库匹配词（文件名/正文）
SPORT_ENTITIES: dict[str, dict[str, list[str]]] = {
    "足球": {
        "aliases": ["足球", "踢球", "踢足球", "踢踢球", "五人制足球", "十一人制"],
        "match": ["足球", "足球场", "五人制"],
    },
    "篮球": {
        "aliases": ["篮球", "打篮球", "打篮", "室内篮球"],
        "match": ["篮球", "篮球场"],
    },
    "排球": {
        "aliases": ["排球", "打排球", "气排球", "硬排"],
        "match": ["排球", "排球场", "气排"],
    },
    "羽毛球": {
        "aliases": ["羽毛球", "打羽毛球", "羽球"],
        "match": ["羽毛球", "羽毛球场"],
    },
    "乒乓球": {
        "aliases": ["乒乓球", "打乒乓球", "乒乓"],
        "match": ["乒乓球", "乒乓球桌", "乒乓"],
    },
    "网球": {
        "aliases": ["网球", "打网球"],
        "match": ["网球", "网球场"],
    },
    "游泳": {
        "aliases": ["游泳", "游游泳", "去游泳"],
        "match": ["游泳", "游泳馆"],
    },
    "健身": {
        "aliases": ["健身", "去健身", "撸铁", "力量训练"],
        "match": ["健身", "健身房"],
    },
    "跑步": {
        "aliases": ["跑步", "慢跑", "长跑", "夜跑"],
        "match": ["跑步", "田径", "田径场"],
    },
    "田径": {
        "aliases": ["田径", "散步", "慢走"],
        "match": ["田径", "田径场", "操场"],
    },
    "橄榄球": {
        "aliases": ["橄榄球", "美式橄榄球", "英式橄榄球"],
        "match": ["橄榄球"],
    },
    "棒球": {
        "aliases": ["棒球"],
        "match": ["棒球"],
    },
    "垒球": {
        "aliases": ["垒球"],
        "match": ["垒球"],
    },
    "高尔夫": {
        "aliases": ["高尔夫", "高尔夫球"],
        "match": ["高尔夫"],
    },
    "台球": {
        "aliases": ["台球", "桌球", "斯诺克"],
        "match": ["台球"],
    },
    "保龄球": {
        "aliases": ["保龄球"],
        "match": ["保龄球"],
    },
    "滑冰": {
        "aliases": ["滑冰", "溜冰", "冰上"],
        "match": ["滑冰", "冰场"],
    },
    "滑雪": {
        "aliases": ["滑雪"],
        "match": ["滑雪"],
    },
    "跆拳道": {
        "aliases": ["跆拳道"],
        "match": ["跆拳道"],
    },
    "武术": {
        "aliases": ["武术", "散打", "太极"],
        "match": ["武术"],
    },
    "瑜伽": {
        "aliases": ["瑜伽"],
        "match": ["瑜伽"],
    },
    "攀岩": {
        "aliases": ["攀岩", "抱石"],
        "match": ["攀岩"],
    },
    "骑行": {
        "aliases": ["骑行", "自行车", "单车"],
        "match": ["骑行", "自行车"],
    },
}

# 分词优先匹配的短语（长词在前）
SPORT_PHRASES: list[str] = sorted(
    {alias for cfg in SPORT_ENTITIES.values() for alias in cfg["aliases"]},
    key=len,
    reverse=True,
)

# 泛化动词：已有具体运动词时不再单独计分
SPORT_GENERIC_VERBS = frozenset({"打", "踢", "玩", "练", "去"})


def extract_sports_from_query(query: str) -> list[str]:
    """从用户 query 提取规范运动名列表（保持出现顺序）。"""
    q = query.strip()
    found: list[str] = []
    for phrase in SPORT_PHRASES:
        if phrase in q:
            for sport, cfg in SPORT_ENTITIES.items():
                if phrase in cfg["aliases"] and sport not in found:
                    found.append(sport)
                    break
    return found


def sport_terms_for_matching(sports: list[str]) -> list[str]:
    """展开为可用于 chunk 匹配的词表。"""
    terms: list[str] = []
    for sport in sports:
        cfg = SPORT_ENTITIES.get(sport, {})
        for t in cfg.get("match", [sport]):
            if t not in terms:
                terms.append(t)
    return terms


def chunk_matches_sports(chunk: dict, sports: list[str]) -> bool:
    if not sports:
        return False
    title = (chunk.get("title", "") or chunk.get("name", "")).lower()
    source = (chunk.get("source", "") or "").lower()
    text = (chunk.get("text", "") or chunk.get("content", "")).lower()
    haystack = f"{title} {source} {text}"
    return any(term in haystack for term in sport_terms_for_matching(sports))


def sport_match_score(chunk: dict, sports: list[str]) -> int:
    if not sports:
        return 0
    title = (chunk.get("title", "") or chunk.get("name", "")).lower()
    source = (chunk.get("source", "") or "").lower()
    text = (chunk.get("text", "") or chunk.get("content", "")).lower()
    score = 0
    for term in sport_terms_for_matching(sports):
        if term in source or term in title:
            score += 4
        elif term in text:
            score += 2
    return score


def build_sport_synonyms() -> dict[str, list[str]]:
    """供 retriever 关键词检索使用的同义词表。"""
    syn: dict[str, list[str]] = {}
    for sport, cfg in SPORT_ENTITIES.items():
        match_terms = list(cfg.get("match", [sport]))
        for alias in cfg.get("aliases", [sport]):
            syn[alias] = match_terms
        syn[sport] = match_terms
    return syn
