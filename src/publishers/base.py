#!/usr/bin/python

import al
import async
import configuration
import db
import dbfs
import ftplib
import glob
import i18n
import media
import os
import shutil
import sys
import tempfile
import threading
import utils
import wordprocessor

from publish import get_animal_data
from sitedefs import MULTIPLE_DATABASES_PUBLISH_DIR, MULTIPLE_DATABASES_PUBLISH_FTP

def quietcallback(x):
    """ ftplib callback that does nothing instead of dumping to stdout """
    pass

class PublishCriteria(object):
    """
    Class containing publishing criteria. Has functions to 
    convert to and from a command line string
    """
    includeCaseAnimals = False
    includeNonNeutered = False
    includeReservedAnimals = False
    includeRetailerAnimals = False
    includeFosterAnimals = False
    includeQuarantine = False
    includeTrial = False
    includeHold = False
    includeWithoutDescription = False
    includeWithoutImage = False
    includeColours = False
    bondedAsSingle = False
    clearExisting = False
    uploadAllImages = False
    uploadDirectly = False
    forceReupload = False
    noImportFile = False # If a 3rd party has a seperate import disable upload
    generateJavascriptDB = False
    thumbnails = False
    thumbnailSize = "70x70"
    checkSocket = False
    order = 1 # 0 = Ascending entry, 1 = Descending entry, 2 = Ascending name
    excludeUnderWeeks = 12
    animalsPerPage = 10
    htmlByChildAdult = False # True if html pages should be prefixed baby/adult_ and split
    childAdultSplit=26 # Number of weeks before an animal is treated as an adult by the child adult publisher
    htmlBySpecies = False # True if html pages should be output with species name and possibly split by age
    htmlByType = False # True if html pages should be output with type name
    outputAdopted = False # True if html publisher should output an adopted.html page
    outputAdoptedDays = 30 # The number of days to go back when considering adopted animals
    outputDeceased = False # True if html publisher should output a deceased.html page
    outputForms = False # True if html publisher should output a forms.html page
    outputRSS = False # True if html publisher should output an rss.xml page
    limit = 0
    style = "."
    extension = "html"
    scaleImages = "" # A resize spec or old values of: 1 = None, 2 = 320x200, 3=640x480, 4=800x600, 5=1024x768, 6=300x300, 7=95x95
    internalLocations = [] # List of either location IDs, or LIKE comparisons
    publishDirectory = None # None = use temp directory for publishing
    ignoreLock = False # Force the publisher to run even if another publisher is running

    def get_int(self, s):
        """
        Returns the val portion of key=val as an int
        """
        return utils.cint(s.split("=")[1])

    def get_str(self, s):
        """
        Returns the val portion of key=val as a string
        """
        return s.split("=")[1]

    def __init__(self, fromstring = ""):
        """
        Initialises the publishing criteria from a string if given
        """
        if fromstring == "": return
        for s in fromstring.split(" "):
            if s == "includecase": self.includeCaseAnimals = True
            if s == "includenonneutered": self.includeNonNeutered = True
            if s == "includereserved": self.includeReservedAnimals = True
            if s == "includeretailer": self.includeRetailerAnimals = True
            if s == "includefosters": self.includeFosterAnimals = True
            if s == "includehold": self.includeHold = True
            if s == "includequarantine": self.includeQuarantine = True
            if s == "includetrial": self.includeTrial = True
            if s == "includewithoutdescription": self.includeWithoutDescription = True
            if s == "includewithoutimage": self.includeWithoutImage = True
            if s == "includecolours": self.includeColours = True
            if s == "bondedassingle": self.bondedAsSingle = True
            if s == "noimportfile": self.noImportFile = True
            if s == "clearexisting": self.clearExisting = True
            if s == "uploadall": self.uploadAllImages = True
            if s == "forcereupload": self.forceReupload = True
            if s == "generatejavascriptdb": self.generateJavascriptDB = True
            if s == "thumbnails": self.thumbnails = True
            if s == "checksocket": self.checkSocket = True
            if s == "uploaddirectly": self.uploadDirectly = True
            if s == "htmlbychildadult": self.htmlByChildAdult = True
            if s == "htmlbyspecies": self.htmlBySpecies = True
            if s == "htmlbytype": self.htmlByType = True
            if s == "outputadopted": self.outputAdopted = True
            if s == "outputdeceased": self.outputDeceased = True
            if s == "outputforms": self.outputForms = True
            if s == "outputrss": self.outputRSS = True
            if s.startswith("outputadopteddays"): self.outputAdoptedDays = self.get_int(s)
            if s.startswith("order"): self.order = self.get_int(s)
            if s.startswith("excludeunder"): self.excludeUnderWeeks = self.get_int(s)
            if s.startswith("animalsperpage"): self.animalsPerPage = self.get_int(s)
            if s.startswith("limit"): self.limit = self.get_int(s)
            if s.startswith("style"): self.style = self.get_str(s)
            if s.startswith("extension"): self.extension = self.get_str(s)
            if s.startswith("scaleimages"): self.scaleImages = self.get_str(s)
            if s.startswith("thumbnailsize"): self.thumbnailSize = self.get_str(s)
            if s.startswith("includelocations"): self.internalLocations = self.get_str(s).split(",")
            if s.startswith("publishdirectory"): self.publishDirectory = self.get_str(s)
            if s.startswith("childadultsplit"): self.childAdultSplit = self.get_int(s)

    def __str__(self):
        """
        Returns a string representation of the criteria (which corresponds
        exactly to an ASM 2.x command line string to a publisher and is how
        we store the defaults in the database)
        """
        s = ""
        if self.includeCaseAnimals: s += " includecase"
        if self.includeNonNeutered: s += " includenonneutered"
        if self.includeReservedAnimals: s += " includereserved"
        if self.includeRetailerAnimals: s += " includeretailer"
        if self.includeFosterAnimals: s += " includefosters"
        if self.includeHold: s += " includehold"
        if self.includeQuarantine: s += " includequarantine"
        if self.includeTrial: s += " includetrial"
        if self.includeWithoutDescription: s += " includewithoutdescription"
        if self.includeWithoutImage: s += " includewithoutimage"
        if self.includeColours: s += " includecolours"
        if self.bondedAsSingle: s += " bondedassingle"
        if self.noImportFile: s += " noimportfile"
        if self.clearExisting: s += " clearexisting"
        if self.uploadAllImages: s += " uploadall"
        if self.forceReupload: s += " forcereupload"
        if self.generateJavascriptDB: s += " generatejavascriptdb"
        if self.thumbnails: s += " thumbnails"
        if self.checkSocket: s += " checksocket"
        if self.uploadDirectly: s += " uploaddirectly"
        if self.htmlBySpecies: s += " htmlbyspecies"
        if self.htmlByType: s += " htmlbytype"
        if self.htmlByChildAdult: s += " htmlbychildadult"
        if self.outputAdopted: s += " outputadopted"
        if self.outputDeceased: s += " outputdeceased"
        if self.outputForms: s += " outputforms"
        if self.outputRSS: s += " outputrss"
        s += " order=" + str(self.order)
        s += " excludeunder=" + str(self.excludeUnderWeeks)
        s += " animalsperpage=" + str(self.animalsPerPage)
        s += " limit=" + str(self.limit)
        s += " style=" + str(self.style)
        s += " extension=" + str(self.extension)
        s += " scaleimages=" + str(self.scaleImages)
        s += " thumbnailsize=" + str(self.thumbnailSize)
        s += " childadultsplit=" + str(self.childAdultSplit)
        s += " outputadopteddays=" + str(self.outputAdoptedDays)
        if len(self.internalLocations) > 0: s += " includelocations=" + ",".join(self.internalLocations)
        if self.publishDirectory is not None: s += " publishdirectory=" + self.publishDirectory
        return s.strip()

