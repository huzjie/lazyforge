from lazyforge.registry import ToolRegistry, build_demo_tools, build_tool_from_dict
from lazyforge.registry.schema import estimate_tokens, validate_parameters


def test_register_and_lookup():
    reg = ToolRegistry()
    tool = build_tool_from_dict({
        "name": "add", "summary": "两数相加",
        "parameters": {"type": "object", "properties": {"a": {"type": "integer"}},
                       "required": ["a"]},
    })
    reg.register(tool)
    assert len(reg) == 1
    stub = reg.get_stub("add")
    assert stub.name == "add"
    loaded = reg.load(stub)
    assert loaded is not None and loaded.name == "add"


def test_demo_tools_count():
    assert len(build_demo_tools()) == 12


def test_estimate_tokens():
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello world") >= 2
    assert estimate_tokens("你好世界") == 4


def test_validate_parameters():
    schema = {"type": "object",
              "properties": {"a": {"type": "integer"}},
              "required": ["a"]}
    assert validate_parameters(schema, {}) == ["缺少必填参数: a"]
    assert validate_parameters(schema, {"a": "x"}) == ["参数 a 类型错误: 期望 integer"]
    assert validate_parameters(schema, {"a": 1}) == []
