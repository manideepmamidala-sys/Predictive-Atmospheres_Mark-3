.PHONY: setup verify-data audit qc-review restore-cp-b pipeline lint test site reproduce-isolated all

setup:
	cd backend && uv sync --frozen --extra dev
	cd frontend && corepack pnpm install --frozen-lockfile

verify-data:
	python3 scripts/build_source_manifest.py --check
	cd backend && uv run --frozen pa verify-data

audit:
	cd backend && uv run --frozen pa audit

qc-review: audit
	cd backend && uv run --frozen pa signals
	cd backend && uv run --frozen pa signal-review

restore-cp-b: setup
	cd backend && uv run --frozen python ../scripts/rebuild_review_ledger.py

pipeline:
	cd backend && uv run --frozen pa pipeline

lint:
	cd backend && uv run --frozen ruff check src tests
	cd frontend && corepack pnpm run api:check
	cd frontend && corepack pnpm run typecheck

test:
	cd backend && uv run --frozen pytest -q
	cd frontend && corepack pnpm test

site:
	cd frontend && PA_REQUIRE_RESEARCH_EXPORT=1 corepack pnpm build

reproduce-isolated:
	python3 scripts/reproduce_isolated.py

all: setup pipeline lint test site
