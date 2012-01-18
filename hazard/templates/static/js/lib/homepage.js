(function() {
  /*
  Naseptavac na uvodni strance.
  */  var renderMenu;
  renderMenu = function(ul, items) {
    var current_category, self;
    self = this;
    current_category = '';
    return $.each(items, function(index, item) {
      if (item.category !== current_category) {
        ul.append("<li class='ui-autocomplete-category'>" + item.category + "</li>");
        current_category = item.category;
      }
      return self._renderItem(ul, item);
    });
  };
  $(document).ready(function() {
    $.widget('custom.catcomplete', $.ui.autocomplete, {
      _renderMenu: renderMenu
    });
    return $('#search').catcomplete({
      delay: 0,
      source: '/autocomplete/',
      select: function(event, ui) {
        return window.location = ui.item.url;
      }
    });
  });
}).call(this);
