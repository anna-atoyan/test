from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

__version__ = "0.1.0"

EXPECTED_INPUT_HEADER = ["timestamp", "level", "service", "message"]
OUTPUT_HEADER = ["level", "service", "message", "count", "first_seen", "last_seen"]


class CliUsageError(Exception):
    """Invalid CLI usage (maps to exit code 2)."""


class CsvStructureError(Exception):
    """Invalid CSV structure (maps to exit code 3)."""


@dataclass
class GroupAgg:
    level: str
    service: str
    message: str
    count: int = 0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    def update(self, ts_utc: datetime) -> None:
        self.count += 1
        if self.first_seen is None or ts_utc < self.first_seen:
            self.first_seen = ts_utc
        if self.last_seen is None or ts_utc > self.last_seen:
            self.last_seen = ts_utc


def _normalize_level(raw_level: str) -> str:
    level = (raw_level or "").strip()
    return level.upper() if level else "UNKNOWN"


def _normalize_field(value: str) -> str:
    return (value or "").strip()


def _parse_iso8601_to_utc(raw_ts: str) -> Optional[datetime]:
    """Parse ISO 8601 timestamp and normalize to UTC.

    Accepted examples include:
      - 2025-01-31T14:03:22Z
      - 2025-01-31T14:03:22+00:00

    Returns None if parsing fails.
    """
    ts = (raw_ts or "").strip()
    if not ts:
        return None

    # datetime.fromisoformat doesn't accept trailing 'Z'
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None

    # Require timezone-aware timestamp for deterministic UTC normalization.
    if dt.tzinfo is None:
        return None

    return dt.astimezone(timezone.utc)


def _format_utc_iso(dt_utc: datetime) -> str:
    """Format a UTC datetime to canonical ISO 8601 with 'Z'."""
    return (
        dt_utc.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", newline="")
    except OSError as e:
        raise RuntimeError(f"Unable to read input file: {path}") from e


def _write_csv(path: Path, rows: Iterable[List[str]]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)
    except OSError as e:
        raise RuntimeError(f"Unable to write output file: {path}") from e


def _is_effectively_empty(contents: str) -> bool:
    return contents.strip() == ""


def _parse_events(contents: str) -> Tuple[List[Tuple[str, str, str, datetime]], int]:
    """Parse events from CSV contents.

    Returns:
      - valid events: (level, service, message, timestamp_utc)
      - count of skipped rows due to malformed timestamps

    Raises CsvStructureError on:
      - non-empty input with incorrect header
      - any row with wrong number of columns
    """
    skipped_bad_ts = 0
    valid: List[Tuple[str, str, str, datetime]] = []

    reader = csv.reader(contents.splitlines())
    try:
        header = next(reader)
    except StopIteration:
        return [], 0

    if header != EXPECTED_INPUT_HEADER:
        raise CsvStructureError(
            f"Invalid CSV header. Expected {EXPECTED_INPUT_HEADER}, got {header}"
        )

    for line_no, row in enumerate(reader, start=2):
        if len(row) != 4:
            raise CsvStructureError(
                f"Invalid CSV structure at line {line_no}: expected 4 columns, got {len(row)}"
            )

        raw_ts, raw_level, raw_service, raw_message = row
        ts_utc = _parse_iso8601_to_utc(raw_ts)
        if ts_utc is None:
            skipped_bad_ts += 1
            continue

        level = _normalize_level(raw_level)
        service = _normalize_field(raw_service)
        message = _normalize_field(raw_message)
        valid.append((level, service, message, ts_utc))

    return valid, skipped_bad_ts


def summarise_events(contents: str) -> Tuple[List[List[str]], int]:
    """Produce output CSV rows including header.

    Returns (rows, skipped_bad_timestamp_count).
    """
    if _is_effectively_empty(contents):
        return [OUTPUT_HEADER], 0

    events, skipped_bad_ts = _parse_events(contents)
    if not events:
        return [OUTPUT_HEADER], skipped_bad_ts

    groups: Dict[Tuple[str, str, str], GroupAgg] = {}
    for level, service, message, ts_utc in events:
        key = (level, service, message)
        agg = groups.get(key)
        if agg is None:
            agg = GroupAgg(level=level, service=service, message=message)
            groups[key] = agg
        agg.update(ts_utc)

    rows: List[List[str]] = [OUTPUT_HEADER]
    for key in sorted(groups.keys()):
        agg = groups[key]
        # Non-None because group created only after at least one valid row
        rows.append(
            [
                agg.level,
                agg.service,
                agg.message,
                str(agg.count),
                _format_utc_iso(agg.first_seen),  # type: ignore[arg-type]
                _format_utc_iso(agg.last_seen),  # type: ignore[arg-type]
            ]
        )

    return rows, skipped_bad_ts


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="logsum")
    p.add_argument("--input", default="events.csv", help="Path to the input CSV file.")
    p.add_argument("--output", default="summary.csv", help="Path to the output CSV file.")
    p.add_argument("--version", action="store_true", help="Print CLI version and exit.")
    return p


def _parse_args(argv: List[str]) -> argparse.Namespace:
    """Parse CLI arguments.

    Supports:
      - logsum --input in.csv --output out.csv
      - python -m src.logsum in.csv out.csv
    """
    # If user provides pure positional args (no flags), interpret as input/output.
    if argv and not any(a.startswith("-") for a in argv) and len(argv) in (1, 2):
        return argparse.Namespace(
            input=argv[0],
            output=argv[1] if len(argv) == 2 else "summary.csv",
            version=False,
        )

    parser = _build_parser()
    try:
        return parser.parse_args(argv)
    except SystemExit as e:
        raise CliUsageError from e


def run(input_path: Path, output_path: Path) -> int:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    contents = _read_text_file(input_path)

    rows, skipped_bad_ts = summarise_events(contents)
    _write_csv(output_path, rows)

    if skipped_bad_ts:
        print(
            f"Warning: skipped {skipped_bad_ts} row(s) due to malformed timestamps",
            file=sys.stderr,
        )

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--version" in argv:
        print(__version__)
        return 0

    try:
        ns = _parse_args(argv)
    except CliUsageError:
        return 2

    try:
        return run(Path(ns.input), Path(ns.output))
    except CsvStructureError as e:
        print(str(e), file=sys.stderr)
        return 3
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
