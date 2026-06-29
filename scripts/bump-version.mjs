#!/usr/bin/env node
// bump-version.mjs — set the package + plugin versions in lockstep.
//
//   node scripts/bump-version.mjs <version>     e.g. node scripts/bump-version.mjs 0.3.0
//
// Updates the three version manifests that must always agree:
//   - primitives/js/package.json        (npm package)
//   - primitives/python/pyproject.toml  (PyPI package)
//   - .claude-plugin/plugin.json        (Claude Code plugin — its version is what
//                                        triggers an update for already-installed users)
//
// NOT touched: PROVENANCE_VERSION (the envelope schema/wire version) — that only
// changes on a breaking change to the metadata format, independent of releases.
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const version = process.argv[2];

if (!version || !/^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$/.test(version)) {
  console.error("usage: node scripts/bump-version.mjs <version>   (e.g. 0.3.0)");
  process.exit(1);
}

const targets = [
  { file: "primitives/js/package.json", re: /("version":\s*")[^"]*(")/, label: "npm" },
  { file: ".claude-plugin/plugin.json", re: /("version":\s*")[^"]*(")/, label: "plugin" },
  { file: "primitives/python/pyproject.toml", re: /^(version\s*=\s*")[^"]*(")/m, label: "PyPI" },
];

let ok = true;
for (const t of targets) {
  const path = join(root, t.file);
  const src = readFileSync(path, "utf8");
  if (!t.re.test(src)) {
    console.error(`✗ ${t.file}: version field not found`);
    ok = false;
    continue;
  }
  writeFileSync(path, src.replace(t.re, `$1${version}$2`));
  console.log(`✓ ${t.label.padEnd(7)} ${t.file} → ${version}`);
}

if (!ok) process.exit(1);
console.log(`\nAll manifests set to ${version}.`);
console.log("Next: commit as a release PR, merge, then `git tag v" + version + " && git push origin v" + version + "`.");
