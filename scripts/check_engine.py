# -*- coding: utf-8 -*-
"""save-memory 预检：探测 MemOS 记忆引擎是否在线（仅标准库，无第三方依赖）。

用法：
    python scripts/check_engine.py [base_url]
    base_url 默认 http://127.0.0.1:18800

退出码：0=在线；2=离线/不可达。
"""
import json
import sys
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18800").rstrip("/")


def main() -> int:
    try:
        with urllib.request.urlopen(f"{BASE}/api/v1/auth/status", timeout=3) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        print(f"引擎在线: {BASE} (auth={data})")
        return 0
    except Exception as e:
        print(f"引擎离线/不可达: {BASE} -> {e}")
        print("请先启动 MemOS 引擎（AgentMemHub: python -m agentmemhub memos-daemon start，或看板/面板）。")
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
