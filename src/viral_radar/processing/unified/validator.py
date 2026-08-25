"""validator.py —— 统一数据模型 v1 装载与校验（spec AC-7 / IFACE-1）。

schema 唯一真源 = unified/v1/schema.json（版本化资产，仓库内可溯源）；本校验器
是标准库实现的 JSON Schema 最小语法子集执行器（object/properties/required/type/
enum/array/items）——组织依赖规则：可用标准库完成判定不为通用引擎引第三方依赖。
fail-closed：schema 中出现不支持的校验关键字时直接报错，绝不静默跳过。
"""

import json
from pathlib import Path

_SCHEMA_KEYWORDS = {
    "type",
    "properties",
    "required",
    "items",
    "enum",
    # 注解关键字（不参与判定，仅为可读性/资产元数据）
    "title",
    "description",
    "schema_version",
}


class UnifiedValidator:
    """统一数据模型校验入口（公共面只有一个方法 validate）。

    validate(doc) -> 错误信息列表；空列表 = 通过。错误信息形如
    ``$..timeline_data[0].source_type: 取值 'BAD' 不在允许枚举内``。
    """

    def __init__(self, schema: dict | None = None) -> None:
        if schema is None:
            raw = (Path(__file__).parent / "v1" / "schema.json").read_text(encoding="utf-8")
            schema = json.loads(raw)
        self._schema = schema

    def validate(self, doc: dict) -> list[str]:
        return self._walk(doc, self._schema, "$")

    def _walk(self, node, schema: dict, path: str) -> list[str]:
        unknown = sorted(set(schema) - _SCHEMA_KEYWORDS)
        if unknown:
            return [f"{path}: schema 含不支持的关键字 {unknown}（fail-closed）"]
        if "type" in schema and not self._type_ok(node, schema["type"]):
            return [f"{path}: 期望 type={schema['type']}，实为 {type(node).__name__}"]
        if "enum" in schema and node not in schema["enum"]:
            return [f"{path}: 取值 {node!r} 不在允许枚举内 {schema['enum']}"]
        if isinstance(node, dict) and "properties" in schema:
            errors: list[str] = []
            for key in schema.get("required", []):
                if key not in node:
                    errors.append(f"{path}: 缺必填字段 {key}")
            for key, subschema in schema["properties"].items():
                if key in node:
                    errors += self._walk(node[key], subschema, f"{path}.{key}")
            return errors
        if isinstance(node, list) and "items" in schema:
            errors = []
            for i, item in enumerate(node):
                errors += self._walk(item, schema["items"], f"{path}[{i}]")
            return errors
        return []

    @staticmethod
    def _type_ok(node, expected: str) -> bool:
        if expected == "string":
            return isinstance(node, str)
        if expected == "number":
            return isinstance(node, (int, float)) and not isinstance(node, bool)
        if expected == "array":
            return isinstance(node, list)
        if expected == "object":
            return isinstance(node, dict)
        return False
