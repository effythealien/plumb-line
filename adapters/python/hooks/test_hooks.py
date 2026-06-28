import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import branch_guard, boundary_guard, pre_commit_gate
import pytest

CFG = {"protected_branches": ["main"], "docs_allowlist": ["docs/", "README.md"]}

def test_branch_blocks_code_on_protected():
    r = branch_guard.decide(file_path="src/app.py", branch="main", **CFG)
    assert r["allow"] is False

def test_branch_allows_docs_on_protected():
    r = branch_guard.decide(file_path="docs/x.md", branch="main", **CFG)
    assert r["allow"] is True

def test_branch_allows_feature_branch():
    r = branch_guard.decide(file_path="src/app.py", branch="feature/x", **CFG)
    assert r["allow"] is True

def test_branch_blocks_path_traversal_through_docs_directory_entry():
    r = branch_guard.decide(
        file_path="docs/../src/app.py",
        branch="main",
        protected_branches=["main"],
        docs_allowlist=["docs/", "README.md"],
    )
    assert r["allow"] is False

def test_branch_blocks_file_with_allowlist_entry_as_prefix():
    r = branch_guard.decide(
        file_path="README.md.bak",
        branch="main",
        protected_branches=["main"],
        docs_allowlist=["README.md"],
    )
    assert r["allow"] is False

def test_branch_raises_on_empty_allowlist_entry():
    with pytest.raises(ValueError, match="docs_allowlist must not contain empty entries"):
        branch_guard.decide(
            file_path="src/app.py",
            branch="main",
            protected_branches=["main"],
            docs_allowlist=[""],
        )

LAYERS = {"layers": ["ui", "engine", "services", "data"], "direction": "downward"}

def test_boundary_blocks_upward_import():
    r = boundary_guard.decide(file_path="src/data/store.py", import_path="src/ui/view.py", **LAYERS)
    assert r["allow"] is False

def test_boundary_allows_downward_import():
    r = boundary_guard.decide(file_path="src/ui/view.py", import_path="src/engine/calc.py", **LAYERS)
    assert r["allow"] is True

def test_pre_commit_blocks_on_failure():
    r = pre_commit_gate.decide(runners=[("tests", lambda: False)])
    assert r["allow"] is False
