FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 依赖极简：核心零依赖，仅可选 pyyaml
COPY requirements.txt .
RUN pip install -r requirements.txt || true

COPY src ./src
COPY README.md pyproject.toml ./

RUN pip install --no-deps .

# 内置一个示例工具库用于 doctor 冒烟
COPY examples ./examples

ENTRYPOINT ["python", "-m", "lazyforge"]
CMD ["doctor"]
