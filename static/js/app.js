(function(_) {


var toggleMenu = function() { _.toggleClass(document.body, 'visible-menu'); };
var openMenu = function() { _.addClass(document.body, 'visible-menu'); };
var closeMenu = function() { _.removeClass(document.body, 'visible-menu'); };


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
