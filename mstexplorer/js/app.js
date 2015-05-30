+function()
{
	var module = angular.module("maTools", ["angularUtils.directives.dirPagination"]);

	module.controller("maTools", ["$scope", function ($scope)
	{
		var reader = new MSTReader();

		$scope.files = null;
		$scope.fileTypes =
		[
			{
				"extension": "WLD",
				"name": "Levels",
				"description": "World levels (.WLD)"
			},
			{
				"extension": "APE",
				"name": "Models",
				"description": "3D models (.APE)"
			},
			{
				"extension": "FPR",
				"name": "Particles",
				"description": "Particle effects (.FPR)"
			},
			{
				"extension": "WVB",
				"name": "Sounds",
				"description": "Wavebanks containing multiple sounds (.WVB)"
			},
			{
				"extension": "CSV",
				"name": "CSV tables",
				"description": "Compiled CSV tables (.CSV)"
			},
			{
				"extension": "other",
				"name": "Other",
				"description": "Other filetypes not yet identified"
			}
		];
		$scope.filter = {query:"", fileTypes: {}};

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

		$scope.applyFilters = function ()
		{
			$scope.filter.query = $scope.search_filename;
		};
	}]);
}();