function CSV()
{
  this.entries = null;
}

CSV.prototype.load = function(mst, buffer, callback)
{
  this.entries = [];
  var view = new DataView(buffer, 0);

  var entryCount = view.getUint32(4, mst.isLittleEndian);
  var pos = 16;

  for (var i = 0; i < entryCount * 16; i += 16)
  {
    var entry = {};

    var keyLocation   = view.getUint32(pos + i, mst.isLittleEndian);
    var keyLength     = view.getUint32(pos + i + 4, mst.isLittleEndian);
    var valueCount    = view.getUint16(pos + i + 8, mst.isLittleEndian);
    entry.index       = view.getUint16(pos + i + 10, mst.isLittleEndian);
    var valueLocation = view.getUint32(pos + i + 12, mst.isLittleEndian);

    var keyBuffer = new Uint8Array(buffer, keyLocation, keyLength);
    entry.key = String.fromCharCode.apply(null, keyBuffer);

    entry.values = [];
    var valuePos = valueLocation;

    for (var j = 0; j < valueCount; j++)
    {
      var type = view.getUint32(valuePos, mst.isLittleEndian);
      valuePos += 4;

      switch (type)
      {
        case 0: // string
          var stringLocation = view.getUint32(valuePos, mst.isLittleEndian);
          var stringLength = view.getUint32(valuePos + 4, mst.isLittleEndian);
          valuePos += 8;

          var stringBuffer = new Uint8Array(buffer, stringLocation, stringLength);
          var stringValue = String.fromCharCode.apply(null, stringBuffer);

          entry.values.push({ type: "string", value: stringValue });
          break;

        case 1: // number (float)
          var floatValue = view.getFloat32(valuePos, mst.isLittleEndian);
          valuePos += 8; // skip a 0 int32

          entry.values.push({ type: "number", value: floatValue });
          break;

        case 2: // pair? (two ints?)
          var pairValues = [
            view.getUint32(valuePos, mst.isLittleEndian),
            view.getUint32(valuePos + 4, mst.isLittleEndian)
          ];
          valuePos += 8;

          entry.values.push({ type: "pair", value: pairValues });
          break;

        default:
          callback(null, new MSTError("Unknown CSV value type: " + type + " at " + valuePos));
          return;
      }
    }

    this.entries.push(entry);
  }

  callback(this, null);
}
