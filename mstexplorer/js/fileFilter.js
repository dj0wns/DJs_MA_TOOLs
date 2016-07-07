angular.module("maTools").filter("fileFilter", () => {
    return (items, filter) => {
        if (items == null) {
            return items;
        }

        const result = [];

        for(let i = 0; i < items.length; ++i) {
            const item = items[i];
            const extension = item.filetype.toUpperCase();
            let checked = filter.fileTypes[extension];

            if (checked == undefined && filter.fileTypes["other"] === true) {
                checked = true;
            }

            if (checked && (filter.query == "" || item.name.indexOf(filter.query) != -1)) {
                result.push(item);
            }
        }

        return result;
    };
})

.filter("rawHtml", ["$sce", ($sce) => {
    return (input, filter) => {
        console.log(input);
        return $sce.trustAsHtml(input);
    };
}]);