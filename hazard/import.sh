#!/bin/bash
# bacha, na notasu to cele trva skorem 40 minut!

echo `date`

# nastaveni defaultni kampane
./manage.py set_default_campaign

# natazeni uzemnich celku
./manage.py import_regions ../data/kraje.csv
./manage.py import_districts ../data/okresy.csv
./manage.py import_towns ../data/obce.csv
./manage.py import_zips ../data/psc.csv

# natazeni budov
./manage.py import_mf_places --no-counter ../data/budovy3.pickle

# natazeni ministerskych heren
./manage.py import_mf_hells --no-counter ../data/herny_ministerstvo_1.csv
./manage.py import_mf_hells --no-counter ../data/herny_ministerstvo_2.csv
./manage.py import_mf_hells --no-counter ../data/herny_ministerstvo_3.csv
./manage.py import_mf_hells --no-counter ../data/herny_ministerstvo_4.csv

# vypocet okoli budov
./manage.py build_mf_surround --no-counter

# vypocet konfliktu
./manage.py compute_conflicts --no-counter

echo `date`
