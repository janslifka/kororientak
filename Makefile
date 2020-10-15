MANAGE=python kororientak/manage.py

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


.PHONY: create_admin
create_admin:
	$(MANAGE) ensure_adminuser --username admin --password password
