
import asm3.animal
import asm3.configuration
import asm3.i18n
import asm3.lookups
import asm3.onlineform
import asm3.smcom
import asm3.template
import asm3.users
import asm3.utils
import asm3.wordprocessor

from .base import FTPPublisher, PublishCriteria, get_animal_data, is_animal_adoptable
from asm3.sitedefs import BASE_URL, SERVICE_URL
from asm3.typehints import Database, ResultRow, Results

import math
import os
import sys

def get_adoptable_animals(dbo: Database, style="", speciesid=0, animaltypeid=0, locationid=0, underweeks=0, overweeks=0) -> str:
    """ Returns a page of adoptable animals.
    style: The HTML publishing template to use
    speciesid: 0 for all species, or a specific one
    animaltypeid: 0 for all animal types or a specific one
    locationid: 0 for all internal locations or a specific one
    underweeks: Only return animals aged under this many weeks (0 to ignore)
    overweeks: Only return animals aged over this many weeks (0 to ignore)
    """
    animals = get_animal_data(dbo, include_additional_fields=True)
    return animals_to_page(dbo, animals, style=style, speciesid=speciesid, animaltypeid=animaltypeid, locationid=locationid, \
        underweeks=underweeks, overweeks=overweeks)

def get_adopted_animals(dbo: Database, daysadopted=0, style="", speciesid=0, animaltypeid=0, orderby="adopted_desc") -> str:
    """ Returns a page of adopted animals.
    daysadopted: The number of days the animals have been adopted
    style: The HTML publishing template to use
    speciesid: 0 for all species, or a specific one
    animaltypeid: 0 for all animal types or a specific one
    """
    if daysadopted == 0: daysadopted = 30
    if orderby == "": orderby = "adopted_desc"
    orderby = get_orderby_const(orderby)
    animals = dbo.query(asm3.animal.get_animal_query(dbo) + \
        " WHERE a.IsNotAvailableForAdoption = 0 AND a.ActiveMovementType = 1 AND " \
        "a.ActiveMovementDate >= ? AND a.DeceasedDate Is Null AND a.NonShelterAnimal = 0 " \
        "ORDER BY %s" % orderby, [ dbo.today(daysadopted * -1)] )
    return animals_to_page(dbo, animals, style=style, speciesid=speciesid, animaltypeid=animaltypeid)

def get_deceased_animals(dbo: Database, daysdeceased=0, style="", speciesid=0, animaltypeid=0, orderby="deceased_desc") -> str:
    """ Returns a page of deceased animals.
    daysdeceased: The number of days the animals have been deceased
    style: The HTML publishing template to use
    speciesid: 0 for all species, or a specific one
    animaltypeid: 0 for all animal types or a specific one
    """
    if daysdeceased == 0: daysdeceased = 30
    if orderby == "": orderby = "deceased_desc"
    orderby = get_orderby_const(orderby)
    animals = dbo.query(asm3.animal.get_animal_query(dbo) + \
        " WHERE a.IsNotAvailableForAdoption = 0 AND a.DeceasedDate Is Not Null AND a.DeceasedDate >= ? AND a.NonShelterAnimal = 0 AND a.DiedOffShelter = 0 "
        "ORDER BY %s" % orderby, [ dbo.today(daysdeceased * -1)] )
    return animals_to_page(dbo, animals, style=style, speciesid=speciesid, animaltypeid=animaltypeid)

def get_flagged_animals(dbo: Database, style="", speciesid=0, animaltypeid=0, flag="", allanimals=0, orderby="entered_desc") -> str:
    """ Returns a page of animals with a particular flag.
    style: The HTML publishing template to use
    speciesid: 0 for all species, or a specific one
    animaltypeid: 0 for all animal types or a specific one
    flag: The flag to show for
    allanimals: 0 = only search shelter animals, 1 = all animals
    """
    afilter = ""
    if allanimals == 0: afilter = "a.Archived = 0 AND "
    if orderby == "": orderby = "entered_desc"
    orderby = get_orderby_const(orderby)
    animals = dbo.query(asm3.animal.get_animal_query(dbo) + " WHERE " + afilter + "a.AdditionalFlags LIKE ? ORDER BY " + orderby, 
        ["%%%s|%%" % flag],
        limit = asm3.configuration.record_search_limit(dbo))
    return animals_to_page(dbo, animals, style=style, speciesid=speciesid, animaltypeid=animaltypeid)

def get_held_animals(dbo: Database, style="", speciesid=0, animaltypeid=0, orderby="entered_desc") -> str:
    """ Returns a page of currently held animals.
    style: The HTML publishing template to use
    speciesid: 0 for all species, or a specific one
    animaltypeid: 0 for all animal types or a specific one
    """
    if orderby == "": orderby = "entered_desc"
    orderby = get_orderby_const(orderby)
    animals = dbo.query(asm3.animal.get_animal_query(dbo) + \
        " WHERE a.Archived = 0 AND a.IsHold = 1 "
        "ORDER BY %s" % orderby)
    return animals_to_page(dbo, animals, style=style, speciesid=speciesid, animaltypeid=animaltypeid)