class AbstractPublisher(threading.Thread):
    """
    Base class for all publishers
    """
    dbo = None
    pc = None
    totalAnimals = 0
    publisherName = ""
    publisherKey = ""
    publishDateTime = None
    successes = 0
    alerts = 0
    publishDir = ""
    tempPublishDir = True
    locale = "en"
    lastError = ""
    logBuffer = []

    def __init__(self, dbo, publishCriteria):
        threading.Thread.__init__(self)
        self.dbo = dbo
        self.locale = configuration.locale(dbo)
        self.pc = publishCriteria
        self.makePublishDirectory()

    def checkMappedSpecies(self):
        """
        Returns True if all species have been mapped for publishers
        """
        return 0 == db.query_int(self.dbo, "SELECT COUNT(*) FROM species " + \
            "WHERE PetFinderSpecies Is Null OR PetFinderSpecies = ''")

    def checkMappedBreeds(self):
        """
        Returns True if all breeds have been mapped for publishers
        """
        return 0 == db.query_int(self.dbo, "SELECT COUNT(*) FROM breed " + \
            "WHERE PetFinderBreed Is Null OR PetFinderBreed = ''")

    def checkMappedColours(self):
        """
        Returns True if all colours have been mapped for publishers
        """
        return 0 == db.query_int(self.dbo, "SELECT COUNT(*) FROM basecolour " + \
            "WHERE AdoptAPetColour Is Null OR AdoptAPetColour = ''")

    def getPublisherBreed(self, an, b1or2 = 1):
        """
        Encapsulates logic for reading publisher breed fields.
        an: The animal row
        b1or2: Whether to get breed 1 or 2
        return value is the publisher breed for datafiles/posts. It can be a blank
        based on whether the animal is a crossbreed or not.
        """
        crossbreed = an["CROSSBREED"]
        breed1id = an["BREEDID"]
        breed2id = an["BREED2ID"]
        breedname = an["BREEDNAME1"]
        publisherbreed = an["PETFINDERBREED"]
        # We're dealing with the first breed field. Always send the mapped
        # publisher breed if it isn't a crossbreed animal
        if b1or2 == 1:
            if crossbreed == 0: 
                return publisherbreed
        # We're dealing with the second breed field. Always send that as a blank
        # if this isn't a crossbreed animal
        elif b1or2 == 2:
            breedname = an["BREEDNAME2"]
            publisherbreed = an["PETFINDERBREED2"]
            if crossbreed == 0: 
                return ""
        # If one of our magic words is found, or both breeds are the
        # same, return a blank. By the time we get here, crossbreed must == 1
        b = utils.nulltostr(breedname).lower()
        if b == "mix" or b == "cross" or b == "unknown" or b == "crossbreed" or breed1id == breed2id:
            return ""
        return publisherbreed

    def isPublisherExecuting(self):
        """
        Returns True if a publisher is already currently running against
        this database. If the ignoreLock publishCriteria option has been
        set, always returns false.
        """
        if self.pc.ignoreLock: return False
        return async.is_task_running(self.dbo)

    def updatePublisherProgress(self, progress):
        """
        Updates the publisher progress in the database
        """
        async.set_task_name(self.dbo, self.publisherName)
        async.set_progress_max(self.dbo, 100)
        async.set_progress_value(self.dbo, progress)

    def replaceMDBTokens(self, dbo, s):
        """
        Replace MULTIPLE_DATABASE tokens in the string given.
        """
        s = s.replace("{alias}", dbo.alias)
        s = s.replace("{database}", dbo.database)
        s = s.replace("{username}", dbo.username)
        return s

    def replaceAnimalTags(self, a, s):
        """
        Replace any $$Tag$$ tags in s, using animal a
        """
        tags = wordprocessor.animal_tags(self.dbo, a)
        return wordprocessor.substitute_tags(s, tags, True, "$$", "$$")

    def resetPublisherProgress(self):
        """
        Resets the publisher progress and stops blocking for other 
        publishers
        """
        async.reset(self.dbo)

    def setPublisherComplete(self):
        """
        Mark the current publisher as complete
        """
        async.set_progress_value(self.dbo, 100)

    def getProgress(self, i, n):
        """
        Returns a progress percentage
        i: Current position
        n: Total elements
        """
        return int((float(i) / float(n)) * 100)

    def shouldStopPublishing(self):
        """
        Returns True if we need to stop publishing
        """
        return async.get_cancel(self.dbo)

    def setStartPublishing(self):
        """
        Clears the stop publishing flag so we can carry on publishing.
        """
        async.set_cancel(self.dbo, False)

    def setLastError(self, msg):
        """
        Sets the last error message and clears the publisher lock
        """
        async.set_last_error(self.dbo, msg)
        self.lastError = msg
        if msg != "": self.logError(self.lastError)
        self.resetPublisherProgress()

    def cleanup(self, save_log=True):
        """
        Call when the publisher has completed to tidy up.
        """
        if save_log: self.saveLog()
        self.setPublisherComplete()

    def makePublishDirectory(self):
        """
        Creates a temporary publish directory if one isn't set, or uses
        the one set in the criteria.
        """
        if self.publisherKey == "html":
            # It's HTML publishing - we have some special rules
            # If the publishing directory has been overridden, set it
            if MULTIPLE_DATABASES_PUBLISH_DIR != "":
                self.publishDir = MULTIPLE_DATABASES_PUBLISH_DIR
                # Replace any tokens
                self.publishDir = self.replaceMDBTokens(self.dbo, self.publishDir)
                self.pc.ignoreLock = True
                # Validate that the directory exists
                if not os.path.exists(self.publishDir):
                    self.setLastError("publishDir does not exist: %s" % self.publishDir)
                    return
                # If they've set the option to reupload animal images, clear down
                # any existing images first
                if self.pc.forceReupload:
                    for f in os.listdir(self.publishDir):
                        if f.lower().endswith(".jpg"):
                            os.unlink(os.path.join(self.publishDir, f))
                # Clear out any existing HTML pages
                for f in os.listdir(self.publishDir):
                    if f.lower().endswith(".html"):
                        os.unlink(os.path.join(self.publishDir, f))
                self.tempPublishDir = False
                return
            if self.pc.publishDirectory is not None and self.pc.publishDirectory.strip() != "":
                # The user has set a target directory for their HTML publishing, use that
                self.publishDir = self.pc.publishDirectory
                # Fix any Windows path backslashes that could have been doubled up
                if self.publishDir.find("\\\\") != -1:
                    self.publishDir = self.publishDir.replace("\\\\", "\\")
                # Validate that the directory exists
                if not os.path.exists(self.publishDir):
                    self.setLastError("publishDir does not exist: %s" % self.publishDir)
                    return
                # If they've set the option to reupload animal images, clear down
                # any existing images first
                if self.pc.forceReupload:
                    for f in os.listdir(self.publishDir):
                        if f.lower().endswith(".jpg"):
                            os.unlink(os.path.join(self.publishDir, f))
                # Clear out any existing HTML pages
                for f in os.listdir(self.publishDir):
                    if f.lower().endswith(".html"):
                        os.unlink(os.path.join(self.publishDir, f))
                self.tempPublishDir = False
                return
        # Use a temporary folder for publishing
        self.tempPublishDir = True
        self.publishDir = tempfile.mkdtemp()

    def deletePublishDirectory(self):
        """
        Removes the publish directory if it was temporary
        """
        if self.tempPublishDir:
            shutil.rmtree(self.publishDir, True)

    def getDescription(self, an, crToBr = False, crToHE = False):
        """
        Returns the description/bio for an animal.
        an: The animal record
        crToBr: Convert line breaks to <br /> tags
        crToHE: Convert line breaks to html entity &#10;
        """
        # Note: WEBSITEMEDIANOTES becomes ANIMALCOMMENTS in get_animal_data when publisher_use_comments is on
        notes = utils.nulltostr(an["WEBSITEMEDIANOTES"])
        # Add any extra text as long as this isn't a courtesy listing
        if an["ISCOURTESY"] != 1: notes += configuration.third_party_publisher_sig(self.dbo)
        # Replace any wp tags used in the notes
        notes = self.replaceAnimalTags(an, notes)
        # Escape carriage returns
        cr = ""
        if crToBr: 
            cr = "<br />"
        if crToHE:
            cr = "&#10;"
        notes = notes.replace("\r\n", cr)
        notes = notes.replace("\r", cr)
        notes = notes.replace("\n", cr)
        # Escape speechmarks
        notes = notes.replace("\"", "\"\"")
        return notes

    def getLastPublishedDate(self, animalid):
        """
        Returns the last date animalid was sent to the current publisher
        """
        return db.query_date(self.dbo, "SELECT SentDate FROM animalpublished WHERE AnimalID = %d AND PublishedTo = '%s'" % (animalid, self.publisherKey))

    def markAnimalPublished(self, animalid, datevalue = None):
        """
        Marks an animal published at the current date/time for this publisher
        animalid:    The animal id to update
        """
        if datevalue is None: datevalue = i18n.now(self.dbo.timezone)
        self.markAnimalUnpublished(animalid)
        db.execute(self.dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) VALUES (%d, '%s', %s)" %
            (animalid, self.publisherKey, db.dd(datevalue)))

    def markAnimalFirstPublished(self, animalid):
        """
        Marks an animal as published to a special "first" publisher - but only if it 
        hasn't been already. This allows the Publishing History to show not only the last
        but the very first time an animal has been published anywhere and effectively
        the date the animal was first made adoptable.
        """
        FIRST_PUBLISHER = "first"
        if 0 == db.query_int(self.dbo, "SELECT COUNT(SentDate) FROM animalpublished WHERE AnimalID = %d AND PUblishedTo = '%s'" % (animalid, FIRST_PUBLISHER)):
            db.execute(self.dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) VALUES (%s, %s, %s)" % (animalid, db.ds(FIRST_PUBLISHER), db.dd(i18n.now(self.dbo.timezone))))

    def markAnimalUnpublished(self, animalid):
        """
        Marks an animal as not published for the current publisher
        """
        db.execute(self.dbo, "DELETE FROM animalpublished WHERE AnimalID = %d AND PublishedTo = '%s'" % (animalid, self.publisherKey))

    def markAnimalsPublished(self, animals, first=False):
        """
        Marks all animals in the set as published at the current date/time
        for the current publisher.
        first: This is an adoptable animal publisher, mark the animal first published for adoption
        """
        batch = []
        inclause = []
        # build a list of IDs and deduplicate them
        for a in animals:
            inclause.append( str(a["ID"]) )
        inclause = set(inclause)
        # build a batch for inserting animalpublished entries into the table
        # and check/mark animals first published
        for i in inclause:
            batch.append( ( int(i), self.publisherKey, i18n.now(self.dbo.timezone) ) )
            if first: self.markAnimalFirstPublished(int(i))
        if len(inclause) == 0: return
        self.dbo.execute("DELETE FROM animalpublished WHERE PublishedTo = '%s' AND AnimalID IN (%s)" % (self.publisherKey, ",".join(inclause)))
        self.dbo.execute_many("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) VALUES (?,?,?)", batch)

    def markAnimalsPublishFailed(self, animals):
        """
        Marks all animals in the set as published at the current date/time
        for the current publisher but with an extra failure message
        """
        batch = []
        inclause = {}
        # build a list of IDs and deduplicate them
        for a in animals:
            m = ""
            if "FAILMESSAGE" in a:
                m = a["FAILMESSAGE"]
            inclause[str(a["ID"])] = m
        # build a batch for inserting animalpublished entries into the table
        for k, v in inclause.iteritems():
            batch.append( ( int(k), self.publisherKey, i18n.now(self.dbo.timezone), v ) )
        if len(inclause) == 0: return
        self.dbo.execute("DELETE FROM animalpublished WHERE PublishedTo = '%s' AND AnimalID IN (%s)" % (self.publisherKey, ",".join(inclause)))
        self.dbo.execute_many("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate, Extra) VALUES (?,?,?,?)", batch)

    def getMatchingAnimals(self):
        a = get_animal_data(self.dbo, self.pc)
        self.log("Got %d matching animals for publishing." % len(a))
        return a

    def saveFile(self, path, contents):
        try:
            f = open(path, "wb")
            f.write(contents)
            f.flush()
            f.close()
        except Exception as err:
            self.logError(str(err), sys.exc_info())

    def initLog(self, publisherKey, publisherName):
        """
        Initialises the log 
        """
        self.publisherKey = publisherKey
        self.publishDateTime = i18n.now(self.dbo.timezone)
        self.publisherName = publisherName
        self.logBuffer = []

    def log(self, msg):
        """
        Logs a message
        """
        self.logBuffer.append(msg)

    def logError(self, msg, ie=None):
        """
        Logs a message to our logger and dumps a stacktrace.
        ie = error info object from sys.exc_info() if available
        """
        self.log("ALERT: %s" % msg)
        al.error(msg, self.publisherName, self.dbo, ie)
        self.alerts += 1

    def logSearch(self, needle):
        """ Does a find on logBuffer """
        return "\n".join(self.logBuffer).find(needle)

    def logSuccess(self, msg):
        """
        Logs a success message to our logger
        """
        self.log("SUCCESS: %s" % msg)
        al.info(msg, self.publisherName, self.dbo)
        self.successes += 1

    def saveLog(self):
        """
        Saves the log to the publishlog table
        """
        plid = db.get_id(self.dbo, "publishlog")
        sql = db.make_insert_sql("publishlog", ( 
            ( "ID", db.di(plid) ), 
            ( "PublishDateTime", db.ddt(self.publishDateTime) ),
            ( "Name", db.ds(self.publisherKey) ),
            ( "Success", db.di(self.successes) ),
            ( "Alerts", db.di(self.alerts) ),
            ( "LogData", db.ds("\n".join(self.logBuffer), False) )
            ))
        db.execute(self.dbo, sql)

    def isImage(self, path):
        """
        Returns True if the path given has a valid image extension
        """
        return path.lower().endswith("jpg") or path.lower().endswith("jpeg")

    def generateThumbnail(self, image, thumbnail):
        """
        Generates a thumbnail 
        image: Path to the image to generate a thumbnail from
        thumbnail: Path to the target thumbnail image
        """
        self.log("generating thumbnail %s -> %s" % ( image, thumbnail ))
        try:
            media.scale_image_file(image, thumbnail, self.pc.thumbnailSize)
        except Exception as err:
            self.logError("Failed scaling thumbnail: %s" % err, sys.exc_info())

    def scaleImage(self, image, scalesize):
        """
        Scales an image. scalesize is the scaleImage publish criteria and
        can either be a resize spec, or it can be one of our old ASM2
        fixed numbers.
        image: The image file
        Empty string = No scaling
        1 = No scaling
        2 = 320x200
        3 = 640x400
        4 = 800x600
        5 = 1024x768
        6 = 300x300
        7 = 95x95
        """
        sizespec = ""
        if scalesize == "" or scalesize == "1": return image
        elif scalesize == "2": sizespec = "320x200"
        elif scalesize == "3": sizespec = "640x400"
        elif scalesize == "4": sizespec = "800x600"
        elif scalesize == "5": sizespec = "1024x768"
        elif scalesize == "6": sizespec = "300x300"
        elif scalesize == "7": sizespec = "95x95"
        else: sizespec = scalesize
        self.log("scaling %s to %s" % ( image, scalesize ))
        try:
            return media.scale_image_file(image, image, sizespec)
        except Exception as err:
            self.logError("Failed scaling image: %s" % err, sys.exc_info())

