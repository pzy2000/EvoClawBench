#!/usr/bin/env bash
# Setup script for repo_05: ML model training project
# Expected: 14 commits, 3 contributors, main files: train.py, model/network.py, data/preprocess.py
set -e
REPO_DIR="${1:-/tmp/evoclaw_repo_05}"
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"
git init
git config user.email "leo@example.com"
git config user.name "Leo Zhang"

mkdir -p model data notebooks experiments
# Commit 1
echo "# ML Training Project" > README.md
git add . && GIT_AUTHOR_DATE="2024-01-03T09:00:00" GIT_COMMITTER_DATE="2024-01-03T09:00:00" git commit -m "Initialize ML project"

# Commit 2
printf "# Preprocessing\ndef load_data(): pass\n" > data/preprocess.py
git add . && GIT_AUTHOR_DATE="2024-01-07T10:00:00" GIT_COMMITTER_DATE="2024-01-07T10:00:00" git commit -m "Add data preprocessing"

# Commit 3
printf "# Neural network\nclass Network: pass\n" > model/network.py
git add . && GIT_AUTHOR_DATE="2024-01-11T14:00:00" GIT_COMMITTER_DATE="2024-01-11T14:00:00" git commit -m "Add neural network architecture"

# Commit 4 - Maya
git config user.email "maya@example.com"
git config user.name "Maya Osei"
printf "# Training script\ndef train(): pass\n" > train.py
git add . && GIT_AUTHOR_DATE="2024-01-15T09:00:00" GIT_COMMITTER_DATE="2024-01-15T09:00:00" git commit -m "Add training loop"

# Commit 5
printf "# Evaluation\ndef evaluate(): pass\n" > evaluate.py
git add . && GIT_AUTHOR_DATE="2024-01-19T11:00:00" GIT_COMMITTER_DATE="2024-01-19T11:00:00" git commit -m "Add model evaluation script"

# Commit 6 - Noah
git config user.email "noah@example.com"
git config user.name "Noah Fischer"
printf "# Config\nLEARNING_RATE = 0.001\nBATCH_SIZE = 32\n" > config.py
git add . && GIT_AUTHOR_DATE="2024-01-23T10:00:00" GIT_COMMITTER_DATE="2024-01-23T10:00:00" git commit -m "Add hyperparameter configuration"

# Commit 7 - Leo
git config user.email "leo@example.com"
git config user.name "Leo Zhang"
echo "# Updated preprocessing" >> data/preprocess.py
git add . && GIT_AUTHOR_DATE="2024-01-27T14:00:00" GIT_COMMITTER_DATE="2024-01-27T14:00:00" git commit -m "Add data augmentation"

# Commit 8 - Maya
git config user.email "maya@example.com"
git config user.name "Maya Osei"
echo "# Updated training" >> train.py
git add . && GIT_AUTHOR_DATE="2024-01-31T09:00:00" GIT_COMMITTER_DATE="2024-01-31T09:00:00" git commit -m "Add learning rate scheduler"

# Commit 9 - Noah
git config user.email "noah@example.com"
git config user.name "Noah Fischer"
echo "# Updated network" >> model/network.py
git add . && GIT_AUTHOR_DATE="2024-02-04T10:00:00" GIT_COMMITTER_DATE="2024-02-04T10:00:00" git commit -m "Add attention mechanism"

# Commit 10 - Leo
git config user.email "leo@example.com"
git config user.name "Leo Zhang"
printf "# Inference\ndef predict(): pass\n" > inference.py
git add . && GIT_AUTHOR_DATE="2024-02-08T14:00:00" GIT_COMMITTER_DATE="2024-02-08T14:00:00" git commit -m "Add inference pipeline"

# Commit 11 - Maya
git config user.email "maya@example.com"
git config user.name "Maya Osei"
echo "# More network layers" >> model/network.py
git add . && GIT_AUTHOR_DATE="2024-02-12T09:00:00" GIT_COMMITTER_DATE="2024-02-12T09:00:00" git commit -m "Add residual connections"

# Commit 12 - Noah
git config user.email "noah@example.com"
git config user.name "Noah Fischer"
echo "# Checkpoint saving" >> train.py
git add . && GIT_AUTHOR_DATE="2024-02-16T11:00:00" GIT_COMMITTER_DATE="2024-02-16T11:00:00" git commit -m "Add model checkpointing"

# Commit 13 - Leo
git config user.email "leo@example.com"
git config user.name "Leo Zhang"
echo "# Experiment tracking" > experiments/tracker.py
git add . && GIT_AUTHOR_DATE="2024-02-20T14:00:00" GIT_COMMITTER_DATE="2024-02-20T14:00:00" git commit -m "Add experiment tracking"

# Commit 14 - Maya
git config user.email "maya@example.com"
git config user.name "Maya Osei"
echo "v0.9.0-beta" > VERSION
git add . && GIT_AUTHOR_DATE="2024-02-25T16:00:00" GIT_COMMITTER_DATE="2024-02-25T16:00:00" git commit -m "Beta release v0.9.0"

echo "repo_05 setup complete: $(git log --oneline | wc -l) commits"