def get_stray_animals(dbo: Database, style="", speciesid=0, animaltypeid=0, orderby="entered_desc") -> str:
    """ Returns a page of stray animals in care.
    style: The HTML publishing template to use
    speciesid: 0 for all species, or a specific one
    animaltypeid: 0 for all animal types or a specific one
    """
    if orderby == "": orderby = "entered_desc"
    orderby = get_orderby_const(orderby)
    animals = dbo.query(asm3.animal.get_animal_query(dbo) + \
        " WHERE a.Archived = 0 AND a.EntryTypeID = 2 "
        "ORDER BY %s" % orderby)
    return animals_to_page(dbo, animals, style=style, speciesid=speciesid, animaltypeid=animaltypeid)

def get_orderby_const(c: str) -> str:
    """
    Returns an ORDER BY clause for a given constant
    Used by the methods above that are called by the html_X_animals service methods.
    """
    CLAUSES = {
        "adopted_asc":      "a.ActiveMovementDate",
        "adopted_desc":     "a.ActiveMovementDate DESC",
        "code_asc":         "a.ShelterCode",
        "code_desc":        "a.ShelterCode DESC",
        "created_asc":      "a.CreatedDate",
        "created_desc":     "a.CreatedDate DESC",
        "dateofbirth_asc":  "a.DateOfBirth",
        "dateofbirth_desc": "a.DateOfBirth DESC",
        "deceased_asc":     "a.DeceasedDate",
        "deceased_desc":    "a.DeceasedDate DESC",
        "entered_asc":      "a.MostRecentEntryDate",
        "entered_desc":     "a.MostRecentEntryDate DESC",
        "holduntil_asc":    "a.HoldUntilDate",
        "holduntil_desc":   "a.HoldUntilDate DESC",
        "lastchanged_asc":  "a.LastChangedDate", 
        "lastchanged_desc": "a.LastChangedDate DESC",
        "litterid_asc":     "a.AcceptanceNumber",
        "litterid_desc":    "a.AcceptanceNumber DESC",
        "name_asc":         "a.AnimalName",
        "name_desc":        "a.AnimalName DESC"
    }
    if c in CLAUSES:
        return CLAUSES[c]
    return "a.DateBroughtIn"

def animals_to_page(dbo: Database, animals: Results, style="", speciesid=0, animaltypeid=0, locationid=0, underweeks=0, overweeks=0) -> str:
    """ Returns a page of animals.
    animals: A resultset containing animal records
    style: The HTML publishing template to use
    speciesid: 0 for all species, or a specific one
    animaltypeid: 0 for all animal types or a specific one
    locationid: 0 for all internal locations or a specific one
    underweeks: Only return animals aged under weeks, 0 = ignore
    overweeks: Only return animals aged over weeks, 0 = ignore
    """
    # Get the specified template
    if style == "":
        head, body, foot = get_animal_view_template(dbo)
    else:
        head, body, foot = asm3.template.get_html_template(dbo, style)
        if head == "":
            raise asm3.utils.ASMError(f"template {style} does not exist")
    # Substitute the header and footer tags
    org_tags = asm3.wordprocessor.org_tags(dbo, "system")
    head = asm3.wordprocessor.substitute_tags(head, org_tags, True, "$$", "$$")
    foot = asm3.wordprocessor.substitute_tags(foot, org_tags, True, "$$", "$$")
    # Substitute the special ADOPTABLEJSURL token if present so animalviewadoptable can be tested/previewed
    body = body.replace("$$ADOPTABLEJSURL$$", "%s?method=animal_view_adoptable_js&account=%s" % (SERVICE_URL, dbo.database))
    # Run through each animal and generate body sections
    bodies = []
    for a in animals:
        if speciesid > 0 and a.SPECIESID != speciesid: continue
        if animaltypeid > 0 and a.ANIMALTYPEID != animaltypeid: continue
        if locationid > 0 and a.SHELTERLOCATION != locationid: continue
        if underweeks > 0 and a.DATEOFBIRTH < dbo.today(offset=underweeks * -7): continue
        if overweeks > 0 and a.DATEOFBIRTH >= dbo.today(offset=overweeks * -7): continue
        # Translate website media name to the service call for images
        if asm3.smcom.active():
            a.WEBSITEMEDIANAME = "%s?account=%s&method=animal_image&animalid=%d" % (SERVICE_URL, dbo.database, a.ID)
        else:
            a.WEBSITEMEDIANAME = "%s?method=animal_image&animalid=%d" % (SERVICE_URL, a.ID)
        # Generate tags for this row
        tags = asm3.wordprocessor.animal_tags_publisher(dbo, a)
        tags = asm3.wordprocessor.append_tags(tags, org_tags)
        # Add extra tags for websitemedianame2-8 if they exist
        if a.WEBSITEIMAGECOUNT > 1: tags["WEBMEDIAFILENAME2"] = "%s&seq=2" % a.WEBSITEMEDIANAME
        if a.WEBSITEIMAGECOUNT > 2: tags["WEBMEDIAFILENAME3"] = "%s&seq=3" % a.WEBSITEMEDIANAME
        if a.WEBSITEIMAGECOUNT > 3: tags["WEBMEDIAFILENAME4"] = "%s&seq=4" % a.WEBSITEMEDIANAME
        if a.WEBSITEIMAGECOUNT > 4: tags["WEBMEDIAFILENAME5"] = "%s&seq=5" % a.WEBSITEMEDIANAME
        if a.WEBSITEIMAGECOUNT > 5: tags["WEBMEDIAFILENAME6"] = "%s&seq=6" % a.WEBSITEMEDIANAME
        if a.WEBSITEIMAGECOUNT > 6: tags["WEBMEDIAFILENAME7"] = "%s&seq=7" % a.WEBSITEMEDIANAME
        if a.WEBSITEIMAGECOUNT > 7: tags["WEBMEDIAFILENAME8"] = "%s&seq=8" % a.WEBSITEMEDIANAME
        # Set the description
        if asm3.configuration.publisher_use_comments(dbo):
            a.WEBSITEMEDIANOTES = a.ANIMALCOMMENTS
        # Add extra publishing text
        notes = asm3.utils.nulltostr(a.WEBSITEMEDIANOTES)
        notes += asm3.configuration.third_party_publisher_sig(dbo)
        tags["WEBMEDIANOTES"] = notes 
        tags["WEBSITEMEDIANOTES"] = notes # Compatibility, both are valid in asm3.wordprocessor.py
        bodies.append(asm3.wordprocessor.substitute_tags(body, tags, True, "$$", "$$"))
    return "%s\n%s\n%s" % (head,"\n".join(bodies), foot)
    
