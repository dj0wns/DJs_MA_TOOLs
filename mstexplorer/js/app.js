+function()
{
	var module = angular.module("maTools", ["angularUtils.directives.dirPagination"]);

	module.controller("maTools", ["$scope", function ($scope)
	{
		var reader = new MSTReader();
		window.reader = reader; // debug

		$scope.files = null;

		$("#dropzone").dragster({
			enter: function (ev)
			{
				$(this).addClass("hover");
			},
			leave: function (ev)
			{
				$(this).removeClass("hover");
			},
			drop: function (ev, jEvent)
			{
				$(this).removeClass("hover");
				var dataTransfer = jEvent.originalEvent.dataTransfer;

				if (dataTransfer.files.length > 1)
				{
					Materialize.toast("More than one file was selected.", UI.TOAST_LONG, UI.ERROR_CLASS);
					return;
				}

				var file = dataTransfer.files[0];
				reader.load(file, function (files, error)
				{
					if (error)
					{
						Materialize.toast(error.message, UI.TOAST_LONG, UI.ERROR_CLASS);
						return;
					}

					$scope.files = files;
					$scope.$apply(); // Update view.
					
					Materialize.toast("Found " + files.length + " files.", UI.TOAST_SHORT);
				});
			}
		});
	}]);
}();