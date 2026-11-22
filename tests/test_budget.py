from lazyforge.budget import BudgetPolicy, ContextEstimator, LoadDecision
from lazyforge.budget.policy import Decision
from lazyforge.registry import build_demo_tools


def _policy(context_limit=2000):
    est = ContextEstimator()
    return BudgetPolicy(context_limit=context_limit, estimator=est)


def test_estimator_full_vs_lazy():
    tools = build_demo_tools()
    stubs = [t.stub for t in tools]
    est = ContextEstimator()
    full = est.full_library_cost(stubs, {t.id: t for t in tools})
    lazy = est.lazy_cost(stubs, stubs[:2], {t.id: t for t in tools})
    assert lazy < full


def test_policy_loads_top_k():
    tools = build_demo_tools()
    stubs = [t.stub for t in tools]
    policy = _policy(context_limit=100000)
    decisions = policy.decide(stubs[:5], stubs, {t.id: t for t in tools})
    assert all(d.decision == Decision.LOAD for d in decisions)


def test_policy_defers_when_over_budget():
    tools = build_demo_tools()
    stubs = [t.stub for t in tools]
    policy = _policy(context_limit=50)  # 极小预算，几乎装不下任何 schema
    decisions = policy.decide(stubs[:5], stubs, {t.id: t for t in tools})
    assert any(d.decision == Decision.DEFER for d in decisions)
