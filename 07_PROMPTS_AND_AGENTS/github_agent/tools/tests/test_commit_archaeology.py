import importlib.util, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("commit_archaeology", ROOT/"commit_archaeology.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_tracked_spec_has_git_facts():
    path="07_PROMPTS_AND_AGENTS/github_agent/2026-07-19__harvested-agent-patterns-v0-1__implementation-spec.md"
    out=mod.analyze(path)
    assert out["status"]=="OK"
    assert out["introducing_commit"]["evidence_class"]=="FACT_FROM_GIT"
    assert out["introducing_commit"]["sha"]

def test_untracked_path_not_determinable():
    out=mod.analyze("07_PROMPTS_AND_AGENTS/github_agent/tools/tests/nope.md")
    assert out["status"]=="NOT_TRACKED"
    assert out["evidence_class"]=="NOT_DETERMINABLE"
