from src.knowledge.literature import export_literature_index


if __name__ == "__main__":
    sources = export_literature_index(min_quality=0.55)
    print(f"Exported {len(sources)} research sources to artifacts/reports/research_index.json")
