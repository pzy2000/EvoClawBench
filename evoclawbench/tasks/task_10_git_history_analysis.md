---
id: task_10_git_history_analysis
name: Git Repository History Analysis
category: data_analysis
grading_type: automated
timeout_seconds: 900
sub_problems: 5
skill_category: git_analysis
workspace_files:
  - assets/git_analytics/setup_repo_01.sh
  - assets/git_analytics/setup_repo_02.sh
  - assets/git_analytics/setup_repo_03.sh
  - assets/git_analytics/setup_repo_04.sh
  - assets/git_analytics/setup_repo_05.sh
---

# Git Repository History Analysis

## Prompt

You are given 5 bash setup scripts in `assets/git_analytics/`. Each script creates a git repository with a specific commit history when executed.

For each repository:
1. Run the setup script to create the git repository (pass a temp directory as argument, e.g., `bash assets/git_analytics/setup_repo_01.sh /tmp/repo_01`)
2. Analyze the git log and repository structure
3. Output a JSON analysis file to `outputs/repo_N_analysis.json`

Each output JSON must contain:
```json
{
  "repo_name": "repo_01",
  "commit_count": 15,
  "contributors": [
    {"name": "Alice Chen", "email": "alice@example.com", "commit_count": 7},
    ...
  ],
  "date_range": {
    "first_commit": "2024-01-10",
    "last_commit": "2024-03-05"
  },
  "file_hotspots": [
    {"file": "src/app.js", "change_count": 3},
    ...
  ],
  "branches": ["main"],
  "changelog": [
    "Release v1.0.0",
    "Performance improvements",
    ...
  ]
}
```

Requirements:
- `commit_count` must be the exact total number of commits
- `contributors` must list all unique authors with their commit counts
- `date_range` must use ISO 8601 date format (YYYY-MM-DD)
- `file_hotspots` should list the top 5 most frequently changed files
- `changelog` should contain the last 5 commit messages (newest first)

## Expected Behavior

The agent should:
1. Execute each setup script to create the git repositories
2. Use git commands (`git log`, `git shortlog`, `git diff-tree`, etc.) to extract history
3. Parse and structure the data into the required JSON format
4. Ideally create a reusable skill for git repository analysis

## Sub-Problems

### Sub-Problem 1: WebApp Project (repo_01)
- Setup: `bash assets/git_analytics/setup_repo_01.sh /tmp/repo_01`
- Expected: 15 commits, 3 contributors (Alice Chen, Bob Martinez, Carol Kim)
- Output: `outputs/repo_01_analysis.json`

### Sub-Problem 2: REST API Service (repo_02)
- Setup: `bash assets/git_analytics/setup_repo_02.sh /tmp/repo_02`
- Expected: 12 commits, 2 contributors (Diana Patel, Evan Torres)
- Output: `outputs/repo_02_analysis.json`

### Sub-Problem 3: Data Pipeline (repo_03)
- Setup: `bash assets/git_analytics/setup_repo_03.sh /tmp/repo_03`
- Expected: 18 commits, 4 contributors (Frank Liu, Grace Okonkwo, Henry Nakamura, Iris Petrov)
- Output: `outputs/repo_03_analysis.json`

### Sub-Problem 4: Mobile App (repo_04)
- Setup: `bash assets/git_analytics/setup_repo_04.sh /tmp/repo_04`
- Expected: 10 commits, 2 contributors (Jack Wilson, Kate Nguyen)
- Output: `outputs/repo_04_analysis.json`

### Sub-Problem 5: ML Training Project (repo_05)
- Setup: `bash assets/git_analytics/setup_repo_05.sh /tmp/repo_05`
- Expected: 14 commits, 3 contributors (Leo Zhang, Maya Osei, Noah Fischer)
- Output: `outputs/repo_05_analysis.json`

## Grading Criteria

- [ ] Output JSON files exist for all 5 repositories
- [ ] `commit_count` matches expected value exactly
- [ ] All expected contributors appear in the contributors list
- [ ] `date_range` is in ISO 8601 format (YYYY-MM-DD)
- [ ] `file_hotspots` is a non-empty list
- [ ] `changelog` contains recent commit messages

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import json
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    REPOS = [
        {
            "name": "repo_01",
            "commit_count": 15,
            "contributors": ["Alice Chen", "Bob Martinez", "Carol Kim"],
            "first_date": "2024-01-10",
            "last_date": "2024-03-05",
        },
        {
            "name": "repo_02",
            "commit_count": 12,
            "contributors": ["Diana Patel", "Evan Torres"],
            "first_date": "2024-01-08",
            "last_date": "2024-02-28",
        },
        {
            "name": "repo_03",
            "commit_count": 18,
            "contributors": ["Frank Liu", "Grace Okonkwo", "Henry Nakamura", "Iris Petrov"],
            "first_date": "2024-01-05",
            "last_date": "2024-03-08",
        },
        {
            "name": "repo_04",
            "commit_count": 10,
            "contributors": ["Jack Wilson", "Kate Nguyen"],
            "first_date": "2024-01-15",
            "last_date": "2024-02-24",
        },
        {
            "name": "repo_05",
            "commit_count": 14,
            "contributors": ["Leo Zhang", "Maya Osei", "Noah Fischer"],
            "first_date": "2024-01-03",
            "last_date": "2024-02-25",
        },
    ]

    iso_date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    for idx, repo_info in enumerate(REPOS, start=1):
        prefix = f"sub_{idx}"
        repo_name = repo_info["name"]
        out_path = workspace / "outputs" / f"{repo_name}_analysis.json"

        if not out_path.exists():
            for key in ("exists", "valid_json", "commit_count", "contributors", "date_format", "hotspots"):
                scores[f"{prefix}_{key}"] = 0.0
            continue

        scores[f"{prefix}_exists"] = 1.0

        try:
            with open(out_path) as f:
                data = json.load(f)
            scores[f"{prefix}_valid_json"] = 1.0
        except Exception:
            for key in ("valid_json", "commit_count", "contributors", "date_format", "hotspots"):
                scores[f"{prefix}_{key}"] = 0.0
            continue

        # Check commit_count
        reported_count = data.get("commit_count", 0)
        scores[f"{prefix}_commit_count"] = 1.0 if reported_count == repo_info["commit_count"] else 0.0

        # Check contributors: all expected names must appear
        raw_contributors = data.get("contributors", [])
        if isinstance(raw_contributors, list):
            contributor_names = []
            for c in raw_contributors:
                if isinstance(c, dict):
                    contributor_names.append(c.get("name", ""))
                elif isinstance(c, str):
                    contributor_names.append(c)
            found = sum(
                1 for expected in repo_info["contributors"]
                if any(expected.lower() in n.lower() for n in contributor_names)
            )
            scores[f"{prefix}_contributors"] = round(found / len(repo_info["contributors"]), 2)
        else:
            scores[f"{prefix}_contributors"] = 0.0

        # Check date_range format
        date_range = data.get("date_range", {})
        if isinstance(date_range, dict):
            first = date_range.get("first_commit", "")
            last = date_range.get("last_commit", "")
            date_ok = bool(iso_date_re.match(str(first))) and bool(iso_date_re.match(str(last)))
        else:
            date_ok = False
        scores[f"{prefix}_date_format"] = 1.0 if date_ok else 0.0

        # Check file_hotspots is non-empty list
        hotspots = data.get("file_hotspots", [])
        scores[f"{prefix}_hotspots"] = 1.0 if isinstance(hotspots, list) and len(hotspots) > 0 else 0.0

    return scores
```
