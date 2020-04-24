#!/bin/sh

sleep 10

cd kororientak

python manage.py migrate
python manage.py ensure_adminuser --username "$ADMIN_USER" --password "$ADMIN_PASS"
python manage.py collectstatic --no-input

exec gunicorn kororientak.wsgi:application --bind 0.0.0.0:8000 --workers 3
