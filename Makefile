.PHONY: setup verify-data audit pipeline lint test site all

setup:
	cd backend && uv sync --frozen --extra dev
	cd frontend && corepack pnpm install --frozen-lockfile

verify-data:
	cd backend && uv run --frozen pa verify-data

audit:
	cd backend && uv run --frozen pa audit

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
	cd frontend && corepack pnpm build

all: setup pipeline lint test site
