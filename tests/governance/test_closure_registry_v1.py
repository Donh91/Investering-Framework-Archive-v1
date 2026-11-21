import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "00_FMOS/closure/CLOSURE_REGISTRY_v1.json"
REPO = "Donh91/Investering-Framework-Archive-v1"
ITEM_REFERENCE = re.compile(rf"{re.escape(REPO)}#[1-9][0-9]*")
EVIDENCE_URL = re.compile(
    rf"https://github\.com/{re.escape(REPO)}/issues/[1-9][0-9]*#issuecomment-[1-9][0-9]*"
)
ITEM_FIELDS = {
    "item_id", "owner", "product", "risk_class", "priority", "due_at",
    "blocking_dependency", "consumer", "next_action", "rollback", "evidence",
}


def test_closure_registry_is_public_advisory_metadata_only():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert set(registry) == {"contract", "authority", "design", "items"}
    assert registry["contract"] == "S1_CLOSURE_REGISTRY_v1"
    assert registry["authority"] == "ADVISORY_METADATA_ONLY"
    assert registry["design"] == "06_RESEARCH_LAB/governance/S1_CLOSURE_INTELLIGENCE_DESIGN_v1.md"
    assert (ROOT / registry["design"]).is_file()
    assert registry["items"]

    item_ids = set()
    for item in registry["items"]:
        assert set(item) == ITEM_FIELDS
        assert ITEM_REFERENCE.fullmatch(item["item_id"])
        assert ITEM_REFERENCE.fullmatch(item["owner"])
        assert EVIDENCE_URL.fullmatch(item["evidence"])
        assert item["item_id"] not in item_ids
        item_ids.add(item["item_id"])
        assert item["risk_class"] in {"LOW", "MEDIUM", "HIGH", "HIGH_IMPACT"}
        assert item["priority"] in {"P0", "P1", "P2", "P3"}
        for field in ("product", "blocking_dependency", "next_action", "rollback"):
            assert isinstance(item[field], str) and item[field].strip()
        assert item["consumer"] in {None, "github_pages", "official_compass_packet"}
        if item["due_at"] is not None:
            date = datetime.strptime(item["due_at"], "%Y-%m-%dT%H:%M:%SZ")
            assert date.strftime("%Y-%m-%dT%H:%M:%SZ") == item["due_at"]
