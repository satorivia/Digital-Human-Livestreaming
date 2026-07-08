.PHONY: help install up down migrate seed test lint typecheck e2e frontend-test
help:
	@echo "Targets: install up down migrate seed test lint typecheck e2e frontend-test"
install:
	python -m pip install -r requirements.txt
up:
	docker compose -f infra/docker-compose.yml up -d
down:
	docker compose -f infra/docker-compose.yml down
migrate:
	cd apps/api-server && alembic upgrade head
seed:
	python apps/api-server/scripts/seed.py
test:
	pytest
lint:
	ruff check apps/api-server packages/event-schema packages/shared-types
typecheck:
	mypy apps/api-server/app packages/event-schema/*.py packages/shared-types/*.py
e2e:
	pytest apps/api-server/tests/test_e2e_mock_flow.py
frontend-test:
	cd apps/admin-web && npm test -- --run && cd ../control-web && npm test -- --run
