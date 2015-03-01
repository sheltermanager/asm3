#!/usr/bin/python

import al
import animal
import audit
import base64
import configuration
import datetime
import db
import dbfs
import i18n
from PIL import ExifTags, Image
import os
import tempfile
import utils
from cStringIO import StringIO
from sitedefs import SCALE_PDF_DURING_ATTACH, SCALE_PDF_DURING_BATCH, SCALE_PDF_CMD

ANIMAL = 0
LOSTANIMAL = 1
FOUNDANIMAL = 2
PERSON = 3
WAITINGLIST = 5
ANIMALCONTROL = 6

MEDIATYPE_FILE = 0
MEDIATYPE_DOCUMENT_LINK = 1
MEDIATYPE_VIDEO_LINK = 2

def mime_type(filename):
    """
    Returns the mime type for a file with the given name
    """
    types = {
        "jpg"           : "image/jpeg",
        "jpeg"          : "image/jpeg",
        "bmp"           : "image/bmp",
        "gif"           : "image/gif",
        "png"           : "image/png",
        "doc"           : "application/msword",
        "xls"           : "application/vnd.ms-excel",
        "ppt"           : "application/vnd.ms-powerpoint",
        "docx"          : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx"          : "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "xslx"          : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "odt"           : "application/vnd.oasis.opendocument.text",
        "sxw"           : "application/vnd.oasis.opendocument.text",
        "ods"           : "application/vnd.oasis.opendocument.spreadsheet",
        "odp"           : "application/vnd.oasis.opendocument.presentation",
        "pdf"           : "application/pdf",
        "mpg"           : "video/mpg",
        "mp3"           : "audio/mpeg3",
        "avi"           : "video/avi"
    }
    ext = filename[filename.rfind(".")+1:]
    if types.has_key(ext):
        return types[ext]
    return "application/octet-stream"

def get_web_preferred_name(dbo, linktype, linkid):
    return db.query_string(dbo, "SELECT MediaName FROM media " \
        "WHERE LinkTypeID = %d AND WebsitePhoto = 1 AND LinkID = %d" % (linktype, linkid))

def get_web_preferred(dbo, linktype, linkid):
    return db.query(dbo, "SELECT * FROM media WHERE LinkTypeID = %d AND " \
        "WebsitePhoto = 1 AND LinkID = %d" % (linktype, linkid))

def get_media_by_seq(dbo, linktype, linkid, seq):
    """ Returns image media by a one-based sequence number. 
        Element 1 is always the preferred.
        Empty list is returned if the item doesn't exist
    """
    rows = db.query(dbo, "SELECT * FROM media WHERE LinkTypeID = %d AND " \
        "LinkID = %d AND LOWER(MediaName) LIKE '%%.jpg' AND ExcludeFromPublish = 0 " \
        "ORDER BY WebsitePhoto DESC, ID" % (linktype, linkid))
    if len(rows) >= seq:
        return [rows[seq-1],]
    else:
        return []

def get_total_seq(dbo, linktype, linkid):
    return db.query_int(dbo, "SELECT COUNT(ID) FROM media WHERE LinkTypeID = %d AND " \
        "LinkID = %d AND LOWER(MediaName) LIKE '%%.jpg' AND ExcludeFromPublish = 0" % (linktype, linkid))

def set_video_preferred(dbo, username, mid):
    """
    Makes the media with id the preferred for video in the link
    """
    link = db.query(dbo, "SELECT LinkID, LinkTypeID FROM media WHERE ID = %d" % int(mid))[0]
    db.execute(dbo, "UPDATE media SET WebsiteVideo = 0 WHERE LinkID = %d AND LinkTypeID = %d" % ( int(link["LINKID"]), int(link["LINKTYPEID"])))
    db.execute(dbo, "UPDATE media SET WebsiteVideo = 1 WHERE ID = %d" % int(mid))
    audit.edit(dbo, username, "media", str(id) + ": video preferred for " + str(link["LINKID"]) + "/" + str(link["LINKTYPEID"]))

