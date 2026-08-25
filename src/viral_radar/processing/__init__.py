"""processing —— 通用多模态处理层（ASR / OCR / 数据融合对齐）。

输入=adapters 产出的素材产物；输出=统一数据模型 JSON（spec IFACE-1）。
本层不得包含任何平台特判分支（spec INV-1），禁止 import analysis/app 层。
"""
