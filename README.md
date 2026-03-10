# API Wordlist Generator — Cipher's Combinatorial Engine v3

A tech-aware, combinatorial API endpoint wordlist generator for penetration testing. Generates crafted endpoint candidates from seed wordlists using naming conventions and path patterns observed in real-world APIs across 11 different tech stacks.

Zero dependencies. Pure Python 3.

---

## Table of Contents

- [Why This Tool](#why-this-tool)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Seed Wordlists](#seed-wordlists)
- [Naming Formats](#naming-formats)
- [Generation Patterns](#generation-patterns)
- [Technology Profiles](#technology-profiles)
- [Scan Profiles](#scan-profiles)
- [Priority Tiers](#priority-tiers)
- [Recon Probe Mode](#recon-probe-mode)
- [HTTP Method Hints](#http-method-hints)
- [Plural Intelligence](#plural-intelligence)
- [Input Cleaning Pipeline](#input-cleaning-pipeline)
- [CLI Reference](#cli-reference)
- [Real-World Workflows](#real-world-workflows)
- [Output Sizing Guide](#output-sizing-guide)

---

## Why This Tool

Generic wordlists like `common.txt` or `raft-large` cast a wide net but miss the combinatorial nature of API endpoints. Real APIs follow predictable patterns:

- **Spring Boot** uses `camelCase` RPC names: `getUserById`, `createOrder`, `deletePayment`
- **Django REST** uses `snake_case` with trailing slashes: `/user_profiles/`, `/order_items/`
- **ASP.NET** uses `PascalCase`: `GetUserByEmail`, `CreateSubscription`
- **Go APIs** use `kebab-case` REST paths: `/users/{id}/activate`, `/orders/{id}/cancel`

This tool generates endpoint candidates that match these real conventions, instead of testing random paths that would never exist.

---

## Quick Start

```bash
# 1. Fingerprint the target stack
python api-wordlist-gen.py --recon-probe -O probe.txt
# Feed probe.txt to ffuf/feroxbuster against the target

# 2. Identified Spring Boot? Generate targeted endpoints
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  --tech spring --tier high \
  -O spring-endpoints.txt

# 3. Feed to your fuzzer
ffuf -u https://target.com/api/FUZZ -w spring-endpoints.txt
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLI FLAGS                            │
│  -a verbs.txt  -o nouns.txt  --tech spring  --tier high │
└──────────┬──────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────┐    ┌─────────────────────────────┐
│  INPUT CLEANING      │    │  FLAG PRECEDENCE            │
│  strip → lowercase   │    │  explicit -f/-p             │
│  → remove specials   │    │    > --tech                 │
│  → min length        │    │    > --profile              │
│  → dedup → sort      │    │    > hardcoded defaults     │
└──────────┬───────────┘    └──────────┬──────────────────┘
           │                           │
           ▼                           ▼
┌──────────────────────┐    ┌─────────────────────────────┐
│  TIER FILTERING      │    │  RESOLVE FORMATS + PATTERNS │
│  high / medium / all │    │  from tech/profile/flags    │
└──────────┬───────────┘    └──────────┬──────────────────┘
           │                           │
           ▼                           ▼
┌─────────────────────────────────────────────────────────┐
│                  PATTERN GENERATORS                      │
│  2-part │ 3-part │ REST │ byField │ prefixed │ suffixed │ event │
│         │        │  ↑   │         │          │          │       │
│         │        │  └── plural intelligence              │
└──────────┬──────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│  POST-PROCESSING                                         │
│  dedup → HTTP method hints → sort → limit → output      │
└─────────────────────────────────────────────────────────┘
```

---

## Seed Wordlists

The `words/` directory contains curated seed files:

| File | Count | Purpose |
|------|------:|---------|
| `top-api-verbs.txt` | 528 | Actions/verbs — CRUD, auth, state changes, infrastructure |
| `top-api-nouns.txt` | 1,800 | Objects/resources — users, orders, configs, k8s resources |
| `modifiers.txt` | 217 | Adjectives/qualifiers for 3-part patterns (all, active, bulk) |
| `top-prefixes.txt` | 257 | URL path prefixes (v1, admin, internal, staging) |
| `suffixes.txt` | 77 | File format suffixes (json, xml, csv, pdf) |
| `sub-objects.txt` | 138 | Nested sub-resources (roles, permissions, items, payments) |
| `fields/top-fields.txt` | 339 | Property names for byField patterns (email, status, id) |
| `fields/identity.txt` | 74 | Identity-specific fields (username, token, apikey) |
| `fields/status.txt` | 56 | Status/state fields (active, pending, locked) |

All wordlists are hand-curated for API relevance. No generic English dictionaries.

---

## Naming Formats

Seven output formats covering all major API naming conventions:

| Format | Flag | Example | Used By |
|--------|------|---------|---------|
| `kebab` | `-f kebab` | `create-user` | Go, Ruby, REST URLs |
| `snake` | `-f snake` | `create_user` | Django, Rails, Laravel, FastAPI, Flask |
| `camel` | `-f camel` | `createUser` | Spring Boot, Express, Next.js, GraphQL |
| `pascal` | `-f pascal` | `CreateUser` | ASP.NET, C# |
| `dot` | `-f dot` | `create.user` | Java package-style, some configs |
| `concat` | `-f concat` | `createuser` | Compressed/legacy endpoints |
| `path` | `-f path` | `/create/user` | Path-segment style |

Use `all` to generate in every format: `-f all`

Multiple formats at once: `-f kebab camel pascal`

---

## Generation Patterns

Seven pattern generators, each producing a different endpoint structure:

### `2` — Two-part combos (default)
The most common API pattern. Combines action + object in both orderings.
```
createUser, userCreate
delete-order, order-delete
```
**Requires:** `-a` actions, `-o` objects

### `3` — Three-part combos
Adds a modifier dimension. Only the 3 realistic permutations (not all 6):
```
get-all-users        (action-modifier-object)
bulk-create-orders   (modifier-action-object)
export-orders-csv    (action-object-modifier)
```
**Requires:** `-a` actions, `-o` objects, `-m` modifiers

### `rest` — REST path patterns
Generates plural-aware RESTful URL paths with `{id}` placeholders:
```
/users                     collection
/users/{id}                single resource
/users/{id}/activate       resource action
/users/search              collection utility
/users/{id}/roles          nested sub-resource
/users/{id}/roles/{sid}    deep nested
/api/v1/users/{id}         prefixed paths
```
**Requires:** `-a` actions, `-o` objects
**Optional:** `--sub-objects`, `--prefixes` (or auto-populated by `--tech`)

### `byfield` — Lookup-by-field patterns
Generates RPC-style lookup methods with connector words (by, with, for, from, using):
```
getUserByEmail       (camel)
get_user_by_email    (snake)
get-user-by-email    (kebab)
FindOrderByStatus    (pascal)
```
**Requires:** `-a` actions, `-o` objects, `--fields`

### `prefixed` — Prefixed patterns
Prepends routing prefixes to action-object combos:
```
admin-create-user
internal-delete-order
v1-get-payment
```
**Requires:** `-a` actions, `-o` objects, `--prefixes`

### `suffixed` — Suffixed patterns
Appends format suffixes to action-object combos:
```
export-orders-json
create-report-pdf
get-users-csv
```
**Requires:** `-a` actions, `-o` objects, `--suffixes`

### `event` — Event/callback patterns
Generates event handler, lifecycle hook, and boolean check names:
```
onUserCreate         (event prefix + object + action)
handlePaymentProcess (handler prefix)
beforeOrderDelete    (lifecycle hook)
doExport             (single prefix + action)
isActive             (boolean check)
hasPermission        (capability check)
```
**Requires:** `-a` actions, `-o` objects

Use `all` to run every pattern: `-p all`

Multiple patterns: `-p 2 rest byfield`

---

## Technology Profiles

The `--tech` flag auto-configures format, patterns, trailing slash, magic paths, and API prefixes for a specific framework.

| Profile | Framework | Formats | Patterns | Trailing Slash | Magic Paths |
|---------|-----------|---------|----------|:--------------:|:-----------:|
| `spring` | Spring Boot / Java | camel | 2, rest, byfield, event | No | 42 |
| `django` | Django / DRF | snake, kebab | 2, rest | Yes | 25 |
| `express` | Express.js / Node.js | camel, kebab | 2, rest, event | No | 22 |
| `dotnet` | ASP.NET / C# | pascal, camel | 2, rest, byfield | No | 25 |
| `rails` | Ruby on Rails | snake, kebab | 2, rest | No | 18 |
| `laravel` | Laravel / PHP | snake, kebab | 2, rest | No | 29 |
| `fastapi` | FastAPI / Python | snake, kebab | 2, rest | No | 19 |
| `flask` | Flask / Python | snake, kebab | 2, rest | No | 17 |
| `go` | Go (Gin/Echo/Fiber) | kebab, snake | 2, rest | No | 24 |
| `nextjs` | Next.js | camel, kebab | 2, rest | No | 12 |
| `graphql` | GraphQL API | camel | 2, byfield, event | No | 8 |

Each profile includes:
- **Magic paths**: Framework-specific fingerprint endpoints (actuator for Spring, /__debug__/ for Django, /telescope for Laravel, /debug/pprof/ for Go, etc.)
- **Path prefixes**: Common API base paths for that framework (/api, /api/v1, etc.)
- **Format + pattern selection**: What real-world apps of that type actually use

When `--tech` is set, its magic paths are automatically injected into the output. You don't need a separate recon step.

---

## Scan Profiles

The `--profile` flag provides pre-configured scan strategies:

| Profile | Description | Formats | Patterns | Tier |
|---------|-------------|---------|----------|------|
| `recon` | Quick high-probability hits | kebab, camel | 2, rest | high |
| `full` | Maximum coverage, all patterns | all 7 formats | all 7 patterns | all |
| `rest` | REST paths only | kebab | rest | all |
| `rpc` | RPC-style function names | camel, pascal | 2, byfield, event | all |

Profiles set defaults for format, pattern, and tier — but explicit flags (`-f`, `-p`, `--tier`) always override them.

---

## Priority Tiers

Tier filtering reduces the combinatorial space to the most statistically likely endpoints:

| Tier | Actions | Objects | Description |
|------|--------:|--------:|-------------|
| `high` | ~68 | ~124 | Core CRUD verbs × common resources (user, order, payment, config) |
| `medium` | ~167 | ~288 | Adds clone, deploy, schedule × pipeline, workflow, cluster |
| `all` | 528 | 1,800 | Everything in your seed files |

The `high` tier targets the endpoints that exist in virtually every API. The `medium` tier adds operations and resources common in production systems. Use `all` when you need maximum breadth.

```bash
# Fast, focused scan (~17k 2-part kebab endpoints)
python api-wordlist-gen.py -a words/top-api-verbs.txt -o words/top-api-nouns.txt \
  --tier high -f kebab -p 2

# Broader coverage
python api-wordlist-gen.py -a words/top-api-verbs.txt -o words/top-api-nouns.txt \
  --tier medium -p 2 rest
```

---

## Recon Probe Mode

Before generating endpoints, identify the target's tech stack:

```bash
# Dump all 203 framework fingerprint paths
python api-wordlist-gen.py --recon-probe -O probe-all.txt

# Probe only for a specific framework
python api-wordlist-gen.py --recon-probe --tech spring -O probe-spring.txt
python api-wordlist-gen.py --recon-probe --tech django -O probe-django.txt
```

Recon probe outputs known magic paths — framework admin panels, debug endpoints, swagger UIs, actuator endpoints, profiling tools. Feed these to your fuzzer first:

```bash
ffuf -u https://target.com/FUZZ -w probe-all.txt -mc 200,301,302,403
```

A hit on `/actuator/health` = Spring Boot. A hit on `/__debug__/` = Django. A hit on `/telescope` = Laravel. Now you know what `--tech` to use for targeted generation.

**Fingerprint path counts per framework:**

| Framework | Paths | Key Indicators |
|-----------|------:|----------------|
| Spring Boot | 42 | `/actuator/*`, `/h2-console`, `/jolokia`, `/swagger-ui` |
| Django/DRF | 25 | `/admin/`, `/__debug__/`, `/silk/`, `/django-rq/` |
| ASP.NET | 25 | `/hangfire`, `/elmah`, `/signalr/*`, `/odata` |
| Laravel | 29 | `/telescope`, `/horizon`, `/nova`, `/_ignition/*` |
| Go | 24 | `/debug/pprof/*`, `/healthz`, `/readyz`, `/livez` |
| Express.js | 22 | `/__express_route_map`, `/graphql`, `/socket.io/` |
| FastAPI | 19 | `/docs`, `/redoc`, `/openapi.json` |
| Rails | 18 | `/rails/info/*`, `/sidekiq`, `/letter_opener` |
| Flask | 17 | `/flasgger/`, `/apidocs`, `/graphiql` |
| Next.js | 12 | `/api/auth/*`, `/_next/*`, `/api/trpc/` |
| GraphQL | 8 | `/graphql`, `/graphiql`, `/playground`, `/voyager` |

---

## HTTP Method Hints

The `--methods` flag prefixes each endpoint with its inferred HTTP method:

```bash
python api-wordlist-gen.py -a words/top-api-verbs.txt -o words/top-api-nouns.txt \
  --tech spring --methods --tier high -O methods.txt
```

Output:
```
POST createUser
GET getUser
PUT updateUser
DELETE deleteUser
GET listOrders
POST submitPayment
PATCH patch
GET /users/{id}
POST /users/{id}/activate
DELETE /users/{id}/sessions
```

Method inference uses a mapping of 90+ verb→method rules:
- `get, list, search, find, fetch, export, download` → **GET**
- `create, add, register, submit, upload, send, execute` → **POST**
- `update, edit, modify, replace, save, upsert` → **PUT**
- `patch` → **PATCH**
- `delete, remove, destroy, purge, revoke, cancel` → **DELETE**

This is useful for method-aware fuzzing tools or when building targeted Burp Intruder/ffuf configs.

---

## Plural Intelligence

REST APIs use plural nouns for collections: `/users/{id}`, not `/user/{id}`. The `--no-plural` flag disables this, but by default the engine auto-pluralizes:

**Handled cases:**
- Irregular plurals: person→people, child→children, datum→data, index→indices, schema→schemas
- API-specific: status→statuses, address→addresses, cache→caches, batch→batches
- Suffix rules: -s/-sh/-ch/-x/-z→+es, consonant+y→ies, -f/-fe→ves
- Uncountable: data, metadata, analytics, metrics, health, compliance, telemetry
- Already plural: words ending in -s (except -ss, -us, -is, -xs) pass through

```
user     → /users/{id}/activate
address  → /addresses/{id}
policy   → /policies/{id}
cache    → /caches/{id}
analysis → /analyses
datum    → /data
health   → /health  (uncountable)
```

---

## Input Cleaning Pipeline

All seed wordlists pass through an automatic cleaning pipeline:

1. **Strip** whitespace
2. **Remove** blank lines and `#` comments
3. **Lowercase** everything
4. **Remove** non-alphanumeric characters (hyphens, underscores, etc.)
5. **Min length** filter (default: 2 characters, configurable with `--min-length`)
6. **Remove** pure-number strings (unless `--keep-numbers`)
7. **Deduplicate**
8. **Sort** alphabetically

The pipeline reports statistics to stderr:
```
[*] Loaded words/top-api-verbs.txt
    Raw:    600 → Cleaned:    528 (removed 72: 0 dupes, 0 short, 32 empty, 0 nums, 40 comments, 0 invalid)
```

Use `--clean-only` to just clean your wordlists without generating endpoints:
```bash
python api-wordlist-gen.py -a dirty-verbs.txt -o messy-nouns.txt --clean-only --save-cleaned cleaned/
```

---

## CLI Reference

### Required Arguments

| Flag | Description |
|------|-------------|
| `-a`, `--actions` | Path to actions/verbs wordlist |
| `-o`, `--objects` | Path to objects/nouns wordlist |

Required for all modes except `--recon-probe` and `--clean-only`.

### Optional Wordlists

| Flag | Description | Used By |
|------|-------------|---------|
| `-m`, `--modifiers` | Modifiers wordlist | 3-part pattern |
| `--prefixes` | Prefixes wordlist | prefixed pattern, REST path prefixes |
| `--suffixes` | Suffixes wordlist | suffixed pattern |
| `--fields` | Fields wordlist | byfield pattern |
| `--sub-objects` | Sub-objects wordlist | REST nested resources |

### Tech & Profile

| Flag | Description |
|------|-------------|
| `--tech TECH` | Target framework (spring, django, express, dotnet, rails, laravel, fastapi, flask, go, nextjs, graphql) |
| `--profile PROFILE` | Scan preset (recon, full, rest, rpc) |
| `--tier TIER` | Priority tier (high, medium, all) |
| `--recon-probe` | Output framework fingerprint paths and exit |
| `--methods` | Prefix output with HTTP method hints |
| `--trailing-slash` | Add trailing slash to REST paths |
| `--no-plural` | Disable auto-pluralization in REST patterns |

### Format & Pattern Selection

| Flag | Description |
|------|-------------|
| `-f`, `--formats` | Output naming formats (kebab, snake, dot, concat, camel, pascal, path, all) |
| `-p`, `--patterns` | Generation patterns (2, 3, rest, byfield, prefixed, suffixed, event, all) |

### Cleaning Options

| Flag | Description |
|------|-------------|
| `--min-length N` | Minimum word length after cleaning (default: 2) |
| `--keep-numbers` | Keep pure number strings |
| `--clean-only` | Only clean input wordlists and exit |
| `--save-cleaned DIR` | Save cleaned wordlists to directory |

### Output Control

| Flag | Description |
|------|-------------|
| `-O`, `--output FILE` | Output file (default: stdout) |
| `--sort` | Sort output alphabetically |
| `--stats` | Print generation statistics to stderr |
| `--limit N` | Limit output to N lines |
| `--no-dedup` | Skip deduplication (faster for huge lists) |
| `--preview` | Show estimated line count and exit |

### Flag Precedence

When multiple sources configure the same setting:

```
Explicit -f / -p flags  (highest priority — always wins)
  ↓
--tech profile          (sets framework-optimal formats + patterns)
  ↓
--profile preset        (sets scan strategy defaults)
  ↓
Hardcoded defaults      (kebab+snake+camel, pattern 2)
```

You can combine `--tech` with explicit flags to override specific choices:
```bash
# Use Spring's patterns but force kebab format instead of camelCase
python api-wordlist-gen.py -a verbs.txt -o nouns.txt --tech spring -f kebab
```

---

## Real-World Workflows

### Workflow 1: Unknown Target — Full Recon

You have a target API at `https://api.target.com` and no idea what stack it runs.

```bash
# Step 1: Probe for framework fingerprints
python api-wordlist-gen.py --recon-probe -O probe.txt
ffuf -u https://api.target.com/FUZZ -w probe.txt -mc 200,301,302,403

# Step 2: You got hits on /actuator/health and /swagger-ui → Spring Boot
# Generate Spring-targeted endpoints
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  --tech spring --tier high \
  -O spring-high.txt

# Step 3: Fuzz with targeted list
ffuf -u https://api.target.com/api/v1/FUZZ -w spring-high.txt -mc 200,201,204,401,403
```

### Workflow 2: Known Django REST Framework

```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  --tech django --tier medium \
  --sub-objects words/sub-objects.txt \
  -O django-endpoints.txt

# Django uses trailing slashes — the tool adds them automatically with --tech django
# Output: /users/, /users/{id}/, /users/{id}/roles/, etc.
```

### Workflow 3: GraphQL Operation Names

GraphQL doesn't use URL paths — it uses operation names in camelCase:

```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  --tech graphql --tier high \
  --fields words/fields/top-fields.txt \
  -O graphql-ops.txt

# Output: getUser, createOrder, getUserByEmail, onPaymentCreate, etc.
```

### Workflow 4: ASP.NET with Method Hints

```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  --tech dotnet --tier high --methods \
  --fields words/fields/top-fields.txt \
  -O dotnet-methods.txt

# Output: GET GetUser, POST CreateOrder, DELETE RemovePayment, etc.
```

### Workflow 5: Maximum Coverage Brute Force

When you don't care about noise and want everything:

```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  -m words/modifiers.txt \
  --prefixes words/top-prefixes.txt \
  --suffixes words/suffixes.txt \
  --fields words/fields/top-fields.txt \
  --sub-objects words/sub-objects.txt \
  --profile full \
  -O everything.txt --stats
```

### Workflow 6: Quick Recon with Minimal Output

```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  --profile recon \
  -O recon-quick.txt

# High-tier only, kebab+camel, 2-part+REST patterns
# Focused list for initial discovery
```

### Workflow 7: REST Paths with Nested Resources

```bash
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  --sub-objects words/sub-objects.txt \
  --prefixes words/top-prefixes.txt \
  -p rest --tier high \
  -O rest-deep.txt

# Output includes:
# /users/{id}/roles
# /users/{id}/roles/{sid}
# /users/{id}/permissions
# /api/v1/orders/{id}/items
# /api/v2/payments/{id}/refunds
```

### Workflow 8: Clean Dirty Wordlists

```bash
# Just clean without generating — useful for preparing custom wordlists
python api-wordlist-gen.py \
  -a my-dirty-verbs.txt \
  -o my-messy-nouns.txt \
  --clean-only --save-cleaned cleaned/
```

### Workflow 9: Preview Before Generating

```bash
# Check how many endpoints will be generated before committing
python api-wordlist-gen.py \
  -a words/top-api-verbs.txt \
  -o words/top-api-nouns.txt \
  --tech spring --tier medium \
  --fields words/fields/top-fields.txt \
  --preview

# [*] Estimated output: ~162,000 lines
```

---

## Output Sizing Guide

Approximate output sizes with the included seed wordlists:

| Configuration | Approx. Output |
|---------------|---------------:|
| `--tier high -f kebab -p 2` | ~17,000 |
| `--tier high --tech spring` | ~160,000 |
| `--profile recon` | ~50,000 |
| `--tier medium -p 2 rest` | ~150,000 |
| `--tech django --tier high` | ~85,000 |
| `--profile full` (all patterns, all formats, all tiers) | millions |

Use `--preview` to get an estimate before generating. Use `--limit N` to cap the output.

---

## Author

**Cipher**

Built for penetration testers who need precision over volume.
