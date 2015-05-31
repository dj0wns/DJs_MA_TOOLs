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
			var extension = item.filetype.toUpperCase();
			var checked = filter.fileTypes[extension];

			if (checked == undefined && filter.fileTypes["other"] === true)
				checked = true;

			if (checked && (filter.query == "" || item.name.indexOf(filter.query) != -1))
			{
				result.push(item);
			}
		}

		return result;
	};
})