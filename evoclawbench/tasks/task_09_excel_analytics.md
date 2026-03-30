---
id: task_09_excel_analytics
name: Excel Analytics Report Generation
category: data_transformation
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: excel_generation
workspace_files:
  - assets/excel_analytics/north_region.csv
  - assets/excel_analytics/south_region.csv
  - assets/excel_analytics/east_region.csv
  - assets/excel_analytics/west_region.csv
  - assets/excel_analytics/central_region.csv
---

# Excel Analytics Report Generation

## Prompt

You are given 5 regional sales CSV files in `assets/excel_analytics/`. Each CSV contains quarterly sales data with columns: `product_id`, `product_name`, `quarter`, `region`, `units_sold`, `unit_price`, `revenue`, `cost`, `profit`.

For each region (north, south, east, west, central), generate a multi-sheet Excel workbook at `outputs/report_<region>.xlsx` (e.g., `outputs/report_north.xlsx`).

Each workbook must contain exactly **3 sheets**:

1. **Raw Data** — A copy of all the source CSV rows as a table (with header row).
2. **Summary** — An aggregated summary table with columns: `Product`, `Total Units`, `Total Revenue`, `Total Cost`, `Total Profit`. Each product (P001–P005) should have one row with totals aggregated across all quarters. Include a totals row at the bottom using SUM formulas.
3. **Quarterly** — A pivot-style table showing revenue by quarter. Columns: `Quarter`, `Q1 Revenue`, `Q2 Revenue`, `Q3 Revenue`, `Q4 Revenue`, `Annual Total`. Each product gets one row, plus a totals row.

Requirements:
- Sheet names must be exactly: `Raw Data`, `Summary`, `Quarterly`
- Use Excel SUM formulas (e.g., `=SUM(B2:B6)`) for the totals rows in Summary and Quarterly sheets
- Numeric values must be stored as numbers (not strings)
- The Summary sheet must have at least 5 data rows (one per product) plus a totals row

## Expected Behavior

The agent should:
1. Read each regional CSV file
2. Install and use `openpyxl` (or equivalent Python library) to generate Excel files
3. Create the required 3-sheet structure with proper formulas
4. Ideally evolve a reusable skill for Excel workbook generation to handle all 5 regions efficiently

## Sub-Problems

### Sub-Problem 1: North Region Report
- Input: `assets/excel_analytics/north_region.csv`
- Expected output: `outputs/report_north.xlsx` with 3 sheets

### Sub-Problem 2: South Region Report
- Input: `assets/excel_analytics/south_region.csv`
- Expected output: `outputs/report_south.xlsx` with 3 sheets

### Sub-Problem 3: East Region Report
- Input: `assets/excel_analytics/east_region.csv`
- Expected output: `outputs/report_east.xlsx` with 3 sheets

### Sub-Problem 4: West Region Report
- Input: `assets/excel_analytics/west_region.csv`
- Expected output: `outputs/report_west.xlsx` with 3 sheets

### Sub-Problem 5: Central Region Report
- Input: `assets/excel_analytics/central_region.csv`
- Expected output: `outputs/report_central.xlsx` with 3 sheets

## Grading Criteria

- [ ] Output .xlsx files exist for all 5 regions
- [ ] Each workbook has exactly 3 sheets named correctly
- [ ] Raw Data sheet contains the expected number of rows (20 data rows + header)
- [ ] Summary sheet has at least 5 product rows plus a totals row
- [ ] Quarterly sheet has at least 5 product rows
- [ ] Numeric values are stored as numbers (not strings)
- [ ] At least one SUM formula present in Summary or Quarterly sheet

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import openpyxl

    scores = {}
    workspace = Path(workspace_path)

    regions = [
        ("north", "report_north.xlsx"),
        ("south", "report_south.xlsx"),
        ("east", "report_east.xlsx"),
        ("west", "report_west.xlsx"),
        ("central", "report_central.xlsx"),
    ]

    REQUIRED_SHEETS = {"Raw Data", "Summary", "Quarterly"}

    for idx, (region, filename) in enumerate(regions, start=1):
        prefix = f"sub_{idx}"
        out_path = workspace / "outputs" / filename

        if not out_path.exists():
            scores[f"{prefix}_exists"] = 0.0
            scores[f"{prefix}_sheets"] = 0.0
            scores[f"{prefix}_raw_rows"] = 0.0
            scores[f"{prefix}_summary_rows"] = 0.0
            scores[f"{prefix}_numeric_values"] = 0.0
            continue

        scores[f"{prefix}_exists"] = 1.0

        try:
            wb = openpyxl.load_workbook(str(out_path), data_only=True)
        except Exception as e:
            try:
                Path("/tmp/grade_task09_error.txt").write_text(
                    f"{prefix}: {type(e).__name__}: {e}\npath={out_path}\n"
                )
            except Exception:
                pass
            scores[f"{prefix}_sheets"] = 0.0
            scores[f"{prefix}_raw_rows"] = 0.0
            scores[f"{prefix}_summary_rows"] = 0.0
            scores[f"{prefix}_numeric_values"] = 0.0
            continue

        sheet_names = set(wb.sheetnames)
        has_all_sheets = REQUIRED_SHEETS.issubset(sheet_names)
        scores[f"{prefix}_sheets"] = 1.0 if has_all_sheets else round(
            len(REQUIRED_SHEETS & sheet_names) / len(REQUIRED_SHEETS), 2
        )

        if "Raw Data" in wb.sheetnames:
            raw_ws = wb["Raw Data"]
            scores[f"{prefix}_raw_rows"] = 1.0 if raw_ws.max_row >= 21 else 0.0
        else:
            scores[f"{prefix}_raw_rows"] = 0.0

        if "Summary" in wb.sheetnames:
            sum_ws = wb["Summary"]
            scores[f"{prefix}_summary_rows"] = 1.0 if sum_ws.max_row >= 6 else 0.0
            numeric_ok = False
            for row in sum_ws.iter_rows(min_row=2, max_row=min(7, sum_ws.max_row)):
                for cell in row:
                    if isinstance(cell.value, (int, float)) and not isinstance(cell.value, bool):
                        numeric_ok = True
                        break
                if numeric_ok:
                    break
            scores[f"{prefix}_numeric_values"] = 1.0 if numeric_ok else 0.0
        else:
            scores[f"{prefix}_summary_rows"] = 0.0
            scores[f"{prefix}_numeric_values"] = 0.0

    return scores
```
