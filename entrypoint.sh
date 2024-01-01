#!/bin/sh

echo 'Run migrations !'
python3 manage.py migrate

echo 'Finish migrations'

exec "$@"