def set_web_preferred(dbo, username, mid):
    """
    Makes the media with id the preferred for the web in the link
    """
    link = db.query(dbo, "SELECT LinkID, LinkTypeID FROM media WHERE ID = %d" % int(mid))[0]
    db.execute(dbo, "UPDATE media SET WebsitePhoto = 0 WHERE LinkID = %d AND LinkTypeID = %d" % ( int(link["LINKID"]), int(link["LINKTYPEID"])))
    db.execute(dbo, "UPDATE media SET WebsitePhoto = 1 WHERE ID = %d" % int(mid))
    audit.edit(dbo, username, "media", str(id) + ": web preferred for " + str(link["LINKID"]) + "/" + str(link["LINKTYPEID"]))

def set_doc_preferred(dbo, username, mid):
    """
    Makes the media with id the preferred for docs in the link
    """
    link = db.query(dbo, "SELECT LinkID, LinkTypeID FROM media WHERE ID = %d" % int(mid))[0]
    db.execute(dbo, "UPDATE media SET DocPhoto = 0 WHERE LinkID = %d AND LinkTypeID = %d" % ( int(link["LINKID"]), int(link["LINKTYPEID"])))
    db.execute(dbo, "UPDATE media SET DocPhoto = 1 WHERE ID = %d" % int(mid))
    audit.edit(dbo, username, "media", str(mid) + ": document preferred for " + str(link["LINKID"]) + "/" + str(link["LINKTYPEID"]))

def set_excluded(dbo, username, mid, exclude = 1):
    """
    Marks the media with id excluded from publishing.
    """
    db.execute(dbo, "UPDATE media SET ExcludeFromPublish = %d WHERE ID = %d" % (exclude, mid))
    audit.edit(dbo, username, "media", str(mid) + ": excluded from publishing")

def get_name_for_id(dbo, mid):
    return db.query_string(dbo, "SELECT MediaName FROM media WHERE ID = %d" % mid)

def get_media_file_data(dbo, mid):
    """
    Gets a piece of media by id
    id: The media id
    Returns a tuple containing the last modified date, media name, 
    mime type and file data
    """
    mm = get_media_by_id(dbo, mid)[0]
    return mm["DATE"], mm["MEDIANAME"], mime_type(mm["MEDIANAME"]), dbfs.get_string(dbo, mm["MEDIANAME"])

