###
Naseptavac na uvodni strance.
###

COOKIE_NAME = 'dialog_opened'

renderMenu = (ul, items) ->
    self = @
    current_category = ''
    $.each items, (index, item) ->
        if item.category != current_category
            ul.append("<li class='ui-autocomplete-category'>#{ item.category }</li>")
            current_category = item.category
        self._renderItem(ul, item)

oldMHModal = () ->
    if not $.cookie(COOKIE_NAME)
        html = """
            <div id="dialog" title="Upozornění" style="display:none">
                <p><strong>MapyHazardu se mění!</strong></p>

                <p>V březnu 2012 jsme naše stránky zásadně změnili. Chceme o hazardu
                informovat v širších souvislostech a tento přerod nám to umožní.</p>

                <p>Původní aplikaci, s pomocí které může kdokoliv prověřovat
                konflikty heren poblíž dříve chráněných budov, jsme ale ponechali.
                Najdete ji na adrese
                <a href="http://puvodni.mapyhazardu.cz/">puvodni.mapyhazardu.cz</a>.
            </div>
        """
        $('body').append(html)
        $('#dialog').dialog
            width: 500
            modal: true
            resizable: false
            draggable: false
            buttons:
                'Rozumím': () -> $(@).dialog('close')
        $.cookie(COOKIE_NAME, '1', {expires: 365})


$(document).ready () ->
    $.widget('custom.catcomplete', $.ui.autocomplete, {
        _renderMenu: renderMenu
    })

    $('#search').catcomplete
        delay: 0
        source: '/autocomplete/'
        select: (event, ui) ->
            window.location = ui.item.url

    oldMHModal()

