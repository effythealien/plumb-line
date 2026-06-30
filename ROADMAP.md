# Roadmap

Planned features for future versions, roughly ordered by adoption impact.
Deferred known issues are tracked separately at the bottom with their GitHub
issue numbers.

---

## Planned

### 1. Static lint for untagged output-producing functions

**Priority: high**

The provenance primitive is fully opt-in: a developer can write
`const result = a.value + b.value` and bypass taint propagation entirely. The
existing `plumb-line-audit` skill can catch this in review, but it is
LLM-probabilistic, not deterministic.

Add a static AST-level pass that identifies functions which *produce* a return
value but never call `mark` or `derive`. This inverts the model from opt-in to
opt-out: provenance is assumed required on output-producing functions, and
absence is a lint error.

Scope:
- JS: ESLint rule (extend `provenance-lint/`) that flags functions returning a
  value without a `mark`/`derive` call on the return path
- Python: extend `adapters/python/provenance_lint.py` with an equivalent AST
  visitor
- Update `primitives/conformance/` to cover the new checker condition
- Hook into `adapters/*/hooks/pre-commit-gate` so untagged outputs block commit

---

### 2. Ecosystem adapters for common data sources

**Priority: high**

Taint propagation in security tools works because common sources (HTTP
requests, user input, env vars) are pre-tagged — developers don't mark every
individual call. plumb-line currently requires manual instrumentation at every
call site, which is a steep on-ramp for data/ML teams.

Build thin wrappers that auto-tag values at the point of ingestion:

- **Python:** `pandas` adapter — `PlumbDataFrame` wraps a DataFrame with a
  provenance envelope; operations that combine frames propagate taint
  automatically via `combineProvenance`. Similar wrapper for `numpy` arrays.
- **Python:** `requests`/`httpx` adapter — responses tagged `source: real` or
  `source: fallback` based on status code / cache header.
- **JS:** `fetch` adapter — same pattern; tags the resolved value before
  returning to the caller.

Each adapter ships as an optional extra in the respective package so the zero-
dependency core is not affected.

---

### 3. IDE integration

**Priority: medium**

Real-time provenance feedback at development time would change the adoption
curve. Right now enforcement is at commit time (git hooks) or review time
(Claude skill). A developer writing code has no inline signal.

- **VS Code extension:** inline decorations showing the provenance envelope on
  a hovered variable; warning gutter icons for untagged outputs or tainted
  values flowing into exports
- **Language server protocol:** surface `auditMeta` violations as diagnostics
  so any LSP-capable editor benefits (JetBrains, Neovim, etc.)
- **Quick-fix:** code action to wrap an untagged return in `mark()`/`derive()`
  with a prompt for source + confidence

---

### 4. `validateEnvelope` structural field-presence checker

**Priority: medium** · GitHub: #27

`auditMeta({})` currently returns `[]` for an empty envelope — it passes
silently even though required fields (`source`, `confidence`, `lineage`,
`derivedFromMock`) are absent. The audit logic assumes a structurally valid
envelope exists; it does not verify that assumption.

Add a companion `validateEnvelope(meta)` function to the primitive that checks
for required field presence and correct types before any combination or audit
logic runs. Both JS and Python implementations required; add to the
conformance suite and update `auditMeta` to call it as a pre-check.

Status table entry in `primitives/README.md` is already marked **planned**.

---

### 5. `PROVENANCE_VERSION` per-envelope embedding and validation

**Priority: medium**

`PROVENANCE_VERSION` is exported from both `primitives/js/provenance.mjs` and
`primitives/python/provenance.py` but is not embedded in individual envelopes
at creation time and is not validated on read. Consumers cannot tell which
schema version produced an envelope they receive.

Embed `PROVENANCE_VERSION` in every envelope produced by `makeMeta` /
`combine`. Add validation in `auditMeta` (or `validateEnvelope` once #4
ships) that the version field is present and matches the running library
version. Document the forward-compatibility policy: unknown future versions
are allowed through with a warning; unknown past versions are flagged.

