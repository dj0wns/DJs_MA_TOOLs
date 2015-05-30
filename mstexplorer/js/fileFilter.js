angular.module("maTools").filter("fileFilter", function ()
{
	return function(items, filter)
	{
		if (items == null)
			return items;

		var result = [];

		for(var i = 0; i < items.length; ++i)
		{
			var item = items[i];
			var extension = item.name.substr(item.name.lastIndexOf(".") + 1);

			if (item.name.indexOf(filter.query) != -1)
			{
				result.push(item);
			}
		}

		return result;
	};
})