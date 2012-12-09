// Ano, modifikovat zakladni type je zlo, ale v tomto pripade sere pes
// http://stackoverflow.com/questions/149055/how-can-i-format-numbers-as-money-in-javascript/149099#149099
Number.prototype.formatMoney = function(c, d, t){
var n = this, c = isNaN(c = Math.abs(c)) ? 2 : c, d = d == undefined ? "," : d, t = t == undefined ? "." : t, s = n < 0 ? "-" : "", i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", j = (j = i.length) > 3 ? j % 3 : 0;
   return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
};

var Kalkulacka = {};

Kalkulacka.run = function() {
	var pocetPenez = $("#suma_penez");
	var pocetMatu = $("#suma_matu");
	var rovnice = $("#rovnice");
	var rovnice = $("#rovnice");
	var rPevna = $(".r_pevna");
	var rPomerna = $(".r_pomerna");
	var rPocetMatu = $("#r_pocet_matu");
	var rPocetPenez = $("#r_pocet_penez");
	var rPomernaCela = $(".r_pomerna_cela");
	var rPomernaCelaProv = $(".r_pomerna_cela_prov");
	var rVysledek = $(".r_vysledek");
	var that = this;

	var counter = function() {
		var pm = parseInt(pocetMatu.val());
		var pp = parseInt(pocetPenez.val());
		if(!(pm > 0 && pp > 0)) {
			return false;
		} 
		var castkaPevna = 0.8*pm*55*365;
		var castkaPomerna = pp - castkaPevna;
		var castkaPomernaCela = castkaPomerna / 80 * 100;
		var castkaPomernaCelaProv = castkaPomernaCela / 20 * 100;
		var vysledek = castkaPomernaCelaProv * 4;

		rPocetMatu.text(pm);
		rPocetPenez.text(pp);
		rPevna.text(castkaPevna.formatMoney(0, ',', ' ')+" Kč");
		rPomerna.text(castkaPomerna.formatMoney(0, ',', ' ')+" Kč");
		rPomernaCela.text(castkaPomernaCela.formatMoney(0, ',', ' ')+" Kč");
		rPomernaCelaProv.text(castkaPomernaCelaProv.formatMoney(0, ',', ' ')+" Kč");
		rVysledek.text(vysledek.formatMoney(0, ',', ' ')+" Kč");
		rovnice.show();
		return false;
	}

	pocetPenez.keyup(counter);
	pocetMatu.keyup(counter);
	$("form").submit(counter);
	counter();

}



