from lazyforge.registry import build_demo_tools
from lazyforge.retrieval import Searcher, ToolIndex


def _searcher(backend="hybrid"):
    index = ToolIndex.from_stubs([t.stub for t in build_demo_tools()])
    return Searcher(index, backend=backend)


def test_search_top1_email():
    searcher = _searcher()
    ranked = searcher.search("给客户发一封邮件", top_k=1)
    assert ranked[0].stub.name == "send_email"


def test_search_top1_weather():
    searcher = _searcher()
    ranked = searcher.search("查询北京天气", top_k=1)
    assert ranked[0].stub.name == "get_weather"


def test_backends_all_run():
    for backend in ("sparse", "dense", "hybrid"):
        ranked = _searcher(backend).search("翻译英文", top_k=3)
        assert ranked, backend


def test_search_ids():
    ids = _searcher().search_ids("计算 1+1", top_k=3)
    assert "calculator" in ids
