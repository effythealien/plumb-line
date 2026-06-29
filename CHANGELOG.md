# Changelog

All notable changes to plumb-line are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/).

The version numbers below track the **packages and plugin**. The envelope wire
format is versioned separately as `PROVENANCE_VERSION` (currently `1`).

## [Unreleased]

_Nothing yet._

## [0.2.0] — 2026-06-29

### Added
- Optional **numeric confidence** (`confidenceScore`, `[0,1]`) and a
  **weakest-source** field on the provenance envelope; two new audit checks
  (numeric over-claiming, source over-claim).
- A versioned **specification** (`primitives/SPEC.md`, envelope schema version 1)
  and a single cross-language **conformance suite** with a report/badge tool.
- **npm + PyPI packaging** — the primitive is published as `plumb-line-provenance`.
- A static **`no-provenance-bypass` lint** (ESLint rule for JS, stdlib-`ast`
  checker for Python) that flags provenance-bypass patterns at review time.
- **GitHub Actions CI** running the JS and Python suites on push and PR.
- **Feedback channels** — a GitHub issue form and a private (Formspree-backed)
  form served via GitHub Pages.

### Changed
- **Relicensed from MIT to Apache-2.0** (added a `NOTICE` file).
- README repositioned to lead with the run-time primitive.

### Notes
- Envelope wire format unchanged: `PROVENANCE_VERSION` stays `1`.

## [0.1.0] — 2026-06-28

### Added
- Initial release: the three Claude Code skills (`method`, `bootstrap`,
  `audit`), the run-time provenance primitive with JS/Python parity, and
  enforcement adapters (ESLint / import-linter boundaries, git hooks) for
  JavaScript/TypeScript and Python.

[Unreleased]: https://github.com/effythealien/plumb-line/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/effythealien/plumb-line/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/effythealien/plumb-line/releases/tag/v0.1.0
