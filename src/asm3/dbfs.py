
import asm3.al
import asm3.cachedisk
import asm3.smcom
import asm3.utils

from asm3.sitedefs import DBFS_STORE, DBFS_FILESTORAGE_FOLDER
from asm3.sitedefs import DBFS_S3_BUCKET, DBFS_S3_ACCESS_KEY_ID, DBFS_S3_SECRET_ACCESS_KEY, DBFS_S3_ENDPOINT_URL
from asm3.sitedefs import DBFS_S3_MIGRATE_BUCKET, DBFS_S3_MIGRATE_ACCESS_KEY_ID, DBFS_S3_MIGRATE_SECRET_ACCESS_KEY, DBFS_S3_MIGRATE_ENDPOINT_URL

import mimetypes
import os, sys, threading, time

import web062 as web

class DBFSStorage(object):
    """ DBFSStorage factory """
    o = None
    def __init__(self, dbo, url = "default" ):
        """ Creates the correct storage object from mode or url """
        if url == "default":
            self._storage_from_mode(dbo)
        else:
            self._storage_from_url(dbo, url)

    def _storage_from_url(self, dbo, url):
        """ Creates an appropriate storage object for the url given. """
        if url is None or url == "" or url.startswith("base64:"):
            self.o = B64DBStorage(dbo)
        elif url.startswith("file:"):
            self.o = FileStorage(dbo)
        elif url.startswith("s3:"):
            self.o = S3Storage(dbo)
        else:
            raise DBFSError("Invalid storage URL: %s" % url)

    def _storage_from_mode(self, dbo):
        """ Creates an appropriate storage object for the mode given """
        if DBFS_STORE == "database":
            self.o = B64DBStorage(dbo)
        elif DBFS_STORE == "file":
            self.o = FileStorage(dbo)
        elif DBFS_STORE == "s3":
            self.o = S3Storage(dbo)
        else:
            raise DBFSError("Invalid storage mode: %s" % DBFS_STORE)

    def _extension_from_filename(self, filename):
        if filename is None or filename.find(".") == -1: return ""
        return filename[filename.rfind("."):]

    def get(self, dbfsid, url):
        """ Get file data for dbfsid/url """
        return self.o.get(dbfsid, url)
    def put(self, dbfsid, filename, filedata):
        """ Store filedata for dbfsid, returning a url """
        return self.o.put(dbfsid, filename, filedata)
    def delete(self, url):
        """ Delete filedata for url """
        return self.o.delete(url)
    def url_prefix(self):
        return self.o.url_prefix()

class B64DBStorage(DBFSStorage):
    """ Storage class for base64 encoding media and storing them
        in the database """
    dbo = None
    
    def __init__(self, dbo):
        self.dbo = dbo
    
    def get(self, dbfsid, dummy):
        """ Returns the file data for dbfsid or blank if not found/error """
        r = self.dbo.query_tuple("SELECT Content FROM dbfs WHERE ID = ?", [dbfsid])
        if len(r) == 0:
            raise DBFSError("Could not find content for ID %s" % dbfsid)
        try:
            return asm3.utils.base64decode(r[0][0])
        except:
            em = str(sys.exc_info()[0])
            raise DBFSError("Failed unpacking base64 content with ID %s: %s" % (dbfsid, em))

    def put(self, dbfsid, filename, filedata):
        """ Stores the file data and returns a URL """
        url = "base64:"
        s = asm3.utils.base64encode(filedata)
        self.dbo.execute("UPDATE dbfs SET URL = ?, Content = ? WHERE ID = ?", (url, s, dbfsid))
        return url

    def delete(self, url):
        """ Do nothing - removing the database row takes care of it """
        pass

    def url_prefix(self):
        return "base64:"

