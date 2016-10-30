(function(_) {


var toggleMenu = function(e) { _.toggleClass(document.body, 'visible-menu'); e.preventDefault(); };
var openMenu = function(e) { _.addClass(document.body, 'visible-menu'); e.preventDefault(); };
var closeMenu = function(e) { _.removeClass(document.body, 'visible-menu'); e.preventDefault(); };


var registerEntryDetail = function() {
	var entryDetail = _.id('entry_detail');
	var summary = _.cls(entryDetail, 'summary')[0];
	var links = _.tag(summary, 'A');
	_.forEach(links, function(link) {
		link.setAttribute('target', '_blank');
	});
};


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
	if (_.id('entry_detail') !== null) {
		registerEntryDetail();
	}
};


_.onLoad(function(e) { register(e.memo); });


}(_utils));
