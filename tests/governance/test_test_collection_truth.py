from pathlib import Path

from scripts.governance.check_test_collection_truth import collected_files, missing_files


def test_collection_parser_extracts_pytest_nodeids():
    text = "tests/governance/test_a.py::test_one\ntests/lib/test_b.py::TestB::test_two\n2 tests collected\n"
    assert collected_files(text) == {"tests/governance/test_a.py", "tests/lib/test_b.py"}


def test_missing_file_is_reported(tmp_path: Path):
    for rel in ("tests/governance/test_a.py", "tests/governance/test_b.py"):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_x(): pass\n")
    text = "tests/governance/test_a.py::test_x\n"
    assert missing_files(tmp_path, ["tests/governance"], text) == ["tests/governance/test_b.py"]
