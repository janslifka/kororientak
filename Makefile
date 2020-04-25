MANAGE=python kororientak/manage.py
IMAGE=registry.lonelyvertex.com/kororientak

.PHONY: run
run:
	$(MANAGE) runserver


.PHONY: test
test:
	$(MANAGE) test competition.tests


.PHONY: coverage
coverage:
	coverage run --source="kororientak/competition" kororientak/manage.py test competition.tests
	coverage html


.PHONY: codestyle
codestyle:
	pycodestyle kororientak


.PHONY: makemigrations
makemigrations:
	$(MANAGE) makemigrations


.PHONY: migrate
migrate:
	$(MANAGE) migrate


.PHONY: shell
shell:
	$(MANAGE) shell_plus


.PHONY: recreate_db
recreate_db:
	rm db.sqlite3
	$(MANAGE) migrate
	$(MANAGE) shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')"


.PHONY: docker.build
docker.build:
	docker build -t $(IMAGE) -f docker/Dockerfile .


.PHONY: docker.push
docker.push:
	docker push $(IMAGE)
