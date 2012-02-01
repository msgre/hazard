###
Popis geografickeho objektu v mape.
###
class GeoObject extends Backbone.Model
    defaults:
        hover: false


###
Popis atributu:

* json_fragments
  Obsahuje fragmenty stranky. Pri kliknuti na jiny radek v tabulce se vyvola
  dotaz na server, stahnou JSON data a podle nich se zaktualizuje stranka.
  To co prijde ze serveru se ulozi do tohoto atributu, at se priste JSON
  dotaz nemusi znovu podavat.

TODO: neuplne...
###
