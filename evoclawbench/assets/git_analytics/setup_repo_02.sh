#!/usr/bin/env bash
# Setup script for repo_02: REST API service project
# Expected: 12 commits, 2 contributors, main files: api/routes.py, api/models.py, api/auth.py
set -e
REPO_DIR="${1:-/tmp/evoclaw_repo_02}"
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"
git init
git config user.email "diana@example.com"
git config user.name "Diana Patel"

mkdir -p api tests
# Commit 1
echo "# API Service" > README.md
git add . && GIT_AUTHOR_DATE="2024-01-08T09:00:00" GIT_COMMITTER_DATE="2024-01-08T09:00:00" git commit -m "Initialize API service project"

# Commit 2
printf "from flask import Flask\napp = Flask(__name__)\n" > api/__init__.py
git add . && GIT_AUTHOR_DATE="2024-01-10T11:00:00" GIT_COMMITTER_DATE="2024-01-10T11:00:00" git commit -m "Add Flask application factory"

# Commit 3
printf "# User model\nclass User:\n    pass\n" > api/models.py
git add . && GIT_AUTHOR_DATE="2024-01-14T09:30:00" GIT_COMMITTER_DATE="2024-01-14T09:30:00" git commit -m "Add User model"

# Commit 4
printf "# Routes\n@app.route('/')\ndef index(): pass\n" > api/routes.py
git add . && GIT_AUTHOR_DATE="2024-01-17T14:00:00" GIT_COMMITTER_DATE="2024-01-17T14:00:00" git commit -m "Add API routes"

# Commit 5 - Evan
git config user.email "evan@example.com"
git config user.name "Evan Torres"
printf "# Auth module\ndef authenticate(): pass\n" > api/auth.py
git add . && GIT_AUTHOR_DATE="2024-01-22T10:00:00" GIT_COMMITTER_DATE="2024-01-22T10:00:00" git commit -m "Add JWT authentication"

# Commit 6
printf "# Tests\nimport pytest\n" > tests/test_api.py
git add . && GIT_AUTHOR_DATE="2024-01-26T15:00:00" GIT_COMMITTER_DATE="2024-01-26T15:00:00" git commit -m "Add initial test suite"

# Commit 7 - Diana
git config user.email "diana@example.com"
git config user.name "Diana Patel"
echo "# Updated models" >> api/models.py
git add . && GIT_AUTHOR_DATE="2024-02-02T09:00:00" GIT_COMMITTER_DATE="2024-02-02T09:00:00" git commit -m "Add Product model"

# Commit 8
echo "# Updated routes" >> api/routes.py
git add . && GIT_AUTHOR_DATE="2024-02-07T11:30:00" GIT_COMMITTER_DATE="2024-02-07T11:30:00" git commit -m "Add CRUD endpoints for products"

# Commit 9 - Evan
git config user.email "evan@example.com"
git config user.name "Evan Torres"
echo "# Rate limiting" >> api/auth.py
git add . && GIT_AUTHOR_DATE="2024-02-12T14:00:00" GIT_COMMITTER_DATE="2024-02-12T14:00:00" git commit -m "Add rate limiting middleware"

# Commit 10 - Diana
git config user.email "diana@example.com"
git config user.name "Diana Patel"
echo "# More tests" >> tests/test_api.py
git add . && GIT_AUTHOR_DATE="2024-02-18T10:00:00" GIT_COMMITTER_DATE="2024-02-18T10:00:00" git commit -m "Add integration tests"

# Commit 11
printf "[databases]\nurl = sqlite:///db.sqlite3\n" > config.ini
git add . && GIT_AUTHOR_DATE="2024-02-22T09:00:00" GIT_COMMITTER_DATE="2024-02-22T09:00:00" git commit -m "Add configuration file"

# Commit 12 - Evan
git config user.email "evan@example.com"
git config user.name "Evan Torres"
echo "v1.2.0" > VERSION
git add . && GIT_AUTHOR_DATE="2024-02-28T16:00:00" GIT_COMMITTER_DATE="2024-02-28T16:00:00" git commit -m "Release v1.2.0"

echo "repo_02 setup complete: $(git log --oneline | wc -l) commits"