def get_animal_view(dbo: Database, animalid: int, style="animalview") -> str:
    """ Constructs the animal view page to the animalview (or another specified) style/template. """
    a = dbo.first_row(get_animal_data(dbo, animalid=animalid, include_additional_fields=True, strip_personal_data=False))
    # The animal is adoptable, use the specified template
    if a is not None and is_animal_adoptable(dbo, a):
        head, body, foot = asm3.template.get_html_template(dbo, style)
        if head == "":
            head, body, foot = get_animal_view_template(dbo)
    else:
        # The animal is not adoptable. 
        # If there is no animalviewnotadoptable template, produce an error
        head, body, foot = asm3.template.get_html_template(dbo, "animalviewnotadoptable")
        if head == "": raise asm3.utils.ASMPermissionError("animal is not adoptable")
        # Otherwise, load the animal record so we can generate the animalviewnotadoptable page
        a = asm3.animal.get_animal(dbo, animalid)
    if head == "":
        head = "<!DOCTYPE html>\n<html>\n<head>\n<title>$$SHELTERCODE$$ - $$ANIMALNAME$$</title></head>\n<body>"
        body = "<h2>$$SHELTERCODE$$ - $$ANIMALNAME$$</h2><p><img src='$$WEBMEDIAFILENAME$$'/></p><p>$$WEBMEDIANOTES$$</p>"
        foot = "</body>\n</html>"
    if asm3.smcom.active():
        a.WEBSITEMEDIANAME = "%s?account=%s&method=animal_image&animalid=%d" % (SERVICE_URL, dbo.database, animalid)
    else:
        a.WEBSITEMEDIANAME = "%s?method=animal_image&animalid=%d" % (SERVICE_URL, animalid)
    s = head + body + foot
    tags = asm3.wordprocessor.animal_tags_publisher(dbo, a)
    tags = asm3.wordprocessor.append_tags(tags, asm3.wordprocessor.org_tags(dbo, "system"))
    # Add extra tags for websitemedianame2-10 if they exist
    for x in range(2, 11):
        if a.WEBSITEIMAGECOUNT > x-1: tags["WEBMEDIAFILENAME%d" % x] = "%s&seq=%d" % (a.WEBSITEMEDIANAME, x)
    # Add extra publishing text
    notes = asm3.utils.nulltostr(a.WEBSITEMEDIANOTES)
    notes += asm3.configuration.third_party_publisher_sig(dbo)
    tags["WEBMEDIANOTES"] = notes 
    tags["WEBSITEMEDIANOTES"] = notes 
    s = asm3.wordprocessor.substitute_tags(s, tags, True, "$$", "$$")
    return s

def get_animal_view_adoptable_html(dbo: Database) -> str:
    """ Returns an HTML wrapper around get_animal_view_adoptable_js - uses
        a template called animalviewadoptable if it exists. 
    """
    head, body, foot = asm3.template.get_html_template(dbo, "animalviewadoptable")
    if head == "":
        head = "<!DOCTYPE html>\n<html>\n<head>\n<title>Adoptable Animals</title>\n" \
            "<meta charset='utf-8'>\n" \
            "<style>\n" \
            ".asm3-adoptable-item { max-width: 200px; font-family: sans-serif; }\n" \
            ".asm3-adoptable-link { font-weight: bold; }\n" \
            ".asm3-adoptable-tag-agegroup, .asm3-adoptable-tag-size { display: none; }\n" \
            "</style>\n" \
            "</head>\n<body>\n"
        body = "<div id=\"asm3-adoptables\"></div>\n" \
            "<script>\n" \
            "asm3_adoptable_filters = \"sex breed agegroup size species goodwith where\";\n" \
            "asm3_adoptable_iframe = true;\n" \
            "asm3_adoptable_iframe_fixed = false; // fixed == true does not work with multi-photos/scrolling\n" \
            "asm3_adoptable_iframe_closeonback = true; // close the popup pane when the user navigates back\n" \
            "</script>\n" \
            "<script src=\"$$ADOPTABLEJSURL$$\"></script>"
        foot = "</body>\n</html>"
    body = body.replace("$$ADOPTABLEJSURL$$", "%s?method=animal_view_adoptable_js&account=%s" % (SERVICE_URL, dbo.database))
    return "%s\n%s\n%s" % (head, body, foot)

