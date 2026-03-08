from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def ensure_dir(path: Path | str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def load_yaml(path: Path | str) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: Path | str) -> dict[str, Any]:
    config = load_yaml(config_path)
    base_ref = config.get("base_config")
    if not base_ref:
        return config
    base_path = Path(config_path).parent / base_ref
    base_config = load_yaml(base_path)
    merged = deep_merge(base_config, {k: v for k, v in config.items() if k != "base_config"})
    return merged


def config_hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def utc_timestamp() -> str:
    return dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def make_run_dir(results_root: Path | str, prefix: str, config: dict[str, Any]) -> Path:
    root = ensure_dir(results_root)
    run_dir = root / f"{prefix}_{utc_timestamp()}_{config_hash(config)}"
    ensure_dir(run_dir)
    return run_dir


def write_jsonl(path: Path | str, rows: Iterable[dict[str, Any]]) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path | str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def git_commit(default: str = "unknown") -> str:
    head_path = project_root() / ".git" / "HEAD"
    if not head_path.exists():
        return default
    try:
        head = head_path.read_text(encoding="utf-8").strip()
        if head.startswith("ref: "):
            ref_path = project_root() / ".git" / head.split(" ", 1)[1]
            if ref_path.exists():
                return ref_path.read_text(encoding="utf-8").strip()
        return head
    except OSError:
        return default


def append_log(log_path: Path | str, message: str) -> None:
    timestamp = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with Path(log_path).open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")


def env_or_default(name: str, default: str) -> str:
    return os.environ.get(name, default)
