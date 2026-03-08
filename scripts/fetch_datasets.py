#!/usr/bin/env python3
from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from src.datasets import DATASET_SPECS, fetch_dataset, write_manifest
from src.utils import ensure_dir, load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download and stage datasets into data/raw.")
    parser.add_argument("--config", default="configs/base.yaml", help="Path to YAML config.")
    parser.add_argument("--force", action="store_true", help="Redownload even if data exists.")
    parser.add_argument("--dataset", action="append", help="Specific dataset name to fetch.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.config)
    raw_root = ensure_dir(Path(config["paths"]["raw_data_dir"]))
    manifest_path = raw_root / "download_manifest.json"
    requested = set(args.dataset or [])
    records = []

    for spec in DATASET_SPECS:
        if requested and spec["name"] not in requested:
            continue
        try:
            result = fetch_dataset(spec, raw_root, force=args.force)
        except Exception as exc:  # pragma: no cover - defensive for cluster runtime
            result = {
                "dataset": spec["name"],
                "config_name": spec["config_name"],
                "status": "failed",
                "error": str(exc),
                "traceback": traceback.format_exc(limit=3),
            }
        records.append(result)
        print(f"{result['dataset']}: {result['status']}")

    write_manifest(manifest_path, records)
    print(f"Wrote manifest to {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
