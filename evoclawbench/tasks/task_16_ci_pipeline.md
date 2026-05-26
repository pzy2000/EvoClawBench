---
id: task_16_ci_pipeline
name: Dockerfile and CI Pipeline Generation
category: devops
grading_type: hybrid
grading_weights:
  automated: 0.85
  llm_judge: 0.15
timeout_seconds: 600
sub_problems: 5
skill_category: devops_codegen
workspace_files:
  - assets/ci_pipeline/app_01_python_fastapi.json
  - assets/ci_pipeline/app_02_node_express.json
  - assets/ci_pipeline/app_03_go_http.json
  - assets/ci_pipeline/app_04_java_spring.json
  - assets/ci_pipeline/app_05_ruby_sinatra.json
---

# Dockerfile and CI Pipeline Generation

Read 5 application specification JSON files and generate a production-quality multi-stage `Dockerfile` plus a GitHub Actions CI/CD workflow YAML for each.

---

## Prompt

You have 5 application specification files in `assets/ci_pipeline/`. Each JSON file describes a different application stack. For each application, generate:

1. A `Dockerfile` using multi-stage builds where applicable
2. A GitHub Actions workflow file (`.github/workflows/ci.yml` style content)

Save outputs in `outputs/<app_id>/` (e.g., `outputs/app_01/Dockerfile` and `outputs/app_01/github_actions.yml`).

**Input files:**

1. `app_01_python_fastapi.json` — Python 3.11 FastAPI, pip, pytest, ruff+mypy lint, uvicorn
2. `app_02_node_express.json` — Node 20 Express, npm, jest, eslint, compiled to dist/
3. `app_03_go_http.json` — Go 1.22, go mod, golangci-lint, CGO disabled, scratch final image
4. `app_04_java_spring.json` — Java 17 Spring Boot, Maven, JUnit, multi-stage with JRE runtime
5. `app_05_ruby_sinatra.json` — Ruby 3.2 Sinatra, Bundler, RSpec, rubocop, single-stage

**Dockerfile requirements (apply to all):**
- Use the exact base image versions from the spec
- Multi-stage build where `multi_stage: true` in spec (builder + runtime stage)
- Run as non-root user where `non_root_user` is specified
- Copy only necessary artifacts to the final stage
- Set `WORKDIR`, `EXPOSE`, and `CMD` / `ENTRYPOINT` correctly
- Add a `HEALTHCHECK` instruction using the spec's `health_check` path

**GitHub Actions workflow requirements (apply to all):**
- Trigger on pushes to `trigger_branches` and pull requests
- Jobs: at minimum `test` and `build-push`
- `build-push` only runs on branches listed in `deploy_on_branch` (or all trigger branches if unspecified)
- Use `docker/build-push-action` for building and pushing
- Tag the image with both `latest` and the git SHA
- Set `REGISTRY`, `IMAGE_NAME` from the spec

---

## Expected Behavior

1. Agent reads app_01 spec and generates a Python multi-stage Dockerfile + GitHub Actions YAML.
2. After app_02, agent identifies the repeating pattern: parse spec → fill Dockerfile template → fill CI template.
3. Agent builds a reusable code generation skill that handles language-specific variations (base image, build cmd, test cmd).
4. Apps 03–05 are generated using the skill with per-language adaptation.
5. All Dockerfiles and workflows are syntactically valid and follow best practices.

---

## Sub-Problems

### Sub-Problem 1: Python FastAPI (app_01_python_fastapi.json)
- Dockerfile: `python:3.11-slim` builder, copy + install deps, non-root `appuser`, HEALTHCHECK `/health`
- CI: lint (ruff+mypy) → test (pytest+coverage) → build+push to ghcr.io, deploy step on `main`
- Expected output: `outputs/app_01/Dockerfile` + `outputs/app_01/github_actions.yml`

### Sub-Problem 2: Node Express (app_02_node_express.json)
- Dockerfile: `node:20-alpine` builder + runtime, build to `dist/`, run as `node` user
- CI: lint → test → build → push to docker.io, image tagged with SHA
- Expected output: `outputs/app_02/Dockerfile` + `outputs/app_02/github_actions.yml`

### Sub-Problem 3: Go HTTP Gateway (app_03_go_http.json)
- Dockerfile: multi-stage `golang:1.22-alpine` builder → `scratch` runtime, CGO_ENABLED=0
- CI: golangci-lint → go test with race detector → build binary → push to ghcr.io
- Expected output: `outputs/app_03/Dockerfile` + `outputs/app_03/github_actions.yml`

### Sub-Problem 4: Java Spring Boot (app_04_java_spring.json)
- Dockerfile: `maven:3.9-eclipse-temurin-17` builder → `eclipse-temurin:17-jre-jammy` runtime, JVM opts set
- CI: test (mvn test) → build JAR → push to docker.io, Maven cache enabled
- Expected output: `outputs/app_04/Dockerfile` + `outputs/app_04/github_actions.yml`

