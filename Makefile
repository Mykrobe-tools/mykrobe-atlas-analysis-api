TEST_IMAGE = analysis-api-tests

build:
	docker-compose build

compose:
	docker-compose up

build_tests:
	docker build -f docker/tests.Dockerfile -t $(TEST_IMAGE) .

test:
	docker run --rm -it $(TEST_IMAGE)

clean:
	docker system prune -f --volumes