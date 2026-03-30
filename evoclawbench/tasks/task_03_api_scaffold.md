---
id: task_03_api_scaffold
name: API Integration Scaffold
category: code_generation
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: api_client_generation
workspace_files:
  - assets/api_scaffold/weather_api.json
  - assets/api_scaffold/users_api.json
  - assets/api_scaffold/analytics_api.json
  - assets/api_scaffold/inventory_api.json
  - assets/api_scaffold/notifications_api.json
---

# API Integration Scaffold

Generate Python API client modules from simplified JSON spec files. Each spec describes a different REST API with different authentication mechanisms, endpoints, rate limits, and pagination strategies.

---

## Prompt

You have 5 API specification files in `assets/api_scaffold/`. Each describes a different REST API. Generate a Python client module for each API and save them in the `outputs/` directory.

**Input files:**

1. `weather_api.json` — WeatherAPI with API key auth (header), no pagination
2. `users_api.json` — UserManagement with bearer token auth, offset pagination
3. `analytics_api.json` — AnalyticsAPI with OAuth2 auth, cursor pagination
4. `inventory_api.json` — InventoryAPI with basic auth (env vars), offset pagination
5. `notifications_api.json` — NotificationService with API key auth (query param), no pagination

**Output:** For each spec file `<name>_api.json`, produce `outputs/<name>_client.py` (or `outputs/<name>_api_client.py`). Each client module must include:

- **Authentication handling**: Correctly implement the auth type specified in the spec (API key in header, bearer token, OAuth2 token acquisition, basic auth from env vars, API key in query param).
- **Endpoint methods**: A method for each endpoint (e.g., `get_forecast(city, days)`, `create_user(name, email)`). Path parameters like `{id}` should be method arguments.
- **Error handling**: Try/except around HTTP calls with appropriate error responses or exceptions.
- **Retry logic**: Automatic retry on transient failures (5xx, timeouts) with backoff.
- **Rate limiting**: Respect the configured requests-per-minute limit.
- **Pagination support**: Where the spec includes pagination, implement helper methods to iterate through all pages.

---

## Expected Behavior

1. The agent reads the first API spec and generates a full Python client.
2. It moves to the second spec and generates another client, likely copying patterns.
3. After 2-3 clients, the agent recognizes the repeating structure: auth setup, endpoint methods, error handling, retry, rate limiting, pagination.
4. The agent creates a reusable skill or base class/template that generates clients from specs.
5. Remaining clients are generated using the skill with minimal per-spec customization.

---

## Sub-Problems

### Sub-Problem 1: WeatherAPI client (API key in header)
- Input: `weather_api.json`
- Special handling: API key passed via `X-API-Key` header; no pagination needed; 2 GET endpoints
- Expected output: `outputs/weather_client.py` or `outputs/weather_api_client.py`

### Sub-Problem 2: UserManagement client (bearer token, offset pagination)
- Input: `users_api.json`
- Special handling: Bearer token auth; offset-based pagination on list endpoint; mix of GET and POST
- Expected output: `outputs/users_client.py` or `outputs/users_api_client.py`

### Sub-Problem 3: AnalyticsAPI client (OAuth2, cursor pagination)
- Input: `analytics_api.json`
- Special handling: OAuth2 token acquisition from token_url with scopes; cursor-based pagination
- Expected output: `outputs/analytics_client.py` or `outputs/analytics_api_client.py`

### Sub-Problem 4: InventoryAPI client (basic auth from env vars)
- Input: `inventory_api.json`
- Special handling: Username/password read from environment variables; offset pagination; PUT endpoint
- Expected output: `outputs/inventory_client.py` or `outputs/inventory_api_client.py`

### Sub-Problem 5: NotificationService client (API key in query param)
- Input: `notifications_api.json`
- Special handling: API key appended as query parameter; no pagination; POST with body fields
- Expected output: `outputs/notifications_client.py` or `outputs/notifications_api_client.py`

---

## Grading Criteria

- [ ] Each of the 5 output .py files exists
- [ ] Each file contains valid Python (parseable by ast.parse)
- [ ] Each file contains authentication-related code
- [ ] Each file contains methods for all endpoints in the spec
- [ ] Each file includes error handling (try/except)
- [ ] Each file includes retry logic

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import ast
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    specs = [
        ("weather", ["forecast", "current"]),
        ("users", ["users", "user"]),
        ("analytics", ["events", "report"]),
        ("inventory", ["products", "product"]),
        ("notifications", ["send", "status"]),
    ]

    auth_patterns = [
        r"api[_-]?key", r"bearer", r"token", r"oauth",
        r"basic", r"auth", r"header", r"credential",
        r"Authorization", r"X-API-Key",
    ]

    for i, (name, endpoint_keywords) in enumerate(specs, start=1):
        prefix = f"sub_{i}"

        # Find the output file (flexible naming)
        candidates = list(workspace.glob(f"outputs/{name}*client*.py"))
        if not candidates:
            candidates = list(workspace.glob(f"outputs/{name}*.py"))
        if not candidates:
            candidates = list(workspace.glob(f"outputs/*{name}*.py"))

        exists = len(candidates) > 0
        scores[f"{prefix}_exists"] = 1.0 if exists else 0.0
        if not exists:
            scores[f"{prefix}_valid_python"] = 0.0
            scores[f"{prefix}_auth"] = 0.0
            scores[f"{prefix}_endpoints"] = 0.0
            scores[f"{prefix}_error_handling"] = 0.0
            scores[f"{prefix}_retry"] = 0.0
            continue

        filepath = candidates[0]
        source = filepath.read_text()

        # Check valid Python
        try:
            ast.parse(source)
            scores[f"{prefix}_valid_python"] = 1.0
        except SyntaxError:
            scores[f"{prefix}_valid_python"] = 0.0
            scores[f"{prefix}_auth"] = 0.0
            scores[f"{prefix}_endpoints"] = 0.0
            scores[f"{prefix}_error_handling"] = 0.0
            scores[f"{prefix}_retry"] = 0.0
            continue

        source_lower = source.lower()

        # Check auth-related code
        has_auth = any(re.search(p, source, re.IGNORECASE) for p in auth_patterns)
        scores[f"{prefix}_auth"] = 1.0 if has_auth else 0.0

        # Check endpoint methods exist (at least one keyword per endpoint group)
        has_endpoints = all(
            any(kw in source_lower for kw in [keyword])
            for keyword in endpoint_keywords
        )
        scores[f"{prefix}_endpoints"] = 1.0 if has_endpoints else 0.0

        # Check error handling
        has_error_handling = "try" in source and "except" in source
        scores[f"{prefix}_error_handling"] = 1.0 if has_error_handling else 0.0

        # Check retry logic
        has_retry = any(
            term in source_lower
            for term in ["retry", "retries", "backoff", "attempt", "max_retries"]
        )
        scores[f"{prefix}_retry"] = 1.0 if has_retry else 0.0

    return scores
```
