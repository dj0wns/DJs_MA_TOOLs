var module = angular.module("maTools");

// Convert byte length into human readable string.
module.filter("friendlySize", function ()
{
	return function(input)
	{
		if (typeof(input) != "number")
			return input.toString();

		if (input < 1000)
			return input + " B";
		if (input < 1000000)
			return (input / 1000).toFixed(2) + " kB";
		if (input < 1000000000)
			return (input / 1000000).toFixed(2) + " mB";
		else
			return (input / 1000000000).toFixed(2) + " gB";

	};
});