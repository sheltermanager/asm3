
import asm3.al
import asm3.animal
import asm3.audit
import asm3.configuration
import asm3.dbfs
import asm3.log
import asm3.utils
from asm3.i18n import _
from asm3.sitedefs import RESIZE_IMAGES_DURING_ATTACH, RESIZE_IMAGES_SPEC, SCALE_PDF_DURING_ATTACH, SCALE_PDF_CMD, SERVICE_URL, WATERMARK_FONT_BASEDIRECTORY
from asm3.typehints import Database, Dict, PostedData, ResultRow, Results, Tuple

from datetime import datetime
import os
import tempfile
import zipfile
from PIL import Image, ImageFont, ImageDraw

ANIMAL = 0
LOSTANIMAL = 1
FOUNDANIMAL = 2
PERSON = 3
WAITINGLIST = 5
ANIMALCONTROL = 6

MEDIASOURCE_ATTACHFILE = 1
MEDIASOURCE_DRAGNDROP = 2
MEDIASOURCE_MOBILEUI = 3
MEDIASOURCE_ONLINEFORM = 4
MEDIASOURCE_DOCUMENT = 5
MEDIASOURCE_CSVIMPORT = 6
MEDIASOURCE_SERVICEUPLOAD = 7
MEDIASOURCE_JPG2PDF = 8
MEDIASOURCE_CLONE = 9

MEDIATYPE_FILE = 0
MEDIATYPE_DOCUMENT_LINK = 1
MEDIATYPE_VIDEO_LINK = 2

DEFAULT_RESIZE_SPEC = "1024x1024" # If no valid resize spec is configured, the default to use
MAX_PDF_PAGES = 50 # Do not scale PDFs with more than this many pages

def mime_type(filename: str) -> str:
    """
    Returns the mime type for a file with the given name
    """
    types = {
        "jpg"   : "image/jpeg",
        "jpeg"  : "image/jpeg",
        "bmp"   : "image/bmp",
        "gif"   : "image/gif",
        "png"   : "image/png",
        "doc"   : "application/msword",
        "xls"   : "application/vnd.ms-excel",
        "ppt"   : "application/vnd.ms-powerpoint",
        "docx"  : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx"  : "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "xslx"  : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "odt"   : "application/vnd.oasis.opendocument.text",
        "sxw"   : "application/vnd.oasis.opendocument.text",
        "ods"   : "application/vnd.oasis.opendocument.spreadsheet",
        "odp"   : "application/vnd.oasis.opendocument.presentation",
        "pdf"   : "application/pdf",
        "mpg"   : "video/mpg",
        "mp3"   : "audio/mpeg3",
        "avi"   : "video/avi",
        "htm"   : "text/html",
        "html"  : "text/html"
    }
    ext = filename[filename.rfind(".")+1:].lower()
    if ext in types:
        return types[ext]
    return "application/octet-stream"

def get_web_preferred_name(dbo: Database, linktype: int, linkid: int) -> str:
    return dbo.query_string("SELECT MediaName FROM media " \
        "WHERE LinkTypeID = ? AND WebsitePhoto = 1 AND LinkID = ?", (linktype, linkid))

def get_web_preferred(dbo: Database, linktype: int, linkid: int) -> ResultRow:
    """ Returns the media record for the web preferred (or None if there isn't one) """
    return dbo.first_row(dbo.query("SELECT * FROM media WHERE LinkTypeID = ? AND " \
        "LinkID = ? AND WebsitePhoto = 1", (linktype, linkid)))

def get_media_by_seq(dbo: Database, linktype: int, linkid: int, seq: int) -> ResultRow:
    """ Returns image media by a one-based sequence number. 
        Element 1 is always the preferred.
        None is returned if the item doesn't exist
    """
    rows = dbo.query("SELECT * FROM media " \
        "WHERE LinkTypeID = ? AND LinkID = ? " \
        "AND MediaMimeType = 'image/jpeg' " \
        "AND (ExcludeFromPublish = 0 OR ExcludeFromPublish Is Null) " \
        "ORDER BY WebsitePhoto DESC, ID", (linktype, linkid))
    if len(rows) >= seq:
        return rows[seq-1]
    else:
        return None

def get_total_seq(dbo: Database, linktype: int, linkid: int) -> int:
    return dbo.query_int(dbo, "SELECT COUNT(ID) FROM media WHERE LinkTypeID = ? AND LinkID = ? " \
        "AND MediaMimeType = 'image/jpeg' " \
        "AND (ExcludeFromPublish = 0 OR ExcludeFromPublish Is Null)", (linktype, linkid))

def set_video_preferred(dbo: Database, username: str, mid: int) -> None:
    """
    Makes the media with id the preferred for video in the link
    """
    link = dbo.first_row(dbo.query("SELECT LinkID, LinkTypeID FROM media WHERE ID = ?", [mid]))
    dbo.update("media", "LinkID=%d AND LinkTypeID=%d" % (link.LINKID, link.LINKTYPEID), { "WebsiteVideo": 0 })
    dbo.update("media", mid, { "WebsiteVideo": 1, "Date": dbo.now() }, username) 

def set_web_preferred(dbo: Database, username: str, mid: int) -> None:
    """
    Makes the media with id the preferred for the web in the link
    """
    link = dbo.first_row(dbo.query("SELECT LinkID, LinkTypeID FROM media WHERE ID = ?", [mid]))
    dbo.update("media", "LinkID=%d AND LinkTypeID=%d" % (link.LINKID, link.LINKTYPEID), { "WebsitePhoto": 0 })
    dbo.update("media", mid, { "WebsitePhoto": 1, "ExcludeFromPublish": 0, "Date": dbo.now() }, username) 

def set_doc_preferred(dbo: Database, username: str, mid: int) -> None:
    """
    Makes the media with id the preferred for docs in the link
    """
    link = dbo.first_row(dbo.query("SELECT LinkID, LinkTypeID FROM media WHERE ID = ?", [mid]))
    dbo.update("media", "LinkID=%d AND LinkTypeID=%d" % (link.LINKID, link.LINKTYPEID), { "DocPhoto": 0 })
    dbo.update("media", mid, { "DocPhoto": 1, "Date": dbo.now() }, username) 

def set_excluded(dbo: Database, username: str, mid: int, exclude: int = 1) -> None:
    """
    Marks the media with id excluded from publishing.
    """
    d = { "ExcludeFromPublish": exclude, "Date": dbo.now() }
    # If we are excluding, we can't be the web or doc or video preferred
    if exclude == 1:
        d["WebsitePhoto"] = 0
        d["DocPhoto"] = 0
    dbo.update("media", mid, d, username)

def get_name_for_id(dbo: Database, mid: int) -> str:
    return dbo.query_string("SELECT MediaName FROM media WHERE ID = ?", [mid])

def get_notes_for_id(dbo: Database, mid: int) -> str:
    return dbo.query_string("SELECT MediaNotes FROM media WHERE ID = ?", [mid])

def get_media_export(dbo: Database) -> Results:
    """
    Produces a dataset of all media with link info for export
    """
    rows = dbo.query("SELECT m.*, " \
        "CASE " \
        "WHEN m.LinkTypeID = 0 THEN (SELECT %s FROM animal WHERE ID = m.LinkID) " \
        "WHEN m.LinkTypeID = 3 THEN (SELECT OwnerName FROM owner WHERE ID = m.LinkID) " \
        "WHEN m.LinkTypeID = 1 THEN %s " \
        "WHEN m.LinkTypeID = 2 THEN %s " \
        "WHEN m.LinkTypeID = 5 THEN %s " \
        "WHEN m.LinkTypeID = 6 THEN %s " \
        "ELSE '' END AS LinkText " \
        "FROM media m " \
        "ORDER BY m.ID" % ( \
            dbo.sql_concat([ "AnimalName", "' - '", "ShelterCode" ]),
            dbo.sql_concat([ "'Lost Animal '", "m.LinkID" ]),
            dbo.sql_concat([ "'Found Animal '", "m.LinkID" ]),
            dbo.sql_concat([ "'Waiting List '", "m.LinkID" ]),
            dbo.sql_concat([ "'Incident '", "m.LinkID" ])  ))
    for m in rows:
        m.DBFSNAME = ""
        if m.MEDIATYPE == MEDIATYPE_FILE:
            ext = m.MEDIANAME[m.MEDIANAME.rfind("."):]
            m.DBFSNAME = "%s%s" % (m.DBFSID, ext)
    return rows

def get_media_file_data(dbo: Database, mid: int) -> Tuple[datetime, str, bytes]:
    """
    Gets a piece of media by id. Returns None if the media record does not exist.
    id: The media id
    Returns a tuple containing the last modified date, media name, 
    mime type and file data as bytes
    """
    mm = get_media_by_id(dbo, mid)
    if mm is None: return (None, "", "", "")
    return mm.DATE, mm.MEDIANAME, mm.MEDIAMIMETYPE, asm3.dbfs.get_string_id(dbo, mm.DBFSID)

