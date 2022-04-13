all:
	@echo "make start	- Run all services"
	@echo "make restart	- Remove all data and start from scratch"
	@exit 0

start:
	    docker-compose up -d --build

down:
	    docker-compose down

restart:
	    docker-compose down && rm -rf resources && docker-compose up -d --build
