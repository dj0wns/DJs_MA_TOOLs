function MSTFile(file, name, location, length)
{
  this._file = file;
  this._fileReader = new FileReader();
  this.name = name;
  this.location = location;
  this.length = length;
  this.filetype = name.substring(name.indexOf(".") + 1).trim();
}

MSTFile.prototype.load = function(callback)
{
  this._loadCallback = callback;

  var blob = this._file.slice(this.location, this.location + this.length);
  this._fileReader.onloadend = this._onLoadData.bind(this);
  this._fileReader.readAsArrayBuffer(blob);
}

MSTFile.prototype._onLoadData = function(evt)
{
  if (evt.target.readyState != FileReader.DONE) {
    this._loadCallback(null, "Error reading file contents");
    return;
  }
  this._loadCallback(evt.target.result, null);
}