class FTPPublisher(AbstractPublisher):
    """
    Base class for publishers that rely on FTP
    """
    socket = None
    ftphost = ""
    ftpuser = ""
    ftppassword = ""
    ftpport = 21
    ftproot = ""
    currentDir = ""
    passive = True
    existingImageList = None

    def __init__(self, dbo, publishCriteria, ftphost, ftpuser, ftppassword, ftpport = 21, ftproot = "", passive = True):
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.ftphost = ftphost
        self.ftpuser = ftpuser
        self.ftppassword = self.unxssPass(ftppassword)
        self.ftpport = ftpport
        self.ftproot = ftproot
        self.passive = passive

    def unxssPass(self, s):
        """
        Passwords stored in the config table are subject to XSS escaping, so
        any >, < or & in the password will have been escaped - turn them back again
        """
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&amp;", "&")
        return s

    def openFTPSocket(self):
        """
        Opens an FTP socket to the server and changes to the
        root FTP directory. Returns True if all was well or
        uploading is disabled.
        """
        if not self.pc.uploadDirectly: return True
        if self.ftphost.strip() == "": raise ValueError("No FTP host set")
        self.log("Connecting to %s as %s" % (self.ftphost, self.ftpuser))
        
        try:
            # open it and login
            self.socket = ftplib.FTP(host=self.ftphost, timeout=15)
            self.socket.login(self.ftpuser, self.ftppassword)
            self.socket.set_pasv(self.passive)

            if self.ftproot is not None and self.ftproot != "":
                # If we had an FTP override, try and create the directory
                # before we change to it.
                if MULTIPLE_DATABASES_PUBLISH_FTP is not None:
                    self.mkdir(self.ftproot)
                self.chdir(self.ftproot)

            return True
        except Exception as err:
            self.logError("Failed opening FTP socket (%s->%s): %s" % (self.dbo.database, self.ftphost, err), sys.exc_info())
            return False

    def closeFTPSocket(self):
        if not self.pc.uploadDirectly: return
        try:
            self.socket.quit()
        except:
            pass

    def reconnectFTPSocket(self):
        """
        Reconnects to the FTP server, changing back to the current directory.
        """
        self.closeFTPSocket()
        self.openFTPSocket()
        if not self.currentDir == "":
            self.chdir(self.currentDir)

    def checkFTPSocket(self):
        """
        Called before each upload if publishCriteria.checkSocket is
        set to true. It verifies that the socket is still active
        by running a command. If the command fails, the socket is
        reopened and the current FTP directory is returned to.
        """
        if not self.pc.uploadDirectly: return
        try:
            self.socket.retrlines("LIST", quietcallback)
        except Exception as err:
            self.log("Dead socket (%s), reconnecting" % err)
            self.reconnectFTPSocket()

    def upload(self, filename):
        """
        Uploads a file to the current FTP directory. If a full path
        is given, this throws it away and just uses the name with
        the temporary publishing directory.
        """
        if filename.find(os.sep) != -1: filename = filename[filename.rfind(os.sep) + 1:]
        if not self.pc.uploadDirectly: return
        if not os.path.exists(os.path.join(self.publishDir, filename)): return
        self.log("Uploading: %s" % filename)
        try:
            if self.pc.checkSocket: self.checkFTPSocket()
            # Store the file
            f = open(os.path.join(self.publishDir, filename), "rb")
            self.socket.storbinary("STOR %s" % filename, f, callback=quietcallback)
            f.close()
        except Exception as err:
            self.logError("Failed uploading %s: %s" % (filename, err), sys.exc_info())
            self.log("reconnecting FTP socket to reset state")
            self.reconnectFTPSocket()

    def lsdir(self):
        if not self.pc.uploadDirectly: return []
        try:
            return self.socket.nlst()
        except Exception as err:
            self.logError("list: %s" % err)

    def mkdir(self, newdir):
        if not self.pc.uploadDirectly: return
        self.log("FTP mkdir %s" % newdir)
        try:
            self.socket.mkd(newdir)
        except Exception as err:
            self.log("mkdir %s: already exists (%s)" % (newdir, err))

    def chdir(self, newdir, fromroot = ""):
        if not self.pc.uploadDirectly: return
        self.log("FTP chdir to %s" % newdir)
        try:
            self.socket.cwd(newdir)
            if fromroot == "":
                self.currentDir = newdir
            else:
                self.currentDir = fromroot
        except Exception as err:
            self.logError("chdir %s: %s" % (newdir, err), sys.exc_info())

    def delete(self, filename):
        try:
            self.socket.delete(filename)
        except Exception as err:
            self.log("delete %s: %s" % (filename, err))

    def clearExistingHTML(self):
        try:
            oldfiles = glob.glob(os.path.join(self.publishDir, "*." + self.pc.extension))
            for f in oldfiles:
                os.remove(f)
        except Exception as err:
            self.logError("warning: failed removing %s from filesystem: %s" % (oldfiles, err), sys.exc_info())
        if not self.pc.uploadDirectly: return
        try:
            for f in self.socket.nlst("*.%s" % self.pc.extension):
                if not f.startswith("search"):
                    self.socket.delete(f)
        except Exception as err:
            self.logError("warning: failed deleting from FTP server: %s" % err, sys.exc_info())

    def clearExistingImages(self):
        try:
            oldfiles = glob.glob(os.path.join(self.publishDir, "*.jpg"))
            for f in oldfiles:
                os.remove(f)
        except Exception as err:
            self.logError("warning: failed removing %s from filesystem: %s" % (oldfiles, err), sys.exc_info())
        if not self.pc.uploadDirectly: return
        try:
            for f in self.socket.nlst("*.jpg"):
                self.socket.delete(f)
        except Exception as err:
            self.logError("warning: failed deleting from FTP server: %s" % err, sys.exc_info())

    def cleanup(self, save_log=True):
        """
        Call when the publisher has completed to tidy up.
        """
        self.closeFTPSocket()
        self.deletePublishDirectory()
        if save_log: self.saveLog()
        self.setPublisherComplete()

    def uploadImage(self, a, medianame, imagename):
        """
        Retrieves image with medianame from the DBFS to the publish
        folder and uploads it via FTP with imagename
        """
        try:
            # Check if the image is already on the server if 
            # forceReupload is off and the animal doesn't
            # have any recently changed images
            if not self.pc.forceReupload and a["RECENTLYCHANGEDIMAGES"] == 0:
                if self.existingImageList is None:
                    self.existingImageList = self.lsdir()
                elif imagename in self.existingImageList:
                    self.log("%s: skipping, already on server" % imagename)
                    return
            imagefile = os.path.join(self.publishDir, imagename)
            thumbnail = os.path.join(self.publishDir, "tn_" + imagename)
            dbfs.get_file(self.dbo, medianame, "", imagefile)
            self.log("Retrieved image: %d::%s::%s" % ( a["ID"], medianame, imagename ))
            # If scaling is on, do it
            if self.pc.scaleImages > 1:
                self.scaleImage(imagefile, self.pc.scaleImages)
            # If thumbnails are on, do it
            if self.pc.thumbnails:
                self.generateThumbnail(imagefile, thumbnail)
            # Upload
            if self.pc.uploadDirectly:
                self.upload(imagefile)
                if self.pc.thumbnails:
                    self.upload(thumbnail)
        except Exception as err:
            self.logError("Failed uploading image %s: %s" % (medianame, err), sys.exc_info())
            return 0

    def uploadImages(self, a, copyWithMediaIDAsName = False, limit = 0):
        """
        Uploads all the images for an animal as sheltercode-X.jpg if
        upload all is on, or just sheltercode.jpg if upload all is off.
        If copyWithMediaIDAsName is on, it uploads the preferred
        image again and calls it mediaID.jpg (for compatibility with
        older templates).
        Even if uploadDirectly is off, we still pull the images to the
        publish folder.
        If limit is set to zero and uploadAll is on, all images
        are uploaded. If uploadAll is off, only the preferred
        image is uploaded.
        Images with the ExcludeFromPublish flag set are ignored.
        """
        # The first image is always the preferred
        totalimages = 0
        animalcode = a["SHELTERCODE"]
        animalweb = a["WEBSITEMEDIANAME"]
        if animalweb is None or animalweb == "": return totalimages
        # If we've got HTML entities in our sheltercode, it's going to
        # mess up filenames. Use the animalid instead.
        if animalcode.find("&#") != -1:
            animalcode = str(a["ID"])
        # Name it sheltercode-1.jpg or sheltercode.jpg if uploadall is off
        imagename = animalcode + ".jpg"
        if self.pc.uploadAllImages:
            imagename = animalcode + "-1.jpg"
        # If we're forcing reupload or the animal has
        # some recently changed images, remove all the images
        # for this animal before doing anything.
        if self.pc.forceReupload or a["RECENTLYCHANGEDIMAGES"] > 0:
            if self.existingImageList is None:
                self.existingImageList = self.lsdir()
            for ei in self.existingImageList:
                if ei.startswith(animalcode):
                    self.log("delete: %s" % ei)
                    self.delete(ei)
        # Save it to the publish directory
        totalimages = 1
        self.uploadImage(a, animalweb, imagename)
        # If we're saving a copy with the media ID, do that too
        if copyWithMediaIDAsName:
            self.uploadImage(a, animalweb, animalweb)
        # If upload all is set, we need to grab the rest of
        # the animal's images upto the limit. If the limit is
        # zero, we upload everything.
        if self.pc.uploadAllImages:
            mrecs = media.get_image_media(self.dbo, media.ANIMAL, a["ID"], True)
            self.log("Animal has %d media files (%d recently changed)" % (len(mrecs), a["RECENTLYCHANGEDIMAGES"]))
            for m in mrecs:
                # Ignore the main media since we used that
                if m["MEDIANAME"] == animalweb:
                    continue
                # Have we hit our limit?
                if totalimages == limit:
                    return totalimages
                totalimages += 1
                # Get the image
                otherpic = m["MEDIANAME"]
                imagename = "%s-%d.jpg" % ( animalcode, totalimages )
                self.uploadImage(a, otherpic, imagename)
        return totalimages


