build:
	docker-compose build

compose:
	docker-compose up

test:
	python -m pytest tests/