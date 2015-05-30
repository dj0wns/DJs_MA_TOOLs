function MSTReader()
{
  this._littleEndian = true;
  this._entryCount = 0;
  this.entries = [];
}

MSTReader.prototype.load = function(file, callback)
{
  this._file = file;
  this._loadCallback = callback;
  this._fileReader = new FileReader();

  var headerBlob = this._file.slice(0, 16);
  this._fileReader.onloadend = this._onLoadHeader.bind(this);
  this._fileReader.readAsArrayBuffer(headerBlob);
}

MSTReader.prototype._onLoadHeader = function(evt)
{
  if (evt.target.readyState != FileReader.DONE) {
    this._loadCallback(null, new MSTError("Error reading header"));
    return;
  }

  var view = new DataView(evt.target.result, 0);

  var fang = view.getUint32(0, true);
  if (fang == 0x474E4146) this._littleEndian = true; // Ascii FANG (Xbox, PS2)
  else if (fang == 0x46414E47) this._littleEndian = false; // Ascii GNAF (GameCube)
  else {
    this._loadCallback(null, new MSTError("MST does not contain a valid FANG header"));
    return;
  }

  this._entryCount = view.getUint32(12, this._littleEndian);

  var entriesBlob = this._file.slice(108, 108 + 36 * this._entryCount);
  this._fileReader.onloadend = this._onLoadEntries.bind(this);
  this._fileReader.readAsArrayBuffer(entriesBlob);
}

MSTReader.prototype._onLoadEntries = function(evt)
{
    if (evt.target.readyState != FileReader.DONE) {
      this._loadCallback(null, new MSTError("Error reading entries"));
      return;
    }

    var view = new DataView(evt.target.result, 0);

    this.entries = [];
    for (var i = 0; i < (this._entryCount - 1) * 36; i += 36) {
      var nameBuffer = new Uint8Array(evt.target.result, i, 20);
      var name = String.fromCharCode.apply(null, nameBuffer).replace(/\0/g, '').trim();

      var location = view.getUint32(i + 20, this._littleEndian);
      var length = view.getUint32(i + 24, this._littleEndian);

      var mstFile = new MSTFile(this._file, name, location, length);
      this.entries.push(mstFile);
    }

    this._loadCallback(this.entries, null);
}
