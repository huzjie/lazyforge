from lazyforge.config import Config
from lazyforge.eval import benchmark, build_default_dataset
from lazyforge.eval.metrics import monotone_skill, mrr, recall_at_k
from lazyforge.gateway.gateway import LazyGateway
from lazyforge.registry import build_large_demo_tools


def test_metrics_monotone():
    # 越靠前 skill 越高
    a = monotone_skill(["x", "y"], ["x"], k=5)
    b = monotone_skill(["y", "x"], ["x"], k=5)
    assert a >= b


def test_mrr_and_recall():
    assert mrr(["x", "y"], ["x"]) == 1.0
    assert mrr(["y", "x"], ["x"]) == 0.5
    assert recall_at_k(["x", "y"], ["x", "z"], k=5) == 0.5


def test_benchmark_full():
    gw = LazyGateway.from_tools(build_large_demo_tools(), Config())
    report = benchmark(gw, build_default_dataset())
    assert len(report.per_task) == len(build_default_dataset())
    assert report.avg_skill > 0.9
    assert report.avg_retrieval_savings > 0.8