def get_image_file_data(dbo: Database, mode: str, iid: str = "", seq: int = 0, justdate: bool = False) -> Tuple[datetime, bytes]:
    """
    Gets an image
    mode: animal | media | animalthumb | person | personthumb | dbfs
    iid: (str) The id of the animal for animal/thumb mode or the media record
        or a template path for dbfs mode
    seq: (int) If the mode is animal or person, returns image X for that person/animal
         The first image is always the preferred photo and seq is 1-based.
    if justdate is True, returns the last modified date
    if justdate is False, returns a tuple containing the last modified date and image data
    """
    def nopic():
        NOPIC_DATE = datetime(2011, 1, 1)
        if justdate: return NOPIC_DATE
        return (NOPIC_DATE, b"NOPIC")
    def thumb_nopic():
        NOPIC_DATE = datetime(2011, 1, 1)
        if justdate: return NOPIC_DATE
        return (NOPIC_DATE, b"NOPIC")
    def mrec(mm):
        if mm is None: return nopic()
        if justdate: return mm.DATE
        return (mm.DATE, asm3.dbfs.get_string_id(dbo, mm.DBFSID))
    def thumb_mrec(mm):
        if mm is None: return thumb_nopic()
        if justdate: return mm.DATE
        return (mm.DATE, scale_image(asm3.dbfs.get_string_id(dbo, mm.DBFSID), asm3.configuration.thumbnail_size(dbo)))

    sid = str(iid)
    iid = asm3.utils.cint(iid)

    if mode == "animal":
        if seq == 0:
            return mrec( get_web_preferred(dbo, ANIMAL, iid) )
        else:
            return mrec( get_media_by_seq(dbo, ANIMAL, iid, seq) )
    elif mode == "person":
        if seq == 0:
            return mrec( get_web_preferred(dbo, PERSON, iid) )
        else:
            return mrec( get_media_by_seq(dbo, PERSON, iid, seq) )
    if mode == "waitinglist":
        if seq == 0:
            return mrec( get_web_preferred(dbo, WAITINGLIST, iid) )
        else:
            return mrec( get_media_by_seq(dbo, WAITINGLIST, iid, seq) )
    if mode == "lostanimal":
        if seq == 0:
            return mrec( get_web_preferred(dbo, LOSTANIMAL, iid) )
        else:
            return mrec( get_media_by_seq(dbo, LOSTANIMAL, iid, seq) )
    if mode == "foundanimal":
        if seq == 0:
            return mrec( get_web_preferred(dbo, FOUNDANIMAL, iid) )
        else:
            return mrec( get_media_by_seq(dbo, FOUNDANIMAL, iid, seq) )
    elif mode == "animalthumb":
        return thumb_mrec( get_web_preferred(dbo, ANIMAL, iid) )

    elif mode == "personthumb":
        return thumb_mrec( get_web_preferred(dbo, PERSON, iid) )
    
    elif mode == "waitinglistthumb":
        return thumb_mrec( get_web_preferred(dbo, WAITINGLIST, iid) )
    
    elif mode == "lostanimalthumb":
        return thumb_mrec( get_web_preferred(dbo, LOSTANIMAL, iid) )
    
    elif mode == "foundanimalthumb":
        return thumb_mrec( get_web_preferred(dbo, FOUNDANIMAL, iid) )

    elif mode == "media":
        return mrec( get_media_by_id(dbo, iid) )

    elif mode == "dbfs":
        if justdate:
            return dbo.now()
        else:
            if sid.startswith("/"):
                # Complete path was given
                return (dbo.now(), asm3.dbfs.get_string_filepath(dbo, sid))
            else:
                # Only name was given
                return (dbo.now(), asm3.dbfs.get_string(dbo, sid))

    elif mode == "nopic":
        if asm3.dbfs.file_exists(dbo, "nopic.jpg"):
            return (dbo.now(), asm3.dbfs.get_string_filepath(dbo, "/reports/nopic.jpg"))
        else:
            return (dbo.now(), asm3.utils.read_binary_file(dbo.installpath + "media/reports/nopic.jpg"))

    else:
        return nopic()

def get_dbfs_path(linkid: int, linktype: int) -> str:
    path = "/animal/%d" % int(linkid)
    if linktype == PERSON:
        path = "/owner/%d" % int(linkid)
    elif linktype == LOSTANIMAL:
        path = "/lostanimal/%d" % int(linkid)
    elif linktype == FOUNDANIMAL:
        path = "/foundanimal/%d" % int(linkid)
    elif linktype == WAITINGLIST:
        path = "/waitinglist/%d" % int(linkid)
    elif linktype == ANIMALCONTROL:
        path = "/animalcontrol/%d" % int(linkid)
    return path

def get_log_from_media_type(x: int) -> int:
    """ Returns the corresponding log type for a media type """
    m = {
        ANIMAL: asm3.log.ANIMAL,
        PERSON: asm3.log.PERSON,
        LOSTANIMAL: asm3.log.LOSTANIMAL,
        FOUNDANIMAL: asm3.log.FOUNDANIMAL,
        WAITINGLIST: asm3.log.WAITINGLIST,
        ANIMALCONTROL: asm3.log.ANIMALCONTROL
    }
    return m[x]

def get_media(dbo: Database, linktype: int, linkid: int) -> Results:
    return dbo.query("SELECT * FROM media WHERE LinkTypeID = ? AND LinkID = ? ORDER BY Date DESC", ( linktype, linkid ))

def get_media_by_id(dbo: Database, mid: int) -> ResultRow:
    return dbo.first_row(dbo.query("SELECT * FROM media WHERE ID = ?", [mid] ))

def get_media_filename(dbo: Database, mid: int) -> str:
    """ Constructs a filename from media notes.
        Truncates if notes are too long, removes unsafe punctuation and checks the extension. """
    return _get_media_filename(get_media_by_id(dbo, mid))

def _get_media_filename(m: ResultRow) -> str:
    """ Constructs a filename from media notes.
        Truncates if notes are too long, removes unsafe punctuation and checks the extension. """
    s = m.MEDIANOTES
    s = s.replace("\n", "_").replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_")
    s = asm3.utils.truncate(s, 20)
    ext = m.MEDIANAME[m.MEDIANAME.rfind("."):]
    if not s.endswith(ext): s += ext
    return s

def get_image_media(dbo: Database, linktype: int, linkid: int, ignoreexcluded: bool = False) -> Results:
    if not ignoreexcluded:
        return dbo.query("SELECT * FROM media WHERE LinkTypeID = ? AND LinkID = ? " \
            "AND (LOWER(MediaName) Like '%%.jpg' OR LOWER(MediaName) Like '%%.jpeg') ORDER BY media.Date DESC", ( linktype, linkid ))
    else:
        return dbo.query("SELECT * FROM media WHERE (ExcludeFromPublish = 0 OR ExcludeFromPublish Is Null) " \
            "AND LinkTypeID = ? AND LinkID = ? AND (LOWER(MediaName) Like '%%.jpg' OR LOWER(MediaName) Like '%%.jpeg') ORDER BY media.Date DESC", ( linktype, linkid ))