class FileStorage(DBFSStorage):
    """ Storage class for putting media on disk """
    dbo = None
    
    def __init__(self, dbo):
        self.dbo = dbo

    def get(self, dbfsid, url):
        """ Returns the file data for url """
        filepath = "%s/%s/%s" % (DBFS_FILESTORAGE_FOLDER, self.dbo.database, url.replace("file:", ""))
        return asm3.utils.read_binary_file(filepath)

    def put(self, dbfsid, filename, filedata):
        """ Stores the file data (clearing the Content column) and returns the URL """
        try:
            path = "%s/%s" % (DBFS_FILESTORAGE_FOLDER, self.dbo.database)
            os.mkdir(path)
        except OSError:
            pass # Directory already exists - ignore
        extension = self._extension_from_filename(filename)
        filepath = "%s/%s/%s%s" % (DBFS_FILESTORAGE_FOLDER, self.dbo.database, dbfsid, extension)
        url = "file:%s%s" % (dbfsid, extension)
        asm3.utils.write_binary_file(filepath, filedata)
        os.chmod(filepath, 0o666) # Make the file world read/write
        self.dbo.execute("UPDATE dbfs SET URL = ?, Content = '' WHERE ID = ?", (url, dbfsid))
        return url

    def delete(self, url):
        """ Deletes the file data """
        filepath = "%s/%s/%s" % (DBFS_FILESTORAGE_FOLDER, self.dbo.database, url.replace("file:", ""))
        try:
            os.unlink(filepath)
        except Exception as err:
            asm3.al.error("Failed deleting '%s': %s" % (url, err), "FileStorage.delete", self.dbo)

    def url_prefix(self):
        return "file:"

