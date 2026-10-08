from pa.config import DATA, RESULTS, ROOT


def test_paths_are_repository_relative():
    assert (ROOT / "AGENTS.md").exists()
    assert DATA == ROOT / "data"
    assert RESULTS == ROOT / "artifacts" / "results"