---

### 6. Bootstrap wiring for the provenance primitive

**Priority: medium**

The `plumb-line-bootstrap` skill generates an `AGENTS.md` ruleset and installs
enforcement adapters, but it does not wire the provenance primitive into the
host project. After bootstrap runs, nothing prevents a developer from ignoring
`mark`/`derive` entirely.

Wire the primitive into bootstrap's output:
- Add a step that installs `plumb-line-provenance` as a dependency
- Generate example instrumentation for the detected language and project shape
- Hook `validateEnvelope` into the pre-commit gate so unmarked returns are
  caught before they reach review

Tracked as a consequence of ADR-0005; the integration was deliberately deferred
to keep that decision scoped to the primitive itself.

---

### 7. Go and Rust adapters

**Priority: low**

JS and Python ship at v0.1; Go and Rust are the next planned ports. Each new
language adapter must:

- Implement the combination law from `primitives/SPEC.md`
- Pass the full `primitives/conformance/cases.json` suite
- Provide the five adapter contract capabilities from
  `adapters/adapter-contract.md` (boundary check, test gate, pre-commit gate,
  branch guard, provenance-bypass lint)

---

### 8. Move `provenance-lint` from `adapters/` to `primitives/`

**Priority: low**

The provenance-bypass lint rules (`adapters/js/provenance-lint/` and
`adapters/python/provenance_lint.py`) check correct *use* of the primitive
library specifically, not domain-neutral architectural boundaries. They are
library-coupled in a way the boundary/branch/pre-commit hooks are not.

Relocating them to `primitives/` makes the coupling explicit and keeps
`adapters/` reserved for domain-neutral enforcement. Both source files note
this move as a future possibility.

---

### 9. Audit report header block

**Priority: low** · GitHub: #28

The output of `plumb-line-audit` lacks a header recording scope, principles
version, date, and git SHA. Without this, a saved audit report cannot be
re-verified or reproduced — it is a snapshot with no provenance of its own.

Add a required header block to the audit report format and introduce
`report-format: v1` versioning so downstream tooling can parse it reliably.

---

### 10. Configurable primitive module/function names in provenance lint

**Priority: low** · GitHub: #29

`PRIMITIVE_MODULES` and `TRACKED` function lists in both the JS ESLint rule
and the Python AST checker are hardcoded. Projects that re-export the
primitive under a different name (e.g., `import { mark } from '@myorg/data'`)
get no lint coverage without patching the source.

Add an injection path (ESLint rule option / Python checker argument) so callers
can extend the tracked module and function lists. This also makes the linter
reusable for third-party primitives that follow the same envelope contract.

---

## Deferred — Known Issues

These are confirmed issues from dogfooding (#23–#26), deferred because fixing
them requires API or spec changes. Tracked on GitHub.

| # | Summary | File | Notes |
|---|---------|------|-------|
| #23 | Step-counter collisions in concurrent runtimes (Node workers, Python async, parallel test runners) | `primitives/*/provenance.{mjs,py}` | Needs context-local counter or per-combine UUID; API change |
| #24 | Dual-import shim can be displaced by a top-level `provenance.py` in consumer project | `primitives/python/provenance.py` | Needs import path review |
| #25 | `combineProvenance()` with zero inputs yields `{source:"derived", lineage:[]}` but `auditMeta` flags it as unreproducible — SPEC §3 vs §5 contradiction | `primitives/*/provenance.{mjs,py}` | Needs spec clarification |
| #26 | `derive()` records input provenance but not the transformation function; two identical inputs with different `fn`s produce identical lineage | `primitives/*/marked.{mjs,py}` | `basis` override is undocumented workaround |

---

## Completed

See [CHANGELOG.md](CHANGELOG.md) for shipped work.
