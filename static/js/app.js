(function(_) {

var urlresolver = _.urlresolver(window._utils._urls);

var preloadCache;

var setEelemntText = function(element, text) {
	element.innerHTML = '';
	var elementText = document.createTextNode(text);
	element.appendChild(elementText);
};


var setNewEntries = function(count) {
	var element = _.id('new_entries_count');
	var message = interpolate(ngettext('%s new entry', '%s new entries', count), [count]);
	setEelemntText(element, message);
};


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


var PreloadCache = function(feedListUrl) {
	var self = {};

	var nextCache = [];
	var prevCache = [];
	var nextId = _.getData(_.id('next_item_link'), 'id') || undefined;
	var prevId = _.getData(_.id('prev_item_link'), 'id') || undefined;
	var current;
	var callbacks = {prev: undefined, next: undefined};
	var waiting = {prev: false, next: false};

	var requestedDirection;

	var getEntryId = function() {
		return _.getData(_.id('entry_detail'), 'id');
	};

	var setEntryId = function(id) {
		return _.setData(_.id('entry_detail'), 'id', id);
	};

	var buildFeedUrl = function(direction) {
		var url;
		if (direction === 'next') {
			if (nextCache.length) {
				url = feedListUrl + '?from=' + nextCache[nextCache.length - 1].id;
			}
		}
		else {
			if (prevCache.length) {
				url = feedListUrl + '?from=' + prevCache[0].id;
			}
		}
		if (url === undefined) {
			url = feedListUrl + '?from=' + getEntryId();
		}
		if (direction === 'next' && current === undefined) {
			url += '&self=';
		}
		if (direction !== 'next') {
			url += '&prev=';
		}
		return url;
	};

	var preloadCache = function(direction, callback) {
		if (waiting[direction]) {
			return;
		}
		waiting[direction] = true;
		var url = buildFeedUrl(direction);
		firstRun = false;
		_.xhrSend({
			url: url,
			successFn: function(response) {
				waiting[direction] = false;
				if (direction == 'next') {
					nextId = response.next;
				}
				else {
					prevId = response.next;
				}
				var nextList = response.result;
				var entryId = getEntryId();
				_.forEach(nextList, function(item) {
					if (item.id == entryId) {
						current = item;
						return;
					}
					if (direction === 'next') {
						nextCache.push(item);
					}
					else {
						prevCache.unshift(item);
					}
				});
				triggerLoad(direction);
			},
			failFn: function(response) {
				waiting[direction] = false;
				triggerLoad(direction);
			}
		});
	};

	var triggerLoad = function(direction) {
		if (callbacks[direction] === undefined) {
			return;
		}

		var item;
		if (direction === 'next') {
			if (nextCache.length) {
				if (current) {
					prevCache.push(current);
				}
				current = nextCache.shift();
			}
		}
		else {
			if (prevCache.length) {
				if (current) {
					nextCache.unshift(current);
				}
				current = prevCache.pop();
			}
		}
		if (current) {
			setEntryId(current.id);
			_.pjax.pushState(current.url);

			_.xhrSend({
				method: 'POST',
				url: urlresolver.reverse("feeds:api_entry_detail", [current.id]),
				data: 'action=mark_read',
				successFn: function(response) {
					setNewEntries(response.new_entries_count);
				}
			});

			var link;

			var nextLink = self.getNextLink() || '#';
			var nextId = self.getNextId() || '';
			link = _.id('next_item_link');
			link.setAttribute('href', nextLink);
			_.setData(link, 'id', nextId);
			if (nextId === '') {
				_.addClass(link, 'disabled');
			}
			else{
				_.removeClass(link, 'disabled');
			}

			var prevLink = self.getPrevLink() || '#';
			var prevId = self.getPrevId() || '';
			link = _.id('prev_item_link');
			link.setAttribute('href', prevLink);
			_.setData(link, 'id', prevId);
			if (prevId === '') {
				_.addClass(link, 'disabled');
			}
			else{
				_.removeClass(link, 'disabled');
			}
		}
		callbacks[direction](current);
		callbacks[direction] = undefined;
	};

	var preload = function(direction) {
		if (direction === 'next') {
			if (nextCache.length) {
				triggerLoad(direction);
			}
			if (nextCache.length < 10) {
				if (nextId || nextCache.length === 0) {
					preloadCache(direction);
				}
			}
		}
		if (direction === 'prev') {
			if (prevCache.length) {
				triggerLoad(direction);
			}
			if (prevCache.length < 10) {
				if (prevId || prevCache.length === 0) {
					preloadCache(direction);
				}
			}
		}
	};

	self.next = function(callback) {
		callbacks.next = callback;
		callbacks.prev = undefined;
		preload('next');
	};

	self.prev = function(callback) {
		callbacks.prev = callback;
		callbacks.next = undefined;
		preload('prev');
	};

	self.clearCallbacks = function() {
		callbacks.next = undefined;
		callbacks.prev = undefined;
	};

	self.getNextId = function() {
		var id = nextId;
		if (nextCache.length) {
			id = nextCache[0].id;
		}
		return id;
	};

	self.getPrevId = function() {
		var id = prevId;
		if (prevCache.length) {
			id = prevCache[prevCache.length - 1].id;
		}
		return id;
	};

	self.getNextLink = function() {
		var id = self.getNextId();
		if (id === undefined) {
			return;
		}
		return urlresolver.reverse("feeds:entry_detail", [id]);
	};

	self.getPrevLink = function() {
		var id = self.getPrevId();
		if (id === undefined) {
			return;
		}
		return urlresolver.reverse("feeds:entry_detail", [id]);
	};

	preload('next');

	return self;
};


var registerPreloader = function() {
	if (!_.checkFeatures(['history_push'])) {
		return;
	}
	if (preloadCache === undefined) {
		preloadCache = PreloadCache(urlresolver.reverse("feeds:api_entry_list"));

		var nextItemLink = _.id('next_item_link');
		var prevItemLink = _.id('prev_item_link');
		var entryDetail = _.id('entry_detail');
		_.addClass(nextItemLink, 'nopjax');
		_.addClass(prevItemLink, 'nopjax');

		_.bindEvent(nextItemLink, 'click', function(e) {
			e.preventDefault();
			preloadCache.next(function(result) {
				if (result) {
					entryDetail.innerHTML = result.rendered;
				}
			});
		});
		_.bindEvent(prevItemLink, 'click', function(e) {
			e.preventDefault();
			preloadCache.prev(function(result) {
				if (result) {
					entryDetail.innerHTML = result.rendered;
				}
			});
		});
	}
};

var unregisterPreloader = function() {
	if (preloadCache !== undefined) {
		preloadCache.clearCallbacks();
		preloadCache = undefined;
	}
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
			var text;
			var resultRow = _.cls(formElement, 'result-row')[0];
			if (resultRow !== undefined) {
				opts.onStart = function() {
					resultRow.style.display = 'block';
					text = _.getData(formElement, 'waitingText');
					if (text) {
						resultRow.innerHTML = text;
					}
				};
				opts.onFinish = function() {
					resultRow.style.display = 'none';
					resultRow.innerHTML = '';
				};
				opts.onFail = function() {
					text = _.getData(formElement, 'errorText');
					if (text) {
						resultRow.style.display = 'block';
						resultRow.innerHTML = text;
					}
				};
			}
			//opts.waitingText = _.getData(formElement, 'celeryWaiting') || 'Loading ...';
			//celery.waitForResult(data.celery_result_url, opts);
			_.celeryTask(data.celery_result_url, opts);
		}
	}
};