def attach_file_from_form(dbo: Database, username: str, linktype: int, linkid: int, sourceid: int, post: PostedData) -> int:
    """
    Attaches a media file from the posted form
    data is the web.py data object and should contain
    comments and either the filechooser object, with filename and value 
    OR filedata, filetype and filename parameters (filetype is the MIME type, filedata is base64 encoded contents)
    Return value is the ID of the newly created media record.
    """
    ext = ""
    filedata = post["filedata"]
    filename = post["filename"]
    comments = post["comments"]
    flags = post["flags"].replace(",", "|") + "|"
    transformed = post.integer("transformed") == 1
    if filedata != "":
        filetype = post["filetype"]
        if filetype.startswith("image") or filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"): ext = ".jpg"
        elif filename.lower().endswith(".png"): ext = ".png"
        elif filetype.find("pdf") != -1 or filename.lower().endswith(".pdf"): ext = ".pdf"
        elif filetype.find("html") != -1 or filename.lower().endswith(".html"): ext = ".html"
        # Strip the data:mime prefix so we just have base64 data
        if filedata.startswith("data:"):
            filedata = filedata[filedata.find(",")+1:]
            # Browser escaping turns base64 pluses back into spaces, so switch back
            filedata = filedata.replace(" ", "+")
        filedata = asm3.utils.base64decode(filedata)
        asm3.al.debug(f"received data URI '{filename}' ({len(filedata)} bytes, mimetype={filetype}, transformed={transformed})", "media.attach_file_from_form", dbo)
        if ext == "":
            msg = "could not determine extension from file.type '%s', abandoning" % filetype
            asm3.al.error(msg, "media.attach_file_from_form", dbo)
            raise asm3.utils.ASMValidationError(msg)
    else:
        # It's a traditional form post with a filechooser
        ext = post.filename()
        ext = ext[ext.rfind("."):].lower()
        filedata = post.filedata()
        filename = post.filename()
        asm3.al.debug("received POST file data '%s' (%d bytes)" % (filename, len(filedata)), "media.attach_file_from_form", dbo)

    # If we receive some images in formats other than JPG, we'll
    # pretend they're jpg as that's what they'll get transformed into
    # by scale_image
    if ext == ".png":
        ext = ".jpg"

    mediaid = dbo.get_id("media")
    medianame = "%d%s" % ( mediaid, ext )
    ispicture = ext == ".jpg" or ext == ".jpeg"
    ispdf = ext == ".pdf"
    excludefrompublish = 0
    if "excludefrompublish" in post: 
        excludefrompublish = post.integer("excludefrompublish")
    if asm3.configuration.auto_new_images_not_for_publish(dbo) and ispicture:
        excludefrompublish = 1

    # Are we allowed to upload this type of media?
    if ispicture and not asm3.configuration.media_allow_jpg(dbo):
        msg = "upload of media type jpg is disabled"
        asm3.al.error(msg, "media.attach_file_from_form", dbo)
        raise asm3.utils.ASMValidationError(msg)
    if ispdf and not asm3.configuration.media_allow_pdf(dbo):
        msg = "upload of media type pdf is disabled"
        asm3.al.error(msg, "media.attach_file_from_form", dbo)
        raise asm3.utils.ASMValidationError(msg)
    
    # Is it a picture, is it valid?
    if ispicture and not verify_image(filedata):
        msg = "image data uploaded is not a valid image"
        asm3.al.error(msg, "media.attach_file_from_form", dbo)
        raise asm3.utils.ASMValidationError(msg)

    # Is it a picture? Was it already rotated and scaled by the browser?
    if ispicture and not transformed:
        # Autorotate it to match the EXIF orientation
        filedata = auto_rotate_image(dbo, filedata)
        # Scale it down to the system set size 
        if RESIZE_IMAGES_DURING_ATTACH:
            filedata = scale_image(filedata, RESIZE_IMAGES_SPEC)
            asm3.al.debug("scaled image to %s (%d bytes)" % (RESIZE_IMAGES_SPEC, len(filedata)), "media.attach_file_from_form", dbo)

    # Is it a PDF? If so, compress it if we can and the option is on 
    if ispdf and SCALE_PDF_DURING_ATTACH and asm3.configuration.scale_pdfs(dbo):
        orig_len = len(filedata)
        filedata = scale_pdf(filedata)
        if len(filedata) < orig_len:
            asm3.al.debug("compressed PDF (%d bytes)" % (len(filedata)), "media.attach_file_from_form", dbo)

    # Attach the file in the dbfs
    path = get_dbfs_path(linkid, linktype)
    dbfsid = asm3.dbfs.put_string(dbo, medianame, path, filedata)

    # Are the notes for an image blank and we're defaulting them from animal comments?
    if comments == "" and ispicture and linktype == ANIMAL and asm3.configuration.auto_media_notes(dbo):
        comments = asm3.animal.get_comments(dbo, int(linkid))
        # Are the notes blank and we're defaulting them from the filename?
    elif comments == "" and asm3.configuration.default_media_notes_from_file(dbo):
        comments = asm3.utils.filename_only(filename)

    # Calculate the retain until date from retainfor years
    retainuntil = calc_retainuntil_from_retainfor(dbo, post.integer("retainfor"))
    
    # Create the media record
    dbo.insert("media", {
        "ID":                   mediaid,
        "DBFSID":               dbfsid,
        "MediaSource":          sourceid,
        "MediaFlags":           flags,
        "MediaSize":            len(filedata),
        "MediaName":            medianame,
        "MediaMimeType":        mime_type(medianame),
        "MediaType":            0,
        "MediaNotes":           comments,
        "WebsitePhoto":         0,
        "WebsiteVideo":         0,
        "DocPhoto":             0,
        "ExcludeFromPublish":   excludefrompublish,
        # ASM2_COMPATIBILITY
        "NewSinceLastPublish":  1,
        "UpdatedSinceLastPublish": 0,
        # ASM2_COMPATIBILITY
        "LinkID":               linkid,
        "LinkTypeID":           linktype,
        "Date":                 dbo.now(),
        "CreatedDate":          dbo.now(),
        "RetainUntil":          retainuntil
    }, username, generateID=False)

    # Verify this record has a web/doc default if we aren't excluding it from publishing
    if ispicture and excludefrompublish == 0:
        check_default_web_doc_pic(dbo, mediaid, linkid, linktype)

    return mediaid

def attach_link_from_form(dbo: Database, username: str, linktype: int, linkid: int, post: PostedData) -> int:
    """
    Attaches a link to a web resource from a form.
    Returns the ID of the newly creatd media record.
    """
    existingvid = dbo.query_int("SELECT COUNT(*) FROM media WHERE WebsiteVideo = 1 " \
        "AND LinkID = ? AND LinkTypeID = ?", (linkid, linktype))
    defvid = 0
    if existingvid == 0 and post.integer("linktype") == MEDIATYPE_VIDEO_LINK:
        defvid = 1
    url = post["linktarget"]
    if url.find("://") == -1:
        url = "http://" + url
    asm3.al.debug("attached link %s" % url, "media.attach_file_from_form")
    return dbo.insert("media", {
        "DBFSID":               0,
        "MediaSize":            0,
        "MediaSource":          MEDIASOURCE_ATTACHFILE,
        "MediaFlags":           "",
        "MediaName":            url,
        "MediaMimeType":        "text/url",
        "MediaType":            post.integer("linktype"),
        "MediaNotes":           post["linkcomments"],
        "WebsitePhoto":         0,
        "WebsiteVideo":         defvid,
        "DocPhoto":             0,
        "ExcludeFromPublish":   0,
        # ASM2_COMPATIBILITY
        "NewSinceLastPublish":  1,
        "UpdatedSinceLastPublish": 0,
        # ASM2_COMPATIBILITY
        "LinkID":               linkid,
        "LinkTypeID":           linktype,
        "Date":                 dbo.now(),
        "CreatedDate":          dbo.now(),
        "RetainUntil":          None
    }, username)


def calc_retainuntil_from_retainfor(dbo: Database, retainfor: int) -> datetime:
    """ Calculates the retain until date from a retain for in years (0 or None = Indefinitely) """
    retainuntil = None
    retainfor = asm3.utils.cint(retainfor)
    if (retainfor > 0):
        retainuntil = dbo.today( retainfor * 365 )
    return retainuntil

def check_default_web_doc_pic(dbo: Database, mediaid: int, linkid: int, linktype: int) -> None:
    """
    Checks if linkid/type has a default pic for the web or documents. If not,
    sets mediaid to be the default.
    """
    existing_web = dbo.query_int("SELECT COUNT(*) FROM media WHERE WebsitePhoto = 1 " \
        "AND LinkID = ? AND LinkTypeID = ?", (linkid, linktype))
    existing_doc = dbo.query_int("SELECT COUNT(*) FROM media WHERE DocPhoto = 1 " \
        "AND LinkID = ? AND LinkTypeID = ?", (linkid, linktype))
    if existing_web == 0:
        dbo.update("media", mediaid, { "WebsitePhoto": 1 })
    if existing_doc == 0:
        dbo.update("media", mediaid, { "DocPhoto": 1 })

def create_blank_document_media(dbo: Database, username: str, linktype: int, linkid: int) -> int:
    """
    Creates a new media record for a blank document for the link given.
    linktype: ANIMAL, PERSON, etc
    linkid: ID for the link
    returns the new media id
    """
    mediaid = dbo.get_id("media")
    path = get_dbfs_path(linkid, linktype)
    name = str(mediaid) + ".html"
    dbfsid = asm3.dbfs.put_string(dbo, name, path, "")
    dbo.insert("media", {
        "ID":                   mediaid,
        "DBFSID":               dbfsid,
        "MediaSize":            0,
        "MediaSource":          MEDIASOURCE_DOCUMENT,
        "MediaFlags":           "",
        "MediaName":            "%d.html" % mediaid,
        "MediaMimeType":        "text/html",
        "MediaType":            0,
        "MediaNotes":           "New document",
        "WebsitePhoto":         0,
        "WebsiteVideo":         0,
        "DocPhoto":             0,
        "ExcludeFromPublish":   0,
        # ASM2_COMPATIBILITY
        "NewSinceLastPublish":  1,
        "UpdatedSinceLastPublish": 0,
        # ASM2_COMPATIBILITY
        "LinkID":               linkid,
        "LinkTypeID":           linktype,
        "Date":                 dbo.now(),
        "CreatedDate":          dbo.now(),
        "RetainUntil":          None
    }, username, generateID=False)
    return mediaid

