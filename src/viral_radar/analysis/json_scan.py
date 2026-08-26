"""json_scan.py —— LLM 自由文本中括号配平 JSON 片段扫描（analysis 内部共用件）。

秒级拆解（decompose.py，JSON 数组）与脚本草稿仿写（draft.py，JSON 对象）各自
复制了同一段「第一个括号配平片段」扫描器——本模块收敛为单一实现。
规则：字符串字面量内的引号/括号不参与配平计数；返回自首个 opener 起、
配平闭合处的原文切片。opener 缺失/未闭合由调用方传入各自文案抛
ValueError（保持逐调用点的既有错误语义不变）。
"""


def scan_balanced_json(
    text: str,
    *,
    opener: str,
    opens: str,
    closes: str,
    absent_message: str,
    unclosed_message: str,
) -> str:
    """取 text 中首个以 ``opener`` 起头、括号配平的完整片段原文。

    opens/closes 为参与深度计数的括号集合（拆解面为 ``[{``/``]}``，仿写面仅
    计花括号）。缺 opener 抛 absent_message；扫到文末仍未闭合抛 unclosed_message。
    """
    start = text.find(opener)
    if start == -1:
        raise ValueError(absent_message)
    depth = 0
    in_string = False
    end = -1
    for idx in range(start, len(text)):
        ch = text[idx]
        if in_string:
            if ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in opens:
            depth += 1
        elif ch in closes:
            depth -= 1
            if depth == 0:
                end = idx
                break
    if end == -1:
        raise ValueError(unclosed_message)
    return text[start : end + 1]
