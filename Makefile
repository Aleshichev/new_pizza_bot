run:
	docker compose up -d

stop:
	docker compose stop

down:
	docker compose down

build:
	docker compose up --build -d

#lockal
# start:
# 	python3 app.py

start:
	docker compose up -d bot

logs:
	docker compose logs -f
