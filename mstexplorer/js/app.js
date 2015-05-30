+function()
{
	var module = angular.module("maTools", []);

	module.controller("maTools", ["$scope", function ($scope)
	{
		var reader = new MSTReader();
		var ui = new UI();

		window.reader = reader; // debug
		window.ui = ui; // debug

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
				reader.load(file, function (data, error)
				{
					if (error)
					{
						Materialize.toast(error.message, UI.TOAST_LONG, UI.ERROR_CLASS);
						return;
					}

					console.log(data);
					Materialize.toast("Found " + data.length + " files.", UI.TOAST_SHORT);
				});
			}
		});
	}]);
}();