class S3Storage(DBFSStorage):
    """ Storage class for putting media in Amazon S3 """
    dbo = None
    access_key_id = ""
    secret_access_key = ""
    endpoint_url = ""
    bucket = ""
    
    def __init__(self, dbo, access_key_id="", secret_access_key="", endpoint_url="", bucket=""):
        self.dbo = dbo
        self.access_key_id = DBFS_S3_ACCESS_KEY_ID
        self.secret_access_key = DBFS_S3_SECRET_ACCESS_KEY
        self.endpoint_url = DBFS_S3_ENDPOINT_URL
        self.bucket = DBFS_S3_BUCKET
        if access_key_id != "": self.access_key_id = access_key_id
        if secret_access_key != "": self.secret_access_key = secret_access_key
        if bucket != "": self.bucket = bucket
        if endpoint_url != "": self.endpoint_url = endpoint_url 
        if self.endpoint_url == "aws": self.endpoint_url = "" # use "aws" in config files for aws default

    def _cache_key(self, url):
        """ Calculates a cache key for url """
        return "%s:%s" % (self.dbo.database, url)

    def _cache_ttl(self, name):
        """ Gets the cache ttl for a file based on its name/extension """
        #name = name.lower()
        #if name.endswith(".jpg") or name.endswith(".jpeg"): return (86400 * 7) # Cache images for a week
        #return (86400 * 2) # Cache everything else for two days
        return (86400 * 7) # Cache everything for 1 week

    def _s3client(self):
        """ Gets an s3 client.
            Creates a new boto3 session each time as the default one is not thread safe
            This does have a significant performance impact. There's a boto issue to make sessions thread safe in future.
            To use the default session, self.s3client = boto3.client("s3")
            We avoid some of the performance problems by using our disk cache and
            forcing put/delete operations onto a background thread.
        """
        import boto3
        session = boto3.Session() 
        # Non-AWS S3 provider with an endpoint url
        if self.endpoint_url != "" and self.access_key_id != "" and self.secret_access_key != "":
            return session.client("s3", endpoint_url=self.endpoint_url, aws_access_key_id=self.access_key_id, aws_secret_access_key=self.secret_access_key)
        # AWS S3
        elif self.access_key_id != "" and self.secret_access_key != "":
            return session.client("s3", aws_access_key_id=self.access_key_id, aws_secret_access_key=self.secret_access_key)
        # Use $HOME/.aws/credentials
        else:
            return session.client("s3")

    def get(self, dbfsid, url, migrate=True):
        """ Returns the file data for url, reads through the disk cache """
        cachekey = self._cache_key(url)
        cachettl = self._cache_ttl(url)
        cachedata = asm3.cachedisk.touch(cachekey, self.dbo.database, cachettl) # Use touch so accessed items stay in the cache longer
        if cachedata is not None:
            return cachedata
        object_key = "%s/%s" % (self.dbo.database, url.replace("s3:", ""))
        try:
            asm3.al.debug("GET: s3://%s/%s" % (self.bucket, object_key), "S3Storage.get", self.dbo)
            x = time.time()
            response = self._s3client().get_object(Bucket=self.bucket, Key=object_key)
            body = response["Body"].read()
            asm3.al.debug("get_object(s3://%s/%s), %s bytes in %0.2fs" % (self.bucket, object_key, len(body), time.time() - x), "dbfs.S3Storage.get", self.dbo)
            asm3.cachedisk.put(cachekey, self.dbo.database, body, cachettl)
            return body
        except Exception as err:
            # We couldn't retrieve the object. Retrieve it from S3 migrate credentials if we have them.
            # On success, copy the migrated object to our current S3 storage on a background thread.
            if migrate and DBFS_S3_MIGRATE_ACCESS_KEY_ID != "":
                asm3.al.debug("%s not found in '%s', migrating from '%s'" % (object_key, self.endpoint_url, DBFS_S3_MIGRATE_ENDPOINT_URL), "dbfs.S3Storage.get", self.dbo)
                migrate = S3Storage(self.dbo, DBFS_S3_MIGRATE_ACCESS_KEY_ID, DBFS_S3_MIGRATE_SECRET_ACCESS_KEY, DBFS_S3_MIGRATE_ENDPOINT_URL, DBFS_S3_MIGRATE_BUCKET)
                body = migrate.get(dbfsid, url, migrate=False)
                threading.Thread(target=self._s3_put_object, args=[self.bucket, object_key, body]).start()
                return body
            else:
                asm3.al.error(str(err), "dbfs.S3Storage.get", self.dbo)
                raise DBFSError("Failed retrieving from S3 (endpoint=%s): %s" % (self.endpoint_url, err))

    def put(self, dbfsid, filename, filedata):
        """ Stores the file data (clearing the Content column) and returns the URL """
        extension = self._extension_from_filename(filename)
        object_key = "%s/%s%s" % (self.dbo.database, dbfsid, extension)
        url = "s3:%s%s" % (dbfsid, extension)
        try:
            asm3.al.debug("PUT: s3://%s/%s" % (self.bucket, object_key), "S3Storage.put", self.dbo)
            asm3.cachedisk.put(self._cache_key(url), self.dbo.database, filedata, self._cache_ttl(filename))
            self.dbo.execute("UPDATE dbfs SET URL = ?, Content = '' WHERE ID = ?", (url, dbfsid))
            threading.Thread(target=self._s3_put_object, args=[self.bucket, object_key, filedata]).start()
            return url
        except Exception as err:
            asm3.al.error(str(err), "dbfs.S3Storage.put", self.dbo)
            raise DBFSError("Failed storing in S3: %s" % err)

    def delete(self, url):
        """ Deletes the file data """
        object_key = "%s/%s" % (self.dbo.database, url.replace("s3:", ""))
        try:
            asm3.al.debug("DELETE: s3://%s/%s" % (self.bucket, object_key), "S3Storage.delete", self.dbo)
            asm3.cachedisk.delete(self._cache_key(url), self.dbo.database)
            threading.Thread(target=self._s3_delete_object, args=[self.bucket, object_key]).start()
        except Exception as err:
            asm3.al.error(str(err), "dbfs.S3Storage.delete", self.dbo)
            raise DBFSError("Failed deleting from S3: %s" % err)

    def _s3_delete_object(self, bucket, key):
        """ Deletes an object in S3. This should be called on a new thread """
        try:
            x = time.time()
            self._s3client().delete_object(Bucket=bucket, Key=key)
            asm3.al.debug("delete_object(s3://%s/%s) in %0.2fs" % (bucket, key, time.time() - x), "dbfs.S3Storage._s3_delete_object", self.dbo)
        except Exception as err:
            asm3.al.error(str(err), "dbfs.S3Storage._s3_delete_object", self.dbo)

    def _s3_put_object(self, bucket, key, body):
        """ Puts an object in S3. This should be called on a new thread """
        try:
            x = time.time()
            self._s3client().put_object(Bucket=bucket, Key=key, Body=body)
            asm3.al.debug("put_object(s3://%s/%s) %s bytes in %0.2fs" % (bucket, key, len(body), time.time() - x), "dbfs.S3Storage._s3_put_object", self.dbo)
        except Exception as err:
            asm3.al.error(str(err), "dbfs.S3Storage._s3_put_object", self.dbo)
            try:
                # The PUT has failed. Wait 10 seconds and try to do it again. 
                # If that fails, send an error email to the admin as this is a lost file and critical.
                time.sleep(10)
                self._s3client().put_object(Bucket=bucket, Key=key, Body=body)
                asm3.al.debug("put_object(s3://%s/%s) %s bytes in %0.2fs" % (bucket, key, len(body), time.time() - x), "dbfs.S3Storage._s3_put_object", self.dbo)
            except Exception as err2:
                asm3.al.error("retry fail: %s" % err2, "dbfs.S3Storage._s3_put_object", self.dbo)
                asm3.utils.send_error_email()

    def url_prefix(self):
        return "s3:"

