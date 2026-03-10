#!/usr/bin/env python3
"""
API Wordlist Generator — Cipher's Combinatorial Engine v3
Generates crafted API endpoint wordlists from seed wordlists using naming conventions
and path patterns observed in real-world APIs.

Zero dependencies. Pure Python 3.

Author: Cipher
"""

import argparse
import sys
import os
import re
import itertools
from pathlib import Path


# ─────────────────────────────────────────────
# PLURALIZATION ENGINE
# ─────────────────────────────────────────────

IRREGULAR_PLURALS = {
    "person": "people", "child": "children", "man": "men", "woman": "women",
    "mouse": "mice", "foot": "feet", "tooth": "teeth", "goose": "geese",
    "ox": "oxen", "analysis": "analyses", "crisis": "crises", "basis": "bases",
    "datum": "data", "medium": "media", "criterion": "criteria",
    "phenomenon": "phenomena", "index": "indices", "vertex": "vertices",
    "matrix": "matrices", "appendix": "appendices", "schema": "schemas",
    "status": "statuses", "alias": "aliases", "bus": "buses", "canvas": "canvases",
    "address": "addresses", "process": "processes", "access": "accesses",
    "class": "classes", "search": "searches", "batch": "batches",
    "match": "matches", "patch": "patches", "switch": "switches",
    "cache": "caches", "database": "databases", "message": "messages",
    "resource": "resources", "response": "responses", "release": "releases",
    "device": "devices", "service": "services", "license": "licenses",
    "invoice": "invoices", "interface": "interfaces", "instance": "instances",
    "practice": "practices", "source": "sources", "namespace": "namespaces",
    "pipeline": "pipelines", "schedule": "schedules", "template": "templates",
    "leaf": "leaves", "knife": "knives", "life": "lives", "self": "selves",
    "half": "halves", "shelf": "shelves", "wolf": "wolves",
    "quiz": "quizzes",
}

# Words that are already plural or uncountable
UNCOUNTABLE = {
    "data", "media", "metadata", "info", "information", "feedback", "software",
    "hardware", "firmware", "middleware", "malware", "analytics", "metrics",
    "statistics", "stats", "news", "series", "species", "sheep", "fish",
    "dns", "sms", "ssl", "tls", "ssh", "cdn", "cors", "csrf", "gdpr",
    "hipaa", "oauth", "oauth2", "saml", "oidc", "ldap", "sso", "mfa",
    "health", "compliance", "evidence", "guidance", "insurance",
    "maintenance", "performance", "surveillance", "telemetry",
}


def pluralize(word):
    """Pluralize an English word. Handles API-common nouns well."""
    if not word:
        return word
    low = word.lower()

    if low in UNCOUNTABLE:
        return word
    # Already looks plural
    if low.endswith("s") and not low.endswith(("ss", "us", "is", "xs")):
        return word
    if low in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[low]
    # Rules
    if low.endswith(("s", "sh", "ch", "x", "z")):
        return word + "es"
    if low.endswith("y") and len(low) > 1 and low[-2] not in "aeiou":
        return word[:-1] + "ies"
    if low.endswith("fe"):
        return word[:-2] + "ves"
    if low.endswith("f") and not low.endswith("ff"):
        return word[:-1] + "ves"
    return word + "s"


# ─────────────────────────────────────────────
# PRIORITY TIERS
# ─────────────────────────────────────────────

HIGH_TIER_ACTIONS = {
    "get", "list", "create", "update", "delete", "search", "find", "post", "put",
    "patch", "read", "write", "save", "remove", "add", "edit", "fetch", "show",
    "login", "logout", "register", "signup", "signin", "signout", "reset",
    "verify", "validate", "confirm", "check", "test", "ping",
    "upload", "download", "export", "import", "sync",
    "activate", "deactivate", "enable", "disable",
    "approve", "reject", "submit", "cancel",
    "subscribe", "unsubscribe", "publish", "unpublish",
    "lock", "unlock", "block", "unblock",
    "archive", "restore", "backup",
    "invite", "revoke", "grant",
    "count", "aggregate", "batch", "bulk",
    "start", "stop", "restart", "pause", "resume",
    "connect", "disconnect", "join",
    "health", "healthcheck", "status", "info", "version",
}

HIGH_TIER_OBJECTS = {
    "user", "users", "account", "accounts", "auth", "authentication",
    "token", "tokens", "session", "sessions", "login", "password", "passwords",
    "role", "roles", "permission", "permissions", "group", "groups",
    "key", "keys", "apikey", "apikeys", "secret", "secrets",
    "order", "orders", "payment", "payments", "invoice", "invoices",
    "product", "products", "item", "items", "cart", "carts",
    "subscription", "subscriptions", "plan", "plans",
    "config", "configs", "setting", "settings", "preference", "preferences",
    "profile", "profiles", "email", "emails", "notification", "notifications",
    "message", "messages", "comment", "comments",
    "file", "files", "upload", "uploads", "image", "images", "document", "documents",
    "report", "reports", "log", "logs", "event", "events", "audit", "audits",
    "webhook", "webhooks", "callback", "callbacks",
    "project", "projects", "task", "tasks", "job", "jobs",
    "team", "teams", "member", "members", "organization", "organizations",
    "tenant", "tenants", "workspace", "workspaces",
    "customer", "customers", "contact", "contacts",
    "health", "status", "info", "version", "metrics", "stats",
    "tag", "tags", "category", "categories", "label", "labels",
    "dashboard", "dashboards", "search",
    "schema", "schemas", "endpoint", "endpoints",
    "resource", "resources", "service", "services",
    "database", "databases", "collection", "collections",
}

