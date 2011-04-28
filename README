Jak to funguje
--------------

Do aplikace muze kdokoliv pridat zaznamy ze sve obce. Staci, kdyz s pomoci Google
maps nakresli dve mapky -- jednu s hernami, druhou s "verejnymi" budovami. Pak
staci zadat URL na tyto mapky do aplikace, a ta provede veskerou zbylou praci:

* vypocita 100m okoli kolem budov
* zjisti ktere herny se nachazi v jejich dosahu
* vyzobne z wikipedie informace o obci (vypocita priblizny stred obce, podle 
  souradnic a sluzby Google Geocode zjisti nazev obce a nakonec vytahne 
  z Wikipedie informaci o rozloze obce a poctu obyvatel)

Pro kazdou takto zadanou obec pak vykresli interaktivni mapu, ve ktere je mozne
zjistit konkretni provozovny porusujici zakon.

Technicke podrobnosti
---------------------

Aplikace je napsana ve webovem frameworku Django verze 1.3. Vyuzive geograficke
rozsireni GeoDjango, databazi PostgreSQL s rozsirenim PostGIS. Javascriptove kody
jsou napsany v Coffee Scriptu, HTML stranky vyuzivaji CSS framework Blueprint.

V souboru requirements.txt je uveden seznam balicku tretich stran.

Pro zjistovani zemepisne polohy lat/lon vyuziva knihovnu
[geocoders](https://github.com/simonw/geocoders) Simona Willisona.