var registerKeyEvents = function() {
	var leftPressed = function() {
		var link = _.cls('left-key-link')[0];
		if (link === undefined) {
			return;
		}
		link.click();
	};

	var rightPressed = function() {
		var link = _.cls('right-key-link')[0];
		if (link === undefined) {
			return;
		}
		link.click();
	};

	var openPressed = function() {
		var link = _.cls('open-key-link')[0];
		if (link === undefined) {
			return;
		}
		link.click();
	};

	var keyDown = function(e) {
		switch (e.which) {
			case 37: leftPressed(); break;
			case 39: rightPressed(); break;
			case 79: openPressed(); break;
			case 13: openPressed(); break;
		}
	};

	_.bindEvent(document, 'keydown', keyDown);
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
	if (element === document.body) {
		registerKeyEvents();
	}
	if (element.getAttribute('id') === 'content' || element === document.body || element.getAttribute('id') === 'entry_detail') {
		if (_.id(element, 'entry_detail') !== null || element.getAttribute('id') === 'entry_detail') {
			registerEntryDetail();
			if (_.id('next_item_link') !== null && preloadCache === undefined) {
				registerPreloader();
			}
		}
	}
};


_.pjax.autoRegister({
	bodyLoadingCls: 'loading',
	pjaxContainerId: 'content',
	extrajsBlock: 'extrajs',
	extrastyleBlock: 'extrastyle',
	titleBlock: 'head_title',
	checkLinkSupported: function(link) {
		if (_.hasClass(link, 'nopjax')) {
			return false;
		}
		return true;
	},
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
		unregisterPreloader();
		if (_.id('entry_detail') !== null) {
			registerPreloader();
		}
	}
});


_.onLoad(function(e) { register(e.memo); });


}(_utils));
