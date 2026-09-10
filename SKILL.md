---
name: save-memory
description: 保存记忆到本地记忆索引（AgentMemHub 内置引擎）并立即评分。当用户明确要求「记住/保存/记一下」，或任务产出重要结论/解决方案/踩坑解法，或发生重要配置变更时触发；写入成功后紧接着给该记忆打分。
---

# 保存记忆（save-memory）

把一条值得长期保留的事实/结论写入本地记忆索引（AgentMemHub 内置 rag 引擎），**写入成功后立即评分**，
让记忆在后续检索中排得上、立得住。

## 触发约束（最高优先）

**用户主动提醒加入记忆时，必须立即触发本 Skill**——包括但不限于「记一下」「记住这个」
「保存一下这个处理方式」「这个值得记」「以后遇到还按这个来」等任何明确或隐含的保存意图。
此类请求不经任务收尾自查、不打折、不延后：当轮就走完 探活 → `memory_save` → `memory_score`。
（任务产出可复用结论时的自动触发，见下方「生效前提」的 AGENTS.md 硬规则。）

## 生效前提（安装后必须配置，二者缺一不可）

本 Skill **不是放进 skills 目录就能自动运转**，它依赖两个前提：

### 前提 1：AGENTS.md 硬规则（触发保障）

Skill 的触发依赖模型自觉，实践证明长对话/高负载下会漏触发。安装本 Skill 后，
**必须**把下面这条硬规则添加进当前项目的 `AGENTS.md`，或当前 Agent Harness 的
全局指令文件（如 `~/.zcode/AGENTS.md`、`~/.config/opencode/AGENTS.md`、`~/.qwen/QWEN.md`）：

> **记忆保存纪律（硬性规则）**：任务收尾时自查：本次是否产出可复用结论
> （问题解决步骤 / 踩坑解法 / 架构决策 / 关键配置变更）？命中即必须走
> save-memory 流程（`memory_stats` 探活 → `memory_save` → 立即 `memory_score`），
> 只写 Agent 本地会话记忆不算完成。

没有这条规则，Skill 只是"能力"而非"义务"，会在最需要它的时候被遗忘。

### 前提 2：agentmemhub MCP 服务（强绑定，执行保障）

本 Skill 与 agentmemhub MCP 服务**强相关、强绑定**：写入、评分、检索全部经由
其 MCP 工具完成，Skill 自身不含任何存储实现，**也没有降级路径**——
MCP 未配置或不可见时，本 Skill 完全无法执行（此时应提醒用户配置，而不是改用
其它方式保存）。MCP 服务信息见下表。

## 绑定的 MCP 服务

本 Skill 不自带任何存储实现，所有读写经由 **agentmemhub MCP server** 完成：

| 项 | 值 |
|---|---|
| MCP server 名 | `agentmemhub` |
| 提供工具 | `memory_stats` · `memory_save` · `memory_score` · `memory_search` · `memory_recent` |
| 服务源码 / 安装 | https://github.com/MerlinShieh/AgentMemHub |
| stdio 启动 | `python -m agentmemhub mcp` |
| HTTP 常驻启动 | `python -m agentmemhub mcp --http --port 9100` |
| 底层引擎 | AgentMemHub 内置 `agentmemhub.rag`（进程内直调，无独立服务/端口/鉴权） |

引擎与 MCP 的启停归用户管理，本 Skill 只读写、不启停。

## 处理逻辑归属（本 Skill 为什么这么"薄"）

本 Skill 仓库刻意只做**行为协议**（何时保存、按什么顺序保存+评分），
不含任何评分/量化实现——找逻辑请到绑定的两个上游仓库去：

