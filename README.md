# API Wordlist Generator — Cipher's Combinatorial Engine v3

A combinatorial API endpoint wordlist generator for penetration testing. Generates crafted endpoint candidates from seed wordlists using naming conventions and path patterns observed in real-world APIs.

Zero dependencies. Pure Python 3.

---

## Table of Contents

- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Seed Wordlists](#seed-wordlists)
- [Naming Formats](#naming-formats)
- [Generation Patterns](#generation-patterns)
- [Priority Tiers](#priority-tiers)
- [HTTP Method Hints](#http-method-hints)
- [Plural Intelligence](#plural-intelligence)
- [Input Cleaning Pipeline](#input-cleaning-pipeline)
- [Tech Stack Cheat Sheet](#tech-stack-cheat-sheet)
- [CLI Reference](#cli-reference)
- [Usage Examples](#usage-examples)
- [Output Sizing Guide](#output-sizing-guide)

---

## Quick Start

```bash
# Basic generation — kebab + camel, 2-part combos
python api-wordlist-gen.py -a words/top-api-verbs.txt -o words/top-api-nouns.txt \
  -O endpoints.txt

# High-tier only for a fast, focused scan
python api-wordlist-gen.py -a words/top-api-verbs.txt -o words/top-api-nouns.txt \
  --tier high -O focused.txt

# Feed to your fuzzer
ffuf -u https://target.com/api/FUZZ -w focused.txt
```

---

## How It Works

```
┌──────────────────────────────────────────────────────┐
│  INPUT: seed wordlists (verbs, nouns, modifiers...)  │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  CLEANING PIPELINE                                    │
│  strip → lowercase → remove specials → dedup → sort  │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  TIER FILTERING (optional)                            │
│  high (~68 verbs × ~124 nouns)                       │
│  medium (~167 × ~288)                                │
│  all (528 × 1,800)                                   │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  PATTERN GENERATORS × FORMAT TRANSFORMS               │
│  7 patterns × 7 formats = targeted endpoint combos   │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│  POST-PROCESSING                                      │
│  dedup → HTTP method hints → sort → limit → output   │
└──────────────────────────────────────────────────────┘
```

---

## Seed Wordlists

The `words/` directory contains curated seed files:

| File | Count | Purpose |
|------|------:|---------|
| `top-api-verbs.txt` | 528 | Actions — CRUD, auth, state changes, infrastructure |
| `top-api-nouns.txt` | 1,800 | Resources — users, orders, configs, k8s resources |
| `modifiers.txt` | 217 | Qualifiers for 3-part patterns (all, active, bulk) |
| `top-prefixes.txt` | 257 | URL path prefixes (v1, admin, internal, staging) |
| `suffixes.txt` | 77 | File format suffixes (json, xml, csv, pdf) |
| `sub-objects.txt` | 138 | Nested sub-resources (roles, permissions, items) |
| `fields/top-fields.txt` | 339 | Property names for byField patterns (email, status, id) |
| `fields/identity.txt` | 74 | Identity-specific fields (username, token, apikey) |
| `fields/status.txt` | 56 | Status/state fields (active, pending, locked) |

All wordlists are hand-curated for API relevance. No generic English dictionaries.

---

## Naming Formats

Seven output formats (`-f`) covering all major API naming conventions:

| Format | Example | Typically Used By |
|--------|---------|-------------------|
| `kebab` | `create-user` | Go, Ruby, REST URLs |
| `snake` | `create_user` | Django, Rails, Laravel, FastAPI, Flask |
| `camel` | `createUser` | Spring Boot, Express, Next.js, GraphQL |
| `pascal` | `CreateUser` | ASP.NET, C# |
| `dot` | `create.user` | Java package-style, some configs |
| `concat` | `createuser` | Compressed/legacy endpoints |
| `path` | `/create/user` | Path-segment style |

```bash
# Single format
-f camel

# Multiple formats
-f kebab camel pascal

# All formats
-f all
```

Default: `kebab snake camel`

---

## Generation Patterns

Seven pattern generators (`-p`), each producing a different endpoint structure:

### `2` — Two-part combos (default)
Combines action + object in both orderings.
```
createUser, userCreate, delete-order, order-delete
```
**Requires:** `-a`, `-o`

### `3` — Three-part combos
Adds a modifier. Only the 3 realistic permutations:
```
get-all-users        (action-modifier-object)
bulk-create-orders   (modifier-action-object)
export-orders-csv    (action-object-modifier)
```
**Requires:** `-a`, `-o`, `-m`

### `rest` — REST path patterns
Plural-aware RESTful URL paths with `{id}` placeholders:
```
/users                     collection
/users/{id}                single resource
/users/{id}/activate       resource action
/users/search              collection utility
/users/{id}/roles          nested sub-resource
/users/{id}/roles/{sid}    deep nested
/api/v1/users/{id}         prefixed path (with --prefixes)
```
**Requires:** `-a`, `-o`
**Optional:** `--sub-objects`, `--prefixes`

### `byfield` — Lookup-by-field patterns
RPC-style lookup methods with connectors (by, with, for, from, using):
```
getUserByEmail, get_user_by_email, get-user-by-email, FindOrderByStatus
```
**Requires:** `-a`, `-o`, `--fields`

### `prefixed` — Prefixed patterns
Prepends routing prefixes:
```
admin-create-user, internal-delete-order, v1-get-payment
```
**Requires:** `-a`, `-o`, `--prefixes`

### `suffixed` — Suffixed patterns
Appends format suffixes:
```
export-orders-json, create-report-pdf, get-users-csv
```
**Requires:** `-a`, `-o`, `--suffixes`

### `event` — Event/callback patterns
Event handlers, lifecycle hooks, and boolean checks:
```
onUserCreate, handlePaymentProcess, beforeOrderDelete
doExport, isActive, hasPermission, canDelete
```
**Requires:** `-a`, `-o`

```bash
# Single pattern
-p rest

# Multiple patterns
-p 2 rest byfield

# All patterns
-p all
```

Default: `2`

---

## Priority Tiers

Tier filtering (`--tier`) reduces the combinatorial space to the most likely endpoints:

| Tier | Actions | Objects | Use Case |
|------|--------:|--------:|----------|
| `high` | ~68 | ~124 | Core CRUD × common resources. Fast, focused scans. |
| `medium` | ~167 | ~288 | Adds clone, deploy, schedule × pipeline, workflow, cluster. |
| `all` | 528 | 1,800 | Everything in the seed files. Maximum breadth. |

```bash
# Fast focused scan
--tier high

# Good coverage
--tier medium

# Everything (default)
--tier all
```

---

## HTTP Method Hints

The `--methods` flag prefixes each endpoint with its inferred HTTP method:

```
POST createUser
GET getUser
PUT updateUser
DELETE deleteUser
GET listOrders
POST submitPayment
GET /users/{id}
POST /users/{id}/activate
DELETE /users/{id}/sessions
```

Method inference maps 90+ verbs:
- `get, list, search, find, fetch, export, download` → **GET**
- `create, add, register, submit, upload, execute` → **POST**
- `update, edit, modify, replace, save, upsert` → **PUT**
- `patch` → **PATCH**
- `delete, remove, destroy, purge, revoke, cancel` → **DELETE**

---

## Plural Intelligence

REST APIs use plural nouns for collections: `/users/{id}`, not `/user/{id}`. Enabled by default in the `rest` pattern. Disable with `--no-plural`.

**Handles:**
- Irregular: person→people, child→children, datum→data, index→indices, schema→schemas
- API-specific: status→statuses, address→addresses, cache→caches, batch→batches
- Suffix rules: -s/-sh/-ch/-x/-z → +es, consonant+y → ies, -f/-fe → ves
- Uncountable: data, metadata, analytics, metrics, health, compliance, telemetry
- Already plural: words ending in -s pass through

---

## Input Cleaning Pipeline

All seed wordlists are automatically cleaned on load:

1. Strip whitespace
2. Remove blank lines and `#` comments
3. Lowercase everything
4. Remove non-alphanumeric characters
5. Min length filter (default: 2, configurable with `--min-length`)
6. Remove pure-number strings (unless `--keep-numbers`)
7. Deduplicate
8. Sort alphabetically

Use `--clean-only` to just clean wordlists without generating:
```bash
python api-wordlist-gen.py -a dirty.txt -o messy.txt --clean-only --save-cleaned cleaned/
```

---

## Tech Stack Cheat Sheet

Once you've identified the target's technology through your own recon, use these format + pattern combinations:

| Tech Stack | Formats | Patterns | Extra Flags |
|------------|---------|----------|-------------|
| **Spring Boot / Java** | `-f camel` | `-p 2 rest byfield event` | `--fields fields.txt` |
| **Django / DRF** | `-f snake kebab` | `-p 2 rest` | `--trailing-slash` |
| **Express.js / Node.js** | `-f camel kebab` | `-p 2 rest event` | |
| **ASP.NET / C#** | `-f pascal camel` | `-p 2 rest byfield` | `--fields fields.txt` |
| **Ruby on Rails** | `-f snake kebab` | `-p 2 rest` | |
| **Laravel / PHP** | `-f snake kebab` | `-p 2 rest` | |
| **FastAPI / Python** | `-f snake kebab` | `-p 2 rest` | |
| **Flask / Python** | `-f snake kebab` | `-p 2 rest` | |
| **Go (Gin/Echo/Fiber)** | `-f kebab snake` | `-p 2 rest` | |
| **Next.js** | `-f camel kebab` | `-p 2 rest` | |
| **GraphQL** | `-f camel` | `-p 2 byfield event` | `--fields fields.txt` |

**Why these choices?**
- **Spring/Java** → camelCase is the Java convention; Spring exposes RPC-style names (`getUserById`) and REST paths
- **Django/Rails/Laravel/Flask/FastAPI** → Python/Ruby/PHP communities use snake_case; Django enforces trailing slashes
- **ASP.NET** → C# uses PascalCase everywhere (`GetUser`, `CreateOrder`)
- **Go** → kebab-case URLs are idiomatic in Go HTTP frameworks
- **GraphQL** → operations are always camelCase (`getUser`, `createOrder`); no URL paths to fuzz
- **Express/Next.js** → JavaScript ecosystem uses camelCase, but URL paths often use kebab-case

---

## CLI Reference

### Required Arguments

| Flag | Description |
|------|-------------|
| `-a`, `--actions` | Path to actions/verbs wordlist |
| `-o`, `--objects` | Path to objects/nouns wordlist |

### Optional Wordlists

| Flag | Description | Used By |
|------|-------------|---------|
| `-m`, `--modifiers` | Modifiers wordlist | `3` pattern |
| `--prefixes` | Prefixes wordlist | `prefixed` and `rest` patterns |
| `--suffixes` | Suffixes wordlist | `suffixed` pattern |
| `--fields` | Fields wordlist | `byfield` pattern |
| `--sub-objects` | Sub-objects wordlist | `rest` nested resources |

### Format & Pattern

| Flag | Description | Default |
|------|-------------|---------|
| `-f`, `--formats` | Naming formats (kebab, snake, dot, concat, camel, pascal, path, all) | kebab snake camel |
| `-p`, `--patterns` | Generation patterns (2, 3, rest, byfield, prefixed, suffixed, event, all) | 2 |

### Generation Options

| Flag | Description | Default |
|------|-------------|---------|
| `--tier` | Priority tier (high, medium, all) | all |
| `--methods` | Prefix output with HTTP method hints | off |
| `--trailing-slash` | Add trailing slash to REST paths | off |
| `--no-plural` | Disable auto-pluralization in REST | off |

### Cleaning Options

| Flag | Description | Default |
|------|-------------|---------|
| `--min-length N` | Minimum word length after cleaning | 2 |
| `--keep-numbers` | Keep pure number strings | off |
| `--clean-only` | Only clean input wordlists and exit | off |
| `--save-cleaned DIR` | Save cleaned wordlists to directory | off |

### Output Control

| Flag | Description | Default |
|------|-------------|---------|
| `-O`, `--output FILE` | Output file | stdout |
| `--sort` | Sort output alphabetically | off |
| `--stats` | Print generation statistics to stderr | off |
| `--limit N` | Limit output to N lines | 0 (unlimited) |
| `--no-dedup` | Skip deduplication | off |
| `--preview` | Show estimated line count and exit | off |

---

## Usage Examples

### Basic 2-part generation
```bash
python api-wordlist-gen.py -a words/top-api-verbs.txt -o words/top-api-nouns.txt \
  -f kebab camel -p 2 -O basic.txt
```

### Spring Boot API (camelCase + byField + events)
```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  -f camel \
  -p 2 rest byfield event \
  --fields words/fields/top-fields.txt \
  --tier high \
  -O spring-endpoints.txt
```

### Django REST Framework (snake_case + trailing slashes)
```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  -f snake kebab \
  -p 2 rest \
  --trailing-slash \
  --tier medium \
  -O django-endpoints.txt
```

### ASP.NET (PascalCase + byField lookups)
```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  -f pascal camel \
  -p 2 rest byfield \
  --fields words/fields/top-fields.txt \
  --tier high \
  -O dotnet-endpoints.txt
```

### Go REST API (kebab-case paths)
```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  -f kebab \
  -p rest \
  --tier high \
  -O go-endpoints.txt
```

### GraphQL operation names
```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  -f camel \
  -p 2 byfield event \
  --fields words/fields/top-fields.txt \
  --tier high \
  -O graphql-ops.txt
```

### REST paths with nested resources and prefixes
```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  -p rest \
  --sub-objects words/sub-objects.txt \
  --prefixes words/top-prefixes.txt \
  --tier high \
  -O rest-deep.txt
```

### Full generation with HTTP method hints
```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  -m words/modifiers.txt \
  --prefixes words/top-prefixes.txt \
  --suffixes words/suffixes.txt \
  --fields words/fields/top-fields.txt \
  --sub-objects words/sub-objects.txt \
  -f all -p all \
  --methods --sort --stats \
  -O everything.txt
```

### Preview before generating
```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  -f camel -p 2 rest byfield \
  --fields words/fields/top-fields.txt \
  --tier high \
  --preview
```

### Clean dirty wordlists
```bash
python api-wordlist-gen.py \
  -a my-dirty-verbs.txt -o my-messy-nouns.txt \
  --clean-only --save-cleaned cleaned/
```

---

## Output Sizing Guide

Approximate output sizes with the included seed wordlists:

| Configuration | Approx. Output |
|---------------|---------------:|
| `--tier high -f kebab -p 2` | ~17,000 |
| `--tier high -f camel -p 2 rest` | ~50,000 |
| `--tier medium -f kebab snake -p 2` | ~190,000 |
| `--tier medium -p 2 rest` | ~350,000 |
| `-f all -p 2` (all tiers) | ~1,900,000 |
| `-f all -p all` (everything) | millions |

Use `--preview` to get an estimate before generating. Use `--limit N` to cap output.

---

## Author

**Cipher**

Built for penetration testers who need precision over volume.