class DBFSError(web.HTTPError):
    """ Custom error thrown by dbfs modules """
    def __init__(self, msg):
        status = '500 Internal Server Error'
        headers = { 'Content-Type': "text/html" }
        data = "<h1>DBFS Error</h1><p>%s</p>" % msg
        web.HTTPError.__init__(self, status, headers, data)

def create_path(dbo, path, name):
    """ Creates a new DBFS folder """
    return dbo.insert("dbfs", {
        "Name": name,
        "Path": path
    })

def check_create_path(dbo, path):
    """ Verifies that portions of a path exist and creates them if not
    only goes to two levels deep as we never need more than that
    for anything within ASM.
    """
    def check(name, path):
        if 0 == dbo.query_int("SELECT COUNT(*) FROM dbfs WHERE Name = ? AND Path = ?", (name, path)):
            create_path(dbo, path, name)
    pat = path[1:].split("/")
    check(pat[0], "/")
    if len(pat) > 1:
        check(pat[1], "/" + pat[0])

def get_string_filepath(dbo, filepath):
    """
    Gets DBFS file contents as a bytes string. Returns
    an empty string if the file is not found. Splits
    filepath into the name and path to do it.
    """
    name = filepath[filepath.rfind("/")+1:]
    path = filepath[0:filepath.rfind("/")]
    return get_string(dbo, name, path)

def get_string(dbo, name, path = ""):
    """
    Gets DBFS file contents as a bytes string.
    If no path is supplied, just finds the first file with that name
    in the dbfs (useful for media files, which have unique names)
    """
    if path != "":
        r = dbo.query("SELECT ID, URL FROM dbfs WHERE Name=? AND Path=?", (name, path))
    else:
        r = dbo.query("SELECT ID, URL FROM dbfs WHERE Name=?", [name])
    if len(r) == 0:
        raise DBFSError("No element found for path=%s, name=%s" % (path, name))
    r = r[0]
    o = DBFSStorage(dbo, r.url)
    return o.get(r.id, r.url)

def get_string_id(dbo, dbfsid):
    """
    Gets DBFS file contents as a bytes string.
    """
    r = dbo.query("SELECT URL FROM dbfs WHERE ID=?", [dbfsid])
    if len(r) == 0:
        raise DBFSError("No row found with ID %s" % dbfsid)
    r = r[0]
    o = DBFSStorage(dbo, r.url)
    return o.get(dbfsid, r.url)

def rename_file(dbo, path, oldname, newname):
    """
    Renames a file in the dbfs.
    """
    dbo.execute("UPDATE dbfs SET Name = ? WHERE Name = ? AND Path = ?", (newname, oldname, path))

def rename_file_id(dbo, dbfsid, newname):
    """
    Renames a file in the dbfs.
    """
    dbo.execute("UPDATE dbfs SET Name = ? WHERE ID = ?", (newname, dbfsid))

def put_file(dbo, name, path, filepath):
    """
    Reads the the file from filepath and stores it with name/path
    """
    check_create_path(dbo, path)
    s = asm3.utils.read_binary_file(filepath)
    dbfsid = dbo.insert("dbfs", {
        "Name": name,
        "Path": path
    })
    o = DBFSStorage(dbo)
    o.put(dbfsid, name, s)
    return dbfsid

def put_string(dbo, name, path, contents):
    """
    Stores the file contents (as a bytes string) at the name and path. If the file exists, overwrites it.
    """
    check_create_path(dbo, path)
    name = name.replace("'", "")
    path = path.replace("'", "")
    dbfsid = dbo.query_int("SELECT ID FROM dbfs WHERE Path = ? AND Name = ?", (path, name))
    if dbfsid == 0:
        dbfsid = dbo.insert("dbfs", {
            "Name": name, 
            "Path": path
        })
    o = DBFSStorage(dbo)
    o.put(dbfsid, name, contents)
    return dbfsid

def put_string_id(dbo, dbfsid, name, contents):
    """
    Stores the file contents (bytes string) at the id given.
    """
    o = DBFSStorage(dbo)
    o.put(dbfsid, name, contents)
    return dbfsid

def put_string_filepath(dbo, filepath, contents):
    """
    Stores the file contents (bytes string) at the name/path given.
    """
    name = filepath[filepath.rfind("/")+1:]
    path = filepath[0:filepath.rfind("/")]
    return put_string(dbo, name, path, contents)

