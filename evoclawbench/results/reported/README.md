# Reported Result Exports

This directory contains sanitized copies of the result files used for the paper's main result table and subset-audit summaries.

The main result files are named `table2_row_01.json` through `table2_row_10.json`
to keep artifact paths neutral. Each file retains the original result filename in
its `source_file` field for auditability.

Subset audit summaries are under `subset_audits/`; they are sanitized copies of
the corresponding subset experiment summary outputs.

Sanitization keeps aggregate metrics, result counts, per-task grades, per-task usage, timeout flags, status fields, and skill mutation flags. It removes raw transcripts, stdout/stderr, local workspace paths, local environment warnings, and detailed generated-skill contents.

Run:

```bash
python print_table2.py
```

The command prints the Table 2 values from the sanitized JSON files.
