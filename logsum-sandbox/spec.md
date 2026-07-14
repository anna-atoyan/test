consumes_from CLAUDE.md

# Tiny CLI Specification

## Goal

Build a tiny CLI named `logsum` that reads an input CSV file of events and writes a summary CSV file with one row per event group.

The CLI is intended for simple offline summarisation of event logs. It should be deterministic, small in scope, and easy to run with default file names.Add 


## Input 

```text
events.csv
```

The input must be a CSV file with the following columns:

```csv
timestamp,level,service,message
```

| Column | Description |
| --- | --- |
| `timestamp` | Event timestamp. Must be parseable as ISO 8601. |
| `level` | Event severity level, such as `INFO`, `WARN`, or `ERROR`. May be blank. |
| `service` | Name of the service that produced the event. |
| `message` | Event message text. |

Quoted fields, commas inside quoted fields, and escaped quotes must follow standard CSV parsing rules.

## Outputs

Default output file:

```text
summary.csv
```

The output CSV must contain one row per event group with the following columns:

```csv
level,service,message,count,first_seen,last_seen
```

| Column | Description |
| --- | --- |
| `level` | Normalized event level used in the group key. |
| `service` | Normalized service value used in the group key. |
| `message` | Normalized message value used in the group key. |
| `count` | Number of valid input rows in the group. |
| `first_seen` | Earliest valid timestamp in the group. |
| `last_seen` | Latest valid timestamp in the group. |

Output rows should be sorted deterministically by:

1. `level` ascending
2. `service` ascending
3. `message` ascending

`first_seen` and `last_seen` must be written as normalized ISO 8601 UTC timestamps, for example:

```text
2025-01-31T14:03:22Z
```

## Normalisation rules

Apply these rules before grouping:

- Trim leading and trailing whitespace from all fields.
- Normalize `level` to uppercase.
- If `level` is missing or blank after trimming, set it to `UNKNOWN`.
- Preserve `service` case after trimming.
- Preserve `message` case after trimming.
- Do not collapse internal whitespace inside `message`.
- Do not normalize punctuation.
- Do not apply fuzzy matching or message deduplication.
- Do not perform Unicode normalization beyond what the CSV parser returns.
- Parse valid timestamps and normalize them to ISO 8601 UTC for output.

Examples:

```text
" error " -> "ERROR"
" api " -> "api"
"Disk  full" -> "Disk  full"
blank level -> "UNKNOWN"
```

## Grouping rule

The exact event group key is the normalized tuple:

```text
level,service,message
```

The `timestamp` field is not part of the group key.

Two input rows belong to the same group only when their normalized `level`, `service`, and `message` values are identical.

## Aggregation

For each event group, compute:

- `count`: number of valid rows in the group
- `first_seen`: earliest valid timestamp in the group
- `last_seen`: latest valid timestamp in the group

Rows skipped due to malformed timestamps or invalid CSV structure must not contribute to `count`, `first_seen`, or `last_seen`.

## Edge cases

### Missing level

If `level` is missing or blank, use:

```text
UNKNOWN
```

The row is still included if the timestamp and CSV structure are otherwise valid.

### Malformed timestamp

Rows with malformed timestamps are skipped.

A timestamp is valid if it can be parsed as ISO 8601. Accepted examples include:

```text
2025-01-31T14:03:22Z
2025-01-31T14:03:22+00:00
```

If any rows are skipped because of malformed timestamps, the CLI should:

- still write `summary.csv` for all valid rows
- print a warning to stderr with the number of skipped rows
- exit with code `0`, unless another error condition occurs

### Empty input

If the input contains no valid events, write `summary.csv` with only the header row:

```csv
level,service,message,count,first_seen,last_seen
```

This applies when:

- `events.csv` contains only the header row
- `events.csv` is completely empty
- all rows are skipped because of malformed timestamps

A valid empty input should exit with code `0`.

If the file is completely empty and has no header, treat it as empty input and write the header-only output file.

### Invalid CSV structure

A non-empty input file with an incorrect header is invalid.

Rows with the wrong number of columns are invalid CSV structure. This should fail the command instead of silently skipping those rows.

## CLI

Command:

```sh
logsum --input events.csv --output summary.csv
```

Supported flags:

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `--input <path>` | No | `events.csv` | Path to the input CSV file. |
| `--output <path>` | No | `summary.csv` | Path to the output CSV file. |
| `--help` | No | n/a | Print usage information and exit. |
| `--version` | No | n/a | Print CLI version and exit. |

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | Success. Output file was written, or `--help` / `--version` completed successfully. |
| `1` | General runtime error, such as unable to read input or write output. |
| `2` | Invalid CLI usage, such as an unknown flag or missing flag value. |
| `3` | Invalid CSV structure, such as rows with the wrong number of columns or a non-empty file with an incorrect header. |

Warnings, such as skipped malformed timestamps, are written to stderr but do not change the exit code unless another error condition occurs.

## Out of scope

The following are intentionally out of scope:

- Real-time log streaming.
- Reading from stdin.
- Writing to stdout instead of a file.
- Recursive directory processing.
- Multiple input files in one command.
- Non-CSV input formats such as JSON, JSONL, or plain text logs.
- Custom grouping fields.
- Custom timestamp formats.
- Time-zone-specific reporting beyond normalizing parsed timestamps to UTC.
- Fuzzy message matching or deduplication.
- Severity ordering beyond lexicographic sorting of normalized `level`.
- Config files.
- Environment variable configuration.
- Compression support.
- Parallel processing guarantees.
- Database output.


## Implementation notes

- Python's `datetime.fromisoformat()` does not directly parse timestamps ending with `Z`. The implementation normalizes `Z` to `+00:00` before parsing, then writes timestamps back in canonical UTC (`Z`) format.
:::

## Signed off

Anna Atoyan — 2026-07-13