def get_animal_view_adoptable_js(dbo: Database) -> str:
    """ Returns js that outputs adoptable animals into a host div """
    js = asm3.utils.read_text_file("%s/static/js/animal_view_adoptable.js" % dbo.installpath)
    # Retrieve the animals, update bio to convert line breaks to break tags
    pc = PublishCriteria(asm3.configuration.publisher_presets(dbo))
    rows = get_animal_data(dbo, pc, include_additional_fields = True, strip_personal_data = True)
    for r in rows:
        if r.ANIMALCOMMENTS is not None: r.ANIMALCOMMENTS = r.ANIMALCOMMENTS.replace("\n", "<br>")
        if r.WEBSITEMEDIANOTES is not None: r.WEBSITEMEDIANOTES = r.WEBSITEMEDIANOTES.replace("\n", "<br>")
    # inject adoptable animals, account and base url
    js = js.replace("{TOKEN_ACCOUNT}", dbo.database)
    js = js.replace("{TOKEN_BASE_URL}", BASE_URL)
    js = js.replace("\"{TOKEN_ADOPTABLES}\"", asm3.utils.json(rows))
    return js

def get_animal_view_template(dbo: Database) -> str:
    """ Returns a tuple of the header, body and footer for the animalview template """
    head, body, foot = asm3.template.get_html_template(dbo, "animalview")
    if head == "":
        head = "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n<title>$$SHELTERCODE$$ - $$ANIMALNAME$$</title></head>\n<body>"
        body = "<h2>$$SHELTERCODE$$ - $$ANIMALNAME$$</h2><p><img src='$$WEBMEDIAFILENAME$$'/></p><p>$$WEBMEDIANOTES$$</p>"
        foot = "</body>\n</html>"
    return ( head, body, foot )