### Sub-Problem 5: Ruby Sinatra (app_05_ruby_sinatra.json)
- Dockerfile: single-stage `ruby:3.2-slim`, bundle install, non-root user, HEALTHCHECK `/health`
- CI: rubocop lint → rspec test → build+push to ghcr.io, vendor/bundle cache
- Expected output: `outputs/app_05/Dockerfile` + `outputs/app_05/github_actions.yml`

---

## Grading Criteria

- [ ] All 10 output files exist (5 Dockerfiles + 5 workflow YAMLs)
- [ ] Each Dockerfile starts with `FROM`
- [ ] Multi-stage Dockerfiles (apps 01–04) contain at least 2 `FROM` instructions
- [ ] Each Dockerfile contains `EXPOSE`, `WORKDIR`, and `CMD` or `ENTRYPOINT`
- [ ] Each Dockerfile contains `HEALTHCHECK`
- [ ] Each GitHub Actions YAML contains `on:` trigger section
- [ ] Each GitHub Actions YAML contains `jobs:` section
- [ ] App_03 Dockerfile references `scratch` as final base image

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    apps = [
        ("app_01", True,  False),  # (app_id, multi_stage, scratch_final)
        ("app_02", True,  False),
        ("app_03", True,  True),
        ("app_04", True,  False),
        ("app_05", False, False),
    ]

    for i, (app_id, multi_stage, scratch_final) in enumerate(apps, start=1):
        prefix = f"sub_{i}"
        df_path = workspace / "outputs" / app_id / "Dockerfile"
        ci_path = workspace / "outputs" / app_id / "github_actions.yml"

        # Check existence
        df_exists = df_path.is_file()
        ci_exists = ci_path.is_file()
        scores[f"{prefix}_dockerfile_exists"] = 1.0 if df_exists else 0.0
        scores[f"{prefix}_ci_exists"] = 1.0 if ci_exists else 0.0

        if df_exists:
            df = df_path.read_text(errors="replace")
            from_count = len(re.findall(r"^FROM\s", df, re.MULTILINE | re.IGNORECASE))
            scores[f"{prefix}_has_from"] = 1.0 if from_count >= 1 else 0.0
            scores[f"{prefix}_multi_stage"] = (
                1.0 if (not multi_stage or from_count >= 2) else 0.0
            )
            scores[f"{prefix}_has_expose"] = 1.0 if re.search(r"^EXPOSE\s", df, re.MULTILINE | re.IGNORECASE) else 0.0
            scores[f"{prefix}_has_workdir"] = 1.0 if re.search(r"^WORKDIR\s", df, re.MULTILINE | re.IGNORECASE) else 0.0
            scores[f"{prefix}_has_cmd"] = 1.0 if re.search(r"^(CMD|ENTRYPOINT)\s", df, re.MULTILINE | re.IGNORECASE) else 0.0
            scores[f"{prefix}_has_healthcheck"] = 1.0 if re.search(r"^HEALTHCHECK\s", df, re.MULTILINE | re.IGNORECASE) else 0.0
            scores[f"{prefix}_scratch"] = (
                1.0 if (not scratch_final or re.search(r"FROM\s+scratch", df, re.IGNORECASE)) else 0.0
            )
        else:
            for k in ["has_from", "multi_stage", "has_expose", "has_workdir", "has_cmd", "has_healthcheck", "scratch"]:
                scores[f"{prefix}_{k}"] = 0.0

        if ci_exists:
            ci = ci_path.read_text(errors="replace")
            scores[f"{prefix}_ci_on"] = 1.0 if re.search(r"^on:", ci, re.MULTILINE) else 0.0
            scores[f"{prefix}_ci_jobs"] = 1.0 if re.search(r"^jobs:", ci, re.MULTILINE) else 0.0
        else:
            scores[f"{prefix}_ci_on"] = 0.0
            scores[f"{prefix}_ci_jobs"] = 0.0

    return scores
```

---

## LLM Judge Rubric

You are evaluating Dockerfiles and GitHub Actions workflows generated from application specifications. Focus on best-practices adherence — automated checks already verified structural correctness.

Score the following criterion from 0.0 to 1.0:

**dockerfile_quality**: For each of the 5 Dockerfiles, does it follow container best practices? Consider: (1) Is the non-root user set up correctly for apps that require it? (2) Are layers ordered to maximize cache efficiency (COPY deps before COPY source)? (3) Are only necessary files copied to the runtime stage in multi-stage builds? (4) Does the image minimize its attack surface (slim/alpine base, no dev tools in runtime)? Return the average across all 5 Dockerfiles.