def replace_string(dbo, content, name, path = ""):
    """
    Replaces the file contents given as a bytes string in the dbfs
    with the name and path given. If no path is given, looks it
    up by just the name.
    """
    if path != "":
        r = dbo.query("SELECT ID, URL, Name FROM dbfs WHERE Name=? AND Path=?", (name, path))
    else:
        r = dbo.query("SELECT ID, URL, Name FROM dbfs WHERE Name=?", [name])
    if len(r) == 0:
        raise DBFSError("No item found for path=%s, name=%s" % (path, name))
    r = r[0]
    o = DBFSStorage(dbo, r.url)
    o.put(r.id, r.name, content)
    return r.id

def get_file(dbo, name, path, saveto):
    """
    Gets DBFS file contents and saves them to the
    filename given. Returns True for success
    """
    asm3.utils.write_binary_file(saveto, get_string(dbo, name, path))
    return True

def get_file_id(dbo, dbfsid, saveto):
    """
    Gets DBFS file contents and saves them to the
    filename given. Returns True for success
    """
    asm3.utils.write_binary_file(saveto, get_string_id(dbo, dbfsid))
    return True

def file_exists(dbo, name):
    """
    Return True if a file with name exists in the database.
    """
    return dbo.query_int("SELECT COUNT(*) FROM dbfs WHERE Name = ?", [name]) > 0

def get_files(dbo, name, path, saveto):
    """
    Gets DBFS files for the pattern given in name (use % like db)
    and belonging to path (blank for all paths). saveto is
    the folder to save all the files to. Returns True for success
    """
    if path != "":
        rows = dbo.query("SELECT ID, URL FROM dbfs WHERE LOWER(Name) LIKE ? AND Path = ?", [name, path])
    else:
        rows = dbo.query("SELECT ID, URL FROM dbfs WHERE LOWER(Name) LIKE ?", [name])
    if len(rows) > 0:
        for r in rows:
            o = DBFSStorage(dbo, r.url)
            asm3.utils.write_binary_file(saveto, o.get(r.id, r.url))
        return True
    return False

def _delete(dbo, where):
    """
    Deletes rows from the DBFS matching where. 
    This the only place where "real" deletion from the table is done.
    """
    # rows = db.query("SELECT ID, URL FROM dbfs WHERE %s" % where)
    dbo.delete("dbfs", where, "dbfs") # Audit the delete and remove from the dbfs table
    # No longer used, for File and S3 storage, this would "really delete" the files.
    # We do not do this because storage is cheap and people invariably delete
    # things by accident. This means that a quick restore of the deleted dbfs
    # item from the deletion table and things are back.
    #for r in rows:
    #    o = DBFSStorage(dbo, r.url)
    #    o.delete(r.url)

def delete_path(dbo, path):
    """
    Deletes all items matching the path given
    """
    _delete(dbo, "Path LIKE %s" % dbo.sql_value(path))

def delete(dbo, name, path = ""):
    """
    Deletes all items matching the name and path given
    """
    if path != "":
        _delete(dbo, "Name=%s AND Path=%s" % (dbo.sql_value(name), dbo.sql_value(path)))
    else:
        _delete(dbo, "Name=%s" % (dbo.sql_value(name)))

def delete_filepath(dbo, filepath):
    """
    Deletes the dbfs entry for the filepath
    """
    name = filepath[filepath.rfind("/")+1:]
    path = filepath[0:filepath.rfind("/")]
    delete(dbo, name, path)

def delete_id(dbo, dbfsid):
    """
    Deletes the dbfs entry for the id
    """
    _delete(dbo, "ID=%d" % dbfsid)

def list_contents(dbo, path):
    """
    Returns a list of items in the path given. Directories
    are identifiable by not having a file extension.
    """
    rows = dbo.query("SELECT Name FROM dbfs WHERE Path = ?", [path])
    l = []
    for r in rows:
        l.append(r.name)
    return l

# End of storage primitives -- everything past here calls functions above

def sanitise_path(path):
    """ Strips disallowed chars from new paths """
    disallowed = (" ", "|", ",", "!", "\"", "'", "$", "%", "^", "*",
        "(", ")", "[", "]", "{", "}", "\\", ":", "@", "?", "+")
    for d in disallowed:
        path = path.replace(d, "_")
    return path

def get_name_for_id(dbo, dbfsid):
    """
    Returns the filename of the item with id dbfsid
    """
    return dbo.query_string("SELECT Name FROM dbfs WHERE ID = ?", [dbfsid])

