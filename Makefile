api:
	docker build -t analysis-api -f docker/api.Dockerfile .

worker:
	docker build -t analysis-worker -f docker/worker.Dockerfile --build-arg=base_image=analysis-api .

build: api worker

up:
	docker-compose up

debug:
	docker run --rm -it analysis-$(svc) bash