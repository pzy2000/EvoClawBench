---
id: task_08_schema_ops
name: Database Schema Operations
category: database
grading_type: automated
timeout_seconds: 600
sub_problems: 5
skill_category: schema_migration
workspace_files:
  - assets/schema_ops/users.sql
  - assets/schema_ops/orders.sql
  - assets/schema_ops/products.sql
  - assets/schema_ops/reviews.sql
  - assets/schema_ops/sessions.sql
---

# Database Schema Operations

Generate PostgreSQL migration SQL files to apply specific schema changes to existing database tables.

---

## Prompt

You have 5 SQL schema files in `assets/schema_ops/` representing existing PostgreSQL tables. Generate migration SQL files in `outputs/` that apply the specified changes to each table.

**Important:** Generate only the migration SQL (ALTER TABLE, CREATE INDEX, CREATE FUNCTION, etc.), not the full CREATE TABLE statement. Each migration file should be executable against the existing schema.

**Files to generate:**

1. `assets/schema_ops/users.sql` → `outputs/migrate_users.sql`
   Required changes:
   - Add column `phone_number VARCHAR(20)`
   - Add column `last_login_at TIMESTAMP`
   - Create index on `email`
   - Add UNIQUE constraint on `username`

2. `assets/schema_ops/orders.sql` → `outputs/migrate_orders.sql`
   Required changes:
   - Add column `shipping_address JSONB`
   - Add column `tracking_number VARCHAR(100)`
   - Rename column `status` to `order_status`
   - Create composite index on `(user_id, created_at)`

3. `assets/schema_ops/products.sql` → `outputs/migrate_products.sql`
   Required changes:
   - Add column `description TEXT`
   - Add column `tags TEXT[]`
   - Add column `updated_at TIMESTAMP DEFAULT NOW()`
   - Create trigger to auto-update `updated_at` on row modification
   - Create full-text search index on `name` and `description` using GIN

4. `assets/schema_ops/reviews.sql` → `outputs/migrate_reviews.sql`
   Required changes:
   - Add column `helpful_count INTEGER DEFAULT 0`
   - Add column `verified_purchase BOOLEAN DEFAULT false`
   - Add CHECK constraint on `rating` to enforce values between 1 and 5
   - Create composite index on `(product_id, rating)`

5. `assets/schema_ops/sessions.sql` → `outputs/migrate_sessions.sql`
   Required changes:
   - Add column `user_agent TEXT`
   - Add column `is_active BOOLEAN DEFAULT true`
   - Add column `created_at TIMESTAMP DEFAULT NOW()`
   - Create a function and scheduled mechanism to clean up expired sessions (delete rows where `expires_at < NOW()`)

---

## Expected Behavior

1. Agent reads the first schema file and writes the migration SQL
2. Agent recognizes the repeating pattern of schema migration tasks
3. Agent creates a reusable skill for generating migration SQL
4. Agent applies the skill to all remaining schema files
5. All outputs contain valid, executable PostgreSQL migration SQL

---

## Sub-Problems

### Sub-Problem 1: Users Table Migration
- Input: `assets/schema_ops/users.sql` (users table with id, username, email, password_hash, is_active, created_at)
- Required: ADD COLUMN (phone_number, last_login_at), CREATE INDEX (email), ADD UNIQUE (username)
- Expected output: `outputs/migrate_users.sql`

### Sub-Problem 2: Orders Table Migration
- Input: `assets/schema_ops/orders.sql` (orders table with id, user_id, total, status, created_at)
- Required: ADD COLUMN (shipping_address JSONB, tracking_number), RENAME COLUMN (status→order_status), CREATE INDEX composite
- Expected output: `outputs/migrate_orders.sql`

### Sub-Problem 3: Products Table Migration
- Input: `assets/schema_ops/products.sql` (products table with id, name, price, stock, category)
- Required: ADD COLUMN (description, tags, updated_at), CREATE TRIGGER (auto-update updated_at), CREATE INDEX (GIN full-text search)
- Expected output: `outputs/migrate_products.sql`

### Sub-Problem 4: Reviews Table Migration
- Input: `assets/schema_ops/reviews.sql` (reviews table with id, product_id, user_id, rating, comment, created_at)
- Required: ADD COLUMN (helpful_count, verified_purchase), ADD CHECK (rating 1-5), CREATE INDEX composite
- Expected output: `outputs/migrate_reviews.sql`

### Sub-Problem 5: Sessions Table Migration
- Input: `assets/schema_ops/sessions.sql` (sessions table with id, user_id, token, expires_at, ip_address)
- Required: ADD COLUMN (user_agent, is_active, created_at), CREATE FUNCTION (cleanup expired sessions)
- Expected output: `outputs/migrate_sessions.sql`

---

## Grading Criteria

- [ ] All 5 output files exist in outputs/
- [ ] All files contain valid SQL statements
- [ ] Each migration contains the required ALTER TABLE statements
- [ ] Correct SQL keywords used (ALTER TABLE, ADD COLUMN, CREATE INDEX, etc.)
- [ ] Table names referenced correctly
- [ ] Column types match specifications
- [ ] Constraints and triggers properly defined

