#!/usr/bin/env bash
# Setup script for repo_03: Data pipeline project
# Expected: 18 commits, 4 contributors, main files: pipeline/etl.py, pipeline/transform.py, pipeline/load.py
set -e
REPO_DIR="${1:-/tmp/evoclaw_repo_03}"
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"
git init
git config user.email "frank@example.com"
git config user.name "Frank Liu"

mkdir -p pipeline tests config
# Commits 1-4 by Frank
echo "# Data Pipeline" > README.md
git add . && GIT_AUTHOR_DATE="2024-01-05T09:00:00" GIT_COMMITTER_DATE="2024-01-05T09:00:00" git commit -m "Initialize data pipeline project"

printf "# Extract module\ndef extract(): pass\n" > pipeline/extract.py
git add . && GIT_AUTHOR_DATE="2024-01-08T10:00:00" GIT_COMMITTER_DATE="2024-01-08T10:00:00" git commit -m "Add extract module"

printf "# Transform module\ndef transform(): pass\n" > pipeline/transform.py
git add . && GIT_AUTHOR_DATE="2024-01-11T14:00:00" GIT_COMMITTER_DATE="2024-01-11T14:00:00" git commit -m "Add transform module"

printf "# Load module\ndef load(): pass\n" > pipeline/load.py
git add . && GIT_AUTHOR_DATE="2024-01-15T09:00:00" GIT_COMMITTER_DATE="2024-01-15T09:00:00" git commit -m "Add load module"

# Commit 5 - Grace
git config user.email "grace@example.com"
git config user.name "Grace Okonkwo"
printf "# ETL orchestration\nfrom pipeline import extract, transform, load\n" > pipeline/etl.py
git add . && GIT_AUTHOR_DATE="2024-01-18T11:00:00" GIT_COMMITTER_DATE="2024-01-18T11:00:00" git commit -m "Add ETL orchestration"

# Commit 6
echo "# Schema validation" > pipeline/validate.py
git add . && GIT_AUTHOR_DATE="2024-01-22T10:00:00" GIT_COMMITTER_DATE="2024-01-22T10:00:00" git commit -m "Add schema validation"

# Commit 7 - Henry
git config user.email "henry@example.com"
git config user.name "Henry Nakamura"
printf "# Config\nDB_URL = 'postgresql://localhost/pipeline'\n" > config/settings.py
git add . && GIT_AUTHOR_DATE="2024-01-25T14:00:00" GIT_COMMITTER_DATE="2024-01-25T14:00:00" git commit -m "Add configuration management"

# Commit 8
echo "# Transform updated" >> pipeline/transform.py
git add . && GIT_AUTHOR_DATE="2024-01-29T09:00:00" GIT_COMMITTER_DATE="2024-01-29T09:00:00" git commit -m "Add data normalization transforms"

# Commit 9 - Iris
git config user.email "iris@example.com"
git config user.name "Iris Petrov"
printf "import pytest\n# Tests\n" > tests/test_pipeline.py
git add . && GIT_AUTHOR_DATE="2024-02-02T10:00:00" GIT_COMMITTER_DATE="2024-02-02T10:00:00" git commit -m "Add pipeline unit tests"

# Commit 10 - Frank
git config user.email "frank@example.com"
git config user.name "Frank Liu"
echo "# ETL updated" >> pipeline/etl.py
git add . && GIT_AUTHOR_DATE="2024-02-06T11:00:00" GIT_COMMITTER_DATE="2024-02-06T11:00:00" git commit -m "Add error recovery in ETL"

# Commit 11 - Grace
git config user.email "grace@example.com"
git config user.name "Grace Okonkwo"
echo "# Load updated" >> pipeline/load.py
git add . && GIT_AUTHOR_DATE="2024-02-10T14:00:00" GIT_COMMITTER_DATE="2024-02-10T14:00:00" git commit -m "Add batch loading support"

# Commit 12 - Henry
git config user.email "henry@example.com"
git config user.name "Henry Nakamura"
echo "# More tests" >> tests/test_pipeline.py
git add . && GIT_AUTHOR_DATE="2024-02-14T09:00:00" GIT_COMMITTER_DATE="2024-02-14T09:00:00" git commit -m "Add integration tests"

# Commit 13 - Iris
git config user.email "iris@example.com"
git config user.name "Iris Petrov"
echo "# Logging" > pipeline/logger.py
git add . && GIT_AUTHOR_DATE="2024-02-18T10:00:00" GIT_COMMITTER_DATE="2024-02-18T10:00:00" git commit -m "Add structured logging"

# Commit 14 - Frank
git config user.email "frank@example.com"
git config user.name "Frank Liu"
echo "# Transform v2" >> pipeline/transform.py
git add . && GIT_AUTHOR_DATE="2024-02-22T11:00:00" GIT_COMMITTER_DATE="2024-02-22T11:00:00" git commit -m "Add aggregation transforms"

# Commit 15 - Grace
git config user.email "grace@example.com"
git config user.name "Grace Okonkwo"
echo "# ETL monitoring" >> pipeline/etl.py
git add . && GIT_AUTHOR_DATE="2024-02-26T14:00:00" GIT_COMMITTER_DATE="2024-02-26T14:00:00" git commit -m "Add metrics collection"

# Commit 16 - Henry
git config user.email "henry@example.com"
git config user.name "Henry Nakamura"
echo "# Extract v2" >> pipeline/extract.py
git add . && GIT_AUTHOR_DATE="2024-03-01T09:00:00" GIT_COMMITTER_DATE="2024-03-01T09:00:00" git commit -m "Add streaming extraction"

# Commit 17 - Iris
git config user.email "iris@example.com"
git config user.name "Iris Petrov"
echo "# Docs" > CONTRIBUTING.md
git add . && GIT_AUTHOR_DATE="2024-03-05T10:00:00" GIT_COMMITTER_DATE="2024-03-05T10:00:00" git commit -m "Add contributing guidelines"

# Commit 18 - Frank
git config user.email "frank@example.com"
git config user.name "Frank Liu"
echo "v2.0.0" > VERSION
git add . && GIT_AUTHOR_DATE="2024-03-08T16:00:00" GIT_COMMITTER_DATE="2024-03-08T16:00:00" git commit -m "Release v2.0.0"

echo "repo_03 setup complete: $(git log --oneline | wc -l) commits"
