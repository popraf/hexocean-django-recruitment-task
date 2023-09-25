#!/bin/sh

until cd /app/backend
do
    echo "Waiting for server volume..."
done

until python manage.py migrate
do
    echo "Waiting for migration..."
    sleep 2
done

until python manage.py loaddata init_ThumbnailHeights.json
do
    echo "Waiting for init_ThumbnailHeights..."
    sleep 2
done

until python manage.py loaddata init_UserTiers.json
do
    echo "Waiting for init_UserTiers..."
    sleep 2
done

until python manage.py loaddata init_CustomUsers.json
do
    echo "Waiting for init_CustomUsers..."
    sleep 2
done
# python manage.py createsuperuser --noinput

# for debug
until python -m celery -A backend worker --detach
do
    echo "Waiting for celery..."
    sleep 2
done

until python manage.py runserver 0.0.0.0:8000
do
    echo "Waiting for server to stand up..."
    sleep 2
done
