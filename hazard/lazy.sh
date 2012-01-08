#!/bin/bash
dropdb hazard3
createdb -T template_postgis hazard3
./manage.py syncdb --noinput
./manage.py migrate
