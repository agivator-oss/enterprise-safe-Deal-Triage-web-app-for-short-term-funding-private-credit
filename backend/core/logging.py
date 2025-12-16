from __future__ import annotations

import datetime as dt


def ts() -> str:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()


def log(level: str, message: str, **fields: object) -> None:
    payload = " ".join([f"{k}={fields[k]!r}" for k in sorted(fields)])
    line = f"[{ts()}] {level.upper():7s} {message}"
    if payload:
        line += f" | {payload}"
    print(line)
