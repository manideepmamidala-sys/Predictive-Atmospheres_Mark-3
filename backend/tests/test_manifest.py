import json

from pa.io.manifest import verify_sources


def test_inventory_detects_changed_file(tmp_path):
    source = tmp_path / "changed.csv"
    source.write_text("changed")
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"entries": [{"source": str(source), "destination": None,
                                                  "size_bytes": 7, "sha256": "0" * 64}]}))
    manifest = tmp_path / "MANIFEST.sha256"
    manifest.write_text(f"{'0' * 64}  {source}\n")
    errors = verify_sources(inventory, manifest)
    assert errors and errors[0].reason == "sha256 mismatch"


def test_missing_or_mismatched_sha_manifest_is_rejected(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("original")
    from pa.io.manifest import sha256

    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"entries": [{"source": str(source), "destination": None,
                                                  "size_bytes": source.stat().st_size,
                                                  "sha256": sha256(source)}]}))
    manifest = tmp_path / "MANIFEST.sha256"
    assert any("missing" in error.reason for error in verify_sources(inventory, manifest))
    manifest.write_text(f"{'0' * 64}  {source}\n")
    assert any("disagrees" in error.reason for error in verify_sources(inventory, manifest))
    manifest.write_text(f"{sha256(source)}  {source}\n")
    assert verify_sources(inventory, manifest) == []
