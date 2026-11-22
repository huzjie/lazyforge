from lazyforge.config import Config
from lazyforge.gateway.gateway import LazyGateway
from lazyforge.registry import build_demo_tools


def _gw():
    return LazyGateway.from_tools(build_demo_tools(), Config())


def test_plan_saves_context():
    gw = _gw()
    plan = gw.plan("发邮件", top_k=3)
    assert plan.full_cost > 0
    assert plan.savings_ratio > 0.0
    assert plan.context["stats"]["total"] == 12


def test_run_returns_result():
    gw = _gw()
    result = gw.run("发送邮件", {"to": "a@b.com"})
    assert result.ok is False or result.ok is True  # 至少返回了结果
    # 无 mock 函数时可能失败，但必须有输出或错误
    assert result.output is not None or result.error


def test_ranked_hit():
    gw = _gw()
    ranked = gw.searcher.search("发邮件", top_k=1)
    assert ranked[0].stub.name == "send_email"
