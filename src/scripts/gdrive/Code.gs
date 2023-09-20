/**
 * Script to download a folder on Google Drive as a zipfile.
 * subject to: https://developers.google.com/apps-script/guides/services/quotas
 */
function doGet(e) {
  /**
   * Expects the query string to include a folderId parameter.
   * Returns a TextOutput object with a JSON body including
   * the downloadUrl of the zipfile.
   */
  var folderId = e.parameter["folderId"];
  var downloadUrl = { "downloadUrl": _getZip(folderId) };
  return ContentService.createTextOutput(
    JSON.stringify(downloadUrl)).setMimeType(ContentService.MimeType.JSON);
}

function _getZip(folderId) {
  /**
   * folderId: the id of the folder to download as a zip.
   */
  var folder = DriveApp.getFolderById(folderId);
  var zippedName = folder.getName + '.zip';
  var zipped = Utilities.zip(_getBlobs(folder, ''), zippedName);


  // create file using the Drive REST API (to limit the scope of the OAuth token required)
  var fileMetadata = {
    title: zippedName,
    parents: ['id of parent folder'] // TODO find the folder to put in
  }
  var mediaData = {
    mimeType: zipped.getContentType(),
    body: zipped.getBytes()
  }
  var zipFile = Drive.Files.insert(fileMetadata, mediaData);
  Drive.Files.trash(zipFile.id); // the file will be deleted in 30 days
  return zipFile.downloadUrl;

  // // requires a very strong scope...
  // var zipFile = folder.getParents().next().createFile(zipped);
  // zipFile.setTrashed(true); // the file will be deleted in 30 days
  // return zipFile.getDownloadUrl()
}

function _getBlobs(rootFolder, path) {
  /**
   * Gets the content of the given folder as a series
   * of relative-pathed blobs, which will be zipped.
   */
  // list of blobs
  var blobs = [];

  // set of unique names
  var names = {};
  var files = rootFolder.getFiles();
  while (files.hasNext()) {
    var file = files.next().getBlob();
    var n = file.getName();
    // prepend an underscore until the name is unique
    while(names[n]) { n = '_' + n }
    names[n] = true;
    blobs.push(file.setName(path+n));
  }
  // reset the set
  names = {};
  var folders = rootFolder.getFolders();
  while (folders.hasNext()) {
    var folder = folders.next();
    var n = folder.getName();
    // prepend an underscore until the name is unique
    while(names[n]) { n = '_' + n }
    names[n] = true;
    var fPath = path+n+'/';
    blobs.push(Utilities.newBlob([]).setName(fPath)); //comment/uncomment this line to skip/include empty folders
    blobs = blobs.concat(getBlobs(folder, fPath));
  }
  return blobs;
}