class HTMLPublisher(FTPPublisher):
    """
    Handles publishing to the internet via static HTML files to 
    an FTP server.
    """
    navbar = ""
    totalAnimals = 0
    user = "cron"

    def __init__(self, dbo: Database, publishCriteria: PublishCriteria, user: str) -> None:
        l = dbo.locale
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            asm3.configuration.ftp_host(dbo), asm3.configuration.ftp_user(dbo), asm3.configuration.ftp_password(dbo),
            asm3.configuration.ftp_port(dbo), asm3.configuration.ftp_root(dbo), asm3.configuration.ftp_passive(dbo))
        self.user = user
        self.initLog("html", asm3.i18n._("HTML/FTP Publisher", l))

    def escapePageName(self, s: str) -> str:
        suppress = [ " ", "(", ")", "/", "\\", "!", "?", "*" ]
        for x in suppress:
            s = s.replace(x, "_")
        return s

    def getHeader(self) -> str:
        header, body, footer = asm3.template.get_html_template(self.dbo, self.pc.style)
        if header == "":
            header = """<!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <title>Animals Available For Adoption</title>
            </head>
            <body>
            <p>$$NAV$$</p>
            <table width="100%%">
            """
        return header

    def getFooter(self) -> str:
        header, body, footer = asm3.template.get_html_template(self.dbo, self.pc.style)
        if footer == "":
            footer = "</table></body></html>"
        return footer

    def getBody(self) -> str:
        header, body, footer = asm3.template.get_html_template(self.dbo, self.pc.style)
        if body == "":
            body = "<tr><td><img height=200 width=320 src=$$IMAGE$$></td>" \
                "<td><b>$$ShelterCode$$ - $$AnimalName$$</b><br>" \
                "$$BreedName$$ $$SpeciesName$$ aged $$Age$$<br><br>" \
                "<b>Details</b><br><br>$$WebMediaNotes$$<hr></td></tr>"
        return body

    def substituteHFTag(self, searchin: str, page: str, user: str, title: str = "") -> str:
        """
        Substitutes special header and footer tokens in searchin. page
        contains the current page number.
        """
        output = searchin
        nav = self.navbar.replace("<a href=\"%d.%s\">%d</a>" % (page, self.pc.extension, page), str(page))
        dateportion = asm3.i18n.python2display(self.locale, asm3.i18n.now(self.dbo.timezone))
        timeportion = asm3.i18n.format_time(asm3.i18n.now(self.dbo.timezone))
        if page != -1:
            output = output.replace("$$NAV$$", nav)
        else:
            output = output.replace("$$NAV$$", "")
        output = output.replace("$$TITLE$$", title)
        output = output.replace("$$TOTAL$$", str(self.totalAnimals))
        output = output.replace("$$DATE$$", dateportion)
        output = output.replace("$$TIME$$", timeportion)
        output = output.replace("$$DATETIME$$", "%s %s" % (dateportion, timeportion))
        output = output.replace("$$VERSION$$", asm3.i18n.get_version())
        output = output.replace("$$REGISTEREDTO$$", asm3.configuration.organisation(self.dbo))
        output = output.replace("$$USER$$", "%s (%s)" % (user, asm3.users.get_real_name(self.dbo, user)))
        output = output.replace("$$ORGNAME$$", asm3.configuration.organisation(self.dbo))
        output = output.replace("$$ORGADDRESS$$", asm3.configuration.organisation_address(self.dbo))
        output = output.replace("$$ORGTEL$$", asm3.configuration.organisation_telephone(self.dbo))
        output = output.replace("$$ORGEMAIL$$", asm3.configuration.email(self.dbo))
        return output

    def substituteBodyTags(self, searchin: str, a: ResultRow) -> str:
        """
        Substitutes any tags in the body for animal data
        """
        tags = asm3.wordprocessor.animal_tags_publisher(self.dbo, a)
        tags["TotalAnimals"] = str(self.totalAnimals)
        tags["IMAGE"] = str(a["WEBSITEMEDIANAME"])
        # Note: WEBSITEMEDIANOTES becomes ANIMALCOMMENTS in get_animal_data when publisher_use_comments is on
        notes = asm3.utils.nulltostr(a["WEBSITEMEDIANOTES"])
        # Add any extra text
        notes += asm3.configuration.third_party_publisher_sig(self.dbo)
        tags["WEBMEDIANOTES"] = notes 
        tags["WEBSITEMEDIANOTES"] = notes 
        output = asm3.wordprocessor.substitute_tags(searchin, tags, True, "$$", "$$")
        return output

    def writeJavaScript(self, animals: Results) -> str:
        # Remove original owner and other sensitive info from javascript database
        # before saving it
        for a in animals:
            for k in a.keys():
                if k.startswith("ORIGINALOWNER") or k.startswith("BROUGHTINBY") \
                    or k.startswith("RESERVEDOWNER") or k.startswith("CURRENTOWNER") \
                    or k == "DISPLAYLOCATION" or k == "DISPLAYLOCATIONAME" or k == "OUTCOMEQUALIFIER":
                    a[k] = ""
        self.saveFile(os.path.join(self.publishDir, "db.js"), "publishDate='%s';animals=%s;" % (
            asm3.i18n.python2display(self.locale, asm3.i18n.now(self.dbo.timezone)), asm3.utils.json(animals)))
        if self.pc.uploadDirectly:
            self.log("Uploading javascript database...")
            self.upload("db.js")
            self.log("Uploaded javascript database.")

    def run(self) -> None:
        self.setLastError("")
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setStartPublishing()
        self.log("Outputting generated pages to %s" % self.publishDir)
        self.executePages()
        if self.pc.htmlByChildAdult or self.pc.htmlBySpecies:
            self.executeAgeSpecies(self.user, self.pc.htmlByChildAdult, self.pc.htmlBySpecies)
        if self.pc.htmlByType:
            self.executeType(self.user)
        if self.pc.outputAdopted:
            self.executeAdoptedPage()
        if self.pc.outputDeceased:
            self.executeDeceasedPage()
        if self.pc.outputForms:
            self.executeFormsPage()
        if self.pc.outputRSS:
            self.executeRSS()
        self.cleanup()
        self.resetPublisherProgress()

    def executeAdoptedPage(self) -> None:
        """
        Generates and uploads the page of recently adopted animals
        """
        self.log("Generating adopted animals page...")

        user = self.user
        thisPage = ""
        thisPageName = "adopted.%s" % self.pc.extension
        totalAnimals = 0
        l = self.dbo.locale

        try:
            cutoff = asm3.i18n.subtract_days(asm3.i18n.now(self.dbo.timezone), self.pc.outputAdoptedDays)
            orderby = "a.AnimalName"
            if self.pc.order == 0: orderby = "a.ActiveMovementDate"
            elif self.pc.order == 1: orderby = "a.ActiveMovementDate DESC"
            elif self.pc.order == 2: orderby = "a.AnimalName"
            animals = self.dbo.query(asm3.animal.get_animal_query(self.dbo) + \
                " WHERE a.IsNotAvailableForAdoption = 0 AND a.ActiveMovementType = 1 AND " \
                "a.ActiveMovementDate >= %s AND a.DeceasedDate Is Null AND a.NonShelterAnimal = 0 "
                "ORDER BY %s" % (self.dbo.sql_date(cutoff), orderby))
            totalAnimals = len(animals)
            header = self.substituteHFTag(self.getHeader(), -1, user, asm3.i18n._("Recently adopted", l))
            footer = self.substituteHFTag(self.getFooter(), -1, user, asm3.i18n._("Recently adopted", l))
            body = self.getBody()
            thisPage = header
        except Exception as err:
            self.setLastError("Error setting up adopted page: %s" % err)
            self.logError("Error setting up adopted page: %s" % err, sys.exc_info())
            return

        anCount = 0
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                # upload images for this animal to our current FTP
                self.uploadImages(an, True)

                # Add to the page
                thisPage += self.substituteBodyTags(body, an)
                self.log("Finished processing: %s" % an["SHELTERCODE"])

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Append the footer, flush and upload the page
        thisPage += footer
        self.log("Saving page to disk: %s (%d bytes)" % (thisPageName, len(thisPage)))
        self.saveFile(os.path.join(self.publishDir, thisPageName), thisPage)
        self.log("Saved page to disk: %s" % thisPageName)
        if self.pc.uploadDirectly:
            self.log("Uploading page: %s" % thisPageName)
            self.upload(thisPageName)
            self.log("Uploaded page: %s" % thisPageName)

    def executeDeceasedPage(self) -> None:
        """
        Generates and uploads the page of recently deceased animals
        """
        self.log("Generating deceased animals page...")

        user = self.user
        thisPage = ""
        thisPageName = "deceased.%s" % self.pc.extension
        totalAnimals = 0
        l = self.dbo.locale

        try:
            cutoff = asm3.i18n.subtract_days(asm3.i18n.now(self.dbo.timezone), self.pc.outputAdoptedDays)
            orderby = "a.AnimalName"
            if self.pc.order == 0: orderby = "a.DeceasedDate"
            elif self.pc.order == 1: orderby = "a.DeceasedDate DESC"
            elif self.pc.order == 2: orderby = "a.AnimalName"
            animals = self.dbo.query(asm3.animal.get_animal_query(self.dbo) + \
                " WHERE a.IsNotAvailableForAdoption = 0 AND a.DeceasedDate Is Not Null AND " \
                "a.DeceasedDate >= %s AND a.NonShelterAnimal = 0 AND a.DiedOffShelter = 0 " \
                "ORDER BY %s" % (self.dbo.sql_date(cutoff), orderby))
            totalAnimals = len(animals)
            header = self.substituteHFTag(self.getHeader(), -1, user, asm3.i18n._("Recently deceased", l))
            footer = self.substituteHFTag(self.getFooter(), -1, user, asm3.i18n._("Recently deceased", l))
            body = self.getBody()
            thisPage = header
        except Exception as err:
            self.setLastError("Error setting up deceased page: %s" % err)
            self.logError("Error setting up deceased page: %s" % err, sys.exc_info())
            return

        anCount = 0
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                # upload images for this animal to our current FTP
                self.uploadImages(an, True)

                # Add to the page
                thisPage += self.substituteBodyTags(body, an)
                self.log("Finished processing: %s" % an["SHELTERCODE"])

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Append the footer, flush and upload the page
        thisPage += footer
        self.log("Saving page to disk: %s (%d bytes)" % (thisPageName, len(thisPage)))
        self.saveFile(os.path.join(self.publishDir, thisPageName), thisPage)
        self.log("Saved page to disk: %s" % thisPageName)
        if self.pc.uploadDirectly:
            self.log("Uploading page: %s" % thisPageName)
            self.upload(thisPageName)
            self.log("Uploaded page: %s" % thisPageName)

    def executeFormsPage(self) -> None:
        """
        Generates and uploads the page of online forms
        """
        self.log("Generating online forms page...")

        thisPageName = "forms.%s" % self.pc.extension
        thisPage = ""

        try:
            forms = asm3.onlineform.get_onlineforms(self.dbo)
            thisPage = "<html><head><title>Online Forms</title></head><body>"
            thisPage += "<h2>Online Forms</h2>"
            account = ""
            if asm3.smcom.active():
                account = "account=%s&" % self.dbo.database 
            for f in forms:
                thisPage += "<p><a target='_blank' href='%s?%smethod=online_form_html&formid=%d'>%s</a></p>" % (SERVICE_URL, account, f["ID"], f["NAME"])
            thisPage += "</body></html>"
        except Exception as err:
            self.setLastError("Error creating forms page: %s" % err)
            self.logError("Error creating forms page: %s" % err, sys.exc_info())
            return

        # Flush and upload the page
        self.log("Saving page to disk: %s (%d bytes)" % (thisPageName, len(thisPage)))
        self.saveFile(os.path.join(self.publishDir, thisPageName), thisPage)
        self.log("Saved page to disk: %s" % thisPageName)
        if self.pc.uploadDirectly:
            self.log("Uploading page: %s" % thisPageName)
            self.upload(thisPageName)
            self.log("Uploaded page: %s" % thisPageName)

    def executeAgeSpecies(self, user: str, childadult: bool = True, species: bool = True) -> None:
        """
        Publisher that puts animals on pages by age and species
        childadult: True if we should split up pages by animals under/over 6 months 
        species: True if we should split up pages by species
        """
        self.log("HTMLPublisher (age/species pages) starting...")

        l = self.dbo.locale
        normHeader = self.getHeader()
        normFooter = self.getFooter()
        body = self.getBody()
        header = self.substituteHFTag(normHeader, 0, user, asm3.i18n._("Available for adoption", l))
        footer = self.substituteHFTag(normFooter, 0, user, asm3.i18n._("Available for adoption", l))

        # Calculate the number of days old an animal has to be to
        # count as an adult
        childAdultSplitDays = self.pc.childAdultSplit * 7

        # Open FTP socket, bail if it fails
        if not self.openFTPSocket():
            self.setLastError("Failed opening FTP socket.")
            return

        try:
            animals = self.getMatchingAnimals()
            self.totalAnimals = len(animals)

            anCount = 0
            pages = {}

            # Create default pages for every possible permutation
            defaultpages = []
            if childadult and species:
                spec = asm3.lookups.get_species(self.dbo)
                for sp in spec:
                    defaultpages.append("adult%s" % sp["SPECIESNAME"])
                    defaultpages.append("baby%s" % sp["SPECIESNAME"])
            elif childadult:
                defaultpages = [ "adult", "baby" ]
            elif species:
                spec = asm3.lookups.get_species(self.dbo)
                for sp in spec:
                    defaultpages.append(sp["SPECIESNAME"])
            for dp in defaultpages:
                pages["%s.%s" % (dp, self.pc.extension)] = header

            # Create an all page
            allpage = "all.%s" % self.pc.extension
            pages[allpage] = header

        except Exception as err:
            self.logError("Error setting up page: %s" % err, sys.exc_info())
            self.setLastError("Error setting up page: %s" % err)
            return

        for an in animals:
            try:
                anCount += 1

                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, self.totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                # upload all images for this animal to our current FTP
                self.uploadImages(an, True)
                
                # Calculate the new page name
                pagename = ".%s" % self.pc.extension
                if species:
                    pagename = "%s%s" % (an["SPECIESNAME"], pagename)
                if childadult:
                    days = asm3.i18n.date_diff_days(an["DATEOFBIRTH"], asm3.i18n.now(self.dbo.timezone))
                    if days < childAdultSplitDays:
                        pagename = "baby%s" % pagename
                    else:
                        pagename = "adult%s" % pagename

                # Does this page exist?
                if pagename not in pages:
                    # No, create it and add the header
                    page = header
                else:
                    page = pages[pagename]

                # Add this item to the page
                page += self.substituteBodyTags(body, an)
                pages[pagename] = page
                self.log("%s -> %s" % (an["SHELTERCODE"], pagename))

                # Add this item to our magic "all" page
                page = pages[allpage]
                page += self.substituteBodyTags(body, an)
                pages[allpage] = page
                
                # Mark success in the log
                self.log("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        # Upload the pages
        for k, v in pages.items():
            self.log("Saving page to disk: %s (%d bytes)" % (k, len(v + footer)))
            self.saveFile(os.path.join(self.publishDir, self.escapePageName(k)), v + footer)
            self.log("Saved page to disk: %s" % k)
            if self.pc.uploadDirectly:
                self.log("Uploading page: %s" % k)
                self.upload(self.escapePageName(k))
                self.log("Uploaded page: %s" % k)

    def executePages(self) -> None:
        """
        Publisher based on assigning animals to pages.
        """

        self.log("HTMLPublisher (numbered pages) starting...")

        user = self.user
        normHeader = self.getHeader()
        normFooter = self.getFooter()
        body = self.getBody()
        l = self.dbo.locale

        # Open FTP socket, bail if it fails
        if not self.openFTPSocket():
            self.setLastError("Failed opening FTP socket.")
            return

        try:
            animals = self.getMatchingAnimals()
            self.totalAnimals = len(animals)
            noPages = 0
            animalsPerPage = self.pc.animalsPerPage
            pages = {}

            # Calculate pages required
            if self.totalAnimals <= animalsPerPage:
                noPages = 1
            else:
                noPages = math.ceil(float(self.totalAnimals) / float(animalsPerPage))

            # Page navigation bar
            if noPages > 1:
                self.navbar = ""
                for i in range(1, int(noPages + 1)):
                    self.navbar += "<a href=\"%d.%s\">%d</a>&nbsp;" % ( i, self.pc.extension, i )

            # Start a new page with a header
            thisPageName = "1.%s" % self.pc.extension
            currentPage = 1
            itemsOnPage = 0

            # Substitute tags in the header and footer
            header = self.substituteHFTag(normHeader, currentPage, user, asm3.i18n._("Available for adoption", l))
            footer = self.substituteHFTag(normFooter, currentPage, user, asm3.i18n._("Available for adoption", l))
            thisPage = header
            anCount = 0

            # Clear any existing uploaded images
            if self.pc.forceReupload:
                self.clearExistingImages()

        except Exception as err:
            self.setLastError("Error setting up page: %s" % err)
            self.logError("Error setting up page: %s" % err, sys.exc_info())
            return

        for an in animals:
            try:
                anCount += 1

                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, self.totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                # upload all images for this animal to our current FTP
                self.uploadImages(an, True)
                
                # Slot free on this page?
                if itemsOnPage < animalsPerPage:
                    thisPage += self.substituteBodyTags(body, an)
                    itemsOnPage += 1
                    self.log("%s -> %s" % (an["SHELTERCODE"], thisPageName))
                else:
                    self.log("Current page complete.")
                    # No, append the footer, store the page
                    thisPage += footer
                    pages[thisPageName] = thisPage
                    # New page
                    currentPage += 1
                    thisPageName = "%d.%s" % ( currentPage, self.pc.extension )
                    header = self.substituteHFTag(normHeader, currentPage, user, asm3.i18n._("Available for adoption", l))
                    footer = self.substituteHFTag(normFooter, currentPage, user, asm3.i18n._("Available for adoption", l))
                    thisPage = header
                    # Append this animal
                    thisPage += self.substituteBodyTags(body, an)
                    itemsOnPage = 1
                    self.log("%s -> %s" % (an["SHELTERCODE"], thisPageName))
                
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals, first=True)

        # Done with animals, store the final page
        thisPage += footer
        pages[thisPageName] = thisPage

        # Clear any existing uploaded pages
        if self.pc.clearExisting: 
            self.clearExistingHTML()

        # Upload the new pages
        for k, v in pages.items():
            self.log("Saving page to disk: %s (%d bytes)" % (k, len(v)))
            self.saveFile(os.path.join(self.publishDir, k), v)
            self.log("Saved page to disk: %s" % k)
            if self.pc.uploadDirectly:
                self.log("Uploading page: %s" % k)
                self.upload(k)
                self.log("Uploaded page: %s" % k)

        # Handle javascript db
        if self.pc.generateJavascriptDB:
            self.writeJavaScript(animals)

    def executeRSS(self) -> None:
        """
        Generates and uploads the rss.xml page
        """
        def rss_header():
            return """<?xml version="1.0" encoding="UTF-8"?>
                <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" >
                <channel rdf:about="http://www.mydomain.com">
                <title>Animals for Adoption at $$ORGNAME$$</title>
                <description></description>
                <link>RDFLINK</link>
                </channel>"""
        def rss_body():
            return """<item rdf:about="RDFLINK">
                <title>$$ShelterCode$$ - $$AnimalName$$ ($$BreedName$$ $$SpeciesName$$ aged $$Age$$)</title>
                <link>RDFLINK</link>
                <description>
                &lt;img src="$$WebMediaFilename$$" align="left" /&gt;
                $$WebMediaNotes$$
                </description>
                </item>"""
        def rss_footer():
            return """</rdf:RDF>"""

        self.log("Generating rss.xml page...")

        user = self.user
        thisPage = ""
        thisPageName = "rss.xml"
        totalAnimals = 0
        link = BASE_URL

        try:
            animals = self.getMatchingAnimals()
            totalAnimals = len(animals)
           
            header, body, footer = asm3.template.get_html_template(self.dbo, "rss")
            if header == "": header = rss_header()
            if footer == "": footer = rss_footer()
            if body == "": body = rss_body()
            header = self.substituteHFTag(header, 1, user)
            footer = self.substituteHFTag(footer, 1, user)
            thisPage = header
        except Exception as err:
            self.setLastError("Error setting up rss.xml: %s" % err)
            self.logError("Error setting up rss.xml: %s" % err, sys.exc_info())
            return

        anCount = 0
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                # Images already uploaded by Page/Species publisher

                # Add to the page
                thisPage += self.substituteBodyTags(body, an)
                self.log("Finished processing: %s" % an["SHELTERCODE"])

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Append the footer, flush and upload the page
        thisPage += footer
        thisPage = thisPage.replace("RDFLINK", link)
        self.log("Saving page to disk: %s (%d bytes)" % (thisPageName, len(thisPage)))
        self.saveFile(os.path.join(self.publishDir, thisPageName), thisPage)
        self.log("Saved page to disk: %s" % thisPageName)
        if self.pc.uploadDirectly:
            self.log("Uploading page: %s" % thisPageName)
            self.upload(thisPageName)
            self.log("Uploaded page: %s" % thisPageName)

    def executeType(self, user: str) -> None:
        """
        Publisher that puts animals on pages by type
        """
        self.log("HTMLPublisher (type) starting...")

        l = self.dbo.locale
        normHeader = self.getHeader()
        normFooter = self.getFooter()
        body = self.getBody()
        header = self.substituteHFTag(normHeader, 0, user, asm3.i18n._("Available for adoption", l))
        footer = self.substituteHFTag(normFooter, 0, user, asm3.i18n._("Available for adoption", l))

        # Open FTP socket, bail if it fails
        if not self.openFTPSocket():
            self.setLastError("Failed opening FTP socket.")
            return

        try:
            animals = self.getMatchingAnimals()
            self.totalAnimals = len(animals)

            anCount = 0
            pages = {}

            # Create default pages for every possible permutation
            defaultpages = []
            atype = asm3.lookups.get_animal_types(self.dbo)
            for atype in asm3.lookups.get_animal_types(self.dbo):
                defaultpages.append(atype["ANIMALTYPE"])
            for dp in defaultpages:
                pages["%s.%s" % (dp, self.pc.extension)] = header

            # Create an all page
            allpage = "all.%s" % self.pc.extension
            pages[allpage] = header

        except Exception as err:
            self.logError("Error setting up page: %s" % err, sys.exc_info())
            self.setLastError("Error setting up page: %s" % err)
            return

        for an in animals:
            try:
                anCount += 1

                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, self.totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                # upload all images for this animal to our current FTP
                self.uploadImages(an, True)
                
                # Calculate the new page name
                pagename = "%s.%s" % (an["ANIMALTYPENAME"], self.pc.extension)

                # Does this page exist?
                if pagename not in pages:
                    # No, create it and add the header
                    page = header
                else:
                    page = pages[pagename]

                # Add this item to the page
                page += self.substituteBodyTags(body, an)
                pages[pagename] = page
                self.log("%s -> %s" % (an["SHELTERCODE"], pagename))

                # Add this item to our magic "all" page
                page = pages[allpage]
                page += self.substituteBodyTags(body, an)
                pages[allpage] = page
                
                # Mark success in the log
                self.log("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        # Upload the pages
        for k, v in pages.items():
            self.log("Saving page to disk: %s (%d bytes)" % (k, len(v + footer)))
            self.saveFile(os.path.join(self.publishDir, self.escapePageName(k)), v + footer)
            self.log("Saved page to disk: %s" % k)
            if self.pc.uploadDirectly:
                self.log("Uploading page: %s" % k)
                self.upload(self.escapePageName(k))
                self.log("Uploaded page: %s" % k)



