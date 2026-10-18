#!/usr/bin/env python3

# >>> minspec:managed:validate-py >>>
"""MinSpec mid-tier validator (DR-037 / #246).

FATAL checks, modelled on MinSpec's Node validate-frontmatter:
  - specs/**/*.md must have `id: SPEC-NNN` frontmatter
  - every docs/decisions/*.md (except INDEX.md / README.md) must have
    `id: DR-NNN` frontmatter — keyed on the DIRECTORY, not the filename, so a
    record not named DR-NNN.md is still checked, never silently skipped (#1908)
  - docs/domain/*.md must have `type: domain` frontmatter
  - a T3/T4 spec past Clarify must declare the code it owns (SPEC-038):
    `implements:` listing repo-relative source paths, or `implements: none`
    with an `implements_reason:`. FAIL when .minspec/config.json sets
    "ownershipDeclaration": "error", otherwise WARN. An `implements:` or
    `affects:` path that escapes the repo always FAILs.
  - a spec/DR/domain file that cannot be read at all (decode error, permission
    error, a pre-commit `git show` failure) FAILs as `unreadable (<reason>)`;
    it is counted and reported, never skipped in silence (invariant 2, #2630).
    The same applies one level up: if the pre-commit git call that LISTS staged
    files itself errors, that is also a FAIL, not an empty — and therefore
    passing — run.

The id/type checks split frontmatter the way the Node validator does (first
--- ... --- block, split each line on the first colon, trim); the ownership rule
ports the MinSpec extension's own readers. No PyYAML, so it runs on a stock
python3. The id/type checks are not an exact twin of the Node validator: values
checked here go through clean_frontmatter_value (one layer of quotes, a trailing
comment), which the Node side does not do yet, and the Node side has no rule
that a decision record must carry an id. #2297 tracks bringing them level.
Deterministic + offline (Tier-0, DR-004)."""

import json
import os
import re
import subprocess
import sys

FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
SPEC_ID_RE = re.compile(r"^SPEC-\d+$")
DR_ID_RE = re.compile(r"^DR-\d+$")
# A DR is any .md under the decisions dir except the register's own listing
# (no id: of its own) and a conventional README (prose, not a record) — #1908.
DR_EXEMPT_FILENAMES = {"INDEX.md", "README.md"}


def clean_frontmatter_value(raw):
    """Strip a trailing inline comment, then one layer of matching quotes.

    `id: "DR-024"  # note` is well-formed YAML for the string `DR-024`, but the
    naive key:value split above leaves the quotes and comment in `raw` verbatim.
    Comment-stripping runs FIRST so the quoted value's closing quote is still the
    last character when the quote check runs — a quote-then-comment strip order
    would leave the trailing comment sitting where the closing quote is expected
    and the quotes would never come off (#1908).
    """
    value = raw.split("#", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1]
    return value

# Spec-to-code ownership (SPEC-038). The owned-path rules below are generated from
# the MinSpec extension's own definitions, so the two cannot disagree about what a
# declared path is.
OWNED_SRC_EXT_RE = re.compile(r"\.(?:ts|tsx|js|jsx|mjs|cjs|py|sh|bash|json|jsonc|css|scss|less|html|htm|vue|svelte|sql|ya?ml|toml)$", re.IGNORECASE)
OWNED_INFRA_PREFIXES = ("node_modules/", "out/", "dist/", "coverage/", ".git/")
PHASE_STATUSES = ("pending", "in-progress", "done", "skipped")
TIERS = ("T1", "T2", "T3", "T4")
FM_KEY = r"[A-Za-z0-9_][A-Za-z0-9_-]*"
OWNERSHIP_HINTS = {
    "ownership.implements.missing": (
        "Add an `implements:` list of the repo-relative code paths this spec creates "
        "or owns (e.g. `implements: [src/feature.ts]`), or `implements: none` plus a "
        "one-line `implements_reason:` when it owns no code (SPEC-038)."
    ),
    "ownership.implements.invalid": (
        "Each entry must be a repo-relative path: no absolute paths and no ../ escapes."
    ),
}
OWNERSHIP_ADVISORY = (
    "Advisory only, because .minspec/config.json does not set "
    "\"ownershipDeclaration\": \"error\"; set it to make this fail."
)