MEDIUM_TIER_ACTIONS = HIGH_TIER_ACTIONS | {
    "assign", "unassign", "associate", "disassociate",
    "clone", "copy", "duplicate", "merge", "split",
    "link", "unlink", "map", "unmap", "bind", "unbind",
    "encrypt", "decrypt", "hash", "encode", "decode",
    "deploy", "undeploy", "rollback", "migrate", "provision",
    "schedule", "unschedule", "trigger", "execute", "run",
    "monitor", "trace", "audit", "scan", "inspect",
    "flag", "unflag", "mark", "unmark", "tag", "untag",
    "follow", "unfollow", "like", "unlike", "star", "unstar",
    "share", "unshare", "pin", "unpin", "mute", "unmute",
    "transfer", "convert", "transform", "process",
    "cache", "flush", "purge", "clear", "drain",
    "enqueue", "dequeue", "dispatch", "relay", "forward",
    "authorize", "authenticate", "impersonate",
    "claim", "release", "reserve", "expire",
    "promote", "demote", "escalate", "throttle",
    "render", "preview", "generate", "compile",
    "notify", "broadcast", "send", "deliver",
    "load", "reload", "refresh", "revalidate",
    "scale", "resize", "rotate", "configure",
    "mount", "unmount", "attach", "detach",
    "install", "uninstall", "upgrade", "downgrade",
}

MEDIUM_TIER_OBJECTS = HIGH_TIER_OBJECTS | {
    "address", "addresses", "phone", "phones",
    "badge", "badges", "reward", "rewards", "achievement", "achievements",
    "campaign", "campaigns", "coupon", "coupons", "discount", "discounts",
    "charge", "charges", "refund", "refunds", "credit", "credits", "payout", "payouts",
    "shipping", "shipment", "shipments", "tracking",
    "inventory", "stock", "warehouse",
    "device", "devices", "sensor", "sensors",
    "certificate", "certificates", "credential", "credentials",
    "pipeline", "pipelines", "workflow", "workflows",
    "template", "templates", "draft", "drafts", "revision", "revisions",
    "attachment", "attachments", "media", "asset", "assets",
    "policy", "policies", "rule", "rules", "constraint", "constraints",
    "scope", "scopes", "claim", "claims", "grant", "grants",
    "connection", "connections", "integration", "integrations",
    "environment", "environments", "namespace", "namespaces",
    "cluster", "clusters", "node", "nodes", "pod", "pods", "container", "containers",
    "instance", "instances", "replica", "replicas",
    "queue", "queues", "topic", "topics", "channel", "channels",
    "alert", "alerts", "incident", "incidents",
    "hook", "hooks", "trigger", "triggers",
    "migration", "migrations", "backup", "backups", "snapshot", "snapshots",
    "batch", "batches", "schedule", "schedules", "cron", "crons",
    "release", "releases", "deployment", "deployments", "build", "builds",
    "test", "tests", "scan", "scans",
    "vote", "votes", "reaction", "reactions", "review", "reviews",
    "bookmark", "bookmarks", "favorite", "favorites",
    "thread", "threads", "conversation", "conversations",
    "note", "notes", "annotation", "annotations",
    "variable", "variables", "parameter", "parameters",
    "record", "records", "entry", "entries",
    "domain", "domains", "dns", "ssl", "tls",
    "proxy", "proxies", "gateway", "gateways", "route", "routes",
    "balance", "balances", "transaction", "transactions", "ledger",
    "currency", "currencies",
}


def filter_by_tier(words, tier, tier_high, tier_medium):
    """Filter a word list by priority tier."""
    if tier == "all":
        return words
    if tier == "high":
        return [w for w in words if w in tier_high]
    if tier == "medium":
        return [w for w in words if w in tier_medium]
    return words


# ─────────────────────────────────────────────
# HTTP METHOD MAPPING
# ─────────────────────────────────────────────

