"""検証スクリプトが共通で使う実行記録ユーティリティ。

各検証スクリプトは Reporter で 1 ステップずつ実行を記録し、同じ形の JSON を
results/ に書き出す。registry/build.py はその JSON だけを読んで台帳の
検証ステータスを生成するため、エンベロープの形は全検証スクリプトで揃える。
"""

from __future__ import annotations

import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Any

PREVIEW_LIMIT = 1500


def preview(value: Any, limit: int = PREVIEW_LIMIT) -> Any:
    """レポートに載せるため大きな戻り値を切り詰める。"""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    if len(text) <= limit:
        return value
    return {"_truncated": True, "_original_chars": len(text), "_head": text[:limit]}


class Reporter:
    """1 検証スクリプト＝1 Reporter。ステップの成否・所要時間・戻り値を集める。"""

    def __init__(self, source_id: str, target: str) -> None:
        self.source_id = source_id
        self.target = target
        self.steps: list[dict] = []
        self.extra: dict[str, Any] = {}

    async def step(self, name: str, coro) -> Any:
        """1 ステップ実行し、成功なら戻り値を、失敗なら例外を記録して None を返す。"""
        started = time.monotonic()
        try:
            value = await coro
        except Exception as exc:  # noqa: BLE001 - 検証目的なので全例外を記録する
            self.steps.append(
                {
                    "step": name,
                    "ok": False,
                    "elapsed_ms": round((time.monotonic() - started) * 1000),
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(limit=3),
                }
            )
            return None
        self.steps.append(
            {
                "step": name,
                "ok": True,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "result": preview(value),
            }
        )
        return value

    def skip(self, name: str, note: str) -> None:
        """前提が揃わず実行できなかったステップを、成功とも失敗とも区別して記録する。"""
        self.steps.append({"step": name, "ok": True, "skipped": True, "note": note})

    @property
    def summary(self) -> dict[str, int]:
        return {
            "total": len(self.steps),
            "ok": sum(1 for s in self.steps if s.get("ok") and not s.get("skipped")),
            "skipped": sum(1 for s in self.steps if s.get("skipped")),
            "failed": sum(1 for s in self.steps if not s.get("ok")),
        }

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target": self.target,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "environment": {
                "python": platform.python_version(),
                "platform": platform.platform(),
            },
            **self.extra,
            "steps": self.steps,
            "summary": self.summary,
        }

    def write(self, path: str) -> dict:
        payload = self.to_dict()
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        return payload

    def print_console(self, out_path: str) -> int:
        """人間向けに結果を表示し、プロセスの終了コードを返す。"""
        for step in self.steps:
            if step.get("skipped"):
                print(f"  [SKIP] {step['step']} - {step.get('note')}")
            elif step.get("ok"):
                print(f"  [OK  ] {step['step']}")
            else:
                print(f"  [FAIL] {step['step']} - {step.get('error')}")
        s = self.summary
        print(
            f"{s['ok']} ok / {s['skipped']} skipped / {s['failed']} failed"
            f" (total {s['total']}) -> {out_path}"
        )
        return 0 if s["failed"] == 0 else 1


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)
