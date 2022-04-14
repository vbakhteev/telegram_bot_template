all:
	@echo "make start	- Run all services"
	@echo "make down	- Shut down all services"
	@echo "make restart	- Remove all data and start from scratch"
	@echo "make volume	- Create volume for grafana"
	@exit 0

start:
	    docker-compose up -d --build

down:
	    docker-compose down

restart:
	    docker-compose down && rm -rf resources && docker-compose up -d --build

volume:
	    docker volume create --name=grafana-data