const module = angular.module("maTools");

module.directive("settingOption", () => {
    return {
        restrict: "A",
        replace: true,
        templateUrl: "templates/settingOption.html",
        link: (scope, elements) => {
            const element = $(elements[0]);
            const inputElement = element.find("input");
            const setting = scope.setting;

            for(const key in setting.meta) {
                inputElement.attr(key, setting.meta[key])
            }

            if (setting.type != "range") {
                element.find(".value-preview").hide();
            }
        }
    };
});