def create_document_animalperson(dbo: Database, username: str, animalid: int, personid: int, 
                                 template: str, content: bytes, retainfor: int = 0) -> Tuple[int, int]:
    """
    Creates media records for an animal and a person sharing a document (same DBFS entry).
    The document itself will be stored on the person's path in the DBFS. The name given will
    be all created media IDs for it, eg: 123.456.html
    In the case of signing, the signing function is clever enough to update the hash on all 
    media records sharing the same DBFSID.
    template: The name of the template used to create the document
    content: The document contents (bytes str, will be converted if str given)
    retainfor: Number of years to retain this document (any non-integer or 0 = Indefinitely)
    """
    path = get_dbfs_path(personid, PERSON)
    mediaida = dbo.get_id("media")
    mediaidp = dbo.get_id("media")
    name = f"{mediaida}.{mediaidp}.html"
    content = asm3.utils.str2bytes(content)
    dbfsid = asm3.dbfs.put_string(dbo, name, path, content)
    retainuntil = calc_retainuntil_from_retainfor(dbo, retainfor)
    dbo.insert("media", {
        "ID":                   mediaida,
        "DBFSID":               dbfsid,
        "MediaSize":            len(content),
        "MediaSource":          MEDIASOURCE_DOCUMENT,
        "MediaFlags":           "",
        "MediaName":            "%d.html" % mediaida,
        "MediaMimeType":        "text/html",
        "MediaType":            0,
        "MediaNotes":           template,
        "WebsitePhoto":         0,
        "WebsiteVideo":         0,
        "DocPhoto":             0,
        "ExcludeFromPublish":   0,
        # ASM2_COMPATIBILITY
        "NewSinceLastPublish":  1,
        "UpdatedSinceLastPublish": 0,
        # ASM2_COMPATIBILITY
        "LinkID":               animalid,
        "LinkTypeID":           ANIMAL,
        "Date":                 dbo.now(),
        "CreatedDate":          dbo.now(),
        "RetainUntil":          retainuntil
    }, username, generateID=False)
    dbo.insert("media", {
        "ID":                   mediaidp,
        "DBFSID":               dbfsid,
        "MediaSize":            len(content),
        "MediaSource":          MEDIASOURCE_DOCUMENT,
        "MediaFlags":           "",
        "MediaName":            "%d.html" % mediaidp,
        "MediaMimeType":        "text/html",
        "MediaType":            0,
        "MediaNotes":           template,
        "WebsitePhoto":         0,
        "WebsiteVideo":         0,
        "DocPhoto":             0,
        "ExcludeFromPublish":   0,
        # ASM2_COMPATIBILITY
        "NewSinceLastPublish":  1,
        "UpdatedSinceLastPublish": 0,
        # ASM2_COMPATIBILITY
        "LinkID":               personid,
        "LinkTypeID":           PERSON,
        "Date":                 dbo.now(),
        "CreatedDate":          dbo.now(),
        "RetainUntil":          retainuntil
    }, username, generateID=False)
    return (mediaida, mediaidp)

def create_document_media(dbo: Database, username: str, linktype: int, linkid: int, template: str, content: bytes, retainfor: int = 0) -> int:
    """
    Creates a new media record for a document for the link given.
    linktype: ANIMAL, PERSON, etc
    linkid: ID for the link
    template: The name of the template used to create the document
    content: The document contents (bytes str, will be converted if str given)
    retainfor: Number of years to retain this document (any non-integer or 0 = Indefinitely)
    """
    mediaid = dbo.get_id("media")
    path = get_dbfs_path(linkid, linktype)
    name = f"{mediaid}.html"
    content = asm3.utils.str2bytes(content)
    dbfsid = asm3.dbfs.put_string(dbo, name, path, content)
    retainuntil = calc_retainuntil_from_retainfor(dbo, retainfor)
    dbo.insert("media", {
        "ID":                   mediaid,
        "DBFSID":               dbfsid,
        "MediaSize":            len(content),
        "MediaSource":          MEDIASOURCE_DOCUMENT,
        "MediaFlags":           "",
        "MediaName":            "%d.html" % mediaid,
        "MediaMimeType":        "text/html",
        "MediaType":            0,
        "MediaNotes":           template,
        "WebsitePhoto":         0,
        "WebsiteVideo":         0,
        "DocPhoto":             0,
        "ExcludeFromPublish":   0,
        # ASM2_COMPATIBILITY
        "NewSinceLastPublish":  1,
        "UpdatedSinceLastPublish": 0,
        # ASM2_COMPATIBILITY
        "LinkID":               linkid,
        "LinkTypeID":           linktype,
        "Date":                 dbo.now(),
        "CreatedDate":          dbo.now(),
        "RetainUntil":          retainuntil
    }, username, generateID=False)
    return mediaid

def create_log(dbo: Database, user: str, mid: int, logcode: str = "UK00", message: str = "") -> None:
    """
    Creates a log message related to media
    mid: The media ID
    logcode: The fixed code for reports to use - 
        ES01 = Document signing request
        ES02 = Document signed
    message: Some human readable text to accompany the code
    """
    m = get_media_by_id(dbo, mid)
    if m is None: return
    logtypeid = asm3.configuration.system_log_type(dbo)
    linktypeid = get_log_from_media_type(m.LINKTYPEID)
    # Only create the log message if it doesn't exist already. This prevents
    # multiple signing requests causing extra alerts after a doc has been signed.
    if 0 == dbo.query_int("SELECT COUNT(*) FROM log WHERE LinkID=? AND LinkType=? AND Comments LIKE ?", [ m.LINKID, linktypeid, f"{logcode}:{m.ID}:%"] ):
        asm3.log.add_log(dbo, user, linktypeid, m.LINKID, logtypeid, f"{logcode}:{m.ID}:{message} - {m.MEDIANOTES}")

def embellish_photo_urls(dbo: Database, rows: Results, linktypeid: int = ANIMAL) -> Results:
    """
    Given a set of rows, goes through them and finds all photo media for each ID
    and assigns them as a list with the name PHOTOURLS.
    Works for any kind of result row (animal, person, incident, etc) with the
    appropriate media linktypeid being passed.
    Retrieves all the media for all rows in a single query for performance.
    """
    if len(rows) == 0: return rows
    ids = ",".join([ str(x.ID) for x in rows ])
    mr = dbo.query("SELECT ID, LinkID, Date FROM media " \
            f"WHERE LinkTypeID = {linktypeid} AND LinkID IN ({ids}) " \
            "AND MediaMimeType = 'image/jpeg' " \
            "AND (ExcludeFromPublish = 0 OR ExcludeFromPublish Is Null) " \
            "ORDER BY WebsitePhoto DESC, LinkID, ID")
    for r in rows:
        r.PHOTOURLS = []
        for m in mr:
            if r.ID == m.LINKID: 
                ts = asm3.i18n.python2unix(m.DATE)
                url = f"{SERVICE_URL}?account={dbo.name()}&method=media_image&mediaid={m.ID}&ts={ts}"
                r.PHOTOURLS.append(url)
    return rows

def send_signature_request(dbo: Database, username: str, mid: int, post: PostedData) -> None:
    """
    Sends a request for a document to be signed by email. 
    mid: The media id of the document we are requesting a signature for.
    The following parameters are expected in post:
    from, to, cc, bcc, subject, body, logtype, addtolog
    """
    l = dbo.locale
    emailadd = post["to"]
    body = post["body"]
    m = get_media_by_id(dbo, mid)
    if m is None: 
        raise asm3.utils.ASMValidationError("cannot find media with ID %s" % mid)
    if m.MEDIAMIMETYPE != "text/html": 
        raise asm3.utils.ASMValidationError("invalid mime type for document signing %s" % m.MEDIAMIMETYPE)
    token = asm3.utils.md5_hash_hex("%s%s" % (m.ID, m.LINKID))
    url = "%s?account=%s&method=sign_document&email=%s&formid=%d&token=%s" % (SERVICE_URL, dbo.name(), asm3.utils.strip_email_address(emailadd).replace("@", "%40"), mid, token)
    body = asm3.utils.replace_url_token(body, url, m.MEDIANOTES)
    if post.boolean("addtolog"):
        asm3.log.add_log_email(dbo, username, get_log_from_media_type(m.LINKTYPEID), m.LINKID, post.integer("logtype"), 
            emailadd, _("Document signing request", l), body)
    create_log(dbo, username, mid, "ES01", _("Document signing request", l))
    asm3.utils.send_email(dbo, post["from"], emailadd, post["cc"], post["bcc"], post["subject"], body, "html")
    if asm3.configuration.audit_on_send_email(dbo): 
        asm3.audit.email(dbo, username, post["from"], emailadd, post["cc"], post["bcc"], post["subject"], body)

