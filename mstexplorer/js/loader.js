var file;
var fileReader;
var fileEntryCount = 0;
var fileEntries = [];

function getSizeString(size) {
  if (size < 1024) return size + " bytes";
  if (size < 1024 * 1024) return Math.round(size / 1024) + " KB";
  return Math.round(size / 1024 / 1024) + " MB";
}

function onReadHeader(evt) {
  if (evt.target.readyState != FileReader.DONE) {
    Materialize.toast("Read error.", 4000);
    return;
  }
  var view = new DataView(evt.target.result, 0);

  var fangMagic = view.getUint32(0, true);
  if (fangMagic != 0x474E4146) {
    Materialize.toast("MST is invalid or wrong endianness. Please select an MST from the Xbox or PS2 version of the game.", 4000);
    return;
  }

  fileEntryCount = view.getUint32(12, true);
  //Materialize.toast("Loading " + fileEntryCount + " entries..", 1000);

  fileReader.onloadend = onReadEntries;
  var entriesBlob = file.slice(108, 108 + 36 * fileEntryCount);
  fileReader.readAsArrayBuffer(entriesBlob);
}

function onReadEntries(evt) {
  if (evt.target.readyState != FileReader.DONE) {
    Materialize.toast("Read error.", 4000);
    return;
  }
  var view = new DataView(evt.target.result, 0);

  for (var i = 0; i < (fileEntryCount - 1) * 36; i += 36) {
    var entryName = String.fromCharCode.apply(null, new Uint8Array(evt.target.result, i, 20)).replace(/\0/g, '');
    var entryLoc = view.getUint32(i + 20, true);
    var entryLen = view.getUint32(i + 24, true);

    fileEntries.push({
      name: entryName,
      location: entryLoc,
      length: entryLen
    });
  }
  
  Materialize.toast("Loaded " + fileEntryCount + " entries.", 4000);

  fileEntries.sort(function (a, b) {
    return b.length - a.length;
  });

  if (fileEntryCount > 0)
    $("#entrylist").html("");

  for (var i = 0; i < 1000; i += 100) {
    var entry = fileEntries[i];

    var ext = entry.name.substring(entry.name.indexOf(".") + 1).trim();
    var icon = "mdi-editor-insert-drive-file";

    if (ext == "tga") icon = "mdi-image-crop-original";
    if (ext == "wvb") icon = "mdi-image-audiotrack";
    if (ext == "wld") icon = "mdi-image-landscape";

    var entrystr = "<a href=\"#\" class=\"collection-item\" data-idx=\"" + i + "\" onclick=\"preview(this)\">";
    entrystr += "<i class=\"" + icon + "\"></i> ";
    entrystr += entry.name;
    entrystr += " (" + getSizeString(entry.length) +")";
    entrystr += "</a>";
    $("#entrylist").append(entrystr);
  }
}

function handleDrop(evt) {
  evt.stopPropagation();
  evt.preventDefault();

  var files = evt.dataTransfer.files;
  if (files.length > 1) {
    Materialize.toast("I never asked for this. One file only pls.", 4000);
    return;
  }
  file = files[0];

  $("#filedropper").hide(100);
  $("#entrylist").show(100);

  //Materialize.toast("Loading " + file.name, 1000);

  fileReader = new FileReader();
  fileReader.onloadend = onReadHeader;

  var headerBlob = file.slice(0, 16);
  fileReader.readAsArrayBuffer(headerBlob);
}

function handleHover(evt) {
  evt.stopPropagation();
  evt.preventDefault();
  evt.dataTransfer.dropEffect = "copy";
}

var dropzone = $("#filedropper")[0];
dropzone.addEventListener("drop", handleDrop, false);
dropzone.addEventListener("dragover", handleHover, false);
