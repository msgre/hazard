(function() {
  /*
  Naseptavac na uvodni strance.
  */  var COOKIE_NAME, oldMHModal, renderMenu;
  COOKIE_NAME = 'dialog_opened';
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
  oldMHModal = function() {
    var html;
    if (!$.cookie(COOKIE_NAME)) {
      html = "<div id=\"dialog\" title=\"Upozornění\" style=\"display:none\">\n    <p><strong>MapyHazardu se mění!</strong></p>\n    <p>V březnu 2012 jsme naše stránky zásadně změnili. Chceme o\n    hazardu informovat v širších souvislostech a tento přerod nám\n    to umožní.</p>\n    <p>Původní aplikaci, s pomocí které může kdokoliv prověřovat\n    konflikty heren poblíž dříve chráněných budov, jsme ponechali.\n    Najdete ji na adrese\n    <a href=\"http://puvodni.mapyhazardu.cz/\">puvodni.mapyhazardu.cz</a>.</p>\n</div>";
      $('body').append(html);
      $('#dialog').dialog({
        width: 500,
        modal: true,
        resizable: false,
        draggable: false,
        buttons: {
          'Rozumím': function() {
            return $(this).dialog('close');
          }
        }
      });
      return $.cookie(COOKIE_NAME, '1', {
        expires: 365
      });
    }
  };
  $(document).ready(function() {
    $.widget('custom.catcomplete', $.ui.autocomplete, {
      _renderMenu: renderMenu
    });
    $('#search').catcomplete({
      delay: 0,
      source: '/autocomplete/',
      select: function(event, ui) {
        return window.location = ui.item.url;
      }
    });
    return oldMHModal();
  });
}).call(this);
