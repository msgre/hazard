$ = jQuery

$.fn.extend
  schovavacz: (options) ->
    self = $.fn.schovavacz

    opts = $.extend {}, self.default_options, options

    $(this).each (i, el) ->
      self.init el, opts


$.extend $.fn.schovavacz,
  default_options:
    show_txt: 'Next'
    hide_txt: 'Hide'
    link_class: 'krl_command_link'
    hidden_container_class: 'krl_hidden'
    shown_container_class: 'krl_shown'
    item_class: 'krl_item'
    item_overlimit_class: 'krl_item_overlimit'
    link_class: 'krl_command_link'
    items_selector: 'a'
    epsilon: 0 # aka parchant
    limit: 2

  init: (el, opts) ->
    $el = $ el
    $el.addClass opts.hidden_container_class
    items = $el.find opts.items_selector
    items.addClass opts.item_class

    if (items.length - opts.epsilon) > opts.limit
        rest = items.filter(":gt(#{(opts.limit-1)})")
        rest.addClass(opts.item_overlimit_class).hide()
        opts.show_txt = opts.show_txt.replace('%count%', rest.length)
        link = $ "<a>", {html:opts.show_txt, href:"#", class:opts.link_class}
        this.makeLinkClickable link,$el,opts
        $el.append link

   makeLinkClickable: (link, container, opts) ->
    link.click ->
        $link = $ this
        isHidden = container.hasClass opts.hidden_container_class

        $link.html(if isHidden then opts.hide_txt else opts.show_txt )

        if isHidden
                container.removeClass(opts.hidden_container_class)
                            .addClass(opts.shown_container_class)
                            .find(".#{opts.item_class}")
                            .show()
            else
                container.addClass(opts.hidden_container_class)
                            .removeClass(opts.shown_container_class)
                            .find(".#{opts.item_overlimit_class}")
                            .hide()

        false;