def get_image_file_data(dbo, mode, iid, seq = -1, justdate = False):
    """
    Gets an image
    mode: animal | media | animalthumb | person | personthumb | dbfs
    iid: The id of the animal for animal/thumb mode or the media record
        or a template path for dbfs mode
    seq: If the mode is animal or person, returns image X for that person/animal
         The first image is always the preferred photo.
    if justdate is True, returns the last modified date
    if justdate is False, returns a tuple containing the last modified date and image data
    """
    def nopic():
        NOPIC_DATE = datetime.datetime(2011, 01, 01)
        if justdate: 
            return NOPIC_DATE
        else:
            return (NOPIC_DATE, "NOPIC")
    def thumb_nopic():
        NOPIC_DATE = datetime.datetime(2011, 01, 01)
        if justdate:
            return NOPIC_DATE
        else:
            return (NOPIC_DATE, "NOPIC")
    def mrec(mm):
        if justdate:
            return mm[0]["DATE"]
        else:
            return (mm[0]["DATE"], dbfs.get_string(dbo, mm[0]["MEDIANAME"]))
    def thumb_mrec(mm):
        if justdate:
            return mm[0]["DATE"]
        else:
            return (mm[0]["DATE"], scale_thumbnail(dbfs.get_string(dbo, mm[0]["MEDIANAME"])))

    if mode == "animal":
        if seq == -1:
            mm = get_web_preferred(dbo, ANIMAL, int(iid))
            if len(mm) == 0:
                return nopic()
            else:
                return mrec(mm)
        else:
            tseq = get_total_seq(dbo, ANIMAL, int(iid))
            if seq > tseq:
                return nopic()
            else:
                mm = get_media_by_seq(dbo, ANIMAL, int(iid), seq)
                return mrec(mm)
    elif mode == "person":
        if seq == -1:
            mm = get_web_preferred(dbo, PERSON, int(iid))
            if len(mm) == 0:
                return nopic()
            else:
                return mrec(mm)
        else:
            tseq = get_total_seq(dbo, PERSON, int(iid))
            if seq > tseq:
                return nopic()
            else:
                mm = get_media_by_seq(dbo, PERSON, int(iid), seq)
                return mrec(mm)
    elif mode == "animalthumb":
        mm = get_web_preferred(dbo, ANIMAL, int(iid))
        if len(mm) == 0:
            return thumb_nopic()
        else:
            return thumb_mrec(mm)
    elif mode == "personthumb":
        mm = get_web_preferred(dbo, PERSON, int(iid))
        if len(mm) == 0:
            return thumb_nopic()
        else:
            return thumb_mrec(mm)
    elif mode == "media":
        mm = get_media_by_id(dbo, int(iid))
        if len(mm) == 0:
            return nopic()
        else:
            return mrec(mm)
    elif mode == "dbfs":
        if justdate:
            return datetime.datetime.today()
        else:
            return (datetime.datetime.today(), dbfs.get_string_filepath(dbo, str(iid)))
    else:
        return nopic()

def get_dbfs_path(linkid, linktype):
    path = "/animal/%d" % int(linkid)
    if linktype == PERSON:
        path = "/owner/%d" % int(linkid)
    elif linktype == LOSTANIMAL:
        path = "/lostanimal/%d" % int(linkid)
    elif linktype == FOUNDANIMAL:
        path = "/foundanimal/%d" % int(linkid)
    elif linktype == WAITINGLIST:
        path = "/waitinglist/%d" % int(linkid)
    return path

def get_media(dbo, linktype, linkid):
    return db.query(dbo, "SELECT * FROM media WHERE LinkTypeID = %d AND LinkID = %d ORDER BY Date DESC" % ( linktype, linkid ))

def get_media_by_id(dbo, mid):
    return db.query(dbo, "SELECT * FROM media WHERE ID = %d" % mid )

def get_image_media(dbo, linktype, linkid, ignoreexcluded = False):
    if not ignoreexcluded:
        return db.query(dbo, "SELECT * FROM media WHERE LinkTypeID = %d AND LinkID = %d AND (LOWER(MediaName) Like '%%.jpg' OR LOWER(MediaName) Like '%%.jpeg')" % ( linktype, linkid ))
    else:
        return db.query(dbo, "SELECT * FROM media WHERE (ExcludeFromPublish = 0 OR ExcludeFromPublish Is Null) AND LinkTypeID = %d AND LinkID = %d AND (LOWER(MediaName) Like '%%.jpg' OR LOWER(MediaName) Like '%%.jpeg')" % ( linktype, linkid ))

