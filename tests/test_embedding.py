from lazyforge.embedding import BM25, TfidfVectorizer, cosine, dot, tokenize


def test_tokenize_cjk_and_ascii():
    toks = tokenize("发送 send email 邮件")
    assert "send" in toks
    assert "发" in toks or "发送" in toks


def test_tfidf_rank_self_higher():
    docs = ["发送邮件给客户", "查询天气", "翻译文本", "计算器"]
    vec = TfidfVectorizer().fit_transform(docs)
    q = vec[0]
    scores = [cosine(q, d) for d in vec]
    assert scores.index(max(scores)) == 0


def test_cosine_identical_is_one():
    a = {"x": 1.0, "y": 2.0}
    assert abs(cosine(a, a) - 1.0) < 1e-9


def test_dot_commutative():
    a = {"x": 2.0, "y": 1.0}
    b = {"x": 1.0, "z": 3.0}
    assert dot(a, b) == dot(b, a)


def test_bm25_hit_scores_higher():
    docs = ["发送邮件", "天气查询", "翻译", "计算", "发送消息"]
    bm = BM25().index(docs)
    scores = bm.scores("发送")
    assert scores[0] > scores[1]
    assert scores[4] > scores[1]
