var module = angular.module("maTools");

// Convert byte length into human readable string.
module.filter("friendlySize", () => {
    return input => {
        if (typeof(input) != "number") {
            return input.toString();
        }

        const kbSize = 1024;
        const mbSize = kbSize * 1024;
        const gbSize = mbSize * 1024;

        if (input < kbSize) {
            return input + " B";
        }
        if (input < mbSize) {
            return (input / kbSize).toFixed(2) + " KB";
        }
        if (input < gbSize) {
            return (input / mbSize).toFixed(2) + " MB";
        } else {
            return (input / gbSize).toFixed(2) + " GB";
        }
    };
});