def attach_file_from_form(dbo, username, linktype, linkid, post):
    """
    Attaches a media file from the posted form
    data is the web.py data object and should contain
    comments, the filechooser object, with filename and value 
    props - OR a parameter called base64image containing a base64
    encoded jpg image.
    """
    ext = ""
    base64data = ""
    base64image = post["base64image"]
    if base64image != "":
        ext = ".jpg"
        # If an HTML5 data url was used, strip the prefix so we just have base64 data
        if base64image.find("data:") != -1:
            base64data = base64image[base64image.find(",")+1:]
            # Browser escaping turns base64 pluses back into spaces, so switch back
            base64data = base64data.replace(" ", "+")
        else:
            base64data = base64image
        al.debug("received HTML5 base64 image data (%d bytes)" % (len(base64image)), "media.attach_file_from_form", dbo)
    else:
        ext = post.filename()
        ext = ext[ext.rfind("."):].lower()
    mediaid = db.get_id(dbo, "media")
    medianame = "%d%s" % ( mediaid, ext )
    ispicture = ext == ".jpg" or ext == ".jpeg"
    ispdf = ext == ".pdf"

    # Does this link have anything with web/doc set? If not, set the
    # web/doc flags
    web = 0
    doc = 0
    existing_web = db.query_int(dbo, "SELECT COUNT(*) FROM media WHERE WebsitePhoto = 1 " \
        "AND LinkID = %d AND LinkTypeID = %d" % ( int(linkid), int(linktype) ))
    existing_doc = db.query_int(dbo, "SELECT COUNT(*) FROM media WHERE DocPhoto = 1 " \
        "AND LinkID = %d AND LinkTypeID = %d" % ( int(linkid), int(linktype) ))
    if existing_web == 0 and ispicture:
        web = 1
    if existing_doc == 0 and ispicture:
        doc = 1

    if base64image != "":
        filedata = base64.b64decode(base64data)
    else:
        filedata = post.filedata()
        al.debug("received POST file data '%s' (%d bytes)" % (post.filename(), len(filedata)), "media.attach_file_from_form", dbo)

    # Is it a picture?
    if ispicture:
        # Autorotate it to match the EXIF orientation
        filedata = auto_rotate_image(dbo, filedata)
        # Scale it down to the system set size
        scalespec = configuration.incoming_media_scaling(dbo)
        if scalespec != "None":
            filedata = scale_image(filedata, scalespec)
            al.debug("scaled image to %s (%d bytes)" % (scalespec, len(filedata)), "media.attach_file_from_form", dbo)

    # Is it a PDF? If so, compress it if we can and the option is on
    if ispdf and SCALE_PDF_DURING_ATTACH and configuration.scale_pdfs(dbo):
        filedata = scale_pdf(filedata)
        medianame = "%d_scaled.pdf" % mediaid
        al.debug("compressed PDF (%d bytes)" % (len(filedata)), "media.attach_file_from_form", dbo)

    # Attach the file in the dbfs
    path = get_dbfs_path(linkid, linktype)
    dbfs.put_string(dbo, medianame, path, filedata)

    # Are the notes for an image blank and we're defaulting them from animal comments?
    comments = post["comments"]
    if comments == "" and ispicture and linktype == ANIMAL and configuration.auto_media_notes(dbo):
        comments = animal.get_comments(dbo, int(linkid))
        # Are the notes blank and we're defaulting them from the filename?
    elif comments == "" and configuration.default_media_notes_from_file(dbo) and base64image == "":
        comments = utils.filename_only(post.filename())
    
    # Create the media record
    sql = db.make_insert_sql("media", (
        ( "ID", db.di(mediaid) ),
        ( "MediaName", db.ds(medianame) ),
        ( "MediaType", db.di(0) ),
        ( "MediaNotes", db.ds(comments) ),
        ( "WebsitePhoto", db.di(web) ),
        ( "WebsiteVideo", db.di(0) ),
        ( "DocPhoto", db.di(doc) ),
        ( "ExcludeFromPublish", db.di(0) ),
        # ASM2_COMPATIBILITY
        ( "NewSinceLastPublish", db.di(1) ),
        ( "UpdatedSinceLastPublish", db.di(0) ),
        # ASM2_COMPATIBILITY
        ( "LinkID", db.di(linkid) ),
        ( "LinkTypeID", db.di(linktype) ),
        ( "Date", db.dd(i18n.now(dbo.timezone)))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "media", str(mediaid) + ": for " + str(linkid) + "/" + str(linktype))

def attach_link_from_form(dbo, username, linktype, linkid, post):
    """
    Attaches a link to a web resource from a form
    """
    existingvid = db.query_int(dbo, "SELECT COUNT(*) FROM media WHERE WebsiteVideo = 1 " \
        "AND LinkID = %d AND LinkTypeID = %d" % ( int(linkid), int(linktype) ))
    defvid = 0
    if existingvid == 0 and post.integer("linktype") == MEDIATYPE_VIDEO_LINK:
        defvid = 1
    mediaid = db.get_id(dbo, "media")
    url = post["linktarget"]
    if url.find("://") == -1:
        url = "http://" + url
    al.debug("attached link %s" % url, "media.attach_file_from_form")
    sql = db.make_insert_sql("media", (
        ( "ID", db.di(mediaid) ),
        ( "MediaName", db.ds(url) ),
        ( "MediaType", post.db_integer("linktype") ),
        ( "MediaNotes", post.db_string("comments") ),
        ( "WebsitePhoto", db.di(0) ),
        ( "WebsiteVideo", db.di(defvid) ),
        ( "DocPhoto", db.di(0) ),
        ( "ExcludeFromPublish", db.di(0) ),
        # ASM2_COMPATIBILITY
        ( "NewSinceLastPublish", db.di(1) ),
        ( "UpdatedSinceLastPublish", db.di(0) ),
        # ASM2_COMPATIBILITY
        ( "LinkID", db.di(linkid) ),
        ( "LinkTypeID", db.di(linktype) ),
        ( "Date", db.nowsql() )
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "media", str(mediaid) + ": for " + str(linkid) + "/" + str(linktype) + ": link to " + post["linktarget"])

def create_blank_document_media(dbo, username, linktype, linkid):
    """
    Creates a new media record for a blank document for the link given.
    linktype: ANIMAL, PERSON, etc
    linkid: ID for the link
    returns the new media id
    """
    mediaid = db.get_id(dbo, "media")
    sql = db.make_insert_sql("media", (
        ( "ID", db.di(mediaid) ),
        ( "MediaName", db.ds("%d.html" % mediaid) ),
        ( "MediaType", db.di(0)),
        ( "MediaNotes", db.ds("New document") ),
        ( "WebsitePhoto", db.di(0) ),
        ( "WebsiteVideo", db.di(0) ),
        ( "DocPhoto", db.di(0) ),
        ( "ExcludeFromPublish", db.di(0) ),
        # ASM2_COMPATIBILITY
        ( "NewSinceLastPublish", db.di(1) ),
        ( "UpdatedSinceLastPublish", db.di(0) ),
        # ASM2_COMPATIBILITY
        ( "LinkID", db.di(linkid) ),
        ( "LinkTypeID", db.di(linktype) ),
        ( "Date", db.nowsql() )
        ))
    db.execute(dbo, sql)
    path = ""
    if linktype == ANIMAL:
        path = "/animal"
    elif linktype == PERSON:
        path = "/owner"
    elif linktype == LOSTANIMAL:
        path = "/lostanimal"
    elif linktype == FOUNDANIMAL:
        path = "/foundanimal"
    path += "/" + str(linkid)
    name = str(mediaid) + ".html"
    dbfs.put_string(dbo, name, path, "")
    audit.create(dbo, username, "media", str(mediaid) + ": for " + str(linkid) + "/" + str(linktype))
    return mediaid

def create_document_media(dbo, username, linktype, linkid, template, content):
    """
    Creates a new media record for a document for the link given.
    linktype: ANIMAL, PERSON, etc
    linkid: ID for the link
    template: The name of the template used to create the document
    content: The document contents
    """
    mediaid = db.get_id(dbo, "media")
    sql = db.make_insert_sql("media", (
        ( "ID", db.di(mediaid) ),
        ( "MediaName", db.ds("%d.html" % mediaid) ),
        ( "MediaType", db.di(0)),
        ( "MediaNotes", db.ds(template) ),
        ( "WebsitePhoto", db.di(0) ),
        ( "WebsiteVideo", db.di(0) ),
        ( "DocPhoto", db.di(0) ),
        ( "ExcludeFromPublish", db.di(0) ),
        # ASM2_COMPATIBILITY
        ( "NewSinceLastPublish", db.di(1) ),
        ( "UpdatedSinceLastPublish", db.di(0) ),
        # ASM2_COMPATIBILITY
        ( "LinkID", db.di(linkid) ),
        ( "LinkTypeID", db.di(linktype) ),
        ( "Date", db.nowsql() )
        ))
    db.execute(dbo, sql)
    path = ""
    if linktype == ANIMAL:
        path = "/animal"
    elif linktype == PERSON:
        path = "/owner"
    elif linktype == LOSTANIMAL:
        path = "/lostanimal"
    elif linktype == FOUNDANIMAL:
        path = "/foundanimal"
    path += "/" + str(linkid)
    name = str(mediaid) + ".html"
    dbfs.put_string(dbo, name, path, content)
    audit.create(dbo, username, "media", str(mediaid) + ": for " + str(linkid) + "/" + str(linktype))

def update_file_content(dbo, username, mid, content):
    """
    Updates the dbfs content for the file pointed to by id
    """
    dbfs.replace_string(dbo, content, get_name_for_id(dbo, mid))
    db.execute(dbo, "UPDATE media SET Date = %s WHERE ID = %d" % ( db.nowsql(), int(mid) ))
    audit.edit(dbo, username, "media", str(mid) + " changed file contents")

def update_media_notes(dbo, username, mid, notes):
    sql = db.make_update_sql("media", "ID=%d" % int(mid), (
        ( "MediaNotes", db.ds(notes)),
        ( "MediaName", "MediaName" ),
        # ASM2_COMPATIBILITY
        ( "UpdatedSinceLastPublish", db.di(1))
        ))
    db.execute(dbo, sql)
    audit.edit(dbo, username, "media", str(mid) + "notes => " + notes)

def delete_media(dbo, username, mid):
    """
    Deletes a media record from the system
    """
    mr = db.query(dbo, "SELECT * FROM media WHERE ID=%d" % int(mid))
    if len(mr) == 0: return
    mr = mr[0]
    mn = mr["MEDIANAME"]
    audit.delete(dbo, username, "media", str(mr))
    dbfs.delete(dbo, mn)
    db.execute(dbo, "DELETE FROM media WHERE ID = %d" % int(mid))
    # Was it the web or doc preferred? If so, make the first image for the link
    # the web or doc preferred instead
    if mr["WEBSITEPHOTO"] == 1:
        ml = db.query(dbo, "SELECT * FROM media WHERE LinkID=%d AND LinkTypeID=%d " \
            "AND (LOWER(MediaName) LIKE '%%.jpg' OR LOWER(MediaName) LIKE '%%.jpeg') " \
            "ORDER BY ID" % ( mr["LINKID"], mr["LINKTYPEID"] ))
        if len(ml) > 0:
            db.execute(dbo, "UPDATE media SET WebsitePhoto = 1 WHERE ID = %d" % ml[0]["ID"])
    if mr["DOCPHOTO"] == 1:
        ml = db.query(dbo, "SELECT * FROM media WHERE LinkID=%d AND LinkTypeID=%d " \
            "AND (LOWER(MediaName) LIKE '%%.jpg' OR LOWER(MediaName) LIKE '%%.jpeg') " \
            "ORDER BY ID" % ( mr["LINKID"], mr["LINKTYPEID"] ))
        if len(ml) > 0:
            db.execute(dbo, "UPDATE media SET DocPhoto = 1 WHERE ID = %d" % ml[0]["ID"])

def rotate_media(dbo, username, mid, clockwise = True):
    """
    Rotates an image media record 90 degrees if clockwise is true, or 270 degrees if false
    """
    mr = db.query(dbo, "SELECT * FROM media WHERE ID=%d" % int(mid))
    if len(mr) == 0: raise utils.ASMError("Record does not exist")
    mr = mr[0]
    mn = mr["MEDIANAME"]
    # If it's not a jpg image, we can stop right now
    ext = mn[mn.rfind("."):].lower()
    if ext != ".jpg" and ext != ".jpeg":
        raise utils.ASMError("Image is not a JPEG file, cannot rotate")
    # Load the image data
    path = get_dbfs_path(mr["LINKID"], mr["LINKTYPEID"])
    imagedata = dbfs.get_string(dbo, mn, path)
    imagedata = rotate_image(imagedata, clockwise)
    # Store it back in the dbfs and add an entry to the audit trail
    dbfs.put_string(dbo, mn, path, imagedata)
    # Update the date stamp on the media record
    db.execute(dbo, "UPDATE media SET Date = %s WHERE ID = %d" % (db.nowsql(), mid))
    audit.edit(dbo, username, "media", "media id %d rotated, clockwise=%s" % (mid, str(clockwise)))

def scale_image(imagedata, resizespec):
    """
    Produce a scaled version of an image. 
    imagedata - The image to scale
    resizespec - a string in WxH format
    returns the scaled image data
    """
    try:
        # Turn the scalespec into a tuple of the largest side
        ws, hs = resizespec.split("x")
        w = int(ws)
        h = int(hs)
        size = w, w
        if h > w: size = h, h
        # Load the image data into a StringIO object and scale it
        file_data = StringIO(imagedata)
        im = Image.open(file_data)
        im.thumbnail(size, Image.ANTIALIAS)
        # Save the scaled down image data into another string for return
        output = StringIO()
        im.save(output, "JPEG")
        scaled_data = output.getvalue()
        output.close()
        return scaled_data
    except Exception,err:
        al.error("failed scaling image: %s" % str(err), "media.scale_image")
        return imagedata

def auto_rotate_image(dbo, imagedata):
    """
    Automatically rotate an image according to the orientation of the
    image in the EXIF data. 
    """
    try:
        inputd = StringIO(imagedata)
        im = Image.open(inputd)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        if not hasattr(im, "_getexif") or im._getexif() is None:
            al.debug("image has no EXIF data, abandoning rotate", "media.auto_rotate_image", dbo)
            return imagedata
        exif = dict(im._getexif().items())
        if exif[orientation] == 3:   im = im.transpose(Image.ROTATE_180)
        elif exif[orientation] == 6: im = im.transpose(Image.ROTATE_270)
        elif exif[orientation] == 8: im = im.transpose(Image.ROTATE_90)
        output = StringIO()
        im.save(output, "JPEG")
        rotated_data = output.getvalue()
        output.close()
        return rotated_data
    except Exception,err:
        al.error("failed rotating image: %s" % str(err), "media.auto_rotate_image", dbo)
        return imagedata

def rotate_image(imagedata, clockwise = True):
    """
    Rotate an image. 
    clockwise: Rotate 90 degrees clockwise, if false rotates anticlockwise
    """
    try:
        inputd = StringIO(imagedata)
        im = Image.open(inputd)
        if clockwise:
            im = im.transpose(Image.ROTATE_270)
        else:
            im = im.transpose(Image.ROTATE_90)
        output = StringIO()
        im.save(output, "JPEG")
        rotated_data = output.getvalue()
        output.close()
        return rotated_data
    except Exception,err:
        al.error("failed rotating image: %s" % str(err), "media.rotate_image")
        return imagedata

def scale_thumbnail(imagedata):
    """
    Scales the given imagedata down to our thumbnail size 
    (70px on the longest side)
    """
    return scale_image(imagedata, "70x70")

def scale_image_file(inimage, outimage, resizespec):
    """
    Scales the given image file from inimage to outimage
    to the size given in resizespec
    """
    # If we haven't been given a valid resizespec,
    # use a default value.
    if resizespec.count("x") != 1:
        resizespec = "400x400"
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

def scale_thumbnail_file(inimage, outimage):
    """
    Scales the given image to a thumbnail
    """
    scale_image_file(inimage, outimage, "70x70")

def scale_pdf(filedata):
    """
    Scales the given PDF filedata down and returns the compressed PDF data.
    """
    inputfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    outputfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    inputfile.write(filedata)
    inputfile.flush()
    inputfile.close()
    outputfile.close()
    scale_pdf_file(inputfile.name, outputfile.name)
    f = open(outputfile.name, "r")
    compressed = f.read()
    f.close()
    os.unlink(inputfile.name)
    os.unlink(outputfile.name)
    # If the original is smaller than the scaled one, return the original
    if len(compressed) > len(filedata):
        return filedata
    return compressed

def scale_pdf_file(inputfile, outputfile):
    """
    Scale a PDF file using the command line. There are different
    approaches to this and gs, imagemagick and pdftk (among others)
    can be used.
    """
    os.system(SCALE_PDF_CMD % { "output": outputfile, "input": inputfile})
   
def check_and_scale_pdfs(dbo):
    """
    Goes through all PDFs in the database to see if they have been
    scaled (have a suffix of _scaled.pdf) and scales down any unscaled
    ones.
    """
    if not SCALE_PDF_DURING_BATCH:
        al.warn("SCALE_PDF_DURING_BATCH is disabled, not scaling pdfs", "media.check_and_scale_pdfs", dbo)
    if not configuration.scale_pdfs(dbo):
        al.warn("ScalePDFs config option disabled in this database, not scaling pdfs", "media.check_and_scale_pdfs", dbo)
    mp = db.query(dbo, \
        "SELECT MediaName FROM media WHERE LOWER(MediaName) LIKE '%.pdf' AND " \
        "LOWER(MediaName) NOT LIKE '%_scaled.pdf'")
    for m in mp:
        filepath = db.query_string(dbo, "SELECT Path FROM dbfs WHERE Name='%s'" % m["MEDIANAME"])
        original_name = str(m["MEDIANAME"])
        new_name = str(m["MEDIANAME"])
        new_name = new_name[0:len(new_name)-4] + "_scaled.pdf"
        odata = dbfs.get_string(dbo, original_name)
        data = scale_pdf(odata)
        # Update the media entry with the new name
        db.execute(dbo, "UPDATE media SET MediaName = '%s' WHERE MediaName = '%s'" % \
            ( new_name, original_name))
        # Update the dbfs entry with the new name
        dbfs.rename_file(dbo, filepath, original_name, new_name)
        # Update the PDF file data
        dbfs.put_string(dbo, new_name, filepath, data)
    al.debug("found and scaled %d pdfs" % len(mp), "media.check_and_scale_pdfs", dbo)

def scale_animal_images(dbo):
    """
    Goes through all animal images in the database and scales
    them to the current incoming media scaling factor.
    """
    mp = db.query(dbo, "SELECT MediaName FROM media WHERE LOWER(MediaName) LIKE '%.jpg' AND LinkTypeID = 0")
    for i, m in enumerate(mp):
        filepath = db.query_string(dbo, "SELECT Path FROM dbfs WHERE Name='%s'" % m["MEDIANAME"])
        name = str(m["MEDIANAME"])
        inputfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        outputfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        odata = dbfs.get_string(dbo, name)
        inputfile.write(odata)
        inputfile.flush()
        inputfile.close()
        outputfile.close()
        al.debug("scaling %s (%d of %d)" % (name, i, len(mp)), "media.scale_animal_images", dbo)
        scale_image_file(inputfile.name, outputfile.name, configuration.incoming_media_scaling(dbo))
        f = open(outputfile.name, "r")
        data = f.read()
        f.close()
        os.unlink(inputfile.name)
        os.unlink(outputfile.name)
        # Update the image file data
        dbfs.put_string(dbo, name, filepath, data)
    al.debug("scaled %d images" % len(mp), "media.scale_animal_images", dbo)

