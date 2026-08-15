#!/usr/bin/env python3
"""Build and verify the repository SHA-256 manifest.

The manifest excludes itself, Git metadata, virtual environments, Python byte
code, and cache directories. MANIFEST_SUMMARY.json is included and therefore
written to a stable size before hashes are calculated.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST_SHA256.csv"
SUMMARY = ROOT / "MANIFEST_SUMMARY.json"
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__"}
IGNORED_NAMES = {MANIFEST.name}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def deposited_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if path.name in IGNORED_NAMES or path.suffix.lower() in IGNORED_SUFFIXES:
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_summary(created: str, source_snapshot: str) -> None:
    previous: tuple[int, int] | None = None
    for _ in range(10):
        files = deposited_files()
        current = (len(files), sum(path.stat().st_size for path in files))
        payload = {
            "created_utc": created,
            "source_snapshot": source_snapshot,
            "file_count_excluding_manifest": current[0],
            "total_bytes_excluding_manifest": current[1],
            "manifest_scope": (
                "All deposited files except MANIFEST_SHA256.csv; excludes Git metadata, "
                "virtual environments, Python bytecode, and cache directories."
            ),
        }
        SUMMARY.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        files = deposited_files()
        updated = (len(files), sum(path.stat().st_size for path in files))
        if updated == current or updated == previous:
            if updated != current:
                payload["file_count_excluding_manifest"] = updated[0]
                payload["total_bytes_excluding_manifest"] = updated[1]
                SUMMARY.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            return
        previous = current
    raise RuntimeError("MANIFEST_SUMMARY.json size did not stabilize")


def write_manifest() -> None:
    with MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "size_bytes", "sha256"])
        for path in deposited_files():
            writer.writerow(
                [
                    path.relative_to(ROOT).as_posix(),
                    path.stat().st_size,
                    sha256(path),
                ]
            )


def verify_manifest() -> None:
    with MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected = {path.relative_to(ROOT).as_posix(): path for path in deposited_files()}
    recorded = {row["path"]: row for row in rows}
    if expected.keys() != recorded.keys():
        missing = sorted(expected.keys() - recorded.keys())
        stale = sorted(recorded.keys() - expected.keys())
        raise RuntimeError(f"manifest path mismatch: missing={missing}, stale={stale}")
    for rel, path in expected.items():
        row = recorded[rel]
        if int(row["size_bytes"]) != path.stat().st_size or row["sha256"] != sha256(path):
            raise RuntimeError(f"manifest checksum mismatch: {rel}")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if summary["file_count_excluding_manifest"] != len(expected):
        raise RuntimeError("summary file count does not match deposited files")
    if summary["total_bytes_excluding_manifest"] != sum(p.stat().st_size for p in expected.values()):
        raise RuntimeError("summary byte count does not match deposited files")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-snapshot",
        default="fe3f1a3b47807a331208e12f0baf7fd611c9137b",
        help="Commit or archive identifier from which this review snapshot was repaired.",
    )
    args = parser.parse_args()
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    write_summary(created, args.source_snapshot)
    write_manifest()
    verify_manifest()
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    print(json.dumps(summary, indent=2))
    print(f"manifest_rows={summary['file_count_excluding_manifest']}")


if __name__ == "__main__":
    main()