def sign_document(dbo: Database, username: str, mid: int, sigurl: str, signdate: datetime, signprefix: str) -> None:
    """
    Signs an HTML document.
    sigurl: An HTML5 data: URL containing an image of the signature
    signdate: A string representing the signing date and time of signing.
    signprefix: A prefix for the hash, useful for identifying types of signing (eg: forms vs user electronic sig)
    """
    asm3.al.debug("signing document %s for %s" % (mid, username), "media.sign_document", dbo)
    SIG_PLACEHOLDER = "signature:placeholder"
    m = dbo.first_row(dbo.query("SELECT * FROM media WHERE ID=?", [mid]))
    if m is None:  
        raise asm3.utils.ASMValidationError("cannot find media with ID %s" % mid)
    # Is this an HTML document?
    if m.MEDIAMIMETYPE != "text/html":
        asm3.al.error("document %s is not HTML (%s)" % (mid, m.MEDIAMIMETYPE), "media.sign_document", dbo)
        raise asm3.utils.ASMValidationError("invalid mime type for document signing %s" % m.MEDIAMIMETYPE)
    # Has this document already been signed? 
    if m.SIGNATUREHASH:
        asm3.al.error("document %s has already been signed" % mid, "media.sign_document", dbo)
        raise asm3.utils.ASMValidationError("Document is already signed")
    try:
        # If a sigurl is set, verify that it contains valid base64 data
        if sigurl != "":
            b64data = sigurl[sigurl.find(",")+1:]
            imgdata = asm3.utils.base64decode(b64data)
            # Verify that the data is a valid image and contains fewer
            # white pixels than a set amount.
            # The normal sized image is 10000 total pixes and the guide line is about 900px
            # We require at least 300 pixels to have been drawn on to qualify as a signature
            # as this is one drawn line of less than about an inch on screen.
            whitepx, totalpx = image_pixel_count_white(imgdata)
            if totalpx - whitepx < 1200:
                asm3.al.error(f"white pixels={whitepx}, total={totalpx}: difference < 1200", "media.sign_document", dbo)
                raise Exception("White pixel ratio too high")
    except Exception as err:
        asm3.al.error("signature data is not valid: %s" % err, "media.sign_document", dbo)
        raise asm3.utils.ASMValidationError("Signature data is not valid")
    # Does the document have a signing placeholder image? If so, replace it
    content = asm3.utils.bytes2str(asm3.dbfs.get_string_id(dbo, m.DBFSID))
    if content.find(SIG_PLACEHOLDER) != -1:
        asm3.al.debug("document %s: found signature placeholder" % mid, "media.sign_document", dbo)
        content = content.replace(SIG_PLACEHOLDER, sigurl)
    else:
        # Create the signature at the foot of the document
        asm3.al.debug("document %s: no placeholder, appending" % mid, "media.sign_document", dbo)
        sig = "<hr />\n"
        if sigurl != "": sig += '<p><img src="' + sigurl + '" /></p>\n'
        sig += "<p>%s</p>\n" % signdate
        content += sig
    # Create a hash of the contents and set it on all media records pointing to this DBFSID
    # (this gracefully handles animal/person media doc entries that point to the same DBFS file)
    for r in dbo.query("SELECT ID, LinkID, LinkTypeID FROM media WHERE DBFSID=?", [m.DBFSID]):
        # NOTE: We re-set linkid/linktypeid in the update query 
        # so that this update shows in the audit trail UI for the linked record.
        dbo.update("media", r.ID, {
            "LinkID": r.LINKID,
            "LinkTypeID": r.LINKTYPEID, 
            "SignatureHash": "%s:%s" % (signprefix, asm3.utils.md5_hash_hex(content)), 
            "Date": dbo.now() 
        }, username)
    # Update the dbfs contents
    content = asm3.utils.str2bytes(content)
    update_file_content(dbo, username, mid, content)

def has_signature(dbo: Database, mid: int) -> bool:
    """ Returns true if a piece of media has a signature """
    return 0 != dbo.query_int("SELECT COUNT(*) FROM media WHERE SignatureHash Is Not Null AND SignatureHash <> '' AND ID = ?", [mid])

def update_file_content(dbo: Database, username: str, mid: int, content: bytes) -> None:
    """
    Updates the dbfs content for the file pointed to by media record mid
    content should be a bytes string.
    This function will update multiple media records if they point to the same DBFSID.
    """
    m = dbo.first_row(dbo.query("SELECT DBFSID, MediaName FROM media WHERE ID=?", [mid]))
    if m is None: raise IOError("media id %s does not exist" % mid)
    if m.DBFSID == 0: raise IOError("cannot update contents of DBFSID 0")
    asm3.dbfs.put_string_id(dbo, m.DBFSID, m.MEDIANAME, content)
    dbo.update("media", f"DBFSID={m.DBFSID}", { "Date": dbo.now(), "MediaSize": len(content) }, username)

def update_media_from_form(dbo: Database, username: str, post: PostedData) -> None:
    mediaid = post.integer("mediaid")
    dbo.update("media", mediaid, { 
        "MediaNotes":   post["medianotes"],
        "RetainUntil":  post.date("retainuntil"),
        "Date":         dbo.now(),
        "MediaFlags":   post["mediaflags"].replace(",", "|") + "|",
        # ASM2_COMPATIBILITY
        "UpdatedSinceLastPublish": 1
    }, username)

def clone_media(dbo: Database, username: str, mediaid: int, linktypeid: int, linkid: int) -> None:
    """ Clones a media record with a new link """
    m = get_media_by_id(dbo, mediaid)
    nextid = dbo.get_id("media")
    return dbo.insert("media", {
        "ID":                   nextid,
        "DBFSID":               m.DBFSID,
        "MediaSize":            m.MEDIASIZE,
        "MediaSource":          MEDIASOURCE_CLONE,
        "MediaFlags":           m.MEDIAFLAGS,
        "MediaName":            m.MEDIANAME,
        "MediaMimeType":        m.MEDIAMIMETYPE,
        "MediaType":            m.MEDIATYPE,
        "MediaNotes":           m.MEDIANOTES,
        "WebsitePhoto":         0,
        "WebsiteVideo":         0,
        "DocPhoto":             0,
        "ExcludeFromPublish":   0,
        # ASM2_COMPATIBILITY
        "NewSinceLastPublish":  0,
        "UpdatedSinceLastPublish": 0,
        # ASM2_COMPATIBILITY
        "LinkID":               linkid,
        "LinkTypeID":           linktypeid,
        "Date":                 dbo.now(),
        "CreatedDate":          dbo.now(),
        "RetainUntil":          m.RETAINUNTIL
    }, username, generateID=False)

def update_media_link(dbo: Database, username: str, mediaid: int, linktypeid: int, linkid: int) -> None:
    """ Updates the media with id to have a new link """
    row = asm3.media.get_media_by_id(dbo, mediaid)
    parentlinks = asm3.audit.get_parent_links(row, "media")
    message = f"{mediaid} moved to linktype={linktypeid} linkid={linkid}"
    asm3.audit.edit(dbo, username, "media", linkid, parentlinks, message)
    dbo.update("media", mediaid, {
        "LinkID":   linkid,
        "LinkTypeID": linktypeid,
        "Date":     dbo.now()
    }, username)
    

def delete_media(dbo: Database, username: str, mid: int) -> None:
    """
    Deletes a media record from the system.
    """
    mr = dbo.first_row(dbo.query("SELECT * FROM media WHERE ID=?", [mid]))
    if not mr: return
    dbo.delete("media", mid, username)
    # Was it the web or doc preferred? If so, make the first image for the link
    # the web or doc preferred instead
    if mr.WEBSITEPHOTO == 1:
        ml = dbo.first_row(dbo.query("SELECT ID FROM media WHERE LinkID = ? AND LinkTypeID = ? " \
            "AND MediaMimeType = 'image/jpeg' AND ExcludeFromPublish = 0 " \
            "ORDER BY ID DESC", (mr.LINKID, mr.LINKTYPEID)))
        if ml: dbo.update("media", ml.ID, { "WebsitePhoto": 1 })
    if mr.DOCPHOTO == 1:
        ml = dbo.first_row(dbo.query("SELECT ID FROM media WHERE LinkID = ? AND LinkTypeID = ? " \
            "AND MediaMimeType = 'image/jpeg' AND ExcludeFromPublish = 0 " \
            "ORDER BY ID DESC", (mr.LINKID, mr.LINKTYPEID)))
        if ml: dbo.update("media", ml.ID, { "DocPhoto": 1 })

