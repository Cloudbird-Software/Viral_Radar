"""app —— 应用编排层（任务调度 / 配置 / 入口）。

组装 adapters → processing → analysis 的流水线，持有异步任务队列、LLM 网关
路由配置与对外接口。可 import 全部下层。
"""
