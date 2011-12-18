(function() {
  var wrapper;
  wrapper = function(selector) {
    var $el, url;
    $el = django.jQuery(selector);
    url = $el.text().trim();
    return $el.wrapInner('<a href="' + url + '" />');
  };
  django.jQuery(document).ready(function() {
    wrapper('.hell_url p');
    wrapper('.building_url p');
    return wrapper('.wikipedia p');
  });
}).call(this);