VERB_TO_METHOD = {
    # GET
    "get": "GET", "list": "GET", "search": "GET", "find": "GET", "fetch": "GET",
    "read": "GET", "show": "GET", "view": "GET", "check": "GET", "count": "GET",
    "export": "GET", "download": "GET", "browse": "GET", "lookup": "GET",
    "describe": "GET", "query": "GET", "select": "GET", "retrieve": "GET",
    "exists": "GET", "peek": "GET", "scan": "GET", "explore": "GET",
    "health": "GET", "healthcheck": "GET", "ping": "GET", "status": "GET",
    "info": "GET", "version": "GET", "enumerate": "GET", "poll": "GET",
    # POST
    "create": "POST", "add": "POST", "register": "POST", "submit": "POST",
    "upload": "POST", "import": "POST", "login": "POST", "signin": "POST",
    "signup": "POST", "post": "POST", "send": "POST", "invite": "POST",
    "subscribe": "POST", "publish": "POST", "broadcast": "POST",
    "trigger": "POST", "execute": "POST", "run": "POST", "start": "POST",
    "launch": "POST", "deploy": "POST", "provision": "POST",
    "clone": "POST", "copy": "POST", "duplicate": "POST", "fork": "POST",
    "generate": "POST", "batch": "POST", "bulk": "POST", "process": "POST",
    "enqueue": "POST", "schedule": "POST", "notify": "POST",
    "validate": "POST", "verify": "POST", "confirm": "POST",
    "analyze": "POST", "compute": "POST", "calculate": "POST",
    "encrypt": "POST", "decrypt": "POST", "encode": "POST", "decode": "POST",
    "translate": "POST", "transform": "POST", "convert": "POST",
    # PUT
    "update": "PUT", "edit": "PUT", "modify": "PUT", "replace": "PUT",
    "put": "PUT", "set": "PUT", "save": "PUT", "write": "PUT",
    "upsert": "PUT", "overwrite": "PUT", "rename": "PUT",
    # PATCH
    "patch": "PATCH",
    # DELETE
    "delete": "DELETE", "remove": "DELETE", "destroy": "DELETE", "purge": "DELETE",
    "drop": "DELETE", "erase": "DELETE", "unsubscribe": "DELETE",
    "revoke": "DELETE", "cancel": "DELETE", "void": "DELETE",
    "unregister": "DELETE", "uninstall": "DELETE", "unpublish": "DELETE",
}


def infer_method(endpoint, action_hint=None):
    """Infer HTTP method from endpoint string or explicit action hint."""
    if action_hint and action_hint in VERB_TO_METHOD:
        return VERB_TO_METHOD[action_hint]

    # Try to extract verb from endpoint structure
    low = endpoint.lower().lstrip("/")
    # REST path: first or last meaningful segment
    segments = [s for s in low.replace("{id}", "").replace("{sid}", "").split("/") if s]
    candidates = []
    if segments:
        candidates.append(segments[-1])  # last segment most likely the action
        candidates.append(segments[0])   # or first

    # camelCase/PascalCase: extract first word
    camel_match = re.match(r'^([a-z]+)', low.replace("-", "").replace("_", "").replace("/", ""))
    if camel_match:
        candidates.append(camel_match.group(1))

    # kebab/snake: first segment
    for sep in ["-", "_", "."]:
        if sep in low:
            candidates.append(low.split(sep)[0])
            break

    for c in candidates:
        if c in VERB_TO_METHOD:
            return VERB_TO_METHOD[c]
    return "GET"


# ─────────────────────────────────────────────
# INPUT CLEANING PIPELINE
# ─────────────────────────────────────────────

def clean_word(word):
    """Clean a single word: strip, lowercase, remove non-alphanumeric."""
    word = word.strip().lower()
    word = re.sub(r'[^a-z0-9]', '', word)
    return word if word else None


def clean_wordlist(words_raw, min_length=2, remove_numbers_only=True):
    """Full cleaning pipeline: strip -> remove empties/comments -> lowercase ->
    remove special chars -> min length -> remove pure numbers -> dedup -> sort."""
    stats = {
        "raw_total": len(words_raw), "empty_removed": 0, "comments_removed": 0,
        "short_removed": 0, "numbers_removed": 0, "duplicates_removed": 0,
        "invalid_removed": 0, "final_count": 0,
    }
    cleaned = []
    seen = set()

    for raw_word in words_raw:
        if not raw_word.strip():
            stats["empty_removed"] += 1
            continue
        if raw_word.strip().startswith("#"):
            stats["comments_removed"] += 1
            continue
        word = clean_word(raw_word)
        if word is None:
            stats["invalid_removed"] += 1
            continue
        if len(word) < min_length:
            stats["short_removed"] += 1
            continue
        if remove_numbers_only and word.isdigit():
            stats["numbers_removed"] += 1
            continue
        if word in seen:
            stats["duplicates_removed"] += 1
            continue
        seen.add(word)
        cleaned.append(word)

    cleaned.sort()
    stats["final_count"] = len(cleaned)
    return cleaned, stats


def load_and_clean(filepath, min_length=2, keep_numbers=False, verbose=True):
    """Load a file and run the cleaning pipeline."""
    empty_stats = {"raw_total": 0, "final_count": 0, "empty_removed": 0,
                   "comments_removed": 0, "short_removed": 0, "numbers_removed": 0,
                   "duplicates_removed": 0, "invalid_removed": 0}
    if filepath is None:
        return [], empty_stats

    path = Path(filepath)
    if not path.exists():
        print(f"[!] Warning: File not found: {filepath}", file=sys.stderr)
        return [], empty_stats

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = f.readlines()

    cleaned, stats = clean_wordlist(raw_lines, min_length=min_length,
                                     remove_numbers_only=not keep_numbers)
    if verbose:
        removed = stats["raw_total"] - stats["final_count"]
        if removed > 0:
            print(f"[*] Loaded {filepath}", file=sys.stderr)
            print(f"    Raw: {stats['raw_total']:>6} -> Cleaned: {stats['final_count']:>6} "
                  f"(removed {removed}: "
                  f"{stats['duplicates_removed']} dupes, "
                  f"{stats['short_removed']} short, "
                  f"{stats['empty_removed']} empty, "
                  f"{stats['numbers_removed']} nums, "
                  f"{stats['comments_removed']} comments, "
                  f"{stats['invalid_removed']} invalid)",
                  file=sys.stderr)
        else:
            print(f"[*] Loaded {filepath} -- {stats['final_count']:>6} words (clean)",
                  file=sys.stderr)
    return cleaned, stats


