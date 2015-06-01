function MSTReader()
{
	this.isLittleEndian = true;
	this._fileNameLen = 20;
	this._fileStride = 36;
	this._entryCount = 0;
	this.entries = [];
}

MSTReader.prototype.load = function(file, callback)
{
	this.file = file;
	this._loadCallback = callback;
	this._fileReader = new FileReader();

	var headerBlob = this.file.slice(0, 108);
	this._fileReader.onloadend = this._onLoadHeader.bind(this);
	this._fileReader.readAsArrayBuffer(headerBlob);
}

MSTReader.prototype._onLoadHeader = function(evt)
{
	if (evt.target.readyState != FileReader.DONE) {
		this._loadCallback(null, new MSTError("Error reading header."));
		return;
	}

	var view = new DataView(evt.target.result, 0);

	var fang = view.getUint32(0, true);
	if (fang == 0x474E4146) this.isLittleEndian = true; // Ascii FANG (Xbox, PS2)
	else if (fang == 0x46414E47) this.isLittleEndian = false; // Ascii GNAF (GameCube)
	else {
		this._loadCallback(null, new MSTError("File does not contain a valid FANG header."));
		return;
	}

	// Hacky check to see if it's the PS2 version which has an extra four nulls at the end of the name string
	var ps2check = view.getUint32(72, this.isLittleEndian);
	if (ps2check == 3) {
		this._fileNameLen = 24;
		this._fileStride = 40;
	}

	this._entryCount = view.getUint32(12, this.isLittleEndian);

	var entriesBlob = this.file.slice(108, 108 + this._fileStride * this._entryCount);
	this._fileReader.onloadend = this._onLoadEntries.bind(this);
	this._fileReader.readAsArrayBuffer(entriesBlob);
}

MSTReader.prototype._onLoadEntries = function(evt)
{
		if (evt.target.readyState != FileReader.DONE) {
			this._loadCallback(null, new MSTError("Error reading entries."));
			return;
		}

		var view = new DataView(evt.target.result, 0);

		this.entries = [];
		for (var i = 0; i < this._entryCount * this._fileStride; i += this._fileStride) {
			var nameBuffer = new Uint8Array(evt.target.result, i, this._fileNameLen);
			var name = String.fromCharCode.apply(null, nameBuffer);
			name = name.substring(0, name.indexOf("\0")).trim();

			var location = view.getUint32(i + this._fileNameLen, this.isLittleEndian);
			var length = view.getUint32(i + this._fileNameLen + 4, this.isLittleEndian);

			var mstFile = new MSTFile(this, name, location, length);
			this.entries.push(mstFile);
		}

		this._loadCallback(this.entries, null);
}