def convert_media_jpg2pdf(dbo: Database, username: str, mid: int) -> int:
    """
    Converts an image into a new PDF file. Returns the new media id. 
    """
    mr = dbo.first_row(dbo.query("SELECT * FROM media WHERE ID=?", [mid]))
    if not mr: raise asm3.utils.ASMError("Record does not exist")
    # If it's not a jpg image, we can stop right now
    if mr.MEDIAMIMETYPE != "image/jpeg": raise asm3.utils.ASMError("Image is not a JPEG file, cannot convert to PDF")
    # Load and convert the image
    imagedata = asm3.dbfs.get_string_id(dbo, mr.DBFSID)
    pdfdata = asm3.utils.generate_image_pdf(dbo.locale, imagedata)
    # Compress the new pdf
    pdfdata = scale_pdf(pdfdata)
    # Create a new media record for this pdf
    mediaid = dbo.get_id("media")
    path = get_dbfs_path(mr.LINKID, mr.LINKTYPEID)
    name = str(mediaid) + ".pdf"
    dbfsid = asm3.dbfs.put_string(dbo, name, path, pdfdata)
    dbo.insert("media", {
        "ID":                   mediaid,
        "DBFSID":               dbfsid,
        "MediaSize":            len(pdfdata),
        "MediaSource":          MEDIASOURCE_JPG2PDF,
        "MediaFlags":           "",
        "MediaName":            name,
        "MediaMimeType":        "application/pdf",
        "MediaType":            0,
        "MediaNotes":           mr.MEDIANOTES,
        "WebsitePhoto":         0,
        "WebsiteVideo":         0,
        "DocPhoto":             0,
        "ExcludeFromPublish":   0,
        # ASM2_COMPATIBILITY
        "NewSinceLastPublish":  0,
        "UpdatedSinceLastPublish": 0,
        # ASM2_COMPATIBILITY
        "LinkID":               mr.LINKID,
        "LinkTypeID":           mr.LINKTYPEID,
        "Date":                 dbo.now(),
        "CreatedDate":          dbo.now(),
        "RetainUntil":          mr.RETAINUNTIL
    }, username, generateID=False)
    return mediaid

def rotate_media(dbo: Database, username: str, mid: int, clockwise: bool = True) -> None:
    """
    Rotates an image media record 90 degrees if clockwise is true, or 270 degrees if false
    """
    mr = dbo.first_row(dbo.query("SELECT * FROM media WHERE ID=?", [mid]))
    if not mr: raise asm3.utils.ASMError("Record does not exist")
    # If it's not a jpg image, we can stop right now
    if mr.MEDIAMIMETYPE != "image/jpeg": raise asm3.utils.ASMError("Image is not a JPEG file, cannot rotate")
    # Load and rotate the image
    imagedata = asm3.dbfs.get_string_id(dbo, mr.DBFSID)
    imagedata = rotate_image(imagedata, clockwise)
    # Update it
    update_file_content(dbo, username, mid, imagedata)
    asm3.audit.edit(dbo, username, "media", mid, "", "media id %d rotated, clockwise=%s" % (mid, str(clockwise)))

def watermark_available(dbo: Database) -> bool:
    """
    Returns true if we can handle watermarking
    """
    return asm3.dbfs.file_exists(dbo, "watermark.png") and os.path.exists(os.path.join(WATERMARK_FONT_BASEDIRECTORY, asm3.configuration.watermark_font_file(dbo)))

def watermark_media(dbo: Database, username: str, mid: int) -> None:
    """
    Watermarks an image with animalname and logo
    """
    mr = dbo.first_row(dbo.query("SELECT * FROM media WHERE ID=?", [mid]))
    if not mr: raise asm3.utils.ASMError("Record does not exist")
    # If it's not a jpg image, we can stop right now
    if mr.MEDIAMIMETYPE != "image/jpeg": raise asm3.utils.ASMError("Image is not a JPEG file, cannot watermark")
    a = dbo.first_row(dbo.query("SELECT animal.AnimalName FROM media INNER JOIN animal ON (media.LinkID = animal.ID) WHERE media.ID = ?", [mid]))
    if a is None: raise asm3.utils.ASMError("Media is not linked to an animal")
    # Load and watermark the image
    imagedata = asm3.dbfs.get_string_id(dbo, mr.DBFSID)
    imagedata = watermark_with_transparency(dbo, imagedata, a.ANIMALNAME)
    # Update it
    update_file_content(dbo, username, mid, imagedata)
    asm3.audit.edit(dbo, username, "media", mid, "", "media id %d watermarked" % (mid))    

def image_pixel_count_colours(imagedata: bytes) -> Tuple[int, Dict]:
    """
    Counts the different coloured pixels in the image represented by imagedata.
    Returns a Tuple of total pixels, followed by a dict of RGB values and their counts within the image.
    """
    file_data = asm3.utils.bytesio(imagedata)
    im = Image.open(file_data)
    cc = {}
    width, height = im.size
    rgb_image = im.convert('RGB')
    # iterate through each pixel in the image and keep a count per unique color
    for x in range(width):
        for y in range(height):
            rgb = rgb_image.getpixel((x, y))
            if rgb in cc:
                cc[rgb] += 1
            else:
                cc[rgb] = 1
    return (width * height, cc)

def image_pixel_count_white(imagedata: bytes) -> Tuple[int, int]:
    """
    Counts the number of white pixels in imagedata.
    Returns a tuple of white pixels vs total pixels.
    """
    totalpixels, cc = image_pixel_count_colours(imagedata)
    for k, v in cc.items():
        if k == (255, 255, 255):
            return (v, totalpixels)
    return (0, totalpixels)

def scale_image(imagedata: bytes, resizespec: str) -> bytes:
    """
    Produce a scaled version of an image. 
    imagedata - The image to scale (bytes string)
    resizespec - a string in WxH format
    returns the scaled image data or the original data if there was a problem.
    """
    try:
        # Turn the scalespec into a tuple of the largest side
        ws, hs = resizespec.split("x")
        w = int(ws)
        h = int(hs)
        size = w, w
        if h > w: size = h, h
        # Load the image data and scale it
        file_data = asm3.utils.bytesio(imagedata)
        im = Image.open(file_data)
        im.thumbnail(size, Image.ANTIALIAS)
        if im.mode in ("RGBA", "P"): im = im.convert("RGB") # throw away alpha layer so we can output as JPEG
        # Save the scaled down image data 
        output = asm3.utils.bytesio()
        im.save(output, "JPEG")
        scaled_data = output.getvalue()
        output.close()
        return scaled_data
    except Exception as err:
        asm3.al.error("failed scaling image: %s" % str(err), "media.scale_image")
        return imagedata
    
def verify_image(imagedata: bytes) -> bool:
    """
    Loads an image to validate whether imagedata contains a valid image.
    """
    try:
        file_data = asm3.utils.bytesio(imagedata)
        Image.open(file_data)
        return True
    except Exception as err:
        asm3.al.error("failed verifying image: %s" % str(err), "media.verify_image")
        return False
    
def auto_rotate_image(dbo: Database, imagedata: bytes) -> bytes:
    """
    Automatically rotate an image according to the orientation of the
    image in the EXIF data. 
    """
    EXIF_ORIENTATION = 274
    OR_TO_ROTATE = {            # Map of EXIF Orientation to image rotation
        1: 0,                   # Correct orientation, no adjustment
        3: Image.ROTATE_180,    # upside down
        6: Image.ROTATE_270,    # rotated 90 degrees clockwise
        8: Image.ROTATE_90,     # rotated 90 degrees antilockwise
        # Flipped orientations        
        2: 0,
        7: Image.ROTATE_90,     # rotated 90 degrees anticlockwise
        4: Image.ROTATE_180,    # upside down
        5: Image.ROTATE_270     # rotated 90 degrees clockwise
    }
    try:
        inputd = asm3.utils.bytesio(imagedata)
        im = Image.open(inputd)
        if not hasattr(im, "_getexif") or im._getexif() is None:
            asm3.al.warn("image has no EXIF data, abandoning rotate", "media.auto_rotate_image", dbo)
            return imagedata
        exif = dict(im._getexif().items())
        if EXIF_ORIENTATION not in exif:
            asm3.al.warn("image EXIF data has no orientation", "media.auto_rotate_image", dbo)
            return imagedata
        rotation_factor = OR_TO_ROTATE[exif[EXIF_ORIENTATION]]
        flip = exif[EXIF_ORIENTATION] in (2, 7, 4, 5)
        if rotation_factor == 0 and not flip: 
            asm3.al.debug("image is already correctly rotated/flipped (EXIF==%s)" % exif[EXIF_ORIENTATION], "media.auto_rotate_image", dbo)
            return imagedata
        asm3.al.debug("orientation=%s --> rotate=%s deg cw, flip=%s" % (exif[EXIF_ORIENTATION], (rotation_factor*90-90), flip), "media.auto_rotate_image", dbo)
        if rotation_factor != 0: im = im.transpose(rotation_factor)
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        output = asm3.utils.bytesio()
        im.save(output, "JPEG")
        transposed_data = output.getvalue()
        output.close()
        return transposed_data
    except Exception as err:
        asm3.al.error("failed rotating/flipping image: %s" % str(err), "media.auto_rotate_image", dbo)
        return imagedata