def save_cleaned_wordlist(words, original_path, output_dir):
    """Save a cleaned wordlist to the output directory."""
    os.makedirs(output_dir, exist_ok=True)
    filename = Path(original_path).stem + "_cleaned.txt"
    outpath = os.path.join(output_dir, filename)
    with open(outpath, "w", encoding="utf-8") as f:
        f.write("\n".join(words) + "\n")
    print(f"    [saved] {outpath} ({len(words)} words)", file=sys.stderr)
    return outpath


# ─────────────────────────────────────────────
# CASING / FORMAT TRANSFORMS
# ─────────────────────────────────────────────

def to_kebab(*parts):
    return "-".join(p.lower() for p in parts if p)

def to_snake(*parts):
    return "_".join(p.lower() for p in parts if p)

def to_dot(*parts):
    return ".".join(p.lower() for p in parts if p)

def to_concat(*parts):
    return "".join(p.lower() for p in parts if p)

def to_camel(*parts):
    parts = [p for p in parts if p]
    if not parts:
        return ""
    return parts[0].lower() + "".join(w.capitalize() for w in parts[1:])

def to_pascal(*parts):
    return "".join(w.capitalize() for w in parts if w)

def to_path(*parts):
    return "/" + "/".join(p.lower() for p in parts if p)


FORMAT_FUNCTIONS = {
    "kebab": to_kebab, "snake": to_snake, "dot": to_dot,
    "concat": to_concat, "camel": to_camel, "pascal": to_pascal, "path": to_path,
}

FORMAT_CASING = {
    "kebab":  "all lowercase, hyphen          -> create-user",
    "snake":  "all lowercase, underscore       -> create_user",
    "dot":    "all lowercase, dot              -> create.user",
    "concat": "all lowercase, no separator     -> createuser",
    "camel":  "first lower, rest Capitalized   -> createUser",
    "pascal": "every word Capitalized           -> CreateUser",
    "path":   "all lowercase, slash            -> /create/user",
}


# ─────────────────────────────────────────────
# PATTERN GENERATORS
# ─────────────────────────────────────────────

def pattern_2part(actions, objects, fmt_fn):
    """action{sep}object + object{sep}action"""
    results = set()
    for a, o in itertools.product(actions, objects):
        results.add(fmt_fn(a, o))
        results.add(fmt_fn(o, a))
    return results


def pattern_3part(actions, objects, modifiers, fmt_fn):
    """3-part combos — only the 3 realistic permutations:
      action-modifier-object  -> get-all-users
      modifier-action-object  -> bulk-create-orders
      action-object-modifier  -> export-orders-csv
    """
    results = set()
    for a, o, m in itertools.product(actions, objects, modifiers):
        results.add(fmt_fn(a, m, o))    # get-all-users
        results.add(fmt_fn(m, a, o))    # bulk-create-users
        results.add(fmt_fn(a, o, m))    # export-orders-csv
    return results


def pattern_rest(actions, objects, sub_objects=None, prefixes=None,
                 use_plural=True, trailing_slash=False):
    """REST path patterns with plural intelligence."""
    results = set()
    sl = "/" if trailing_slash else ""

    for a, o in itertools.product(actions, objects):
        pl = pluralize(o) if use_plural else o
        # Collection
        results.add(f"/{pl}{sl}")
        results.add(f"/{pl}/{a}{sl}")
        # Single resource
        results.add(f"/{pl}/{{id}}{sl}")
        results.add(f"/{pl}/{{id}}/{a}{sl}")
        # Action-first variant
        results.add(f"/{a}/{pl}{sl}")
        # Singular resource (e.g. /user/me, /user/current)
        results.add(f"/{o}/{a}{sl}")

    # Special singleton endpoints
    for o in objects:
        pl = pluralize(o) if use_plural else o
        for special in ["me", "self", "current", "search", "count", "batch", "bulk", "export", "import"]:
            results.add(f"/{pl}/{special}{sl}")

    if sub_objects:
        for a, o, s in itertools.product(actions, objects, sub_objects):
            pl_o = pluralize(o) if use_plural else o
            results.add(f"/{pl_o}/{{id}}/{s}{sl}")
            results.add(f"/{pl_o}/{{id}}/{s}/{a}{sl}")
            results.add(f"/{pl_o}/{{id}}/{s}/{{sid}}{sl}")
            results.add(f"/{pl_o}/{{id}}/{s}/{{sid}}/{a}{sl}")

    if prefixes:
        for a, o, p in itertools.product(actions, objects, prefixes):
            pl = pluralize(o) if use_plural else o
            results.add(f"/{p}/{pl}{sl}")
            results.add(f"/{p}/{pl}/{a}{sl}")
            results.add(f"/{p}/{pl}/{{id}}{sl}")
            results.add(f"/{p}/{pl}/{{id}}/{a}{sl}")

    return results


