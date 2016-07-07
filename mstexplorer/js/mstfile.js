import MSTError from './msterror';
import CSV from './csv';

export default class MSTFile {
    constructor(mst, name, location, length) {
        this._mst = mst;
        this._fileReader = new FileReader();
        this.name = name;
        this.location = location;
        this.length = length;
        this.filetype = name.substring(name.indexOf(".") + 1).trim();
    }

    load(callback) {
        this._loadCallback = callback;

        var blob = this._mst.file.slice(this.location, this.location + this.length);
        this._fileReader.onloadend = this._onLoadData;
        this._fileReader.readAsArrayBuffer(blob);
    }

    _onLoadData = evt => {
        if (evt.target.readyState != FileReader.DONE) {
            this._loadCallback(null, new MSTError("Error reading file contents."));
            return;
        }

        switch (this.filetype) {
            case "csv":
                new CSV().load(this._mst, evt.target.result, this._loadCallback);
                break;

            default:
                this._loadCallback(evt.target.result, new MSTError("This file type can't be read yet."));
        }
    }
}