def rotate_image(imagedata: bytes, clockwise: bool = True) -> bytes:
    """
    Rotate an image. 
    clockwise: Rotate 90 degrees clockwise, if false rotates anticlockwise
    """
    try:
        inputd = asm3.utils.bytesio(imagedata)
        im = Image.open(inputd)
        if clockwise:
            im = im.transpose(Image.ROTATE_270)
        else:
            im = im.transpose(Image.ROTATE_90)
        output = asm3.utils.bytesio()
        im.save(output, "JPEG")
        rotated_data = output.getvalue()
        output.close()
        return rotated_data
    except Exception as err:
        asm3.al.error("failed rotating image: %s" % str(err), "media.rotate_image")
        return imagedata

def remove_expired_media(dbo: Database, years: int = None, username: str = "system") -> str:
    """
    Removes all media where retainuntil < today
    and document media older than today - remove document media years.
    No longer physically deletes dbfs rows - that should be done manually via delete_orphaned_media
    If years is set, overrides the config options. Useful for unit testing.
    """
    rows = dbo.query("SELECT ID, DBFSID FROM media WHERE RetainUntil Is Not Null AND RetainUntil < ?", [ dbo.today() ])
    #for r in rows:
    #    asm3.dbfs.delete_id(dbo, r.dbfsid)
    dbo.execute("DELETE FROM media WHERE RetainUntil Is Not Null AND RetainUntil < ?", [ dbo.today() ])
    asm3.al.debug("removed %d expired media items (retain until)" % len(rows), "media.remove_expired_media", dbo)
    enabled = asm3.configuration.auto_remove_document_media(dbo)
    retainyears = asm3.configuration.auto_remove_document_media_years(dbo)
    if years:
        enabled = True
        retainyears = years
    if enabled and retainyears > 0:
        cutoff = dbo.today(offset = retainyears * -365)
        rows = dbo.query("SELECT ID, DBFSID FROM media WHERE MediaType = ? AND MediaMimeType <> 'image/jpeg' AND Date < ?", ( MEDIATYPE_FILE, cutoff ))
        #for r in rows:
        #    asm3.dbfs.delete_id(dbo, r.dbfsid) 
        dbo.execute("DELETE FROM media WHERE MediaType = ? AND MediaMimeType <> 'image/jpeg' AND Date < ?", ( MEDIATYPE_FILE, cutoff ))
        asm3.al.debug("removed %d expired document media items (remove after %s years)" % (len(rows), retainyears), "media.remove_expired_media", dbo)
        return "OK %s" % len(rows)

def remove_media_after_exit(dbo: Database, years: int = None, username: str = "system") -> str:
    """
    Removes media where the animal left the shelter or died more than X years ago.
    No longer physically deletes dbfs rows - that should be done manually
    via delete_orphaned_media
    If years is set, overrides the config options. Useful for unit testing.
    """
    enabled = asm3.configuration.auto_remove_animal_media_exit(dbo)
    exityears = asm3.configuration.auto_remove_animal_media_exit_years(dbo)
    if years:
        enabled = True
        exityears = years
    if enabled and exityears > 0:
        cutoff = dbo.today(offset = exityears * -365)
        animals = dbo.query_list("SELECT ID FROM animal WHERE Archived=1 AND (ActiveMovementDate < ? OR DeceasedDate < ?)", (cutoff, cutoff))
        affected = 0
        if len(animals) > 0:
            affected = dbo.delete("media", "LinkType=0 AND LinkID IN (%s)" % ",".join(animals), username) 
        asm3.al.debug("removed %d expired animal media items (remove %s years after exit)" % (affected, years), "media.remove_media_after_exit", dbo)
        return "OK %s" % affected
    
def replace_doc_image(dbo: Database, findstr: str, replacestr: str) -> None:
    """
    Goes through all html document media and looks for image attributes that contain
    findstr, and replaces the whole image attribute with replacestr. 
    Very useful for people who copied and pasted logo images as large data-uris
    and need to replace them with links to extra images.
    """
    mo = dbo.query("SELECT ID, DBFSID, MediaName FROM media WHERE MediaMimeType = 'text/html' ORDER BY ID")
    total = 0
    for i, m in enumerate(mo):
        try:
            asm3.al.debug("find/replace image %s (%d of %d)" % (m.MEDIANAME, i, len(mo)), "media.replace_doc_image", dbo)
            data = asm3.utils.bytes2str(asm3.dbfs.get_string_id(dbo, m.DBFSID))
            fpos = data.find(findstr)
            if fpos == -1:
                asm3.al.warn("findstr not present, skipping (ID=%s, DBFSID=%s)" % (m.ID, m.DBFSID), "media.replace_doc_image", dbo)
                continue
            while fpos != -1:
                spos = data.rfind("\"", 0, fpos)
                epos = data.find("\"", fpos)
                if spos == -1 or epos == -1:
                    asm3.al.debug("findstr found, but no attribute quotes either side, abandoning", "media.replace_doc_image", dbo)
                    continue
                asm3.al.debug(f"found findstr at pos {fpos}, attribute starts at {spos} and ends at {epos}", "media.replace_doc_image", dbo)
                data = data[0:spos+1] + replacestr + data[epos:]
                fpos = data.find(findstr)
            asm3.dbfs.put_string_id(dbo, m.DBFSID, m.MEDIANAME, asm3.utils.str2bytes(data))
            dbo.update("media", m.ID, { "MediaSize": len(data) }) 
            total += 1
        except Exception as err:
            asm3.al.error("failed find/replace (ID=%s, DBFSID=%s): %s" % (m.ID, m.DBFSID, err), "media.replace_doc_image", dbo)
    asm3.al.debug("find/replace image on %d of %d html documents" % (total, len(mo)), "media.replace_doc_image", dbo)

def scale_image_file(inimage: bytes, outimage: bytes, resizespec: str) -> None:
    """
    Scales the given image file from inimage to outimage
    to the size given in resizespec
    """
    # If we haven't been given a valid resizespec,
    # use a default value.
    if resizespec.count("x") != 1:
        resizespec = DEFAULT_RESIZE_SPEC
    # Turn the scalespec into a tuple of the largest side
    ws, hs = resizespec.split("x")
    w = int(ws)
    h = int(hs)
    size = w, w
    if h > w: size = h, h
    # Scale and save
    im = Image.open(inimage)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(outimage, "JPEG")

def scale_pdf(filedata: bytes) -> bytes:
    """
    Scales the given PDF filedata down and returns the compressed PDF data.
    """
    # If there are more than 50 pages, it's going to take forever to scale -
    # don't even bother trying. 
    pagecount = asm3.utils.pdf_count_pages(filedata)
    if pagecount > MAX_PDF_PAGES:
        asm3.al.error("Abandon PDF scaling - has > %d pages (%s found)" % (MAX_PDF_PAGES, pagecount), "media.scale_pdf")
        return filedata
    inputfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    outputfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    inputfile.write(filedata)
    inputfile.flush()
    inputfile.close()
    outputfile.close()
    # If something went wrong during the scaling, use the original data
    if not scale_pdf_file(inputfile.name, outputfile.name):
        return filedata
    compressed = asm3.utils.read_binary_file(outputfile.name)
    os.unlink(inputfile.name)
    os.unlink(outputfile.name)
    # If something has gone wrong and the scaled one has no size, return the original
    if len(compressed) == 0:
        return filedata
    # If the original is smaller than the scaled one, return the original
    if len(compressed) > len(filedata):
        return filedata
    return compressed

def scale_odt(filedata: bytes) -> bytes:
    """
    Scales an ODT file down by stripping anything starting with the name "Object"
    in the root or in the "ObjectReplacements" folder. Everything in the "Pictures"
    folder is also removed.
    """
    odt = asm3.utils.bytesio(filedata)
    try:
        zf = zipfile.ZipFile(odt, "r")
    except zipfile.BadZipfile:
        return ""
    # Write the replacement file
    zo = asm3.utils.bytesio()
    zfo = zipfile.ZipFile(zo, "w", zipfile.ZIP_DEFLATED)
    for info in zf.infolist():
        # Skip any object or image files to save space
        if info.filename.startswith("ObjectReplacements/Object ") or info.filename.startswith("Object ") or info.filename.endswith(".jpg") or info.filename.endswith(".png"):
            pass
        else:
            zfo.writestr(info.filename, zf.open(info.filename).read())
    zf.close()
    zfo.close()
    # Return the zip data
    return zo.getvalue()

