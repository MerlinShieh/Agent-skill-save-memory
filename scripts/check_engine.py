# -*- coding: utf-8 -*-
"""save-memory 预检：探测 AgentMemHub 记忆索引是否就绪。

内置 rag 引擎是**进程内**的（无 HTTP 服务、无守护进程、无端口），所以本脚本
不探测网络，而是检查索引库与模型资产是否就位；必要时给出可执行的修复命令。

用法：
    python scripts/check_engine.py [项目根]
    项目根默认 D:\\data\\vibeCoding\\Agent_Memory\\AgentMemHub

退出码：0=就绪；2=未就绪（附修复指引）。
"""
import os
import sqlite3
import sys
from pathlib import Path

DEFAULT_ROOT = Path(r"D:\data\vibeCoding\Agent_Memory\AgentMemHub")


def _backend(root: Path) -> str:
    """从 agentmemhub.yaml 读后端（不依赖 yaml 库：简单文本匹配）。"""
    cfg = root / "agentmemhub.yaml"
    try:
        for line in cfg.read_text(encoding="utf-8").splitlines():
            t = line.strip()
            if t.startswith("backend:") and "#" not in t.split(":", 1)[0]:
                return t.split(":", 1)[1].strip().strip("'\"") or "rag"
    except Exception:
        pass
    return "rag"


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ROOT
    if not root.exists():
        print(f"[X] 未找到 AgentMemHub 项目根：{root}")
        print("    传入正确路径：python scripts/check_engine.py <项目根>")
        return 2

    backend = _backend(root)
    db = root / "database" / "session_rag.db"

    if backend != "rag":
        # 回退后端（vendored MemOS）：它才有独立服务需要探活
        print(f"[i] 后端 = {backend}（回退模式，需独立的 MemOS 服务）")
        print("    启动：python -m agentmemhub memos-daemon start")
        return 2

    if not db.exists():
        print("[X] 记忆索引未建立：缺少 database/session_rag.db")
        print("    建立索引（采集 + 向量化写入）：")
        print(f"      cd {root}")
        print("      uv run python -m agentmemhub sync")
        return 2

    try:
        conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
        units = conn.execute("SELECT COUNT(*) FROM units").fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"[X] 索引库不可读：{db} -> {e}")
        return 2

    if units == 0:
        print("[X] 索引为空（units=0）——尚未向量化任何会话")
        print(f"    提示：cd {root} 后跑 uv run python -m agentmemhub sync")
        return 2

    models_dir = root / "models"
    has_model = models_dir.is_dir() and any(models_dir.iterdir())
    print(f"[OK] 记忆索引就绪（内置 rag 引擎）")
    print(f"     units = {units}")
    print(f"     模型  = {'已就绪' if has_model else '缺失（models/ 为空）'}")
    print(f"     库    = {db}")
    print("     可直接使用 memory_save / memory_score / memory_search。")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
