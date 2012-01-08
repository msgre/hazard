# -*- coding: utf-8 -*-
# vim: set et si ts=4 sw=4:

class JSONView(object):
    """
    Pomocna trida, pro osetreni ajaxovych dotazu z katalogovych stranek.

    Detekuje pritomnost parametru `ajax` v GETu, a pokud ho tam najde, povazuje
    dotaz za "ajaxovy".

    V tom pripadku upravi nazev self.base_template (napr.  z hodnoty
    "news/base.html" na "news/json_base.html", tj. pred jmeno sablony prida
    prefix "json_") a pri generovani vystupu z view v metode render_to_response
    upravi vystupni mimetype.

    Aby tohle vsechno ale fachalo, je nutne, aby sablona uvedena
    v self.template_name mela na prvnim radku:

        {% extends base_template %}

    tj. aby se odvozovala ne z explicitne zadane rodicovske sablony, ale podle
    sablony v promenne base_template.
    Samozrejme je nutne hodnotu self.base_template s pomoci metody
    get_context_data poslat do sablony.
    """

    def render_to_response(self, context, **response_kwargs):
        """
        Pokud byl podan AJAXovy dotaz, vratime spravne MIMETYPE.
        """
        response_kwargs.update({
            'mimetype': self.ajax and 'application/json' or 'text/html'
        })
        return super(JSONView, self).render_to_response(context, **response_kwargs)

    def modify_base_template(self, request):
        """
        Zjistime, jestli tento get neni nahodou Ajaxovy, a pokud ano,
        ovlivnime bazovou sablonu (aby se namisto HTML generovala JSON
        struktura).
        """
        self.ajax = request.is_ajax() or 'ajax' in request.GET

        if self.ajax:
            if '/' in self.base_template:
                path = self.base_template[:self.base_template.rfind('/') + 1]
                template = self.base_template[self.base_template.rfind('/') + 1:]
            else:
                path = ''
                template = self.base_template
            self.base_template = '%sjson_%s' % (path, template)

    def get(self, request, *args, **kwargs):
        self.modify_base_template(request)
        return super(JSONView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.modify_base_template(request)
        return super(JSONView, self).post(request, *args, **kwargs)
