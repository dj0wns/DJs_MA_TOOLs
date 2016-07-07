import MSTReader from './mstreader';

const module = angular.module("maTools", ["angularUtils.directives.dirPagination", "ngStorage"]);

module.controller("maTools", ["$scope", "$localStorage", ($scope, $localStorage) => {
    // Set storage defaults.
    $localStorage.$default({

        // Default settings
        settings: {
            itemsPerPage: 30
        }

    });

    const reader = new MSTReader();

    function loadFilesArray(filesArray, callback) {
        if (filesArray.length > 1) {
            Materialize.toast("More than one file was selected.", UI.TOAST_LONG, UI.ERROR_CLASS);
            callback && callback(null, new UIError("More than one file was selected."));
            return;
        }

        var file = filesArray[0];
        reader.load(file, (files, error) => {
            if (error) {
                Materialize.toast(error.message, UI.TOAST_LONG, UI.ERROR_CLASS);
                callback && callback(null, error);
                return;
            }

            $scope.files = files;
            $scope.$apply(); // Update view.

            Materialize.toast("Found " + files.length + " files.", UI.TOAST_SHORT);
            callback && callback(files);
            console.log(files);
        });
    }

    $("#settingsOpener").leanModal();

    $scope.files = null;
    $scope.openedFile = null;
    $scope.fileTypes = [
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
    $scope.settingsForm = [
        {
            "type": "range", // The element input type.
            "meta": {min: 5, max: 100, step: 5},
            "class": "validate", // Classes to apply to the input element.
            "setting": "itemsPerPage", // The setting key in $scope.settings.
            "text": "Files per page",
            "description": "The number of files to show per page."
        }
    ];

    $scope.settings = $localStorage.settings;

    $scope.search_filename = "";
    $scope.filter = { query: "", fileTypes: {} };

    // Apply default checked state to filter
    for (const i in $scope.fileTypes) {
        $scope.filter.fileTypes[$scope.fileTypes[i].extension.toUpperCase()] = $scope.fileTypes[i].checked;
    }

    // Watch for changes to filename search input and update.
    $scope.$watch("search_filename", (newVal, oldVal) => {
        if (newVal == oldVal)
            return;

        $scope.applyFilters();
    });

    $("#dropzone").dragster({
        enter: ev => { $(this).addClass("hover"); },
        leave: ev => { $(this).removeClass("hover"); },
        drop: (ev, jEvent) => {
            $(this).removeClass("hover");
            const dataTransfer = jEvent.originalEvent.dataTransfer;
            loadFilesArray(dataTransfer.files);
        }
    });

    $scope.applyFilters = () => {
        $scope.filter.query = $scope.search_filename;

        $scope.filter.fileTypes = {};
        for (const i in $scope.fileTypes) {
            const fileType = $scope.fileTypes[i];
            $scope.filter.fileTypes[fileType.extension] = fileType.checked;
        }
    };

    $scope.toggleFiletypeCheckboxes = state => {
        for (const i in $scope.fileTypes) {
            const fileType = $scope.fileTypes[i];
            fileType.checked = state;
        }

        $scope.applyFilters();
    };

    $scope.browseForFile = () => {
        var elm = $("#fileBrowser");

        elm.unbind("change").one("change", () => { loadFilesArray(elm[0].files); });
        elm.click();
    };

    $scope.openFile = file => {
        file.load((data, error) => {
            if (error) {
                Materialize.toast(error.message, UI.TOAST_LONG, UI.ERROR_CLASS);
                return;
            }

            switch(file.filetype) {
                case "csv":
                {
                    initializeCsv(data);
                    break;
                }
            }

            $scope.openedFile = { file: file, data: data };
            $scope.$apply(); // Apply scope view since this code is called inside the callback function.
            switchTab("previewtab"); // bug: the tab doesn't show unless you click it with the mouse for some reason.
        });
    };

    function switchTab(tab) {
        $("ul.tabs").tabs("select_tab", tab);
    }

    // Sets up the preview page with data from the file.
    function initializeCsv(file) {
        // Destroy previous editor if any.
        if ($scope.currentCsvEditor) {
            $scope.currentCsvEditor.destroy();
        }

        var data = file.toHandsOnFormat();
        var containerElement = $("#csv-preview")[0];
        var table = new Handsontable(containerElement, {
            data: data,
            colHeaders: true
        });

        $scope.currentCsvEditor = table;
    };
}]);