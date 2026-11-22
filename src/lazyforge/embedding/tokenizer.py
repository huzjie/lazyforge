"""tokenize —— 零依赖分词：CJK 按字、ASCII 按词/ngram，供 TF-IDF 与 BM25 用。

不需要结巴/HF tokenizer 也能对中文工具描述做可用的语义检索：中文按字符
切分 + 二元组，英文按空格切词 + 小写化，混合文本都能落在同一稀疏空间里。
"""
from __future__ import annotations

import re

_WORD_RE = re.compile(r"[a-zA-Z0-9_]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")

# 中文停用字：虚词 + 量词 + 代词。去掉「一张/两个/一段/的」这类无信息量 token，
# 避免跨工具误匹配（例如「生成一张发票」与「生成一张流程图」因「一张」撞车）。
_CJK_STOP = set(
    "的了是在我你他她它这那有和与及或就都也把被将给让向从对于到用一二两三"
    "四五六七八九十百千个些之而等但并且还要能会可以为着过得地啊呢吧吗"
    "种份条封篇张门款笔次件台部套组只项名位"
)

# 英文停用词（小写）
_EN_STOP = {
    "a", "an", "the", "to", "of", "in", "on", "for", "with", "is", "are",
    "be", "do", "does", "at", "by", "from", "as", "and", "or", "not",
    "this", "that", "it", "its", "into", "via", "per",
}


def _cjk_bigrams(text: str) -> list[str]:
    chars = [c for c in _CJK_RE.findall(text) if c not in _CJK_STOP]
    if len(chars) == 1:
        return chars
    return chars + ["".join(chars[i:i + 2]) for i in range(len(chars) - 1)]


def tokenize(text: str, ngram_range: tuple[int, int] = (1, 2)) -> list[str]:
    """把一段文本切成 token 列表（中文去停用字后逐字 + 二元组，英文按词）。"""
    if not text:
        return []
    tokens: list[str] = []
    # 英文 / 数字 / 下划线词（过滤停用词）
    for w in _WORD_RE.findall(text):
        wl = w.lower()
        if wl not in _EN_STOP:
            tokens.append(wl)
    # 中文去停用字后：单字 + 二元组
    tokens.extend(_cjk_bigrams(text))
    if ngram_range[1] >= 2:
        # 英文二元组（跨相邻词）
        words = [w.lower() for w in _WORD_RE.findall(text) if w.lower() not in _EN_STOP]
        tokens.extend("_".join(words[i:i + 2]) for i in range(len(words) - 1))
    return [t for t in tokens if t]