def pattern_byfield(actions, objects, fields, fmt_fn):
    """ByField patterns using the selected format function.
      getUserByEmail (camel), get_user_by_email (snake), get-user-by-email (kebab), etc.
    """
    results = set()
    connectors = ["by", "with", "for", "from", "using"]
    for a, o, f in itertools.product(actions, objects, fields):
        for conn in connectors:
            results.add(fmt_fn(a, o, conn, f))
    return results


def pattern_prefixed(actions, objects, prefixes, fmt_fn):
    """prefix{sep}action{sep}object + prefix{sep}object{sep}action"""
    results = set()
    for a, o, p in itertools.product(actions, objects, prefixes):
        results.add(fmt_fn(p, a, o))
        results.add(fmt_fn(p, o, a))
    return results


def pattern_suffixed(actions, objects, suffixes, fmt_fn):
    """action{sep}object{sep}suffix + object{sep}action{sep}suffix"""
    results = set()
    for a, o, s in itertools.product(actions, objects, suffixes):
        results.add(fmt_fn(a, o, s))
        results.add(fmt_fn(o, a, s))
    return results


def pattern_event(actions, objects, fmt_fn):
    """Event/callback patterns."""
    results = set()
    event_prefixes = ["on", "handle", "before", "after"]
    single_prefixes = ["do", "process", "trigger", "is", "has", "can", "should"]

    # 3-part: prefix + object + action (requires both)
    for a, o in itertools.product(actions, objects):
        for ep in event_prefixes:
            results.add(fmt_fn(ep, o, a))
        for sp in single_prefixes:
            results.add(fmt_fn(sp, a, o))

    # 2-part: prefix + action OR prefix + object (independent)
    for sp in single_prefixes:
        for a in actions:
            results.add(fmt_fn(sp, a))
        for o in objects:
            results.add(fmt_fn(sp, o))

    return results


# ─────────────────────────────────────────────
# ESTIMATION
# ─────────────────────────────────────────────

def estimate_output(actions, objects, modifiers, prefixes, suffixes, fields,
                    sub_objects, formats, patterns):
    """Rough upper-bound estimate of output lines."""
    a, o = len(actions), len(objects)
    m = len(modifiers) if modifiers else 0
    p = len(prefixes) if prefixes else 0
    s = len(suffixes) if suffixes else 0
    fl = len(fields) if fields else 0
    so = len(sub_objects) if sub_objects else 0
    nf = len(formats)
    total = 0

    if "2" in patterns:
        total += (a * o * 2) * nf
    if "3" in patterns and m > 0:
        total += (a * o * m * 3) * nf
    if "rest" in patterns:
        total += (a * o * 6) + (o * 9)
        if so > 0:
            total += (a * o * so * 4)
        if p > 0:
            total += (a * o * p * 4)
    if "byfield" in patterns and fl > 0:
        total += (a * o * fl * 5) * nf
    if "prefixed" in patterns and p > 0:
        total += (a * o * p * 2) * nf
    if "suffixed" in patterns and s > 0:
        total += (a * o * s * 2) * nf
    if "event" in patterns:
        total += (a * o * (4 + 7)) * nf + (7 * (a + o)) * nf

    return total


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Cipher's API Wordlist Generator v3 — Combinatorial endpoint builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Basic 2-part kebab + camel
  %(prog)s -a actions.txt -o objects.txt -f kebab camel -p 2

  # High-tier REST paths with nested resources
  %(prog)s -a actions.txt -o objects.txt -p rest --tier high \\
           --sub-objects subs.txt --prefixes prefixes.txt -O rest.txt

  # Spring-style camelCase with byField lookups
  %(prog)s -a actions.txt -o objects.txt -f camel -p 2 byfield event \\
           --fields fields.txt --tier high -O spring-style.txt

  # Django-style snake_case REST with trailing slashes
  %(prog)s -a actions.txt -o objects.txt -f snake -p 2 rest \\
           --trailing-slash --tier medium -O django-style.txt

  # ASP.NET-style PascalCase with byField
  %(prog)s -a actions.txt -o objects.txt -f pascal -p 2 byfield \\
           --fields fields.txt -O dotnet-style.txt

  # Go-style kebab REST paths
  %(prog)s -a actions.txt -o objects.txt -f kebab -p rest \\
           --tier high -O go-style.txt

  # Full generation with all patterns and HTTP method hints
  %(prog)s -a actions.txt -o objects.txt -m modifiers.txt \\
           --prefixes prefixes.txt --suffixes suffixes.txt \\
           --fields fields.txt --sub-objects subs.txt \\
           -f all -p all --methods --sort -O everything.txt

  # Output with HTTP method hints
  %(prog)s -a actions.txt -o objects.txt --methods -O methods.txt

  # Clean dirty wordlists without generating
  %(prog)s -a dirty.txt -o messy.txt --clean-only --save-cleaned cleaned/

