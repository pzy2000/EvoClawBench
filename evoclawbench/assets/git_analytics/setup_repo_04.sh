#!/usr/bin/env bash
# Setup script for repo_04: Mobile app project
# Expected: 10 commits, 2 contributors, main files: lib/main.dart, lib/screens/home.dart
set -e
REPO_DIR="${1:-/tmp/evoclaw_repo_04}"
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"
git init
git config user.email "jack@example.com"
git config user.name "Jack Wilson"

mkdir -p lib/screens lib/widgets lib/services
# Commit 1
echo "# Flutter Mobile App" > README.md
git add . && GIT_AUTHOR_DATE="2024-01-15T09:00:00" GIT_COMMITTER_DATE="2024-01-15T09:00:00" git commit -m "Initialize Flutter project"

# Commit 2
printf "// Main entry\nvoid main() {}\n" > lib/main.dart
git add . && GIT_AUTHOR_DATE="2024-01-18T10:00:00" GIT_COMMITTER_DATE="2024-01-18T10:00:00" git commit -m "Add main entry point"

# Commit 3
printf "// Home screen\nclass HomeScreen {}\n" > lib/screens/home.dart
git add . && GIT_AUTHOR_DATE="2024-01-22T14:00:00" GIT_COMMITTER_DATE="2024-01-22T14:00:00" git commit -m "Add Home screen"

# Commit 4 - Kate
git config user.email "kate@example.com"
git config user.name "Kate Nguyen"
printf "// Profile screen\nclass ProfileScreen {}\n" > lib/screens/profile.dart
git add . && GIT_AUTHOR_DATE="2024-01-26T09:00:00" GIT_COMMITTER_DATE="2024-01-26T09:00:00" git commit -m "Add Profile screen"

# Commit 5
printf "// API service\nclass ApiService {}\n" > lib/services/api.dart
git add . && GIT_AUTHOR_DATE="2024-01-30T11:00:00" GIT_COMMITTER_DATE="2024-01-30T11:00:00" git commit -m "Add API service layer"

# Commit 6 - Jack
git config user.email "jack@example.com"
git config user.name "Jack Wilson"
printf "// Button widget\nclass CustomButton {}\n" > lib/widgets/button.dart
git add . && GIT_AUTHOR_DATE="2024-02-03T14:00:00" GIT_COMMITTER_DATE="2024-02-03T14:00:00" git commit -m "Add custom Button widget"

# Commit 7 - Kate
git config user.email "kate@example.com"
git config user.name "Kate Nguyen"
echo "// Updated home" >> lib/screens/home.dart
git add . && GIT_AUTHOR_DATE="2024-02-08T10:00:00" GIT_COMMITTER_DATE="2024-02-08T10:00:00" git commit -m "Add feed to Home screen"

# Commit 8 - Jack
git config user.email "jack@example.com"
git config user.name "Jack Wilson"
echo "// Updated main" >> lib/main.dart
git add . && GIT_AUTHOR_DATE="2024-02-12T09:00:00" GIT_COMMITTER_DATE="2024-02-12T09:00:00" git commit -m "Add push notifications setup"

# Commit 9 - Kate
git config user.email "kate@example.com"
git config user.name "Kate Nguyen"
printf "// Settings screen\nclass SettingsScreen {}\n" > lib/screens/settings.dart
git add . && GIT_AUTHOR_DATE="2024-02-18T14:00:00" GIT_COMMITTER_DATE="2024-02-18T14:00:00" git commit -m "Add Settings screen"

# Commit 10 - Jack
git config user.email "jack@example.com"
git config user.name "Jack Wilson"
echo "1.0.0+1" > VERSION
git add . && GIT_AUTHOR_DATE="2024-02-24T16:00:00" GIT_COMMITTER_DATE="2024-02-24T16:00:00" git commit -m "Release v1.0.0"

echo "repo_04 setup complete: $(git log --oneline | wc -l) commits"