| 环节 | 实现位置 | 职责 |
|---|---|---|
| 何时保存/评分 | 本仓库 `SKILL.md` + AGENTS.md 硬规则 | 触发纪律（说明书，零代码） |
| 引擎预检 | 本仓库 `scripts/check_engine.py` | 唯一脚本：探活（读 AgentMemHub 配置判断后端与就绪态） |
| 写入/评分转发 | AgentMemHub 仓库 `agentmemhub/mcp_server.py`（`_save`/`_score`） | 把 MCP 工具调用翻译成引擎 API（feedback 极性分 + 已评清单 + r_task 同步） |
| LLM 批量评估 | AgentMemHub 仓库 `agentmemhub/scoring.py`（CLI `agentmemhub score`） | 三轴（目标达成/过程质量/用户价值）评估出极性，用于批量补评 |
| **量化计算** | **agentmemhub/rag/**（内置引擎，`memstore.put_feedback`） | 收到 feedback 后立即重算 value / r_human / priority（写入侧做确定性聚合，打分策略在 AgentMemHub 侧） |

解耦边界：**Skill 仓库=行为协议，AgentMemHub=适配层，agentmemhub.rag=计算引擎**。

## 调用前检查（必做，顺序执行）

1. **Harness 限制检查**：先读当前项目根的 `AGENTS.md` 与当前 Agent Harness 的
   用户级全局指令（如 `~/.zcode/AGENTS.md`、`~/.config/opencode/AGENTS.md`、
   `~/.qwen/QWEN.md`），确认其中**没有与本 Skill 冲突的约束**
   （例如「禁止自动写入外部服务」「只允许使用内置记忆」「本会话不落盘」等）。
   冲突时以 Harness 限制为准，跳过本流程并告知用户原因。
2. **MCP 可用性**：本会话必须能看到上表所列的 agentmemhub 工具；
   缺失则提醒用户在当前 harness 中配置 agentmemhub MCP server 后停止，不硬写。
3. **引擎探活**：调用 `memory_stats`；不可用时按返回的提示处理——
   内置 rag 引擎无守护进程，"启动引擎"即"建立索引"：在 AgentMemHub 项目内跑
   `python -m agentmemhub sync`（采集 + 向量化写入），之后即可读写。
   也可先在终端跑本仓库的预检脚本：`python scripts/check_engine.py`。

## 使用步骤

### 1. 写入记忆

调用 MCP 工具 `memory_save`，`content` 写一条**自包含**的结论：
包含背景一句话 + 结论/做法，例如：
「【运维】XX 项目嵌入模型为 bge-small-zh-v1.5（随仓库分发）；换用更大模型时
用 scripts/fetch_model.py 下载并在 agentmemhub.yaml 的 rag.models 注册。」

`memory_save` 成功返回 `id=<trace_id>`；若返回「写入未生效/失败」，直接告知用户
（无需评分，因为记忆没落库）。

### 2. 写后即评（本 skill 的核心）

对**刚写入的那一条**调用 MCP 工具 `memory_score`：

- `trace_id`：上一步返回的 id；
- `polarity`：按你自己的判断取 `positive`（值得保留）/ `negative`（噪音，几乎不用）/
  `neutral`（一般）。**大部分应给 positive**——能触发本 skill 的通常都有价值。

引擎会立即重算该记忆的 value/priority（检索排序生效），无需额外等待。

### 3. 多条记忆的批量评分（可选）

若一次任务保存了多条（短时间多次 memory_save），不想逐条评时，可改为在对话结束前
用终端跑一次（仅评未评的，自动跳过已评；需本机装有 AgentMemHub）：

```bash
python -m agentmemhub score            # 只评未评分记忆
python -m agentmemhub score --ids <id1>,<id2>   # 或只评指定条
```

## 检索怎么触发（不是本 skill 的职责）

检索与保存无关：**需要历史经验时直接调用 MCP 工具 `memory_search`**（模型自触发）——
例如新任务开始、用户问的问题疑似以前解决过、要复用某段配置/结论时。

## 注意事项

- 不要保存一次性/临时内容（如本次具体的修复文件名列表）；保存「结论 + 关键步骤」。
- 同一条结论措辞不同可能重复入库（引擎按内容幂等，但表述差异会生成新 id）；
  保存前如不确定可先 `memory_search` 同名话题，命中高度相似就跳过。
- 引擎离线时 `memory_save`/`memory_score` 会明确报错（isError），按报错提示处理即可。
