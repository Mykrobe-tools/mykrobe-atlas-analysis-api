build:
	docker-compose build

compose:
	docker-compose up

test:
	docker exec -ti mykrobe-atlas-analysis-api_worker_1 python -m pytest tests/ $(args)

clean:
	docker system prune -f --volumes