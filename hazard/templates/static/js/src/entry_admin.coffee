wrapper = (selector) ->
    $el = django.jQuery(selector)
    url = $el.text().trim()
    $el.wrapInner('<a href="' + url + '" />')

django.jQuery(document).ready () ->
    wrapper('.hell_url p')
    wrapper('.building_url p')
    wrapper('.wikipedia p')
