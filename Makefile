# Viral_Radar —— 统一命令入口（CI 只认本文件；Python 面 + TS 治理脚手架面双轨）
PY        ?= python3
VENV_PY   ?= .venv/bin/python

.PHONY: setup fmt lint arch test build check card-test gates-pr gates-fast
setup: ; npm ci && $(PY) -m venv .venv && $(VENV_PY) -m pip install --quiet --disable-pip-version-check "uv==0.12.5" && $(VENV_PY) -m uv sync
fmt: ; $(VENV_PY) -m ruff format src tests tools && npx prettier --write .
lint: ; $(VENV_PY) -m ruff check src tests tools && $(VENV_PY) -m ruff format --check src tests tools && npx prettier --check . && npx tsc --noEmit
arch: ; $(VENV_PY) tools/check_arch.py
test: ; $(VENV_PY) -m pytest tests/pytest -q
build: ; $(VENV_PY) -m compileall -q src

# ---------- quality 关卡（org 治理基线；quality/ 关卡逻辑不动，配置面在 quality/contract.yaml） ----------
# gates-fast：quality 关卡自测（零网络/零 LLM，bash+python 标准库）——关卡自身
# 变更必须带测试。check 串上它：lint 逻辑坏=整仓红，不留"检查器无人检查"的洞。
# （check 目标属人类专属治理面（AGENTS.md 硬规则 2），本次经卡 #6 授权仅改
#   lint/arch/test 的实现面内容——check 依赖链行保持不变，合并由人把关。）
gates-fast: ## 本地快跑：quality 自测 + 脚本语法 + 契约解析
	@bash quality/run-gates.sh fast

check:  lint arch test gates-fast

# ---------- 入口协议块第 4 步（认领/开工协议见 AGENTS.md entry-protocol v1） ----------
# card-test：拉卡 AC 列表提示测试先行 + 卡级测试集编排（TS 驱动 tests/card/** + pytest）
CARD ?=
REPO ?= Cloudbird-Software/Viral_Radar   # 卡所在仓

card-test: ## 读卡 AC 列表并提示测试先行：make card-test CARD=<issue#>
	@test -n "$(CARD)" || { echo "用法: make card-test CARD=<issue#>（缺 CARD）" >&2; exit 2; }
	@echo "== 卡 $(REPO)#$(CARD) 的 AC（测试先行：先按 AC 写红测试再实现）=="
	@gh issue view "$(CARD)" -R "$(REPO)" --json number,title,body \
	  --jq '"#\(.number) \(.title)\n\n\(.body)"' 2>/dev/null \
	  | awk 'NR==1{print;print ""} /^## AC/{f=1} f{print} f && /^## / && !/^## AC/{exit}' | head -60
	@echo "(空=拉取失败或卡无 AC 节——手动: gh issue view $(CARD) -R $(REPO))"
	@bash quality/run-gates.sh fast
	@npx vitest run "tests/card" || { echo "卡 #$(CARD) TS 驱动测试失败" >&2; exit 1; }
	@$(VENV_PY) -m pytest tests/pytest -q || { echo "卡 #$(CARD) pytest 测试失败" >&2; exit 1; }

# ---------- 测试产物拓扑二命令（同一编排器入口 quality/run-gates.sh） ----------
# 与 CI（ci.yml quality-gates job）同一编排器入口——同一脚本、同一 GATE_* env 注入协议。
gates-pr: ## 本地复现 CI 关卡等价物（quality 关卡 + node 检查面）
	@bash quality/run-gates.sh pr
	@echo "== 开 PR 前检查单（机器不可判部分）：PR body 引用 ADR-NNNN（C1）/ body 带 Card: 元数据行 / 一个 PR 一件事 diff<400 行 =="