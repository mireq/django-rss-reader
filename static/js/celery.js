(function(_) {


var celeryTask = function(url, opts) {
	var self = {};
	var modal, timer, counter;

	var checkTask = function() {
		_.xhrSend({
			method: 'GET',
			url: url,
			successFn: function(result) {
				if (result.celery_task) {
					var task = result.celery_task;
					if (task.status === 'PROGRESS') {
						onCheck(result.celery_task);
					}
					else if (task.status === 'FAILURE') {
						onFail();
					}
					else if (task.status === 'SUCCESS') {
						onFinish();
					}
				}
				if (result.redirect !== undefined) {
					onFinish();
					_.pjax.load(result.redirect);
				}
			}
		});
	};

	var stopTinmer = function() {
		if (timer !== undefined) {
			clearInterval(timer);
			timer = undefined;
		}
	};

	var onStart = function() {
		timer = setInterval(checkTask, 500);

		if (opts.onStart !== undefined) {
			opts.onStart();
		}
	};

	var onFinish = function() {
		if (opts.onFinish !== undefined) {
			opts.onFinish();
		}
		stopTinmer();
	};

	var onFail = function() {
		if (opts.onFail !== undefined) {
			opts.onFail();
		}
		stopTinmer();
	};

	var onCheck = function(celery_task) {
		if (opts.onStart !== undefined) {
			opts.onCheck(celery_task);
		}
	};

	onStart();

	return self;
};


_utils.celeryTask = celeryTask;


}(_utils));
