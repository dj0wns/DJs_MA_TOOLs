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
				"description": "World levels (.WLD)",
				"checked": true
			},
			{
				"extension": "TGA",
				"name": "Textures",
				"description": "Textures (.TGA)",
				"checked": true
			},
			{
				"extension": "APE",
				"name": "Models",
				"description": "3D models (.APE)",
				"checked": true
			},
			{
				"extension": "FPR",
				"name": "Particles",
				"description": "Particle effects (.FPR)",
				"checked": true
			},
			{
				"extension": "WVB",
				"name": "Sounds",
				"description": "Wavebanks containing multiple sounds (.WVB)",
				"checked": true
			},
			{
				"extension": "CSV",
				"name": "CSV tables",
				"description": "Compiled CSV tables (.CSV)",
				"checked": true
			},
			{
				"extension": "other",
				"name": "Other",
				"description": "Other filetypes not yet identified",
				"checked": true
			}
		];

		$scope.settings = {
			itemsPerPage: 30
		};

		$scope.search_filename = "";
		$scope.filter = { query: "", fileTypes: {} };

		// Apply default checked state to filter
		for (var i in $scope.fileTypes)
			$scope.filter.fileTypes[$scope.fileTypes[i].extension.toUpperCase()] = $scope.fileTypes[i].checked;

		// Watch for changes to filename search input and update.
		$scope.$watch("search_filename", function (newVal, oldVal)
		{
			if (newVal == oldVal)
				return;

			$scope.applyFilters();
		});

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

			$scope.filter.fileTypes = {};
			for (var i in $scope.fileTypes)
			{
				var fileType = $scope.fileTypes[i];
				$scope.filter.fileTypes[fileType.extension] = fileType.checked;
			}
		};

		$scope.toggleFiletypeCheckboxes = function (state)
		{
			for (var i in $scope.fileTypes)
			{
				var fileType = $scope.fileTypes[i];
				fileType.checked = state;
			}

			$scope.applyFilters();
		};
	}]);
}();