def get_document_repository(dbo):
    """
    Returns a list of all documents in the /document_repository directory,
    also includes MIMETYPE field for display
    """
    rows = dbo.query("SELECT ID, Name, Path FROM dbfs WHERE " \
        "Path Like '/document_repository%' AND Name Like '%.%' ORDER BY Path, Name")
    for r in rows:
        mimetype, dummy = mimetypes.guess_type("file://" + r.name, strict=False)
        r["MIMETYPE"] = mimetype
    return rows

def get_report_images(dbo):
    """
    Returns a list of all extra images in the /reports directory
    """
    return dbo.query("SELECT Name, Path FROM dbfs WHERE " \
        "(LOWER(Name) Like '%.jpg' OR LOWER(Name) Like '%.png' OR LOWER(Name) Like '%.gif') " \
        "AND Path Like '/report%' ORDER BY Path, Name")

def upload_report_image(dbo, fc):
    """
    Attaches an image from a form filechooser object and puts
    it in the /reports directory. 
    """
    ext = ""
    ext = fc.filename
    filename = asm3.utils.filename_only(fc.filename)
    filedata = fc.value
    ext = ext[ext.rfind("."):].lower()
    ispicture = ext == ".jpg" or ext == ".jpeg" or ext == ".png" or ext == ".gif"
    if not ispicture:
        raise asm3.utils.ASMValidationError("upload_report_image only accepts images.")
    put_string(dbo, filename, "/reports", filedata)

def upload_document_repository(dbo, path, filename, filedata):
    """
    Attaches a document from a form filechooser object and puts
    it in the /document_repository directory. 
    An extra path portion can be specified in path.
    """
    ext = ""
    ext = filename
    filename = asm3.utils.filename_only(filename)
    ext = ext[ext.rfind("."):].lower()
    if path != "" and path.startswith("/"): path = path[1:]
    if path == "":
        filepath = "/document_repository/%s" % filename
    else:
        path = sanitise_path(path)
        filepath = "/document_repository/%s/%s" % (path, filename)
    put_string_filepath(dbo, filepath, filedata)

def delete_orphaned_media(dbo):
    """
    Removes all dbfs content should have an entry in the media table and doesn't
    """
    where = "WHERE " \
        "(Path LIKE '/animal%' OR Path LIKE '/owner%' OR Path LIKE '/lostanimal%' OR Path LIKE '/foundanimal%' " \
        "OR Path LIKE '/waitinglist%' OR Path LIKE '/animalcontrol%') " \
        "AND (LOWER(Name) LIKE '%.jpg' OR LOWER(Name) LIKE '%.jpeg' OR LOWER(Name) LIKE '%.pdf' OR LOWER(Name) LIKE '%.html') " \
        "AND ID NOT IN (SELECT DBFSID FROM media)"
    rows = dbo.query("SELECT ID, Name, Path, URL FROM dbfs %s" % where) 
    dbo.execute("DELETE FROM dbfs %s" % where)
    for r in rows:
        o = DBFSStorage(dbo, r.url)
        o.delete(r.url)
    asm3.al.debug("Removed %s orphaned dbfs/media records" % len(rows), "dbfs.delete_orphaned_media", dbo)

def switch_storage(dbo):
    """ Goes through all files in dbfs and swaps them into the current storage scheme """
    rows = dbo.query("SELECT ID, Name, Path, URL FROM dbfs WHERE Name LIKE '%.%' ORDER BY ID")
    for i, r in enumerate(rows):
        asm3.al.debug("Storage transfer %s/%s (%d of %d)" % (r.path, r.name, i, len(rows)), "dbfs.switch_storage", dbo)
        source = DBFSStorage(dbo, r.url)
        target = DBFSStorage(dbo)
        # Don't bother if the file is already stored in the target format
        if source.url_prefix() == target.url_prefix():
            asm3.al.debug("source is already %s, skipping" % source.url_prefix(), "dbfs.switch_storage", dbo)
            continue
        try:
            filedata = source.get(r.id, r.url)
            target.put(r.id, r.name, filedata)
            # Update the media size while we're switching in case it wasn't set previously
            dbo.execute("UPDATE media SET MediaSize=? WHERE DBFSID=?", ( len(filedata), r.id ))
        except Exception as err:
            asm3.al.error("Error reading, skipping: %s" % str(err), "dbfs.switch_storage", dbo)
    # reclaim any space from the deletion
    dbo.vacuum("dbfs")
    # smcom only - perform postgresql full vacuum after switching
    if asm3.smcom.active(): asm3.smcom.vacuum_full(dbo)


