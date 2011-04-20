#!/bin/bash
dropdb hazard
createdb -T template_postgis hazard
./manage.py syncdb --noinput
