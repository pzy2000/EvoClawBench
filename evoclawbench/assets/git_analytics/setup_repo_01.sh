#!/usr/bin/env bash
# Setup script for repo_01: WebApp frontend project
# Expected: 15 commits, 3 contributors, main files: src/app.js, src/components/Header.js, src/utils/api.js
set -e
REPO_DIR="${1:-/tmp/evoclaw_repo_01}"
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"
git init
git config user.email "alice@example.com"
git config user.name "Alice Chen"

# Commit 1
mkdir -p src/components src/utils
echo "// App entry point" > src/app.js
git add . && GIT_AUTHOR_DATE="2024-01-10T09:00:00" GIT_COMMITTER_DATE="2024-01-10T09:00:00" git commit -m "Initial project setup"

# Commit 2
echo "// Header component" > src/components/Header.js
git add . && GIT_AUTHOR_DATE="2024-01-12T10:30:00" GIT_COMMITTER_DATE="2024-01-12T10:30:00" git commit -m "Add Header component"

# Commit 3
echo "// API utilities" > src/utils/api.js
git add . && GIT_AUTHOR_DATE="2024-01-15T14:00:00" GIT_COMMITTER_DATE="2024-01-15T14:00:00" git commit -m "Add API utility functions"

# Commit 4 - Bob
git config user.email "bob@example.com"
git config user.name "Bob Martinez"
echo "// Footer component" > src/components/Footer.js
git add . && GIT_AUTHOR_DATE="2024-01-18T11:00:00" GIT_COMMITTER_DATE="2024-01-18T11:00:00" git commit -m "Add Footer component"

# Commit 5
echo "const routes = [];" > src/routes.js
git add . && GIT_AUTHOR_DATE="2024-01-20T16:00:00" GIT_COMMITTER_DATE="2024-01-20T16:00:00" git commit -m "Add routing configuration"

# Commit 6
echo "// Updated API" >> src/utils/api.js
git add . && GIT_AUTHOR_DATE="2024-01-25T09:30:00" GIT_COMMITTER_DATE="2024-01-25T09:30:00" git commit -m "Refactor API error handling"

# Commit 7 - Carol
git config user.email "carol@example.com"
git config user.name "Carol Kim"
echo "// Auth module" > src/auth.js
git add . && GIT_AUTHOR_DATE="2024-02-01T10:00:00" GIT_COMMITTER_DATE="2024-02-01T10:00:00" git commit -m "Add authentication module"

# Commit 8
echo "// Updated Header" >> src/components/Header.js
git add . && GIT_AUTHOR_DATE="2024-02-05T14:30:00" GIT_COMMITTER_DATE="2024-02-05T14:30:00" git commit -m "Add navigation to Header"

# Commit 9 - Alice
git config user.email "alice@example.com"
git config user.name "Alice Chen"
echo "// App updated" >> src/app.js
git add . && GIT_AUTHOR_DATE="2024-02-08T09:00:00" GIT_COMMITTER_DATE="2024-02-08T09:00:00" git commit -m "Integrate auth into app"

# Commit 10
echo "// State management" > src/store.js
git add . && GIT_AUTHOR_DATE="2024-02-12T11:00:00" GIT_COMMITTER_DATE="2024-02-12T11:00:00" git commit -m "Add state management"

# Commit 11 - Bob
git config user.email "bob@example.com"
git config user.name "Bob Martinez"
echo "// Dashboard" > src/components/Dashboard.js
git add . && GIT_AUTHOR_DATE="2024-02-15T15:00:00" GIT_COMMITTER_DATE="2024-02-15T15:00:00" git commit -m "Add Dashboard component"

# Commit 12
echo "// Updated routes" >> src/routes.js
git add . && GIT_AUTHOR_DATE="2024-02-20T10:00:00" GIT_COMMITTER_DATE="2024-02-20T10:00:00" git commit -m "Add dashboard route"

# Commit 13 - Carol
git config user.email "carol@example.com"
git config user.name "Carol Kim"
echo "// Search component" > src/components/Search.js
git add . && GIT_AUTHOR_DATE="2024-02-25T14:00:00" GIT_COMMITTER_DATE="2024-02-25T14:00:00" git commit -m "Add Search component"

# Commit 14 - Alice
git config user.email "alice@example.com"
git config user.name "Alice Chen"
echo "// Final app updates" >> src/app.js
git add . && GIT_AUTHOR_DATE="2024-03-01T09:00:00" GIT_COMMITTER_DATE="2024-03-01T09:00:00" git commit -m "Performance improvements"

# Commit 15
echo "v1.0.0" > VERSION
git add . && GIT_AUTHOR_DATE="2024-03-05T16:00:00" GIT_COMMITTER_DATE="2024-03-05T16:00:00" git commit -m "Release v1.0.0"

echo "repo_01 setup complete: $(git log --oneline | wc -l) commits"
