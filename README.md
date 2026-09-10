# Agent-skill-save-memory

让 Agent 在任务收尾时**自动把可复用结论沉淀成长期记忆**的技能（Skill）。

配套项目：[AgentMemHub](https://github.com/MerlinShieh/AgentMemHub)（记忆存储与检索服务）。

## 它解决什么问题

Agent 的上下文是一次性的：会话结束，这次踩的坑、定的方案就没了，下次还得重来。
本 Skill 建立一条**纪律**——什么时候必须保存、按什么顺序保存+评分，
让经验真正沉淀下来并可被后续会话检索到。

## 安装

1. 把本目录放入 Agent 的 skills 目录（ZCode 为 `~/.zcode/skills/save-memory/`）；
2. 配置 `agentmemhub` MCP server（见 [AgentMemHub](https://github.com/MerlinShieh/AgentMemHub) 的 MCP 章节）；
3. 把 AGENTS.md 硬规则加入你的全局/项目指令文件（见 SKILL.md「生效前提」）。

## 依赖（强绑定，无降级路径）

| 依赖 | 说明 |
|---|---|
| `agentmemhub` MCP server | 提供 `memory_save` / `memory_score` / `memory_search` 等工具 |
| AgentMemHub 内置记忆引擎 | 写入与检索的实际执行者（`agentmemhub.rag`，进程内直调） |

## 结构

```
SKILL.md                技能主文件（触发纪律 + 使用步骤）
scripts/check_engine.py 预检脚本：确认记忆索引已就绪
```

## 边界

本仓库**只做行为协议**（何时保存、按什么顺序），不含存储/检索/评分实现——
那些在 [AgentMemHub](https://github.com/MerlinShieh/AgentMemHub)。