FORMATS (-f):
  kebab  -> create-user    snake  -> create_user    camel  -> createUser
  pascal -> CreateUser     dot    -> create.user    concat -> createuser
  path   -> /create/user   all    -> all of the above

PATTERNS (-p):
  2        action+object (2-part combos)
  3        action+modifier+object (3-part, needs -m)
  rest     /resource/{id}/action (REST paths with plural intelligence)
  byfield  getUserByEmail (needs --fields)
  prefixed admin-create-user (needs --prefixes)
  suffixed export-orders-csv (needs --suffixes)
  event    onUserCreate, handlePayment, doExport
  all      all patterns

PRIORITY TIERS (--tier):
  high     ~68 core verbs x ~124 common resources — fast, focused
  medium   ~167 verbs x ~288 resources — good coverage
  all      Everything in your seed files — maximum breadth
        """
    )

    # ── Required wordlists ──
    parser.add_argument("-a", "--actions", required=True,
                        help="Path to actions/verbs wordlist")
    parser.add_argument("-o", "--objects", required=True,
                        help="Path to objects/nouns wordlist")

    # ── Optional wordlists ──
    parser.add_argument("-m", "--modifiers", default=None,
                        help="Path to modifiers wordlist (for 3-part patterns)")
    parser.add_argument("--prefixes", default=None,
                        help="Path to prefixes wordlist (for prefixed/REST patterns)")
    parser.add_argument("--suffixes", default=None,
                        help="Path to suffixes wordlist (for suffixed patterns)")
    parser.add_argument("--fields", default=None,
                        help="Path to fields wordlist (for byField patterns)")
    parser.add_argument("--sub-objects", default=None,
                        help="Path to sub-objects wordlist (for REST nested patterns)")

    # ── Format & pattern selection ──
    parser.add_argument("-f", "--formats", nargs="+", default=["kebab", "snake", "camel"],
                        choices=["kebab", "snake", "dot", "concat", "camel", "pascal", "path", "all"],
                        help="Output naming formats (default: kebab snake camel)")
    parser.add_argument("-p", "--patterns", nargs="+", default=["2"],
                        choices=["2", "3", "rest", "byfield", "prefixed", "suffixed", "event", "all"],
                        help="Patterns to generate (default: 2)")

    # ── Tier & options ──
    parser.add_argument("--tier", default="all",
                        choices=["high", "medium", "all"],
                        help="Priority tier — filter seed words by frequency (default: all)")
    parser.add_argument("--methods", action="store_true", default=False,
                        help="Prefix output with HTTP method hints (GET /path)")
    parser.add_argument("--trailing-slash", action="store_true", default=False,
                        help="Add trailing slash to REST paths")
    parser.add_argument("--no-plural", action="store_true", default=False,
                        help="Disable auto-pluralization in REST patterns")

    # ── Cleaning options ──
    parser.add_argument("--min-length", type=int, default=2,
                        help="Minimum word length after cleaning (default: 2)")
    parser.add_argument("--keep-numbers", action="store_true", default=False,
                        help="Keep pure number strings like '123' (default: remove)")
    parser.add_argument("--clean-only", action="store_true", default=False,
                        help="Only clean input wordlists and exit")
    parser.add_argument("--save-cleaned", default=None, metavar="DIR",
                        help="Save cleaned wordlists to directory")

    # ── Output control ──
    parser.add_argument("--output", "-O", default=None,
                        help="Output file (default: stdout)")
    parser.add_argument("--sort", action="store_true", default=False,
                        help="Sort output alphabetically")
    parser.add_argument("--stats", action="store_true", default=False,
                        help="Print generation stats to stderr")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit output to N lines (0 = no limit)")
    parser.add_argument("--no-dedup", action="store_true", default=False,
                        help="Skip deduplication (faster for huge lists)")
    parser.add_argument("--preview", action="store_true", default=False,
                        help="Show estimated line count and exit")

    args = parser.parse_args()

    # ─────────────────────────────────────────
    # RESOLVE "ALL"
    # ─────────────────────────────────────────
    if "all" in args.formats:
        args.formats = list(FORMAT_FUNCTIONS.keys())
    if "all" in args.patterns:
        args.patterns = ["2", "3", "rest", "byfield", "prefixed", "suffixed", "event"]

    # ─────────────────────────────────────────
    # LOAD + CLEAN WORDLISTS
    # ─────────────────────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  CIPHER'S API WORDLIST GENERATOR v3", file=sys.stderr)
    print(f"  Tier: {args.tier} | Formats: {', '.join(args.formats)} | "
          f"Patterns: {', '.join(args.patterns)}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    sources = {}

    actions, a_stats = load_and_clean(args.actions, min_length=args.min_length,
                                       keep_numbers=args.keep_numbers)
    sources["actions"] = (args.actions, actions, a_stats)

    objects, o_stats = load_and_clean(args.objects, min_length=args.min_length,
                                      keep_numbers=args.keep_numbers)
    sources["objects"] = (args.objects, objects, o_stats)

    modifiers, m_stats = load_and_clean(args.modifiers, min_length=args.min_length,
                                         keep_numbers=args.keep_numbers)
    sources["modifiers"] = (args.modifiers, modifiers, m_stats)

    prefixes, p_stats = load_and_clean(args.prefixes, min_length=args.min_length,
                                        keep_numbers=args.keep_numbers)
    sources["prefixes"] = (args.prefixes, prefixes, p_stats)

    suffixes, s_stats = load_and_clean(args.suffixes, min_length=args.min_length,
                                        keep_numbers=args.keep_numbers)
    sources["suffixes"] = (args.suffixes, suffixes, s_stats)

    fields, f_stats = load_and_clean(args.fields, min_length=args.min_length,
                                      keep_numbers=args.keep_numbers)
    sources["fields"] = (args.fields, fields, f_stats)

    sub_objects, so_stats = load_and_clean(args.sub_objects, min_length=args.min_length,
                                            keep_numbers=args.keep_numbers)
    sources["sub_objects"] = (args.sub_objects, sub_objects, so_stats)

    # Print cleaning summary
    has_loaded = any(fpath is not None for _, (fpath, _, _) in sources.items())
    if has_loaded:
        print(f"\n  {'Wordlist':<15} {'Raw':>8} {'Cleaned':>8} {'Removed':>8}", file=sys.stderr)
        print(f"  {'-'*43}", file=sys.stderr)
        for name, (fpath, words, stats) in sources.items():
            if fpath is not None:
                removed = stats["raw_total"] - stats["final_count"]
                print(f"  {name:<15} {stats['raw_total']:>8} {stats['final_count']:>8} {removed:>8}",
                      file=sys.stderr)
        print(f"  {'-'*43}", file=sys.stderr)

    # Save cleaned wordlists if requested
    if args.save_cleaned:
        print(f"\n[+] Saving cleaned wordlists to: {args.save_cleaned}/", file=sys.stderr)
        for name, (fpath, words, stats) in sources.items():
            if fpath is not None and words:
                save_cleaned_wordlist(words, fpath, args.save_cleaned)

    if args.clean_only:
        print(f"\n[+] Clean-only mode. No combos generated.", file=sys.stderr)
        if not args.save_cleaned:
            print(f"[*] Tip: Use --save-cleaned DIR to save the cleaned files.", file=sys.stderr)
        sys.exit(0)

    # ─────────────────────────────────────────
    # APPLY TIER FILTERING
    # ─────────────────────────────────────────
    if args.tier != "all":
        pre_a, pre_o = len(actions), len(objects)
        actions = filter_by_tier(actions, args.tier, HIGH_TIER_ACTIONS, MEDIUM_TIER_ACTIONS)
        objects = filter_by_tier(objects, args.tier, HIGH_TIER_OBJECTS, MEDIUM_TIER_OBJECTS)
        print(f"\n[*] Tier '{args.tier}' filter: actions {pre_a}->{len(actions)}, "
              f"objects {pre_o}->{len(objects)}", file=sys.stderr)

    # Validate
    if not actions:
        print("[!] Error: Actions wordlist is empty (or all filtered by tier).", file=sys.stderr)
        sys.exit(1)
    if not objects:
        print("[!] Error: Objects wordlist is empty (or all filtered by tier).", file=sys.stderr)
        sys.exit(1)

    # ─────────────────────────────────────────
    # DEPENDENCY CHECKS
    # ─────────────────────────────────────────
    if "3" in args.patterns and not modifiers:
        print("[!] Warning: Pattern '3' requires --modifiers (-m). Skipping.", file=sys.stderr)
        args.patterns = [p for p in args.patterns if p != "3"]
    if "byfield" in args.patterns and not fields:
        print("[!] Warning: Pattern 'byfield' requires --fields. Skipping.", file=sys.stderr)
        args.patterns = [p for p in args.patterns if p != "byfield"]
    if "prefixed" in args.patterns and not prefixes:
        print("[!] Warning: Pattern 'prefixed' requires --prefixes. Skipping.", file=sys.stderr)
        args.patterns = [p for p in args.patterns if p != "prefixed"]
    if "suffixed" in args.patterns and not suffixes:
        print("[!] Warning: Pattern 'suffixed' requires --suffixes. Skipping.", file=sys.stderr)
        args.patterns = [p for p in args.patterns if p != "suffixed"]

    # ─────────────────────────────────────────
    # PREVIEW MODE
    # ─────────────────────────────────────────
    if args.preview:
        est = estimate_output(actions, objects, modifiers, prefixes, suffixes,
                              fields, sub_objects, args.formats, args.patterns)
        print(f"\n[*] Estimated output: ~{est:,} lines", file=sys.stderr)
        print(f"[*] Formats: {', '.join(args.formats)}", file=sys.stderr)
        print(f"[*] Patterns: {', '.join(args.patterns)}", file=sys.stderr)
        sys.exit(0)

    # ─────────────────────────────────────────
    # GENERATE
    # ─────────────────────────────────────────
    print(f"\n[+] Generating wordlist...", file=sys.stderr)
    print(f"    Formats: {', '.join(args.formats)}", file=sys.stderr)
    print(f"    Patterns: {', '.join(args.patterns)}", file=sys.stderr)

    if args.no_dedup:
        all_results = []
    else:
        all_results = set()

    def collect(results):
        if args.no_dedup:
            all_results.extend(results)
        else:
            all_results.update(results)

    pattern_stats = {}
    use_plural = not args.no_plural

    for pattern in args.patterns:
        pattern_results = set()

        if pattern == "2":
            for fmt_name in args.formats:
                fmt_fn = FORMAT_FUNCTIONS[fmt_name]
                pattern_results.update(pattern_2part(actions, objects, fmt_fn))

        elif pattern == "3":
            for fmt_name in args.formats:
                fmt_fn = FORMAT_FUNCTIONS[fmt_name]
                pattern_results.update(pattern_3part(actions, objects, modifiers, fmt_fn))

        elif pattern == "rest":
            pattern_results.update(pattern_rest(
                actions, objects, sub_objects, prefixes,
                use_plural=use_plural, trailing_slash=args.trailing_slash
            ))

        elif pattern == "byfield":
            for fmt_name in args.formats:
                fmt_fn = FORMAT_FUNCTIONS[fmt_name]
                pattern_results.update(pattern_byfield(actions, objects, fields, fmt_fn))

        elif pattern == "prefixed":
            for fmt_name in args.formats:
                fmt_fn = FORMAT_FUNCTIONS[fmt_name]
                pattern_results.update(pattern_prefixed(actions, objects, prefixes, fmt_fn))

        elif pattern == "suffixed":
            for fmt_name in args.formats:
                fmt_fn = FORMAT_FUNCTIONS[fmt_name]
                pattern_results.update(pattern_suffixed(actions, objects, suffixes, fmt_fn))

        elif pattern == "event":
            for fmt_name in args.formats:
                fmt_fn = FORMAT_FUNCTIONS[fmt_name]
                pattern_results.update(pattern_event(actions, objects, fmt_fn))

        count = len(pattern_results)
        pattern_stats[pattern] = count
        collect(pattern_results)
        print(f"    [{pattern:>8}] -> {count:>10,} entries", file=sys.stderr)

    # ─────────────────────────────────────────
    # POST-PROCESS: Methods, Sort, Limit
    # ─────────────────────────────────────────
    if args.no_dedup:
        output_list = all_results
    else:
        output_list = list(all_results)

    # Apply HTTP method hints
    if args.methods:
        output_list = [f"{infer_method(ep)} {ep}" for ep in output_list]

    # Sort
    if args.sort:
        output_list.sort()

    # Limit
    if args.limit > 0:
        output_list = output_list[:args.limit]

    # ─────────────────────────────────────────
    # WRITE OUTPUT
    # ─────────────────────────────────────────
    total = len(output_list)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(output_list) + "\n")
        print(f"\n[+] Written {total:,} unique entries -> {args.output}", file=sys.stderr)
    else:
        for entry in output_list:
            print(entry)
        print(f"\n[+] Generated {total:,} unique entries (stdout)", file=sys.stderr)

    # ─────────────────────────────────────────
    # STATS
    # ─────────────────────────────────────────
    if args.stats:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"  GENERATION STATS", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print(f"  Priority Tier: {args.tier}", file=sys.stderr)
        print(f"  Pluralization: {'enabled' if use_plural else 'disabled'}", file=sys.stderr)
        print(f"  HTTP Methods: {'enabled' if args.methods else 'disabled'}", file=sys.stderr)
        print(f"  Trailing Slash: {'enabled' if args.trailing_slash else 'disabled'}", file=sys.stderr)

        print(f"\n  Seed Wordlists (after cleaning + tier filter):", file=sys.stderr)
        print(f"    {'Name':<15} {'Clean':>6}", file=sys.stderr)
        print(f"    {'-'*25}", file=sys.stderr)
        print(f"    {'actions':<15} {len(actions):>6}", file=sys.stderr)
        print(f"    {'objects':<15} {len(objects):>6}", file=sys.stderr)
        if modifiers:
            print(f"    {'modifiers':<15} {len(modifiers):>6}", file=sys.stderr)
        if prefixes:
            print(f"    {'prefixes':<15} {len(prefixes):>6}", file=sys.stderr)
        if suffixes:
            print(f"    {'suffixes':<15} {len(suffixes):>6}", file=sys.stderr)
        if fields:
            print(f"    {'fields':<15} {len(fields):>6}", file=sys.stderr)
        if sub_objects:
            print(f"    {'sub_objects':<15} {len(sub_objects):>6}", file=sys.stderr)

        print(f"\n  Casing Rules:", file=sys.stderr)
        for fmt in args.formats:
            print(f"    {FORMAT_CASING[fmt]}", file=sys.stderr)

        print(f"\n  Pattern Breakdown:", file=sys.stderr)
        for pat, count in pattern_stats.items():
            print(f"    {pat:>12}: {count:>10,}", file=sys.stderr)
        print(f"  {'-'*30}", file=sys.stderr)
        print(f"  {'Total output':>12}: {total:>10,}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)


if __name__ == "__main__":
    main()
