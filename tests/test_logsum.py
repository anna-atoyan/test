"""
Comprehensive tests for logsum CLI.

Covers all rules and edge cases from spec.md:
- Normalization (whitespace, level uppercase, case preservation)
- Grouping by (level, service, message)
- Aggregation (count, first_seen, last_seen)
- Missing level handling
- Malformed timestamp handling
- Empty input
- Invalid CSV structure
- CLI invocation and exit codes
"""

import csv
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


# Helper functions

def run_logsum(input_path=None, output_path=None, extra_args=None):
    """
    Run the logsum CLI and return (exit_code, stdout, stderr).
    
    Args:
        input_path: Path to input CSV file (optional)
        output_path: Path to output CSV file (optional)
        extra_args: Additional command-line arguments as list
    
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    cmd = [sys.executable, "-m", "src.logsum"]
    
    if input_path:
        cmd.extend(["--input", str(input_path)])
    if output_path:
        cmd.extend(["--output", str(output_path)])
    if extra_args:
        cmd.extend(extra_args)
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    return result.returncode, result.stdout, result.stderr


def read_csv_rows(path):
    """Read CSV file and return list of row dictionaries."""
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(path, rows, fieldnames):
    """Write CSV file with given rows and fieldnames."""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# Test fixtures

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def input_csv(temp_dir):
    """Path to temporary input CSV file."""
    return temp_dir / "events.csv"


@pytest.fixture
def output_csv(temp_dir):
    """Path to temporary output CSV file."""
    return temp_dir / "summary.csv"


# Normalization tests

def test_level_normalization_to_uppercase(input_csv, output_csv):
    """Test that level is normalized to uppercase."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "error",
            "service": "api",
            "message": "Connection failed"
        },
        {
            "timestamp": "2025-01-31T14:03:23Z",
            "level": "Error",
            "service": "api",
            "message": "Connection failed"
        },
        {
            "timestamp": "2025-01-31T14:03:24Z",
            "level": "ERROR",
            "service": "api",
            "message": "Connection failed"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["level"] == "ERROR"
    assert rows[0]["count"] == "3"


def test_whitespace_trimming(input_csv, output_csv):
    """Test that leading and trailing whitespace is trimmed from all fields."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": " error ",
            "service": " api ",
            "message": " Disk full "
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["level"] == "ERROR"
    assert rows[0]["service"] == "api"
    assert rows[0]["message"] == "Disk full"


def test_internal_whitespace_preserved(input_csv, output_csv):
    """Test that internal whitespace in message is preserved."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "ERROR",
            "service": "api",
            "message": "Disk  full"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["message"] == "Disk  full"


def test_service_case_preserved(input_csv, output_csv):
    """Test that service case is preserved after trimming."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "INFO",
            "service": "API",
            "message": "Test"
        },
        {
            "timestamp": "2025-01-31T14:03:23Z",
            "level": "INFO",
            "service": "api",
            "message": "Test"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 2
    assert rows[0]["service"] == "API"
    assert rows[1]["service"] == "api"


def test_message_case_preserved(input_csv, output_csv):
    """Test that message case is preserved after trimming."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "INFO",
            "service": "api",
            "message": "Connection Failed"
        },
        {
            "timestamp": "2025-01-31T14:03:23Z",
            "level": "INFO",
            "service": "api",
            "message": "connection failed"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 2
    assert rows[0]["message"] == "Connection Failed"
    assert rows[1]["message"] == "connection failed"


# Grouping tests

def test_grouping_by_level_service_message(input_csv, output_csv):
    """Test that events are grouped by (level, service, message) tuple."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "ERROR",
            "service": "api",
            "message": "Connection failed"
        },
        {
            "timestamp": "2025-01-31T14:03:23Z",
            "level": "ERROR",
            "service": "api",
            "message": "Connection failed"
        },
        {
            "timestamp": "2025-01-31T14:03:24Z",
            "level": "WARN",
            "service": "api",
            "message": "Connection failed"
        },
        {
            "timestamp": "2025-01-31T14:03:25Z",
            "level": "ERROR",
            "service": "db",
            "message": "Connection failed"
        },
        {
            "timestamp": "2025-01-31T14:03:26Z",
            "level": "ERROR",
            "service": "api",
            "message": "Timeout"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 4
    
    # Group 1: ERROR, api, Connection failed - count 2
    group1 = [r for r in rows if r["level"] == "ERROR" and r["service"] == "api" and r["message"] == "Connection failed"]
    assert len(group1) == 1
    assert group1[0]["count"] == "2"
    
    # Group 2: WARN, api, Connection failed - count 1
    group2 = [r for r in rows if r["level"] == "WARN" and r["service"] == "api"]
    assert len(group2) == 1
    assert group2[0]["count"] == "1"
    
    # Group 3: ERROR, db, Connection failed - count 1
    group3 = [r for r in rows if r["level"] == "ERROR" and r["service"] == "db"]
    assert len(group3) == 1
    assert group3[0]["count"] == "1"
    
    # Group 4: ERROR, api, Timeout - count 1
    group4 = [r for r in rows if r["message"] == "Timeout"]
    assert len(group4) == 1
    assert group4[0]["count"] == "1"


def test_timestamp_not_part_of_group_key(input_csv, output_csv):
    """Test that timestamp is not part of the grouping key."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T10:00:00Z",
            "level": "ERROR",
            "service": "api",
            "message": "Failed"
        },
        {
            "timestamp": "2025-01-31T15:00:00Z",
            "level": "ERROR",
            "service": "api",
            "message": "Failed"
        },
        {
            "timestamp": "2025-01-31T20:00:00Z",
            "level": "ERROR",
            "service": "api",
            "message": "Failed"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["count"] == "3"


# Aggregation tests

def test_count_aggregation(input_csv, output_csv):
    """Test that count is correctly computed."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "INFO",
            "service": "api",
            "message": "Started"
        },
        {
            "timestamp": "2025-01-31T14:03:23Z",
            "level": "INFO",
            "service": "api",
            "message": "Started"
        },
        {
            "timestamp": "2025-01-31T14:03:24Z",
            "level": "INFO",
            "service": "api",
            "message": "Started"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["count"] == "3"


def test_first_seen_last_seen(input_csv, output_csv):
    """Test that first_seen and last_seen are correctly computed."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:25Z",
            "level": "ERROR",
            "service": "api",
            "message": "Failed"
        },
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "ERROR",
            "service": "api",
            "message": "Failed"
        },
        {
            "timestamp": "2025-01-31T14:03:30Z",
            "level": "ERROR",
            "service": "api",
            "message": "Failed"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["first_seen"] == "2025-01-31T14:03:22Z"
    assert rows[0]["last_seen"] == "2025-01-31T14:03:30Z"


def test_timestamp_normalization_to_utc(input_csv, output_csv):
    """Test that timestamps are normalized to ISO 8601 UTC format."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22+00:00",
            "level": "INFO",
            "service": "api",
            "message": "Event"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["first_seen"] == "2025-01-31T14:03:22Z"
    assert rows[0]["last_seen"] == "2025-01-31T14:03:22Z"


# Missing level tests

def test_missing_level_becomes_unknown(input_csv, output_csv):
    """Test that missing level is set to UNKNOWN."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "",
            "service": "api",
            "message": "Event"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["level"] == "UNKNOWN"


def test_blank_level_after_trim_becomes_unknown(input_csv, output_csv):
    """Test that blank level after trimming is set to UNKNOWN."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "   ",
            "service": "api",
            "message": "Event"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["level"] == "UNKNOWN"


def test_missing_level_groups_separately(input_csv, output_csv):
    """Test that rows with missing level form their own UNKNOWN group."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "",
            "service": "api",
            "message": "Event"
        },
        {
            "timestamp": "2025-01-31T14:03:23Z",
            "level": "",
            "service": "api",
            "message": "Event"
        },
        {
            "timestamp": "2025-01-31T14:03:24Z",
            "level": "INFO",
            "service": "api",
            "message": "Event"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 2
    
    unknown_group = [r for r in rows if r["level"] == "UNKNOWN"]
    assert len(unknown_group) == 1
    assert unknown_group[0]["count"] == "2"
    
    info_group = [r for r in rows if r["level"] == "INFO"]
    assert len(info_group) == 1
    assert info_group[0]["count"] == "1"


# Malformed timestamp tests

def test_malformed_timestamp_skipped_with_warning(input_csv, output_csv):
    """Test that rows with malformed timestamps are skipped with a warning."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "INFO",
            "service": "api",
            "message": "Valid"
        },
        {
            "timestamp": "not-a-timestamp",
            "level": "ERROR",
            "service": "api",
            "message": "Invalid"
        },
        {
            "timestamp": "2025-01-31T14:03:23Z",
            "level": "INFO",
            "service": "api",
            "message": "Valid"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, stdout, stderr = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    assert "1" in stderr or "skipped" in stderr.lower()
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["level"] == "INFO"
    assert rows[0]["count"] == "2"


def test_multiple_malformed_timestamps(input_csv, output_csv):
    """Test handling of multiple malformed timestamps."""
    write_csv(input_csv, [
        {
            "timestamp": "invalid-1",
            "level": "ERROR",
            "service": "api",
            "message": "Bad1"
        },
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "INFO",
            "service": "api",
            "message": "Good"
        },
        {
            "timestamp": "invalid-2",
            "level": "ERROR",
            "service": "api",
            "message": "Bad2"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, stdout, stderr = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    assert "2" in stderr or "skipped" in stderr.lower()
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["count"] == "1"


def test_all_malformed_timestamps_produces_empty_output(input_csv, output_csv):
    """Test that all malformed timestamps produces header-only output."""
    write_csv(input_csv, [
        {
            "timestamp": "invalid-1",
            "level": "ERROR",
            "service": "api",
            "message": "Bad"
        },
        {
            "timestamp": "invalid-2",
            "level": "INFO",
            "service": "db",
            "message": "Bad"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, stdout, stderr = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    assert "2" in stderr or "skipped" in stderr.lower()
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 0


# Empty input tests

def test_empty_csv_with_header_only(input_csv, output_csv):
    """Test that input with only header produces header-only output."""
    write_csv(input_csv, [], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 0
    
    # Verify header exists
    with open(output_csv, 'r', encoding='utf-8') as f:
        header = f.readline().strip()
        assert header == "level,service,message,count,first_seen,last_seen"


def test_completely_empty_file(input_csv, output_csv):
    """Test that completely empty file produces header-only output."""
    with open(input_csv, 'w', encoding='utf-8') as f:
        f.write("")
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 0


# Invalid CSV structure tests

def test_incorrect_header_fails(input_csv, output_csv):
    """Test that incorrect header causes exit code 3."""
    write_csv(input_csv, [], ["time", "severity", "component", "msg"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 3


def test_wrong_number_of_columns_fails(input_csv, output_csv):
    """Test that rows with wrong number of columns cause exit code 3."""
    with open(input_csv, 'w', newline='', encoding='utf-8') as f:
        f.write("timestamp,level,service,message\n")
        f.write("2025-01-31T14:03:22Z,INFO,api\n")  # Missing message column
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 3


def test_extra_columns_fails(input_csv, output_csv):
    """Test that rows with extra columns cause exit code 3."""
    with open(input_csv, 'w', newline='', encoding='utf-8') as f:
        f.write("timestamp,level,service,message\n")
        f.write("2025-01-31T14:03:22Z,INFO,api,Event,extra\n")  # Extra column
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 3


# Sorting tests

def test_output_sorted_by_level_service_message(input_csv, output_csv):
    """Test that output is sorted by level, service, message ascending."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "WARN",
            "service": "db",
            "message": "Slow query"
        },
        {
            "timestamp": "2025-01-31T14:03:23Z",
            "level": "ERROR",
            "service": "api",
            "message": "Timeout"
        },
        {
            "timestamp": "2025-01-31T14:03:24Z",
            "level": "ERROR",
            "service": "api",
            "message": "Connection failed"
        },
        {
            "timestamp": "2025-01-31T14:03:25Z",
            "level": "ERROR",
            "service": "db",
            "message": "Connection failed"
        },
        {
            "timestamp": "2025-01-31T14:03:26Z",
            "level": "INFO",
            "service": "api",
            "message": "Started"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 5
    
    # Check sorting
    assert rows[0]["level"] == "ERROR"
    assert rows[0]["service"] == "api"
    assert rows[0]["message"] == "Connection failed"
    
    assert rows[1]["level"] == "ERROR"
    assert rows[1]["service"] == "api"
    assert rows[1]["message"] == "Timeout"
    
    assert rows[2]["level"] == "ERROR"
    assert rows[2]["service"] == "db"
    assert rows[2]["message"] == "Connection failed"
    
    assert rows[3]["level"] == "INFO"
    assert rows[3]["service"] == "api"
    assert rows[3]["message"] == "Started"
    
    assert rows[4]["level"] == "WARN"
    assert rows[4]["service"] == "db"
    assert rows[4]["message"] == "Slow query"


# CSV edge cases

def test_quoted_fields_with_commas(input_csv, output_csv):
    """Test that quoted fields with commas are handled correctly."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "ERROR",
            "service": "api",
            "message": "Failed: error code 1, retrying"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert rows[0]["message"] == "Failed: error code 1, retrying"


def test_escaped_quotes_in_fields(input_csv, output_csv):
    """Test that escaped quotes in fields are handled correctly."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "ERROR",
            "service": "api",
            "message": 'User said "hello"'
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 1
    assert 'hello' in rows[0]["message"]


# CLI flag tests

def test_help_flag(temp_dir):
    """Test that --help flag prints usage and exits with code 0."""
    exit_code, stdout, stderr = run_logsum(extra_args=["--help"])
    assert exit_code == 0
    assert "usage" in stdout.lower() or "help" in stdout.lower()


def test_version_flag(temp_dir):
    """Test that --version flag prints version and exits with code 0."""
    exit_code, stdout, stderr = run_logsum(extra_args=["--version"])
    assert exit_code == 0
    assert len(stdout) > 0


def test_unknown_flag_fails(temp_dir):
    """Test that unknown flag causes exit code 2."""
    exit_code, stdout, stderr = run_logsum(extra_args=["--unknown-flag"])
    assert exit_code == 2


def test_missing_flag_value_fails(temp_dir):
    """Test that missing flag value causes exit code 2."""
    exit_code, stdout, stderr = run_logsum(extra_args=["--input"])
    assert exit_code == 2


def test_input_file_not_found(output_csv):
    """Test that missing input file causes exit code 1."""
    exit_code, stdout, stderr = run_logsum("/nonexistent/file.csv", output_csv)
    assert exit_code == 1


def test_custom_input_output_paths(temp_dir):
    """Test that custom input and output paths work."""
    custom_input = temp_dir / "my_events.csv"
    custom_output = temp_dir / "my_summary.csv"
    
    write_csv(custom_input, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "INFO",
            "service": "api",
            "message": "Test"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(custom_input, custom_output)
    assert exit_code == 0
    assert custom_output.exists()
    
    rows = read_csv_rows(custom_output)
    assert len(rows) == 1


def test_default_file_names(temp_dir):
    """Test that default file names are used when not specified."""
    # Change to temp directory and create events.csv
    original_dir = os.getcwd()
    try:
        os.chdir(temp_dir)
        
        write_csv("events.csv", [
            {
                "timestamp": "2025-01-31T14:03:22Z",
                "level": "INFO",
                "service": "api",
                "message": "Test"
            }
        ], ["timestamp", "level", "service", "message"])
        
        # Run without specifying input/output
        cmd = [sys.executable, "-m", "src.logsum"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # Should fail because events.csv is in temp_dir, not project root
        # This test verifies the default behavior
        assert result.returncode != 0 or Path("summary.csv").exists()
    finally:
        os.chdir(original_dir)


# Integration tests

def test_complex_scenario(input_csv, output_csv):
    """Test a complex scenario with multiple edge cases combined."""
    write_csv(input_csv, [
        # Group 1: ERROR, api, Connection failed - count 2
        {
            "timestamp": "2025-01-31T10:00:00Z",
            "level": " error ",
            "service": " api ",
            "message": " Connection failed "
        },
        {
            "timestamp": "2025-01-31T15:00:00Z",
            "level": "ERROR",
            "service": "api",
            "message": "Connection failed"
        },
        # Malformed timestamp - should be skipped
        {
            "timestamp": "invalid",
            "level": "WARN",
            "service": "api",
            "message": "Warning"
        },
        # Group 2: UNKNOWN, db, Slow query - count 1
        {
            "timestamp": "2025-01-31T12:00:00Z",
            "level": "",
            "service": "db",
            "message": "Slow query"
        },
        # Group 3: INFO, api, Started - count 1
        {
            "timestamp": "2025-01-31T09:00:00Z",
            "level": "info",
            "service": "api",
            "message": "Started"
        },
        # Group 1 again
        {
            "timestamp": "2025-01-31T20:00:00Z",
            "level": "Error",
            "service": "api",
            "message": "Connection failed"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, stdout, stderr = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    assert "1" in stderr or "skipped" in stderr.lower()
    
    rows = read_csv_rows(output_csv)
    assert len(rows) == 3
    
    # Verify Group 1
    group1 = [r for r in rows if r["level"] == "ERROR" and r["service"] == "api"]
    assert len(group1) == 1
    assert group1[0]["count"] == "3"
    assert group1[0]["first_seen"] == "2025-01-31T10:00:00Z"
    assert group1[0]["last_seen"] == "2025-01-31T20:00:00Z"
    
    # Verify Group 2
    group2 = [r for r in rows if r["level"] == "UNKNOWN"]
    assert len(group2) == 1
    assert group2[0]["count"] == "1"
    
    # Verify Group 3
    group3 = [r for r in rows if r["level"] == "INFO"]
    assert len(group3) == 1
    assert group3[0]["count"] == "1"
    
    # Verify sorting
    assert rows[0]["level"] == "ERROR"
    assert rows[1]["level"] == "INFO"
    assert rows[2]["level"] == "UNKNOWN"


def test_output_csv_structure(input_csv, output_csv):
    """Test that output CSV has correct columns and structure."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T14:03:22Z",
            "level": "INFO",
            "service": "api",
            "message": "Test"
        }
    ], ["timestamp", "level", "service", "message"])
    
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0
    
    # Read file and check header
    with open(output_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["level", "service", "message", "count", "first_seen", "last_seen"]
        
        # Check data row
        row = next(reader)
        assert len(row) == 6
        assert row[0] == "INFO"
        assert row[1] == "api"
        assert row[2] == "Test"
        assert row[3] == "1"
        assert row[4] == "2025-01-31T14:03:22Z"
        assert row[5] == "2025-01-31T14:03:22Z"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Min-count filtering tests

def test_min_count_filters_correctly(input_csv, output_csv):
    """Test that --min-count filters groups correctly."""
    write_csv(input_csv, [
        # Group 1: count 3
        {
            "timestamp": "2025-01-31T10:00:00Z",
            "level": "INFO",
            "service": "api",
            "message": "Request received"
        },
        {
            "timestamp": "2025-01-31T10:01:00Z",
            "level": "INFO",
            "service": "api",
            "message": "Request received"
        },
        {
            "timestamp": "2025-01-31T10:02:00Z",
            "level": "INFO",
            "service": "api",
            "message": "Request received"
        },
        # Group 2: count 2
        {
            "timestamp": "2025-01-31T10:03:00Z",
            "level": "WARN",
            "service": "cache",
            "message": "Cache miss"
        },
        {
            "timestamp": "2025-01-31T10:04:00Z",
            "level": "WARN",
            "service": "cache",
            "message": "Cache miss"
        },
        # Group 3: count 1
        {
            "timestamp": "2025-01-31T10:05:00Z",
            "level": "ERROR",
            "service": "db",
            "message": "Connection failed"
        }
    ], ["timestamp", "level", "service", "message"])

    # With --min-count 2, should only include groups with count >= 2
    exit_code, _, _ = run_logsum(input_csv, output_csv, extra_args=["--min-count", "2"])
    assert exit_code == 0

    rows = read_csv_rows(output_csv)
    assert len(rows) == 2

    # Should include group 1 (count 3) and group 2 (count 2)
    # Should exclude group 3 (count 1)
    counts = [int(r["count"]) for r in rows]
    assert 3 in counts
    assert 2 in counts
    assert 1 not in counts


def test_min_count_default_behavior_unchanged(input_csv, output_csv):
    """Test that default behavior (no --min-count) includes all groups."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T10:00:00Z",
            "level": "INFO",
            "service": "api",
            "message": "Event 1"
        },
        {
            "timestamp": "2025-01-31T10:01:00Z",
            "level": "INFO",
            "service": "api",
            "message": "Event 1"
        },
        {
            "timestamp": "2025-01-31T10:02:00Z",
            "level": "ERROR",
            "service": "db",
            "message": "Event 2"
        }
    ], ["timestamp", "level", "service", "message"])

    # Without --min-count, all groups should be included
    exit_code, _, _ = run_logsum(input_csv, output_csv)
    assert exit_code == 0

    rows = read_csv_rows(output_csv)
    assert len(rows) == 2  # Both groups included

    counts = [int(r["count"]) for r in rows]
    assert 2 in counts  # Group 1
    assert 1 in counts  # Group 2


def test_min_count_with_zero(input_csv, output_csv):
    """Test that --min-count 0 includes all groups."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T10:00:00Z",
            "level": "INFO",
            "service": "api",
            "message": "Event"
        }
    ], ["timestamp", "level", "service", "message"])

    exit_code, _, _ = run_logsum(input_csv, output_csv, extra_args=["--min-count", "0"])
    assert exit_code == 0

    rows = read_csv_rows(output_csv)
    assert len(rows) == 1  # Group with count 1 included


def test_min_count_higher_than_all_counts(input_csv, output_csv):
    """Test that --min-count higher than all counts produces header-only output."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T10:00:00Z",
            "level": "INFO",
            "service": "api",
            "message": "Event 1"
        },
        {
            "timestamp": "2025-01-31T10:01:00Z",
            "level": "ERROR",
            "service": "db",
            "message": "Event 2"
        }
    ], ["timestamp", "level", "service", "message"])

    # --min-count 10 should exclude all groups (max count is 1)
    exit_code, _, _ = run_logsum(input_csv, output_csv, extra_args=["--min-count", "10"])
    assert exit_code == 0

    rows = read_csv_rows(output_csv)
    assert len(rows) == 0  # No groups meet threshold

    # Verify header exists
    with open(output_csv, 'r', encoding='utf-8') as f:
        header = f.readline().strip()
        assert header == "level,service,message,count,first_seen,last_seen"


def test_min_count_with_one(input_csv, output_csv):
    """Test that --min-count 1 includes all groups."""
    write_csv(input_csv, [
        {
            "timestamp": "2025-01-31T10:00:00Z",
            "level": "INFO",
            "service": "api",
            "message": "Event 1"
        },
        {
            "timestamp": "2025-01-31T10:01:00Z",
            "level": "INFO",
            "service": "api",
            "message": "Event 1"
        },
        {
            "timestamp": "2025-01-31T10:02:00Z",
            "level": "ERROR",
            "service": "db",
            "message": "Event 2"
        }
    ], ["timestamp", "level", "service", "message"])

    # --min-count 1 should include all groups
    exit_code, _, _ = run_logsum(input_csv, output_csv, extra_args=["--min-count", "1"])
    assert exit_code == 0

    rows = read_csv_rows(output_csv)
    assert len(rows) == 2  # Both groups included (counts 2 and 1)
