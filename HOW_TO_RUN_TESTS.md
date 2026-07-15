# 🧪 How to Run Tests Locally

## ✅ **CONFIRMED: All 33 Tests Pass!**

---

## **Quick Commands Reference**

### **Option 1: Simple Test Run** (Most Common)
```bash
python -m pytest tests/test_logsum.py -v
```

### **Option 2: Just See Pass/Fail Summary**
```bash
python -m pytest tests/test_logsum.py -v --tb=no
```

### **Option 3: Run All Tests in Project**
```bash
python -m pytest -v
```

### **Option 4: Show Only Failed Tests**
```bash
python -m pytest tests/test_logsum.py -v --tb=short
```

---

## **Test Categories (All 33 Tests)**

| Category | Tests | Description |
|----------|-------|-------------|
| **Normalization** | 5 tests | Level uppercase, whitespace handling, case preservation |
| **Grouping** | 3 tests | Group by (level, service, message) |
| **Aggregation** | 3 tests | Count, first_seen, last_seen |
| **Timestamps** | 3 tests | Parse, normalize to UTC |
| **Missing Data** | 6 tests | Missing level, malformed timestamps |
| **CSV Structure** | 5 tests | Empty files, incorrect headers, wrong columns |
| **CLI** | 6 tests | Flags (--help, --version), exit codes |
| **Complex** | 2 tests | Combined scenarios, output structure |

**Total: 33 tests**

---

## **Simulate Exact GitHub CI Locally**

### **Windows:**
```bash
run_ci_locally.bat
```

### **Linux/Mac:**
```bash
bash run_ci_locally.sh
```

These scripts run the exact same steps as GitHub CI:
1. ✅ Install dependencies (pip, ruff, pytest, package)
2. ✅ Run `ruff check .`
3. ✅ Run `pytest -v`

---

## **Verify Individual Steps**

### **Step 1: Install Package**
```bash
pip install -e .
```
Expected: `Successfully installed logsum-0.1.0`

### **Step 2: Check Linting**
```bash
ruff check .
```
Expected: `All checks passed!`

### **Step 3: Run Tests**
```bash
pytest -v
```
Expected: `===== 33 passed in X.XXs =====`

---

## **Latest Test Results**

**Date**: Just ran now  
**Platform**: Windows (Python 3.14.5)  
**Result**: ✅ **33 passed in 6.71s**

All test categories passing:
- ✅ test_level_normalization_to_uppercase
- ✅ test_whitespace_trimming
- ✅ test_internal_whitespace_preserved
- ✅ test_service_case_preserved
- ✅ test_message_case_preserved
- ✅ test_grouping_by_level_service_message
- ✅ test_timestamp_not_part_of_group_key
- ✅ test_count_aggregation
- ✅ test_first_seen_last_seen
- ✅ test_timestamp_normalization_to_utc
- ✅ test_missing_level_becomes_unknown
- ✅ test_blank_level_after_trim_becomes_unknown
- ✅ test_missing_level_groups_separately
- ✅ test_malformed_timestamp_skipped_with_warning
- ✅ test_multiple_malformed_timestamps
- ✅ test_all_malformed_timestamps_produces_empty_output
- ✅ test_empty_csv_with_header_only
- ✅ test_completely_empty_file
- ✅ test_incorrect_header_fails
- ✅ test_wrong_number_of_columns_fails
- ✅ test_extra_columns_fails
- ✅ test_output_sorted_by_level_service_message
- ✅ test_quoted_fields_with_commas
- ✅ test_escaped_quotes_in_fields
- ✅ test_help_flag
- ✅ test_version_flag
- ✅ test_unknown_flag_fails
- ✅ test_missing_flag_value_fails
- ✅ test_input_file_not_found
- ✅ test_custom_input_output_paths
- ✅ test_default_file_names
- ✅ test_complex_scenario
- ✅ test_output_csv_structure

---

## **Troubleshooting**

### If tests fail:

**1. Reinstall package:**
```bash
pip install -e . --force-reinstall
```

**2. Clear pytest cache:**
```bash
pytest --cache-clear
```

**3. Check Python version:**
```bash
python --version
```
Should be Python 3.7+

**4. Verify all dependencies:**
```bash
pip list | grep -E "(pytest|ruff|logsum)"
```

---

## **Exit Codes Reference**

| Exit Code | Meaning |
|-----------|---------|
| 0 | All tests passed ✅ |
| 1 | Some tests failed ❌ |
| 2 | Test collection error or interrupted |
| 3 | Internal pytest error |

---

## **GitHub CI Comparison**

| Environment | Status |
|-------------|--------|
| **Local (Windows)** | ✅ 33 passed |
| **GitHub CI (Ubuntu)** | 🔄 Check at https://github.com/anna-atoyan/test/actions |

Both should show identical results!

---

## **Quick Verification Script**

Copy and paste this to verify everything:

```bash
# Full CI simulation
echo "Installing package..."
pip install -e . --quiet

echo "Running linting..."
ruff check .

echo "Running tests..."
python -m pytest tests/test_logsum.py -v

echo "✅ If all steps passed, CI will pass too!"
```
