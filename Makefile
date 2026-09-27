.PHONY: install up down run test fmt

CHAPTER ?= chapter1

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

up:
	docker compose up -d postgres redis rabbitmq

up-kafka:
	docker compose up -d zookeeper kafka

down:
	docker compose down

run:
	# usage: make run CHAPTER=chapter6
	cd $(CHAPTER)/app && uvicorn main:app --reload --port 8000

test:
	# usage: make test CHAPTER=chapter23
	cd $(CHAPTER) && pytest -v

fmt:
	black . || true
