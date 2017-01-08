(function(_) {


var preloaderNext;
var preloaderPrev;


var toggleMenu = function(e) {
	_.toggleClass(document.body, 'visible-menu');
	if (e) {
		e.preventDefault();
	}
};
var openMenu = function(e) {
	_.addClass(document.body, 'visible-menu');
	if (e) {
		e.preventDefault();
	}
};
var closeMenu = function(e) {
	_.removeClass(document.body, 'visible-menu');
	if (e) {
		e.preventDefault();
	}
};

var registerEntryDetail = function() {
	var entryDetail = _.id('entry_detail');
	var summary = _.cls(entryDetail, 'summary')[0];
	var links = _.tag(summary, 'A');
	_.forEach(links, function(link) {
		link.setAttribute('target', '_blank');
	});
};

var registerPreloader = function() {
	var nextItemLink = _.id('next_item_link');
	if (nextItemLink !== null && nextItemLink.getAttribute('href') !== '#') {
		var preloaderNext = preloadUrl(nextItemLink.getAttribute('href'));
		var clone = nextItemLink.cloneNode(false);
		nextItemLink.parentNode.replaceChild(clone, nextItemLink);
		nextItemLink = clone;
		_.bindEvent(nextItemLink, 'click', function(e) {
			e.preventDefault();
			preloaderNext.open();
			_.xhrSend({
				url: nextItemLink.getAttribute('href') + '?mark',
				successFn: function(response, res, opts) {
				}
			});
		});
	}
};

var preloadUrl = function(url) {
	var self = {};

	var opened = false;
	var responseData;

	self.open = function() {
		opened = true;
		if (responseData !== undefined) {
			if (responseData === null) {
				_.pjax.load(url);
			}
			else {
				_.pjax.load(url, { response: responseData });
			}
		}
	};

	_.xhrSend({
		url: url + '?cache',
		extraHeaders: {
			'X-PJAX': 'true'
		},
		successFn: function(response) {
			responseData = response;
			if (opened) {
				_.pjax.load(url, { response: responseData });
			}
		},
		failFn: function() {
			responseData = null;
			if (opened) {
				_.pjax.load(url);
			}
		}
	});

	return self;
};

var transformToSelect = function(element) {
	var select = _.elem('select');

	var links = [];
	_.forEach(_.tag(element, 'a'), function(link, num) {
		var option = _.elem('option');
		if (_.hasClass(link, 'active')) {
			option.setAttribute('selected', 'selected');
		}
		option.setAttribute('value', num);
		option.innerHTML = link.innerHTML;
		links.push(link.getAttribute('href'));
		select.appendChild(option);
	});

	var onChange = function() {
		var link = links[parseInt(select.value, 10)];
		_.pjax.load(link);
	};
	_.bindEvent(select, 'change', onChange);

	element.innerHTML = '';
	element.appendChild(select);
};

var formOptions = {
	onResponse: function(data, formElement) {
		if (_.has(data, 'redirect') && _.has(_, 'pjax')) {
			_.pjax.load(data.redirect);
			return false;
		}
		if (_.has(data, 'celery_result_url')) {
			var opts = {};
			opts.waitingText = _.getData(formElement, 'celeryWaiting') || 'Loading ...';
			celery.waitForResult(data.celery_result_url, opts);
		}
	}
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
	_.forEach(_.cls(element, 'select-link'), function(element) {
		transformToSelect(element);
	});
	_.forEach(_.cls(element, 'ajaxform'), function(formElement) {
		_.ajaxform(formElement, formOptions);
	});
	if (_.id(element, 'entry_detail') !== null) {
		registerEntryDetail();
	}
	if (element === document.body) {
		registerPreloader();
	}
};


_.pjax.autoRegister({
	bodyLoadingCls: 'loading',
	pjaxContainerId: 'content',
	extrajsBlock: 'extrajs',
	extrastyleBlock: 'extrastyle',
	titleBlock: 'head_title',
	checkUrlSupported: function(url) {
		if (url[0] !== '/') {
			return false;
		}
		if (url.match(/^\/media\/.*$/) || url.match(/^\/static\/.*$/) || url.match(/^\/admin\/.*$/)) {
			return false;
		}
		return true;
	},
	onLoaded: function(response, url) {
		closeMenu();
		var copyBlocks = ['site_title', 'top_navigation', 'navigation'];
		_.forEach(copyBlocks, function(blockName) {
			var block = _.id(blockName);
			block.innerHTML = response.blocks[blockName];
			_.triggerLoad(block);
		});
		document.body.className = response.blocks.bodyclass;
		if (_.id('entry_detail') !== null) {
			registerPreloader();
		}
	}
});


_.onLoad(function(e) { register(e.memo); });


}(_utils));
