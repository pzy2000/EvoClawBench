---
id: task_04_test_generation
name: Test Generation
category: testing
grading_type: automated
timeout_seconds: 600
sub_problems: 6
skill_category: test_writing
workspace_files:
  - assets/test_generation/string_utils.py
  - assets/test_generation/math_utils.py
  - assets/test_generation/data_utils.py
  - assets/test_generation/date_utils.py
  - assets/test_generation/file_utils.py
  - assets/test_generation/validation_utils.py
---

# Test Generation

Generate comprehensive pytest test suites for 6 Python utility modules. Each module contains 3 functions that need thorough testing with positive cases, negative cases, and edge cases.

---

## Prompt

You have 6 Python utility modules in `assets/test_generation/`. Each module contains 3 functions. Generate a comprehensive pytest test file for each module and save them in the `outputs/` directory.

**Input files:**

1. `string_utils.py` — Functions: `slugify(text)`, `truncate(text, max_len, suffix="...")`, `extract_emails(text)`
2. `math_utils.py` — Functions: `fibonacci(n)`, `is_prime(n)`, `gcd(a, b)`
3. `data_utils.py` — Functions: `flatten_dict(d, prefix, sep)`, `chunk_list(lst, size)`, `deep_merge(dict1, dict2)`
4. `date_utils.py` — Functions: `parse_relative_date(text)`, `business_days_between(start, end)`, `format_duration(seconds)`
5. `file_utils.py` — Functions: `safe_read_json(path, default)`, `find_files(directory, pattern)`, `file_checksum(path, algorithm)`
6. `validation_utils.py` — Functions: `validate_email(email)`, `validate_url(url)`, `validate_phone(phone, country)`

**Output:** For each input file `<name>.py`, produce `outputs/test_<name>.py` with:

- **Import** the module under test and pytest
- **At least 3 test cases per function** (9+ tests per file minimum)
- **Edge cases**: empty strings, zero, negative numbers, None, empty collections, etc.
- **Boundary conditions**: max/min values, off-by-one scenarios
- **Both positive and negative tests**: valid inputs that should succeed AND invalid inputs that should fail or raise exceptions
- Use descriptive test function names (`def test_slugify_with_special_characters():`)

---

## Expected Behavior

1. The agent reads the first module and writes a test file for its 3 functions.
2. It moves to the second module and writes another test file.
3. After 2-3 modules, the agent recognizes the pattern: read function signatures and docstrings -> generate positive tests -> generate negative/edge tests -> ensure pytest structure.
4. The agent creates a reusable skill for test generation that takes a module and produces tests.
5. Remaining test files are generated using the skill.

---

## Sub-Problems

### Sub-Problem 1: String utilities tests (string_utils.py)
- Input: Module with slugify, truncate, extract_emails
- Special handling: Unicode normalization in slugify; suffix handling in truncate; regex-based email extraction
- Expected output: `outputs/test_string_utils.py`

### Sub-Problem 2: Math utilities tests (math_utils.py)
- Input: Module with fibonacci, is_prime, gcd
- Special handling: Negative input handling; large numbers; edge cases like fibonacci(0), is_prime(1), gcd(0,0)
- Expected output: `outputs/test_math_utils.py`

### Sub-Problem 3: Data utilities tests (data_utils.py)
- Input: Module with flatten_dict, chunk_list, deep_merge
- Special handling: Deeply nested dicts; empty inputs; chunk size larger than list; merge conflict resolution
- Expected output: `outputs/test_data_utils.py`

### Sub-Problem 4: Date utilities tests (date_utils.py)
- Input: Module with parse_relative_date, business_days_between, format_duration
- Special handling: Relative date expressions; weekend handling; singular/plural formatting
- Expected output: `outputs/test_date_utils.py`

### Sub-Problem 5: File utilities tests (file_utils.py)
- Input: Module with safe_read_json, find_files, file_checksum
- Special handling: File I/O mocking; missing files; different hash algorithms; permission errors
- Expected output: `outputs/test_file_utils.py`

### Sub-Problem 6: Validation utilities tests (validation_utils.py)
- Input: Module with validate_email, validate_url, validate_phone
- Special handling: Various valid/invalid formats; country-specific phone formats; edge cases like empty strings
- Expected output: `outputs/test_validation_utils.py`

---

## Grading Criteria

- [ ] Each of the 6 test files exists in `outputs/`
- [ ] Each file contains valid Python syntax
- [ ] Each file imports pytest
- [ ] Each file contains test functions (def test_*)
- [ ] Each file has at least 9 test functions (3 per source function)
- [ ] Tests cover both positive and negative cases

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import ast
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    modules = [
        "string_utils",
        "math_utils",
        "data_utils",
        "date_utils",
        "file_utils",
        "validation_utils",
    ]

    min_tests_per_file = 9  # 3 functions x 3 tests each

    for i, module in enumerate(modules, start=1):
        prefix = f"sub_{i}"
        filename = f"test_{module}.py"
        filepath = workspace / "outputs" / filename

        # Check existence
        exists = filepath.is_file()
        scores[f"{prefix}_exists"] = 1.0 if exists else 0.0
        if not exists:
            scores[f"{prefix}_valid_python"] = 0.0
            scores[f"{prefix}_imports_pytest"] = 0.0
            scores[f"{prefix}_has_tests"] = 0.0
            scores[f"{prefix}_min_tests"] = 0.0
            continue

        source = filepath.read_text()

        # Check valid Python
        try:
            tree = ast.parse(source)
            scores[f"{prefix}_valid_python"] = 1.0
        except SyntaxError:
            scores[f"{prefix}_valid_python"] = 0.0
            scores[f"{prefix}_imports_pytest"] = 0.0
            scores[f"{prefix}_has_tests"] = 0.0
            scores[f"{prefix}_min_tests"] = 0.0
            continue

        # Check imports pytest
        has_pytest_import = any(
            (isinstance(node, ast.Import) and any(a.name == "pytest" for a in node.names))
            or (isinstance(node, ast.ImportFrom) and node.module == "pytest")
            for node in ast.walk(tree)
        )
        scores[f"{prefix}_imports_pytest"] = 1.0 if has_pytest_import else 0.0

        # Count test functions
        test_functions = [
            node for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        ]
        num_tests = len(test_functions)

        scores[f"{prefix}_has_tests"] = 1.0 if num_tests > 0 else 0.0
        scores[f"{prefix}_min_tests"] = 1.0 if num_tests >= min_tests_per_file else 0.0

    return scores
```
