"""check_arch.py —— 四层架构导入边界执法（make arch 目标）。

规则（docs/ARCHITECTURE.md）：adapters < processing < analysis < app，
模块只许 import 同层或下层（上层可依赖下层，下层不得反向依赖上层）。
判定只认 `import viral_radar.<层>.…` / `from viral_radar.<层>…` 形态的包内导入；
标准库与第三方导入不判。退出码：0=通过，1=违规（逐条输出文件:行号）。

本文件位于 tools/（不在 quality 关卡扫描面内），只依赖标准库。
"""

import ast
import os
import sys

LAYERS = ["adapters", "processing", "analysis", "app"]
PACKAGE = "viral_radar"


def layer_of(module_path):
    # src/viral_radar/adapters/douyin.py -> viral_radar.adapters.douyin
    rel = module_path.replace(os.sep, "/")
    if rel.endswith("__init__.py"):
        rel = rel[: -len("__init__.py")].rstrip("/")
    else:
        rel = rel[: -len(".py")]
    parts = rel.split("/")
    try:
        idx = parts.index(PACKAGE)
    except ValueError:
        return None, None
    sub = parts[idx + 1 :]
    if not sub:
        return PACKAGE, -1
    head = sub[0]
    if head in LAYERS:
        return head, LAYERS.index(head)
    return None, None


def package_imports(code):
    hits = []
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == PACKAGE or alias.name.startswith(PACKAGE + "."):
                    hits.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module and (node.module == PACKAGE or node.module.startswith(PACKAGE + ".")):
                hits.append((node.lineno, node.module))
    return hits


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root, "src")
    violations = []
    for dirpath, _dirs, files in os.walk(src):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root)
            own_layer, own_idx = layer_of(rel)
            if own_layer is None:
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    code = f.read()
            except OSError as e:
                print(f"读取失败：{rel} ({e})", file=sys.stderr)
                return 2
            for lineno, target in package_imports(code):
                tgt_layer, tgt_idx = layer_of(target.replace(".", "/") + "/x.py")
                if tgt_layer is None:
                    continue
                if own_idx < tgt_idx:
                    violations.append(
                        f"{rel}:{lineno} 层间导入违规：{own_layer} -> {tgt_layer}"
                        "（下层不得依赖上层）"
                    )
    if violations:
        print(f"arch 违规 {len(violations)} 条：")
        for v in violations:
            print("  - " + v)
        return 1
    print("arch 通过：四层导入方向符合 adapters < processing < analysis < app")
    return 0


if __name__ == "__main__":
    sys.exit(main())
