# Releasing plumb-line

Merging to `main` does **not** release anything — it just updates the source.
Users on the published npm/PyPI packages and the installed Claude Code plugin
only get changes when you cut a release. So: **merge freely, release
deliberately.** `main` is "latest dev"; the registries and plugin reflect the
last release.

## Cadence

Release when there's a meaningful unit to ship — a feature, a batch of fixes, or
"enough has accumulated" — not on a fixed schedule, and not per-PR. The one
exception: a bug users are actually hitting → cut a patch promptly.

Stack small focused PRs onto `main` as you go; let them accumulate; release a
batch.

## Versioning (semver)

Pick the bump by what changed since the last release:

| Bump  | Example         | When |
| ----- | --------------- | ---- |
| patch | `0.2.0 → 0.2.1` | bug fixes, no API change |
| minor | `0.2.0 → 0.3.0` | new backward-compatible features |
| major | `0.x → 1.0.0`   | breaking changes (while `0.x`, breaking changes may ride a minor bump — `0.x` signals the API is still moving) |

Three version manifests must always agree and are bumped together:
`primitives/js/package.json`, `primitives/python/pyproject.toml`, and
`.claude-plugin/plugin.json` (the plugin version is what makes an update visible
to already-installed plugin users).

**Not** a release version: `PROVENANCE_VERSION` (the envelope wire-format
version in the primitive). That only changes on a breaking change to the metadata
format — see [`primitives/SPEC.md`](primitives/SPEC.md) §1.

## The process

1. **Merge** the PRs you want shipped (all green through CI).
2. **Bump** all three manifests in one command, on a release branch:
   ```bash
   node scripts/bump-version.mjs 0.3.0
   ```
3. Update [`CHANGELOG.md`](CHANGELOG.md) — move items from *Unreleased* into a new
   version section.
4. Open that as a **release PR** ("release: 0.3.0"), let CI pass, **merge** it.
5. **Tag the merged commit and push the tag:**
   ```bash
   git checkout main && git pull
   git tag v0.3.0
   git push origin v0.3.0
   ```
6. The **[Release workflow](.github/workflows/release.yml)** takes it from here on
   the tag push: runs the test suites, publishes to npm and PyPI, and creates the
   GitHub release with generated notes. The plugin needs no publish step — it
   updated when the bumped `plugin.json` merged to `main`.

> Push the **tag** to release — don't create the GitHub release by hand; the
> workflow creates it. Creating it manually first will make the workflow's
> release step fail (it already exists).

### One-time setup

The Release workflow needs two repository secrets
(Settings → Secrets and variables → Actions → New repository secret):

- **`NPM_TOKEN`** — an npm *automation* token with publish rights.
- **`PYPI_API_TOKEN`** — a PyPI API token scoped to the `plumb-line-provenance`
  project.

Until both exist, the publish steps fail — so add them before the first
tag-triggered release.

### Manual fallback

If you ever need to publish by hand (workflow down, secret expired), the raw
`npm publish` / `twine upload` commands are in the maintainer's private
publishing checklist. The automated flow above is the normal path.

## After releasing

- Confirm the versions are live: `npm view plumb-line-provenance version` and the
  [PyPI page](https://pypi.org/project/plumb-line-provenance/).
- Existing plugin users update with `/plugin marketplace update plumb-line` then
  `/plugin install plumb-line@plumb-line`.
