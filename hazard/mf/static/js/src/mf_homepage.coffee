###
Naseptavac na uvodni strance kampane MF VLT.
###

renderMenu = (ul, items) ->
    self = @
    current_category = ''
    $.each items, (index, item) ->
        if item.category != current_category
            ul.append("<li class='ui-autocomplete-category'>#{ item.category }</li>")
            current_category = item.category
        self._renderItem(ul, item)

$(document).ready () ->
    $.widget('custom.catcomplete', $.ui.autocomplete, {
        _renderMenu: renderMenu
    })

    $('#search').catcomplete
        delay: 0
        source: '/autocomplete/'
        select: (event, ui) ->
            window.location = "#{ ui.item.url }kampan/mf/"
