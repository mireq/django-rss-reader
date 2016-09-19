(function(_) {


var toggleMenu = function(e) { _.toggleClass(document.body, 'visible-menu'); e.preventDefault(); };
var openMenu = function(e) { _.addClass(document.body, 'visible-menu'); e.preventDefault(); };
var closeMenu = function(e) { _.removeClass(document.body, 'visible-menu'); e.preventDefault(); };


var register = function(element) {
	_.forEach(_.cls(element, 'toggle-menu'), function(element) {
		_.bindEvent(element, 'click', toggleMenu);
	});
	_.forEach(_.cls(element, 'close-menu'), function(element) {
		_.bindEvent(element, 'click', closeMenu);
	});
	_.forEach(_.cls(element, 'open-menu'), function(element) {
		_.bindEvent(element, 'click', openMenu);
	});
};


_.onLoad(function(e) { register(e.memo); });


}(_utils));
