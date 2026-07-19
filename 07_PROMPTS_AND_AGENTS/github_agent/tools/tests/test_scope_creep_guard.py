import importlib.util, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("scope_creep_guard", ROOT/"scope_creep_guard.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_in_scope_fixture_keeps():
    diff=(ROOT/"tests/fixtures/in_scope.diff").read_text()
    out=mod.analyze("Wave A github_agent tools only", diff)
    assert out["status"]=="KEEP"
    assert out["changed_paths"]==["07_PROMPTS_AND_AGENTS/github_agent/tools/scope_creep_guard.py"]

def test_workflow_dependency_and_deletion_block():
    diff=(ROOT/"tests/fixtures/block_workflow.diff").read_text()+"\ndiff --git a/requirements.txt b/requirements.txt\n+x\n\ndiff --git a/old.md b/old.md\ndeleted file mode 100644\n"
    out=mod.analyze("Wave A github_agent tools only", diff)
    codes={f["code"] for f in out["findings"]}
    assert out["status"]=="BLOCK_REVIEW"
    assert {"WORKFLOW_OR_SCHEDULE_CHANGE","DEPENDENCY_MANIFEST_CHANGE","DESTRUCTIVE_OR_MOVE_SIGNAL"} <= codes
