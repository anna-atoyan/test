# Tests for logsum CLI

This directory contains comprehensive tests for the `logsum` CLI tool, covering all rules and edge cases specified in `logsum-sandbox/spec.md`.

## Test Structure

### Main Test File: `test_logsum.py`

The test suite is organized into the following categories:

#### 1. Normalization Tests
- `test_level_normalization_to_uppercase` - Verifies level is converted to uppercase
- `test_whitespace_trimming` - Verifies leading/trailing whitespace is removed
- `test_internal_whitespace_preserved` - Verifies internal whitespace in messages is kept
- `test_service_case_preserved` - Verifies service name case is preserved
- `test_message_case_preserved` - Verifies message case is preserved

#### 2. Grouping Tests
- `test_grouping_by_level_service_message` - Verifies grouping by (level, service, message) tuple
- `test_timestamp_not_part_of_group_key` - Verifies timestamp doesn't affect grouping

#### 3. Aggregation Tests
- `test_count_aggregation` - Verifies event count per group
- `test_first_seen_last_seen` - Verifies earliest and latest timestamps
- `test_timestamp_normalization_to_utc` - Verifies timestamps are normalized to UTC format

#### 4. Missing Level Tests
- `test_missing_level_becomes_unknown` - Verifies empty level becomes UNKNOWN
- `test_blank_level_after_trim_becomes_unknown` - Verifies blank level becomes UNKNOWN
- `test_missing_level_groups_separately` - Verifies UNKNOWN forms separate groups

#### 5. Malformed Timestamp Tests
- `test_malformed_timestamp_skipped_with_warning` - Verifies bad timestamps are skipped
- `test_multiple_malformed_timestamps` - Verifies multiple bad timestamps handling
- `test_all_malformed_timestamps_produces_empty_output` - Verifies all bad timestamps produce empty output

#### 6. Empty Input Tests
- `test_empty_csv_with_header_only` - Verifies header-only input produces header-only output
- `test_completely_empty_file` - Verifies empty file produces header-only output

#### 7. Invalid CSV Structure Tests
- `test_incorrect_header_fails` - Verifies wrong header causes exit code 3
- `test_wrong_number_of_columns_fails` - Verifies missing columns cause exit code 3
- `test_extra_columns_fails` - Verifies extra columns cause exit code 3

#### 8. Sorting Tests
- `test_output_sorted_by_level_service_message` - Verifies output is sorted correctly

#### 9. CSV Edge Cases
- `test_quoted_fields_with_commas` - Verifies comma handling in quoted fields
- `test_escaped_quotes_in_fields` - Verifies escaped quote handling

#### 10. CLI Flag Tests
- `test_help_flag` - Verifies --help flag behavior
- `test_version_flag` - Verifies --version flag behavior
- `test_unknown_flag_fails` - Verifies unknown flag causes exit code 2
- `test_missing_flag_value_fails` - Verifies missing flag value causes exit code 2
- `test_input_file_not_found` - Verifies missing input file causes exit code 1
- `test_custom_input_output_paths` - Verifies custom paths work
- `test_default_file_names` - Verifies default file names are used

#### 11. Integration Tests
- `test_complex_scenario` - Combines multiple edge cases
- `test_output_csv_structure` - Verifies output CSV format

## Test Fixtures

The `fixtures/` directory contains sample CSV files for testing:

- `basic_events.csv` - Simple valid events for basic testing
- `normalization_test.csv` - Events with whitespace and case variations
- `malformed_timestamps.csv` - Mix of valid and invalid timestamps
- `empty_with_header.csv` - CSV with only header row
- `completely_empty.csv` - Completely empty file
- `wrong_header.csv` - CSV with incorrect column names
- `missing_columns.csv` - CSV with rows having wrong number of columns
- `quoted_fields.csv` - CSV with quoted fields containing commas and quotes
- `sorting_test.csv` - Events for testing sort order
- `complex_scenario.csv` - Complex mix of edge cases

## Running Tests

### Run all tests:
```bash
pytest tests/test_logsum.py -v
```

### Run specific test:
```bash
pytest tests/test_logsum.py::test_level_normalization_to_uppercase -v
```

### Run tests by category (using keyword matching):
```bash
pytest tests/test_logsum.py -v -k "normalization"
pytest tests/test_logsum.py -v -k "grouping"
pytest tests/test_logsum.py -v -k "malformed"
```

## Exit Code Coverage

The tests verify all specified exit codes:

- **Exit Code 0**: Success cases (valid processing, --help, --version)
- **Exit Code 1**: Runtime errors (missing input file, write failures)
- **Exit Code 2**: Invalid CLI usage (unknown flags, missing flag values)
- **Exit Code 3**: Invalid CSV structure (wrong header, wrong column count)

## Coverage Requirements

These tests ensure 100% coverage of the specification including:

✅ All normalization rules (trim, uppercase, case preservation)  
✅ Exact grouping by (level, service, message)  
✅ Aggregation (count, first_seen, last_seen)  
✅ Missing level → UNKNOWN  
✅ Malformed timestamp → skip with warning  
✅ Empty input → header-only output  
✅ Invalid CSV → exit code 3  
✅ CLI flags and exit codes  
✅ Timestamp normalization to ISO 8601 UTC  
✅ CSV quoting and escaping  
✅ Deterministic sorting  

## Notes

- Tests use temporary directories to avoid file pollution
- All tests are independent and can run in any order
- The test suite does not read `src/logsum.py` directly, only tests the CLI behavior
- Each test has descriptive names and docstrings explaining what is being tested
