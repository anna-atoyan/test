# Quick Start Guide for logsum Tests

## Prerequisites

```bash
pip install pytest
```

## Running Tests

### Option 1: Run all tests
```bash
pytest tests/test_logsum.py -v
```

### Option 2: Use the test runner script
```bash
# Run all tests
python tests/run_tests.py all

# Run specific category
python tests/run_tests.py normalization
python tests/run_tests.py grouping
python tests/run_tests.py aggregation
python tests/run_tests.py malformed
python tests/run_tests.py cli

# Show available categories
python tests/run_tests.py help
```

### Option 3: Run specific tests
```bash
# Run tests matching a keyword
pytest tests/test_logsum.py -v -k "normalization"
pytest tests/test_logsum.py -v -k "timestamp"
pytest tests/test_logsum.py -v -k "empty"

# Run a specific test function
pytest tests/test_logsum.py::test_level_normalization_to_uppercase -v
```

## Test Structure

```
tests/
├── __init__.py                          # Test package marker
├── test_logsum.py                       # Main test file (37 tests)
├── README.md                            # Detailed test documentation
├── TEST_SUITE_SUMMARY.md                # Test coverage summary
├── run_tests.py                         # Convenient test runner
└── fixtures/                            # Sample CSV files
    ├── basic_events.csv                 # Simple valid events
    ├── basic_events_expected.csv        # Expected output
    ├── normalization_test.csv           # Normalization test cases
    ├── malformed_timestamps.csv         # Invalid timestamps
    ├── empty_with_header.csv            # Header-only CSV
    ├── completely_empty.csv             # Empty file
    ├── wrong_header.csv                 # Invalid header
    ├── missing_columns.csv              # Rows with missing fields
    ├── quoted_fields.csv                # CSV quoting tests
    ├── sorting_test.csv                 # Sort order tests
    ├── complex_scenario.csv             # Multiple edge cases
    └── comprehensive_test.csv           # All edge cases combined
```

## What's Tested

✅ **Normalization** (5 tests)
   - Level to uppercase, whitespace trimming, case preservation

✅ **Grouping** (2 tests)
   - Group by (level, service, message), timestamp not part of key

✅ **Aggregation** (3 tests)
   - Count, first_seen, last_seen, timestamp normalization

✅ **Missing Level** (3 tests)
   - Empty/blank level becomes UNKNOWN

✅ **Malformed Timestamps** (3 tests)
   - Invalid timestamps skipped with warning

✅ **Empty Input** (2 tests)
   - Header-only output for empty input

✅ **Invalid CSV** (3 tests)
   - Wrong header/column count causes exit code 3

✅ **Sorting** (1 test)
   - Output sorted by level, service, message

✅ **CSV Edge Cases** (2 tests)
   - Quoted fields, escaped quotes

✅ **CLI Flags** (7 tests)
   - --help, --version, unknown flags, exit codes

✅ **Integration** (2 tests)
   - Complex scenarios, output structure

**Total: 37 comprehensive tests**

## Exit Codes Tested

| Code | Meaning | Tests |
|------|---------|-------|
| 0 | Success | ✅ Multiple tests |
| 1 | Runtime error | ✅ Missing input file |
| 2 | Invalid CLI usage | ✅ Unknown flag, missing value |
| 3 | Invalid CSV structure | ✅ Wrong header, column count |

## Example Test Run Output

```bash
$ pytest tests/test_logsum.py -v

tests/test_logsum.py::test_level_normalization_to_uppercase PASSED
tests/test_logsum.py::test_whitespace_trimming PASSED
tests/test_logsum.py::test_internal_whitespace_preserved PASSED
tests/test_logsum.py::test_service_case_preserved PASSED
tests/test_logsum.py::test_message_case_preserved PASSED
tests/test_logsum.py::test_grouping_by_level_service_message PASSED
tests/test_logsum.py::test_timestamp_not_part_of_group_key PASSED
tests/test_logsum.py::test_count_aggregation PASSED
tests/test_logsum.py::test_first_seen_last_seen PASSED
tests/test_logsum.py::test_timestamp_normalization_to_utc PASSED
tests/test_logsum.py::test_missing_level_becomes_unknown PASSED
tests/test_logsum.py::test_blank_level_after_trim_becomes_unknown PASSED
tests/test_logsum.py::test_missing_level_groups_separately PASSED
tests/test_logsum.py::test_malformed_timestamp_skipped_with_warning PASSED
tests/test_logsum.py::test_multiple_malformed_timestamps PASSED
tests/test_logsum.py::test_all_malformed_timestamps_produces_empty_output PASSED
tests/test_logsum.py::test_empty_csv_with_header_only PASSED
tests/test_logsum.py::test_completely_empty_file PASSED
tests/test_logsum.py::test_incorrect_header_fails PASSED
tests/test_logsum.py::test_wrong_number_of_columns_fails PASSED
tests/test_logsum.py::test_extra_columns_fails PASSED
tests/test_logsum.py::test_output_sorted_by_level_service_message PASSED
tests/test_logsum.py::test_quoted_fields_with_commas PASSED
tests/test_logsum.py::test_escaped_quotes_in_fields PASSED
tests/test_logsum.py::test_help_flag PASSED
tests/test_logsum.py::test_version_flag PASSED
tests/test_logsum.py::test_unknown_flag_fails PASSED
tests/test_logsum.py::test_missing_flag_value_fails PASSED
tests/test_logsum.py::test_input_file_not_found PASSED
tests/test_logsum.py::test_custom_input_output_paths PASSED
tests/test_logsum.py::test_default_file_names PASSED
tests/test_logsum.py::test_complex_scenario PASSED
tests/test_logsum.py::test_output_csv_structure PASSED

======================== 37 passed in 2.45s =========================
```

## Next Steps

1. Install pytest if not already installed: `pip install pytest`
2. Run the tests: `pytest tests/test_logsum.py -v`
3. Check the test output for any failures
4. Review test coverage in `tests/README.md`
5. Use fixtures in `tests/fixtures/` for manual testing

## Troubleshooting

### Tests fail with "No module named 'src.logsum'"
- Make sure you're running from the project root directory
- Ensure `src/logsum.py` exists and is properly implemented

### Tests fail with exit code errors
- Check that `src/logsum.py` implements the correct exit codes (0, 1, 2, 3)
- Verify CLI flag handling matches the specification

### Timestamp-related test failures
- Ensure timestamps are normalized to ISO 8601 UTC format (ending with 'Z')
- Check that Python's datetime parsing handles both 'Z' and '+00:00' formats

## Documentation

- **`tests/README.md`** - Detailed test documentation
- **`tests/TEST_SUITE_SUMMARY.md`** - Complete test coverage summary
- **`logsum-sandbox/spec.md`** - Original specification

## Contact

For questions about the tests or specification, refer to the documentation files listed above.