def repo_root():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return os.getcwd()


def parse_frontmatter(content):
    """Mirror the Node parseFrontmatter: first --- ... --- block, key:value split."""
    m = FM_RE.match(content)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split("\n"):
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        key = key.strip()
        if key:
            fm[key] = rest.strip()
    return fm


def staged_files(root):
    """Staged added/copied/modified files (pre-commit scope). Returns the
    Exception itself on any git error — never `[]` — so a git failure cannot
    be read as "nothing staged" and validate zero files while still exiting 0
    (invariant 2: an errored witness fails the gate closed, visibly, never by
    going quiet)."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=root, capture_output=True, text=True, check=True,
        )
        return [f for f in out.stdout.splitlines() if f.strip()]
    except Exception as exc:
        return exc


def staged_content(root, rel):
    """Content of the staged blob (what is ACTUALLY being committed). Returns
    the Exception itself on failure — never `None` — so the caller can tell
    "nothing to read" apart from "could not read it" (invariant 2)."""
    try:
        out = subprocess.run(
            ["git", "show", ":" + rel],
            cwd=root, capture_output=True, text=True, check=True,
        )
        return out.stdout
    except Exception as exc:
        return exc


def all_md(root, rel_dir):
    base = os.path.join(root, rel_dir)
    found = []
    for dirpath, _dirs, files in os.walk(base):
        for name in files:
            if name.endswith(".md"):
                found.append(os.path.relpath(os.path.join(dirpath, name), root))
    return found


# ── Spec-to-code ownership (SPEC-038) ────────────────────────────────────────
# A line-for-line port of the MinSpec extension's `validateOwnership` and of the
# frontmatter readers it calls (spec.ts, spec-vocabulary.ts, spec-validator.ts,
# ownership-path-rules.ts). MinSpec's test suite runs both over the same inputs,
# and over its own spec corpus, and requires identical verdicts: change the two
# together. Before this port a repo whose CI runs this file never evaluated
# SPEC-038 at all (AIClarityAU/minspec#2250).


def ownership_declaration(root):
    """`ownershipDeclaration` as the extension's loadConfig resolves it: "warn"
    unless .minspec/config.json says otherwise. An unreadable config falls back to
    that default exactly as loadConfig does, but says so rather than silently."""
    path = os.path.join(root, ".minspec", "config.json")
    if not os.path.exists(path):
        return "warn"
    try:
        with open(path, "r", encoding="utf-8") as fh:
            config = json.load(fh)
    except (OSError, ValueError) as exc:
        sys.stderr.write(
            "WARN .minspec/config.json: unreadable (" + str(exc) + "), so the "
            "ownership rule runs at its default, warn, until it parses.\n"
        )
        return "warn"
    value = config.get("ownershipDeclaration") if isinstance(config, dict) else None
    return value if isinstance(value, str) else "warn"


def strip_inline_comment(value):
    """A scalar without surrounding quotes or a trailing ` # comment`."""
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    m = re.search(r"\s#", v)
    return v[:m.start()].strip() if m else v


def parse_frontmatter_yaml(yaml):
    """Top-level scalars plus one indented level (`phases:`), as the extension's
    parser reads them. An empty key with no indented children reads as ""."""
    result = {}
    current_key = None
    nested = None
    for line in yaml.split("\n"):
        trimmed = line.rstrip()
        if trimmed == "" or trimmed.startswith("#"):
            continue
        if re.match(r"\s{2,}[A-Za-z0-9_]", line) and current_key:
            m = re.match("(" + FM_KEY + r")\s*:\s*(.+)$", trimmed.strip())
            if m:
                if nested is None:
                    nested = {}
                nested[m.group(1)] = m.group(2).strip()
            continue
        if nested is not None and current_key:
            result[current_key] = nested if nested else ""
            nested = None
        m = re.match("(" + FM_KEY + r")\s*:\s*(.*)$", trimmed)
        if m:
            current_key = m.group(1)
            value = m.group(2).strip()
            if value == "":
                nested = {}
            else:
                result[current_key] = value
                current_key = None
    if nested is not None and current_key:
        result[current_key] = nested if nested else ""
    return result


def raw_frontmatter_field(raw, key):
    """A top-level (column-0) frontmatter value, comment-stripped. None when the
    key is absent or its value is empty. Horizontal whitespace only after the
    colon, so a block-form key never reads its first list item as a value."""
    block = FM_RE.match(raw)
    if not block:
        return None
    m = re.search(
        "^" + re.escape(key) + r"[ \t]*:[ \t]*(.*)$", block.group(1), re.MULTILINE
    )
    if not m:
        return None
    stripped = strip_inline_comment(m.group(1))
    return stripped if stripped != "" else None


def unquote_token(token):
    return re.sub(r"^[\"']+|[\"']+$", "", token)


def frontmatter_list(raw, key):
    """Tokens of a frontmatter list: inline (`key: a, b` or `key: [a, b]`) or
    block form (`key:` then `  - item` lines). Empty when the key is absent."""
    block = FM_RE.match(raw)
    if not block:
        return []
    inline = raw_frontmatter_field(raw, key)
    if inline is not None:
        return [unquote_token(t) for t in re.split(r"[,\s\[\]]+", inline) if t]
    key_line = re.compile(re.escape(key) + r"[ \t]*:[ \t]*(?:#.*)?$")
    item = re.compile(r"[ \t]+-[ \t]*(.+?)[ \t]*(?:#.*)?$")
    lines = block.group(1).split("\n")
    tokens = []
    for i, line in enumerate(lines):
        if key_line.match(line):
            for cont in lines[i + 1:]:
                if re.match(r"[ \t]*$", cont):
                    continue
                m = item.match(cont)
                if not m:
                    break
                tokens.append(unquote_token(m.group(1)))
            break
    return tokens


def owned_path(token):
    """The normalized repo path a token names, or None when it names no path."""
    t = token.strip()
    t = re.sub(r'^"+|"+$', "", t)
    t = re.sub(r"^'+|'+$", "", t)
    t = t.strip()
    if not t or "/" not in t:
        return None
    p = t.replace("\\", "/")
    return p[2:] if p.startswith("./") else p


def escapes_repo(p):
    return p.startswith("/") or p.startswith("../") or ".." in p.split("/")


def is_escaping_path(token):
    """An absolute path, a ../ climb, or any .. segment: outside the repo."""
    p = owned_path(token)
    return p is not None and escapes_repo(p)


def is_valid_owned_path(token):
    """A repo-relative source path: the only kind of token that declares code.
    Existence is NOT required; a not-yet-created file is valid ownership."""
    p = owned_path(token)
    if p is None or escapes_repo(p):
        return False
    if any(p.startswith(prefix) for prefix in OWNED_INFRA_PREFIXES):
        return False
    return OWNED_SRC_EXT_RE.search(p) is not None


def ownership_violations(content, declaration):
    """SPEC-038 for one spec file's text: [(rule, severity, message), ...].

    Armed only for a primary spec (no `type:`, or `type: requirements`) at T3/T4
    whose `phases.plan` is `in-progress` or `done`. A tier edit arms it exactly as
    a phase advance does, which is how voip-sms-inbox SPEC-003 reached main at T3
    without `implements:` while nothing here checked (#2250)."""
    raw = re.sub(r"\r\n?", "\n", content)
    block = FM_RE.match(raw)
    fm = parse_frontmatter_yaml(block.group(1)) if block else {}
    spec_type = fm.get("type")
    spec_type = spec_type.lower() if isinstance(spec_type, str) else ""
    tier = fm.get("tier")
    tier = strip_inline_comment(tier) if isinstance(tier, str) else ""
    tier = tier if tier in TIERS else "T2"
    phases = fm.get("phases")
    plan = phases.get("plan") if isinstance(phases, dict) else None
    plan = strip_inline_comment(plan) if isinstance(plan, str) else "pending"
    plan = plan if plan in PHASE_STATUSES else "pending"
    if (
        spec_type not in ("", "requirements")
        or tier in ("T1", "T2")
        or plan not in ("in-progress", "done")
    ):
        return []

    implemented = frontmatter_list(raw, "implements")
    is_none = len(implemented) == 1 and implemented[0].lower() == "none"
    has_reason = raw_frontmatter_field(raw, "implements_reason") is not None
    out = []
    if not any(is_valid_owned_path(t) for t in implemented) and not (
        is_none and has_reason
    ):
        out.append((
            "ownership.implements.missing",
            "error" if declaration == "error" else "warning",
            tier + " spec past Clarify does not declare its owned code (implements:).",
        ))
    declared = ([] if is_none else implemented) + frontmatter_list(raw, "affects")
    escaping = [t for t in declared if is_escaping_path(t)]
    if escaping:
        out.append((
            "ownership.implements.invalid",
            "error",
            "implements:/affects: contains invalid owned-code path(s): "
            + ", ".join(escaping) + ".",
        ))
    return out


def main():
    pre_commit = "--pre-commit" in sys.argv[1:]
    root = repo_root()

    if pre_commit:
        targets = staged_files(root)
        if isinstance(targets, Exception):
            sys.stderr.write(
                "FAIL pre-commit: could not list staged files (" + str(targets) + "). "
                "Refusing to treat an unknown staged set as an empty one.\n"
            )
            return 1
        reader = lambda rel: staged_content(root, rel)
    else:
        targets = (
            all_md(root, "specs")
            + all_md(root, os.path.join("docs", "decisions"))
            + all_md(root, os.path.join("docs", "domain"))
        )
        def reader(rel):
            try:
                with open(os.path.join(root, rel), "r", encoding="utf-8") as fh:
                    return fh.read()
            except Exception as exc:
                return exc

    errors = 0
    # Read on the first spec, not up front: a commit that stages no spec never
    # needs it, so a broken config does not nag on every unrelated commit.
    declaration = None

    for rel in targets:
        norm = rel.replace(os.sep, "/")
        is_spec = norm.startswith("specs/") and norm.endswith(".md")
        is_domain = norm.startswith("docs/domain/") and norm.endswith(".md")
        # ANY decision record, not just one named DR-NNN.md — a record kept under a
        # different name (docs/decisions/0024-some-name.md, say) was previously
        # unchecked and unreported as skipped (#1908). The register's own INDEX.md
        # and a conventional README are the only exemptions, since neither carries
        # an id of its own.
        is_dr = (
            norm.startswith("docs/decisions/")
            and norm.endswith(".md")
            and os.path.basename(norm) not in DR_EXEMPT_FILENAMES
        )
        if not (is_spec or is_dr or is_domain):
            continue

        content = reader(rel)
        if isinstance(content, Exception):
            sys.stderr.write(
                "FAIL " + norm + ": unreadable (" + str(content) + ")\n"
            )
            errors += 1
            continue
        fm = parse_frontmatter(content)

        if is_spec:
            spec_id = clean_frontmatter_value(fm.get("id", ""))
            if not spec_id:
                sys.stderr.write(
                    "FAIL " + norm + ": missing `id: SPEC-NNN` frontmatter\n"
                )
                errors += 1
            elif not SPEC_ID_RE.match(spec_id):
                sys.stderr.write(
                    "FAIL " + norm + ": invalid `id: SPEC-NNN` frontmatter (got `" + spec_id + "`)\n"
                )
                errors += 1

            if declaration is None:
                declaration = ownership_declaration(root)
            for rule, severity, message in ownership_violations(content, declaration):
                if severity == "error":
                    sys.stderr.write(
                        "FAIL " + norm + ": " + message + " "
                        + OWNERSHIP_HINTS[rule] + "\n"
                    )
                    errors += 1
                else:
                    sys.stderr.write(
                        "WARN " + norm + ": " + message + " " + OWNERSHIP_ADVISORY + "\n"
                    )

        if is_dr:
            dr_id = clean_frontmatter_value(fm.get("id", ""))
            if not dr_id:
                sys.stderr.write(
                    "FAIL " + norm + ": missing `id: DR-NNN` frontmatter\n"
                )
                errors += 1
            elif not DR_ID_RE.match(dr_id):
                sys.stderr.write(
                    "FAIL " + norm + ": invalid `id: DR-NNN` frontmatter (got `" + dr_id + "`)\n"
                )
                errors += 1

        if is_domain:
            if clean_frontmatter_value(fm.get("type", "")) != "domain":
                sys.stderr.write(
                    "FAIL " + norm + ": missing `type: domain` frontmatter\n"
                )
                errors += 1

    if errors:
        sys.stderr.write(
            "\n" + str(errors) + " validation error(s). Fix before committing.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
# <<< minspec:managed:validate-py <<<
