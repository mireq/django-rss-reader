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
	setEelemntText(element, text);
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
		var url = buildFeedUrl(direction);
		firstRun = false;
		_.xhrSend({
			url: url,
			successFn: function(response) {
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
				triggerLoad(direction);
			}
		});
	};

	var preloadNext = function() {
		preloadCache('next');
	};

	var preloadPrev = function() {
		preloadCache('prev');
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
				setEntryId(current.id);
			}
		}
		else {
			if (prevCache.length) {
				if (current) {
					nextCache.unshift(current);
				}
				current = prevCache.pop();
				setEntryId(current.id);
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
			if (nextCache.length < 5) {
				preloadNext();
			}
		}
		if (direction === 'prev') {
			if (prevCache.length) {
				triggerLoad(direction);
			}
			if (prevCache.length < 5) {
				preloadPrev();
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


var module = {
	getNextId: function() {
		return preloadCache.getNextId();
	},
	getPrevId: function() {
		return preloadCache.getPrevId();
	},
	getNextLink: function() {
		return preloadCache.getNextLink();
	},
	getPrevLink: function() {
		return preloadCache.getPrevLink();
	}
};


var registerPreloader = function() {
	if (!_.checkFeatures(['history_push'])) {
		return;
	}
	if (preloadCache === undefined && window.template !== undefined && window.template.entry !== undefined) {
		preloadCache = PreloadCache(urlresolver.reverse("feeds:api_entry_list"));

		var nextItemLink = _.id('next_item_link');
		var prevItemLink = _.id('prev_item_link');
		_.addClass(nextItemLink, 'nopjax');
		_.addClass(prevItemLink, 'nopjax');

		_.bindEvent(nextItemLink, 'click', function(e) {
			e.preventDefault();
			preloadCache.next(function(result) {
				if (result) {
					window.template.entry(result, module);
				}
			});
		});
		_.bindEvent(prevItemLink, 'click', function(e) {
			e.preventDefault();
			preloadCache.prev(function(result) {
				if (result) {
					window.template.entry(result, module);
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

//var registerPreloader = function() {
//	var nextItemLink = _.id('next_item_link');
//	if (nextItemLink !== null && nextItemLink.getAttribute('href') !== '#') {
//		var preloaderNext = preloadUrl(nextItemLink.getAttribute('href'));
//		var clone = nextItemLink.cloneNode(false);
//		nextItemLink.parentNode.replaceChild(clone, nextItemLink);
//		nextItemLink = clone;
//		_.bindEvent(nextItemLink, 'click', function(e) {
//			e.preventDefault();
//			preloaderNext.open();
//			_.xhrSend({
//				url: nextItemLink.getAttribute('href') + '?mark',
//				successFn: function(response, res, opts) {
//					setNewEntries(response.new_entries_count);
//				}
//			});
//		});
//	}
//};
//
//var preloadUrl = function(url) {
//	var self = {};
//
//	var opened = false;
//	var responseData;
//
//	self.open = function() {
//		opened = true;
//		if (responseData !== undefined) {
//			if (responseData === null) {
//				_.pjax.load(url);
//			}
//			else {
//				_.pjax.load(url, { response: responseData });
//			}
//		}
//	};
//
//	_.xhrSend({
//		url: url + '?cache',
//		extraHeaders: {
//			'X-PJAX': 'true'
//		},
//		successFn: function(response) {
//			responseData = response;
//			if (opened) {
//				_.pjax.load(url, { response: responseData });
//			}
//		},
//		failFn: function() {
//			responseData = null;
//			if (opened) {
//				_.pjax.load(url);
//			}
//		}
//	});
//
//	return self;
//};

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
	if (element.getAttribute('id') === 'content' || element === document.body) {
		if (_.id(element, 'entry_detail') !== null) {
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