---

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    import re
    from pathlib import Path

    scores = {}
    workspace = Path(workspace_path)

    migrations = [
        (
            "migrate_users.sql",
            {
                "alter_table": "users",
                "required_patterns": [
                    (r"(?i)ADD\s+(COLUMN\s+)?phone_number", "add_phone"),
                    (r"(?i)ADD\s+(COLUMN\s+)?last_login_at", "add_last_login"),
                    (r"(?i)CREATE\s+(UNIQUE\s+)?INDEX.*\bemail\b", "index_email"),
                    (r"(?i)(ADD\s+CONSTRAINT.*UNIQUE.*username|UNIQUE.*username|ALTER.*ADD\s+UNIQUE)", "unique_username"),
                ],
            },
        ),
        (
            "migrate_orders.sql",
            {
                "alter_table": "orders",
                "required_patterns": [
                    (r"(?i)ADD\s+(COLUMN\s+)?shipping_address\s+JSONB", "add_shipping_address"),
                    (r"(?i)ADD\s+(COLUMN\s+)?tracking_number", "add_tracking_number"),
                    (r"(?i)RENAME\s+(COLUMN\s+)?status\s+TO\s+order_status", "rename_status"),
                    (r"(?i)CREATE\s+INDEX.*user_id.*created_at|CREATE\s+INDEX.*\(user_id\s*,\s*created_at\)", "composite_index"),
                ],
            },
        ),
        (
            "migrate_products.sql",
            {
                "alter_table": "products",
                "required_patterns": [
                    (r"(?i)ADD\s+(COLUMN\s+)?description\s+TEXT", "add_description"),
                    (r"(?i)ADD\s+(COLUMN\s+)?tags\s+TEXT\s*\[\s*\]", "add_tags"),
                    (r"(?i)ADD\s+(COLUMN\s+)?updated_at", "add_updated_at"),
                    (r"(?i)CREATE\s+(OR\s+REPLACE\s+)?FUNCTION", "trigger_function"),
                    (r"(?i)CREATE\s+INDEX.*USING\s+GIN|CREATE\s+INDEX.*to_tsvector", "gin_index"),
                ],
            },
        ),
        (
            "migrate_reviews.sql",
            {
                "alter_table": "reviews",
                "required_patterns": [
                    (r"(?i)ADD\s+(COLUMN\s+)?helpful_count", "add_helpful_count"),
                    (r"(?i)ADD\s+(COLUMN\s+)?verified_purchase", "add_verified_purchase"),
                    (r"(?i)CHECK\s*\(.*rating.*[1-5]|CHECK\s*\(.*rating\s*(>=|BETWEEN)", "check_rating"),
                    (r"(?i)CREATE\s+INDEX.*product_id.*rating|CREATE\s+INDEX.*\(product_id\s*,\s*rating\)", "composite_index"),
                ],
            },
        ),
        (
            "migrate_sessions.sql",
            {
                "alter_table": "sessions",
                "required_patterns": [
                    (r"(?i)ADD\s+(COLUMN\s+)?user_agent", "add_user_agent"),
                    (r"(?i)ADD\s+(COLUMN\s+)?is_active", "add_is_active"),
                    (r"(?i)ADD\s+(COLUMN\s+)?created_at", "add_created_at"),
                    (r"(?i)CREATE\s+(OR\s+REPLACE\s+)?FUNCTION.*clean|DELETE\s+FROM\s+sessions\s+WHERE\s+expires_at", "cleanup_function"),
                ],
            },
        ),
    ]

    for idx, (filename, checks) in enumerate(migrations, start=1):
        prefix = f"sub_{idx}"
        out_path = workspace / "outputs" / filename

        # Check file exists
        if not out_path.exists():
            scores[f"{prefix}_exists"] = 0.0
            scores[f"{prefix}_valid_sql"] = 0.0
            scores[f"{prefix}_modifications"] = 0.0
            continue

        scores[f"{prefix}_exists"] = 1.0

        # Read content
        try:
            content = out_path.read_text()
        except Exception:
            scores[f"{prefix}_valid_sql"] = 0.0
            scores[f"{prefix}_modifications"] = 0.0
            continue

        # Check basic SQL validity (contains ALTER TABLE or CREATE)
        has_alter = bool(re.search(r"(?i)ALTER\s+TABLE", content))
        has_create = bool(re.search(r"(?i)CREATE\s+(INDEX|FUNCTION|TRIGGER|OR)", content))
        has_table_ref = bool(re.search(r"(?i)\b" + checks["alter_table"] + r"\b", content))

        scores[f"{prefix}_valid_sql"] = 1.0 if (has_alter or has_create) and has_table_ref else 0.0

        # Check required modifications
        patterns = checks["required_patterns"]
        matched = 0
        for pattern, label in patterns:
            if re.search(pattern, content):
                matched += 1

        scores[f"{prefix}_modifications"] = round(matched / len(patterns), 2)

    return scores
```
