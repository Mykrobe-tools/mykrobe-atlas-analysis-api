build:
	docker-compose build

compose:
	docker-compose up

build_tests:
	docker build -f docker/tests.Dockerfile -t analysis-api-tests .

test:
	docker run --rm -it analysis-api-tests

clean:
	docker system prune -f --volumes