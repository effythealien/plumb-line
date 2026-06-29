# Publishing the provenance primitive

The run-time primitive ships as `plumb-line-provenance` on **npm** (JavaScript)
and **PyPI** (Python). Both names were confirmed available. This is the
maintainer release checklist; the final upload steps require your authenticated
accounts and cannot be run by an automated agent.

Version `0.1.0` is the intended first release. `0.x` deliberately signals the API
may still move — but note both registries treat a published version as
**immutable** (you cannot overwrite `0.1.0`; a fix means `0.1.1`), and the first
publish **reserves the name**.

## 0. Prerequisites (one-time)

- **npm:** an npm account, membership confirmed, 2FA enabled. Either `npm login`
  interactively, or a granular automation token in `~/.npmrc`
  (`//registry.npmjs.org/:_authToken=…`).
- **PyPI:** a PyPI account with 2FA, and an API token (`pypi-…`). Put it in
  `~/.pypirc` or pass it to `twine` as `__token__`. A **TestPyPI** account is
  recommended for a rehearsal upload.

## 1. Pre-publish verification (run from repo root)

```bash
# Tests green in both languages
( cd primitives/js && npm install && npm test )       # expect 63/63
( cd primitives/python && python3 -m pytest )          # expect 45/45

# Conformance passes and prints the schema version
node primitives/conformance/report.mjs                 # expect 10/10, exit 0
```

Confirm the version is what you intend in **both** manifests:
`primitives/js/package.json` (`"version"`) and
`primitives/python/pyproject.toml` (`version`). They must match.

## 2. Publish JavaScript → npm

```bash
cd primitives/js
npm pack --dry-run        # inspect: should list exactly README.md, index.mjs,
                          # provenance.mjs, marked.mjs, audit.mjs, package.json
npm publish               # unscoped + public by default; 2FA OTP if prompted
```

Verify: `npm view plumb-line-provenance version` returns `0.1.0`, and in a scratch
dir `npm install plumb-line-provenance` then
`node -e "import('plumb-line-provenance').then(m=>console.log(typeof m.mark))"`
prints `function`.

## 3. Publish Python → PyPI

```bash
cd primitives/python
rm -rf dist build *.egg-info
python3 -m build                       # builds sdist + wheel into dist/
twine check dist/*                     # expect PASSED for both

# Optional rehearsal on TestPyPI first:
twine upload --repository testpypi dist/*

# Real upload:
twine upload dist/*                    # user __token__, password = pypi-… token
```

Verify: in a fresh venv, `pip install plumb-line-provenance` then
`python3 -c "from plumb_line_provenance import mark; print(mark)"` works.

> The wheel ships only the four source modules (`provenance`, `marked`, `audit`,
> `__init__`) — confirmed clean. The sdist also carries `tests/` (conventional);
> those tests need the full repo to run, since `cases.json` lives outside the
> package, so don't expect `pytest` to pass from an unpacked sdist alone.

## 4. Post-publish

- Tag the release: `git tag primitive-v0.1.0 && git push --tags`.
- Drop the "publication pending" caveats now that the install lines are true:
  in `README.md` (Install + Status sections) and the package READMEs if needed.
- Confirm the conformance badge resolves and the spec link in each package README
  points at the right tag/branch.

## Re-releasing

Bump the version in **both** manifests, rebuild, and republish. Never reuse a
version number. Keep `primitives/js/package.json` and
`primitives/python/pyproject.toml` versions in lockstep so the two language
packages always describe the same envelope schema.
