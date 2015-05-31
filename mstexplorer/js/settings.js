var module = angular.module("maTools");

module.directive("settingOption", function ()
{
	return {
		restrict: "A",
		replace: true,
		templateUrl: "templates/settingOption.html",
		link: function (scope, elements)
		{
			var element = $(elements[0]);
			var inputElement = element.find("input");
			var setting = scope.setting;

			for(var key in setting.meta)
			{
				inputElement.attr(key, setting.meta[key])
			}

			if (setting.type != "range")
			{
				element.find(".value-preview").hide();
			}
		}
	};
});