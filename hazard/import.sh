#!/bin/bash

# natazeni budov
./manage.py import_places1 ../data/budovy3.pickle --ignore=obce
./manage.py import_places1 ../data/budovy3.pickle --include=obce

# procisteni dat o krajich/okresech/obcich
./manage.py update_regions1 ../data/kraje.csv
./manage.py update_districts1 ../data/okresy.csv
./manage.py update_towns1 ../data/obce.csv

# natazeni ministerskych heren
./manage.py import_hells1 ../data/herny_ministerstvo_1.csv
./manage.py import_hells1 ../data/herny_ministerstvo_2.csv
./manage.py import_hells1 ../data/herny_ministerstvo_3.csv
./manage.py import_hells1 ../data/herny_ministerstvo_4.csv