def scale_pdf_file(inputfile: str, outputfile: str) -> bool:
    """
    Scale a PDF file using the command line. There are different
    approaches to this and gs, imagemagick and pdftk (among others)
    can be used.
    Returns True for success or False for failure.
    """
    KNOWN_ERRORS = [ 
        # GS produces this with out of date libpoppler and Microsoft Print PDF
        b"Can't find CMap Identity-UTF16-H building a CIDDecoding resource.",
        b"Error: Couldn't initialise file.",
        b"circular reference to indirect object"
    ]
    code, output = asm3.utils.cmd(SCALE_PDF_CMD % { "output": outputfile, "input": inputfile})
    for e in KNOWN_ERRORS:
        # Any known errors in the output should return failure
        if output.find(e) != -1: 
            asm3.al.error("Abandon PDF scaling - found known error: %s" % e, "media.scale_pdf_file")
            return False
    # A nonzero exit code is a failure
    if code > 0: 
        asm3.al.error("Abandon PDF scaling - nonzero exit code (%s)" % code, "media.scale_pdf_file")
        return False
    return True
   
def scale_all_animal_images(dbo: Database) -> None:
    """
    Goes through all animal images in the database and scales
    them to the current incoming media scaling factor.
    """
    mp = dbo.query("SELECT ID, DBFSID, MediaName FROM media WHERE MediaMimeType = 'image/jpeg' AND LinkTypeID = 0 ORDER BY ID")
    for i, m in enumerate(mp):
        try:
            inputfile = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            outputfile = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            odata = asm3.dbfs.get_string_id(dbo, m.DBFSID)
            inputfile.write(odata)
            inputfile.flush()
            inputfile.close()
            outputfile.close()
            asm3.al.debug("scaling %s (%d of %d)" % (m.MEDIANAME, i, len(mp)), "media.scale_all_animal_images", dbo)
            scale_image_file(inputfile.name, outputfile.name, RESIZE_IMAGES_SPEC)
            data = asm3.utils.read_binary_file(outputfile.name)
            os.unlink(inputfile.name)
            os.unlink(outputfile.name)
            # Update the image file data
            asm3.dbfs.put_string_id(dbo, m.DBFSID, m.MEDIANAME, data)
            dbo.update("media", m.ID, { "MediaSize": len(data) })
        except Exception as err:
            asm3.al.error("failed scaling image (ID=%s, DBFSID=%s): %s" % (m.ID, m.DBFSID, err), "media.scale_all_animal_images", dbo)
    asm3.al.debug("scaled %d images" % len(mp), "media.scale_all_animal_images", dbo)

def scale_all_odt(dbo: Database) -> None:
    """
    Goes through all odt files attached to records in the database and 
    scales them down (throws away images and objects so only the text remains to save space)
    """
    mo = dbo.query("SELECT ID, DBFSID, MediaName FROM media WHERE MediaMimeType = 'application/vnd.oasis.opendocument.text' ORDER BY ID")
    total = 0
    for i, m in enumerate(mo):
        try:
            asm3.al.debug("scaling %s (%d of %d)" % (m.MEDIANAME, i, len(mo)), "media.scale_all_odt", dbo)
            odata = asm3.dbfs.get_string_id(dbo, m.DBFSID)
            ndata = scale_odt(odata)
            if len(ndata) < 512:
                asm3.al.error("scaled odt %s came back at %d bytes, abandoning" % (m.MEDIANAME, len(ndata)), "scale_all_odt", dbo)
            else:
                asm3.dbfs.put_string_id(dbo, m.DBFSID, m.MEDIANAME, ndata)
                dbo.update("media", m.ID, { "MediaSize": len(ndata) }) 
                total += 1
        except Exception as err:
            asm3.al.error("failed scaling ODT (ID=%s, DBFSID=%s): %s" % (m.ID, m.DBFSID, err), "media.scale_all_odt", dbo)
    asm3.al.debug("scaled %d of %d odts" % (total, len(mo)), "media.scale_all_odt", dbo)

def scale_all_pdf(dbo: Database) -> None:
    """
    Goes through all PDFs in the database and attempts to scale them down.
    """
    mp = dbo.query("SELECT ID, DBFSID, MediaName FROM media WHERE MediaMimeType = 'application/pdf' ORDER BY ID")
    total = 0
    for i, m in enumerate(mp):
        try:
            odata = asm3.dbfs.get_string_id(dbo, m.DBFSID)
            data = scale_pdf(odata)
            asm3.al.debug("scaled %s (DBFSID=%s) (%d of %d): old size %d, new size %d" % (m.MEDIANAME, m.DBFSID, i, len(mp), len(odata), len(data)), "check_and_scale_pdfs", dbo)
            # Store the new compressed PDF file data - if it's smaller
            if len(data) < len(odata):
                asm3.dbfs.put_string_id(dbo, m.DBFSID, m.MEDIANAME, data)
                dbo.update("media", m.ID, { "MediaSize": len(data) })
                total += 1
        except Exception as err:
            asm3.al.error("failed scaling PDF (ID=%s, DBFSID=%s): %s" % (m.ID, m.DBFSID, err), "media.scale_all_pdf", dbo)
    asm3.al.debug("scaled %d of %d pdfs" % (total, len(mp)), "media.scale_all_pdf", dbo)

def watermark_font_preview(fontfile: str) -> bytes:
    """
    Generate image of preview text for fontname
    """
    i = Image.new(mode = "RGB", size = (200, 40), color = (255, 255, 255))
    d = ImageDraw.Draw(i)
    font_file = os.path.join(WATERMARK_FONT_BASEDIRECTORY, fontfile)
    if not os.path.exists(font_file) or not fontfile.endswith(".ttf"): raise asm3.utils.ASMError("Invalid font file")
    font_size = 26
    font = ImageFont.truetype(font_file, font_size)
    d.text((5, 5), "Lorem Ipsum", font=font, fill="black")
    output = asm3.utils.bytesio()
    i.save(output, "JPEG")
    imagedata = output.getvalue()
    output.close()
    return imagedata

def watermark_with_transparency(dbo: Database, imagedata: bytes, animalname: str) -> bytes:
    """
    Watermark the image with animalname and logo. 
    """
    try:

        if not watermark_available(dbo): 
            raise asm3.utils.ASMError("Watermarking is not available (no watermark.png or missing font)")

        inputd = asm3.utils.bytesio(imagedata)
        base_image = Image.open(inputd)
        watermark = Image.open(asm3.utils.bytesio(asm3.dbfs.get_string_filepath(dbo, "/reports/watermark.png")))
       
        width, height = base_image.size
        wm_width, wm_height = watermark.size
        x_offset = asm3.configuration.watermark_x_offset(dbo)
        y_offset = asm3.configuration.watermark_y_offset(dbo)
        x_position = width - (wm_width + x_offset)
        y_position = height - (wm_height + y_offset)
        position = (x_position,y_position)
        shadowcolor = asm3.configuration.watermark_font_shadow_color(dbo)
        fillcolor = asm3.configuration.watermark_font_fill_color(dbo)
        stroke = asm3.configuration.watermark_font_stroke(dbo)
        transparent = Image.new('RGB', (width, height), (0,0,0,0))
        transparent.paste(base_image, (0,0))
        transparent.paste(watermark, position, mask=watermark)
        draw = ImageDraw.Draw(transparent)

        font_offset = asm3.configuration.watermark_font_offset(dbo)
        font_maxsize = asm3.configuration.watermark_font_max_size(dbo)       
        font_file = os.path.join(WATERMARK_FONT_BASEDIRECTORY, asm3.configuration.watermark_font_file(dbo))

        for fontsize in range(20, font_maxsize, 5):
            font = ImageFont.truetype(font_file, fontsize)
            font_dimensions = draw.textsize(animalname,font=font)
            if font_dimensions[0]+font_offset > (width-wm_width-font_offset):
                fontsize = fontsize - 10
                break

        font = ImageFont.truetype(font_file, fontsize)
        font_position = height - (font_dimensions[1] + y_offset)

        draw.text((font_offset-stroke,font_position-stroke), animalname, font=font, fill=shadowcolor)
        draw.text((font_offset+stroke,font_position-stroke), animalname, font=font, fill=shadowcolor)
        draw.text((font_offset-stroke,font_position+stroke), animalname, font=font, fill=shadowcolor)
        draw.text((font_offset+stroke,font_position+stroke), animalname, font=font, fill=shadowcolor)

        draw.text((font_offset,font_position+stroke), animalname, font=font, fill=shadowcolor)
        draw.text((font_offset,font_position-stroke), animalname, font=font, fill=shadowcolor)
        draw.text((font_offset-stroke,font_position), animalname, font=font, fill=shadowcolor)
        draw.text((font_offset+stroke,font_position), animalname, font=font, fill=shadowcolor)

        draw.text((font_offset,font_position), animalname, font=font, fill=fillcolor)
        draw = ImageDraw.Draw(transparent)

        output = asm3.utils.bytesio()
        transparent.save(output, "JPEG")
        watermarked = output.getvalue()
        output.close()
        return watermarked

    except Exception as err:
        asm3.al.error("failed watermarking image: %s" % str(err), "media.watermark_with_transparency")
        return imagedata


