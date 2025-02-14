MASTER := spark://spark:7077
DOCKER_COMPOSE := docker-compose -f .devcontainer/docker-compose.yml
WORDCLOUD_TXT_FILE := faust.txt

.PHONY: all test coverage
all: get build install

df: ## Run document frequency batch rdd job
	spark-submit --master $(MASTER) --driver-class-path /fake-hdfs/postgresql-42.3.4.jar --jars /fake-hdfs/postgresql-42.3.4.jar spark/df.py

tfidf: ## Run term frequency rdd job
	spark-submit --master $(MASTER) --driver-class-path /fake-hdfs/postgresql-42.3.4.jar --jars /fake-hdfs/postgresql-42.3.4.jar spark/tfidf.py $(WORDCLOUD_TXT_FILE)

tfidf-cumulative: ## Run cumulative term frequency rdd job
	spark-submit --master $(MASTER) --driver-class-path /fake-hdfs/postgresql-42.3.4.jar --jars /fake-hdfs/postgresql-42.3.4.jar spark/tfidf-cumulative.py

docker-up: ## Start docker setup
	$(DOCKER_COMPOSE) up -d

docker-bash: ## Start bash on app service
	$(DOCKER_COMPOSE) exec app bash

postgres:
	$(DOCKER_COMPOSE) exec postgres psql -U postgres

start: ## Start the webserver
	FLASK_APP=backend/server FLASK_ENV=development flask run --host=0.0.0.0

docker-start: ## Start the webserver inside docker
	$(DOCKER_COMPOSE) exec app make start

start-frontend: ## Start frontend
	cd frontend && npm i && yarn dev

docker-start-frontend: ## Start frontend inside docker
	$(DOCKER_COMPOSE) exec app make start-frontend

help: ## Display this help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Remove all generated wordcloud files
	@rm /fake-hdfs/wordclouds/*.svg
