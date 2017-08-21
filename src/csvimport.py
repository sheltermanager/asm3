#!/usr/bin/python

import additional
import al
import animal
import async
import collections
import configuration
import csv
import datetime
import db
import dbupdate
import financial
import i18n
import movement
import person
import re
import sys
import utils
from cStringIO import StringIO

VALID_FIELDS = [
    "ANIMALNAME", "ANIMALSEX", "ANIMALTYPE", "ANIMALCOLOR", "ANIMALBREED1", 
    "ANIMALBREED2", "ANIMALDOB", "ANIMALLOCATION", "ANIMALUNIT", 
    "ANIMALSPECIES", "ANIMALAGE", 
    "ANIMALCOMMENTS", "ANIMALMARKINGS", "ANIMALNEUTERED", "ANIMALNEUTEREDDATE", "ANIMALMICROCHIP", "ANIMALMICROCHIPDATE", 
    "ANIMALENTRYDATE", "ANIMALDECEASEDDATE", "ANIMALCODE",
    "ANIMALREASONFORENTRY", "ANIMALHIDDENDETAILS", "ANIMALNOTFORADOPTION",
    "ANIMALGOODWITHCATS", "ANIMALGOODWITHDOGS", "ANIMALGOODWITHKIDS", 
    "ANIMALHOUSETRAINED", "ANIMALHEALTHPROBLEMS",
    "ORIGINALOWNERTITLE", "ORIGINALOWNERINITIALS", "ORIGINALOWNERFIRSTNAME",
    "ORIGINALOWNERLASTNAME", "ORIGINALOWNERADDRESS", "ORIGINALOWNERCITY",
    "ORIGINALOWNERSTATE", "ORIGINALOWNERZIPCODE", "ORIGINALOWNERHOMEPHONE",
    "ORIGINALOWNERWORKPHONE", "ORIGINALOWNERCELLPHONE", "ORIGINALOWNEREMAIL",
    "DONATIONDATE", "DONATIONAMOUNT", "DONATIONCHECKNUMBER", "DONATIONCOMMENTS", "DONATIONTYPE", "DONATIONPAYMENT", 
    "MOVEMENTTYPE", "MOVEMENTDATE", "MOVEMENTCOMMENTS", "MOVEMENTRETURNDATE", 
    "PERSONTITLE", "PERSONINITIALS", "PERSONFIRSTNAME", "PERSONLASTNAME", "PERSONNAME",
    "PERSONADDRESS", "PERSONCITY", "PERSONSTATE",
    "PERSONZIPCODE", "PERSONFOSTERER", "PERSONDONOR",
    "PERSONFLAGS", "PERSONCOMMENTS", "PERSONHOMEPHONE", "PERSONWORKPHONE",
    "PERSONCELLPHONE", "PERSONEMAIL", "PERSONCLASS",
    "PERSONMEMBER", "PERSONMEMBERSHIPEXPIRY"
]

def gkc(m, f):
    """ reads field f from map m, assuming a currency amount and returning 
        an integer """
    if f not in m: return 0
    try:
        # Remove non-numeric characters
        v = re.sub(r'[^\d.]+', '', str(m[f]))
        fl = float(v)
        fl *= 100
        return int(fl)
    except:
        return 0

def gks(m, f):
    """ reads field f from map m, returning a string. 
        string is empty if key not present """
    if f not in m: return ""
    return str(utils.strip_non_ascii(m[f]))

def gkd(dbo, m, f, usetoday = False):
    """ reads field f from map m, returning a display date. 
        string is empty if key not present or date is invalid.
        If usetoday is set to True, then today's date is returned
        if the date is blank.
    """
    if f not in m: return ""
    lv = str(m[f])
    # If there's a space, then I guess we have time info - throw it away
    if lv.find(" ") > 0:
        lv = lv[0:lv.find(" ")]
    # Now split it by either / or -
    b = lv.split("/")
    if lv.find("-") != -1:
        b = lv.split("-")
    # We should have three date bits now
    if len(b) != 3:
        # We don't have a valid date, if use today is on return that
        if usetoday:
            return i18n.python2display(dbo.locale, i18n.now(dbo.timezone))
        else:
            return ""
    else:
        try:
            # Which of our 3 bits is the year?
            if utils.cint(b[0]) > 1900:
                # it's Y/M/D
                d = datetime.datetime(utils.cint(b[0]), utils.cint(b[1]), utils.cint(b[2]))
            elif dbo.locale == "en":
                # Assume it's M/D/Y for US
                d = datetime.datetime(utils.cint(b[2]), utils.cint(b[0]), utils.cint(b[1]))
            else:
                # Assume it's D/M/Y
                d = datetime.datetime(utils.cint(b[2]), utils.cint(b[1]), utils.cint(b[0]))
            return i18n.python2display(dbo.locale, d)
        except:
            # We've got an invalid date - return today
            if usetoday:
                return i18n.python2display(dbo.locale, i18n.now(dbo.timezone))
            else:
                return ""

def gkb(m, f):
    """ reads field f from map m, returning a boolean. 
        boolean is false if key not present. Interprets
        anything but blank, 0 or N as yes """
    if f not in m: return False
    if m[f] == "" or m[f] == "0" or m[f].upper().startswith("N"): return False
    return True

def gkbi(m, f):
    """ reads boolean field f from map m, returning 1 for yes or 0 for no """
    if gkb(m,f):
        return "1"
    else:
        return "0"

def gkbc(m, f):
    """ reads boolean field f from map m, returning a fake checkbox 
        field of blank for no, "on" for yes """
    if gkb(m,f):
        return "on"
    else:
        return ""

def gkynu(m, f):
    """ reads field f from map m, returning a tri-state
        switch. Returns 2 (unknown) for a blank field
        Input should start with Y/N/U or 0/1/2 """
    if f not in m: return 2
    if m[f].upper().startswith("Y") or m[f] == "0": return 0
    if m[f].upper().startswith("N") or m[f] == "1": return 1
    return 2

def gkbr(dbo, m, f, speciesid, create):
    """ reads lookup field f from map m, returning a str(int) that
        corresponds to a lookup match for BreedName in breed.
        if create is True, adds a row to the table if it doesn't
        find a match and then returns str(newid)
        speciesid is the linked species for any newly created breed
        returns "0" if key not present, or if no match was found and create is off """
    if f not in m: return "0"
    lv = m[f]
    matchid = dbo.query_int("SELECT ID FROM breed WHERE LOWER(BreedName) = ?", [ lv.strip().lower().replace("'", "`")] )
    if matchid == 0 and create:
        nextid = dbo.get_id("breed")
        sql = "INSERT INTO breed (ID, SpeciesID, BreedName) VALUES (?,?,?)"
        dbo.execute(sql, (nextid, speciesid, lv.replace("'", "`")))
        return str(nextid)
    return str(matchid)

def gkl(dbo, m, f, table, namefield, create):
    """ reads lookup field f from map m, returning a str(int) that
        corresponds to a lookup match for namefield in table.
        if create is True, adds a row to the table if it doesn't
        find a match and then returns str(newid)
        returns "0" if key not present, or if no match was found and create is off """
    if f not in m: return "0"
    lv = m[f]
    matchid = dbo.query_int("SELECT ID FROM %s WHERE LOWER(%s) = ?" % (table, namefield), [ lv.strip().lower().replace("'", "`") ])
    if matchid == 0 and create:
        nextid = db.get_id(dbo, table)
        sql = "INSERT INTO %s (ID, %s) VALUES (?, ?)" % (table, namefield)
        dbo.execute(sql, (nextid, lv.replace("'", "`")))
        return str(nextid)
    return str(matchid)

def create_additional_fields(dbo, row, errors, rowno, csvkey = "ANIMALADDITIONAL", linktype = "animal", linkid = 0):
    # Identify any additional fields that may have been specified with
    # ANIMALADDITIONAL<fieldname>
    for a in additional.get_field_definitions(dbo, linktype):
        v = gks(row, csvkey + str(a["FIELDNAME"]).upper())
        if v != "":
            sql = db.make_insert_sql("additional", (
                ( "LinkType", db.di(a["LINKTYPE"]) ),
                ( "LinkID", db.di(int(linkid)) ),
                ( "AdditionalFieldID", db.di(a["ID"]) ),
                ( "Value", db.ds(v) ) ))
            try:
                db.execute(dbo, sql)
            except Exception as e:
                errors.append( (rowno, str(row), str(e)) )

def csvimport(dbo, csvdata, createmissinglookups = False, cleartables = False, checkduplicates = False):
    """
    Imports the csvdata.
    createmissinglookups: If a lookup value is given that's not in our data, add it
    cleartables: Clear down the animal, owner and adoption tables before import
    """

    # Convert line endings to standard unix lf to prevent
    # the Python CSV importer barfing.
    csvdata = csvdata.replace("\r\n", "\n")
    csvdata = csvdata.replace("\r", "\n")

    reader = utils.UnicodeCSVReader(StringIO(csvdata))

    # Make sure we have a valid header
    cols = None
    for row in reader:
        cols = row
        break
    if cols is None:
        async.set_last_error(dbo, "Your CSV file is empty")
        return

    onevalid = False
    hasanimal = False
    hasanimalname = False
    hasperson = False
    haspersonlastname = False
    haspersonname = False
    hasmovement = False
    hasmovementdate = False
    hasdonation = False
    hasdonationamount = False
    hasoriginalowner = False
    hasoriginalownerlastname = False
    for col in cols:
        if col in VALID_FIELDS: onevalid = True
        if col.startswith("ANIMAL"): hasanimal = True
        if col == "ANIMALNAME": hasanimalname = True
        if col.startswith("ORIGINALOWNER"): hasoriginalowner = True
        if col == "ORIGINALOWNERLASTNAME": hasoriginalownerlastname = True
        if col.startswith("PERSON"): hasperson = True
        if col == "PERSONLASTNAME": haspersonlastname = True
        if col == "PERSONNAME": haspersonname = True
        if col.startswith("MOVEMENT"): hasmovement = True
        if col == "MOVEMENTDATE": hasmovementdate = True
        if col.startswith("DONATION"): hasdonation = True
        if col == "DONATIONAMOUNT": hasdonationamount = True

    # Any valid fields?
    if not onevalid:
        async.set_last_error(dbo, "Your CSV file did not contain any fields that ASM recognises")
        return

    # If we have any animal fields, make sure at least ANIMALNAME is supplied
    if hasanimal and not hasanimalname:
        async.set_last_error(dbo, "Your CSV file has animal fields, but no ANIMALNAME column")
        return

    # If we have any person fields, make sure at least PERSONLASTNAME or PERSONNAME is supplied
    if hasperson and not haspersonlastname and not haspersonname:
        async.set_last_error(dbo, "Your CSV file has person fields, but no PERSONNAME or PERSONLASTNAME column")
        return

    # If we have any original owner fields, make sure at least ORIGINALOWNERLASTNAME is supplied
    if hasoriginalowner and not hasoriginalownerlastname:
        async.set_last_error(dbo, "Your CSV file has original owner fields, but no ORIGINALOWNERLASTNAME column")
        return

    # If we have any movement fields, make sure MOVEMENTDATE is supplied
    if hasmovement and not hasmovementdate:
        async.set_last_error(dbo, "Your CSV file has movement fields, but no MOVEMENTDATE column")
        return

    # If we have any donation fields, we need an amount
    if hasdonation and not hasdonationamount:
        async.set_last_error(dbo, "Your CSV file has donation fields, but no DONATIONAMOUNT column")
        return

    # We also need a valid person
    if hasdonation and not (haspersonlastname or haspersonname):
        async.set_last_error(dbo, "Your CSV file has donation fields, but no person to apply the donation to")
        return

    # Read the whole CSV file into a list of maps. Note, the
    # reader has a cursor at the second row already because
    # we read the header in the first row above
    data = []
    for row in reader:
        currow = {}
        for i, col in enumerate(row):
            if i >= len(cols): continue # skip if we run out of cols
            currow[cols[i]] = col
        data.append(currow)

    al.debug("reading CSV data, found %d rows" % len(data), "csvimport.csvimport", dbo)

    # If we're clearing down tables first, do it now
    if cleartables:
        al.warn("Resetting the database by removing all non-lookup data", "csvimport.csvimport", dbo)
        dbupdate.reset_db(dbo)

    # Now that we've read them in, go through all the rows
    # and start importing.
    errors = []
    rowno = 1
    async.set_progress_max(dbo, len(data))
    for row in data:

        al.debug("import csv: row %d of %d" % (rowno, len(data)), "csvimport.csvimport", dbo)
        async.increment_progress_value(dbo)

        # Do we have animal data to read?
        animalid = 0
        if hasanimal and gks(row, "ANIMALNAME") != "":
            a = {}
            a["animalname"] = gks(row, "ANIMALNAME")
            a["sheltercode"] = gks(row, "ANIMALCODE")
            a["shortcode"] = gks(row, "ANIMALCODE")
            if gks(row, "ANIMALSEX") == "": 
                a["sex"] = "2" # Default unknown if not set
            else:
                a["sex"] = gks(row, "ANIMALSEX").lower().startswith("m") and "1" or "0"
            a["basecolour"] = gkl(dbo, row, "ANIMALCOLOR", "basecolour", "BaseColour", createmissinglookups)
            if a["basecolour"] == "0":
                a["basecolour"] = str(configuration.default_colour(dbo))
            a["species"] = gkl(dbo, row, "ANIMALSPECIES", "species", "SpeciesName", createmissinglookups)
            if a["species"] == "0":
                a["species"] = str(configuration.default_species(dbo))
            a["animaltype"] = gkl(dbo, row, "ANIMALTYPE", "animaltype", "AnimalType", createmissinglookups)
            if a["animaltype"] == "0":
                a["animaltype"] = str(configuration.default_type(dbo))
            a["breed1"] = gkbr(dbo, row, "ANIMALBREED1", a["species"], createmissinglookups)
            if a["breed1"] == "0":
                a["breed1"] = str(configuration.default_breed(dbo))
            a["breed2"] = gkbr(dbo, row, "ANIMALBREED2", a["species"], createmissinglookups)
            if a["breed2"] != "0" and a["breed2"] != a["breed1"]:
                a["crossbreed"] = "on"
            a["size"] = str(configuration.default_size(dbo))
            a["internallocation"] = gkl(dbo, row, "ANIMALLOCATION", "internallocation", "LocationName", createmissinglookups)
            if a["internallocation"] == "0":
                a["internallocation"] = str(configuration.default_location(dbo))
            a["unit"] = gks(row, "ANIMALUNIT")
            a["comments"] = gks(row, "ANIMALCOMMENTS")
            a["markings"] = gks(row, "ANIMALMARKINGS")
            a["hiddenanimaldetails"] = gks(row, "ANIMALHIDDENDETAILS")
            a["healthproblems"] = gks(row, "ANIMALHEALTHPROBLEMS")
            a["notforadoption"] = gkbi(row, "ANIMALNOTFORADOPTION")
            a["housetrained"] = gkynu(row, "ANIMALHOUSETRAINED")
            a["goodwithcats"] = gkynu(row, "ANIMALGOODWITHCATS")
            a["goodwithdogs"] = gkynu(row, "ANIMALGOODWITHDOGS")
            a["goodwithkids"] = gkynu(row, "ANIMALGOODWITHKIDS")
            a["reasonforentry"] = gks(row, "ANIMALREASONFORENTRY")
            a["estimatedage"] = gks(row, "ANIMALAGE")
            a["dateofbirth"] = gkd(dbo, row, "ANIMALDOB", True)
            if gks(row, "ANIMALDOB") == "" and a["estimatedage"] != "":
                a["dateofbirth"] = "" # if we had an age and dob was blank, prefer the age
            a["datebroughtin"] = gkd(dbo, row, "ANIMALENTRYDATE", True)
            a["deceaseddate"] = gkd(dbo, row, "ANIMALDECEASEDDATE")
            a["neutered"] = gkbc(row, "ANIMALNEUTERED")
            a["neutereddate"] = gkd(dbo, row, "ANIMALNEUTEREDDATE")
            if a["neutereddate"] != "": a["neutered"] = "on"
            a["microchipnumber"] = gks(row, "ANIMALMICROCHIP")
            if a["microchipnumber"] != "": a["microchipped"] = "on"
            a["microchipdate"] = gkd(dbo, row, "ANIMALMICROCHIPDATE")
            # If an original owner is specified, create a person record
            # for them and attach it to the animal as original owner
            if gks(row, "ORIGINALOWNERLASTNAME") != "":
                p = {}
                p["title"] = gks(row, "ORIGINALOWNERTITLE")
                p["initials"] = gks(row, "ORIGINALOWNERINITIALS")
                p["forenames"] = gks(row, "ORIGINALOWNERFIRSTNAME")
                p["surname"] = gks(row, "ORIGINALOWNERLASTNAME")
                p["address"] = gks(row, "ORIGINALOWNERADDRESS")
                p["town"] = gks(row, "ORIGINALOWNERCITY")
                p["county"] = gks(row, "ORIGINALOWNERSTATE")
                p["postcode"] = gks(row, "ORIGINALOWNERZIPCODE")
                p["hometelephone"] = gks(row, "ORIGINALOWNERHOMEPHONE")
                p["worktelephone"] = gks(row, "ORIGINALOWNERWORKPHONE")
                p["mobiletelephone"] = gks(row, "ORIGINALOWNERCELLPHONE")
                p["emailaddress"] = gks(row, "ORIGINALOWNEREMAIL")
                try:
                    if checkduplicates:
                        dups = person.get_person_similar(dbo, p["emailaddress"], p["surname"], p["forenames"], p["address"])
                        if len(dups) > 0:
                            a["originalowner"] = str(dups[0]["ID"])
                    if "originalowner" not in a:
                        ooid = person.insert_person_from_form(dbo, utils.PostedData(p, dbo.locale), "import")
                        a["originalowner"] = str(ooid)
                        # Identify an ORIGINALOWNERADDITIONAL additional fields and create them
                        create_additional_fields(dbo, row, errors, rowno, "ORIGINALOWNERADDITIONAL", "person", ooid)
                except Exception as e:
                    al.error("row %d (%s), originalowner: %s" % (rowno, str(row), str(e)), "csvimport.csvimport", dbo, sys.exc_info())
                    errors.append( (rowno, str(row), "originalowner: " + str(e)) )
            try:
                if checkduplicates:
                    dup = animal.get_animal_sheltercode(dbo, a["sheltercode"])
                    if dup is not None:
                        animalid = dup["ID"]
                if animalid == 0:
                    animalid, newcode = animal.insert_animal_from_form(dbo, utils.PostedData(a, dbo.locale), "import")
                    # Identify an ANIMALADDITIONAL additional fields and create them
                    create_additional_fields(dbo, row, errors, rowno, "ANIMALADDITIONAL", "animal", animalid)
            except Exception as e:
                al.error("row %d (%s): %s" % (rowno, str(row), str(e)), "csvimport.csvimport", dbo, sys.exc_info())
                errmsg = str(e)
                if type(e) == utils.ASMValidationError: errmsg = e.getMsg()
                errors.append( (rowno, str(row), errmsg) )

        # Person data?
        personid = 0
        if hasperson and (gks(row, "PERSONLASTNAME") != "" or gks(row, "PERSONNAME") != ""):
            p = {}
            p["ownertype"] = gks(row, "PERSONCLASS")
            if p["ownertype"] != "1" and p["ownertype"] != "2": 
                p["ownertype"] = "1"
            p["title"] = gks(row, "PERSONTITLE")
            p["initials"] = gks(row, "PERSONINITIALS")
            p["forenames"] = gks(row, "PERSONFIRSTNAME")
            p["surname"] = gks(row, "PERSONLASTNAME")
            # If we have a person name, all upto the last space is first names,
            # everything after the last name
            if gks(row, "PERSONNAME") != "":
                pname = gks(row, "PERSONNAME")
                if pname.find(" ") != -1:
                    p["forenames"] = pname[0:pname.rfind(" ")]
                    p["surname"] = pname[pname.rfind(" ")+1:]
                else:
                    p["surname"] = pname
            p["address"] = gks(row, "PERSONADDRESS")
            p["town"] = gks(row, "PERSONCITY")
            p["county"] = gks(row, "PERSONSTATE")
            p["postcode"] = gks(row, "PERSONZIPCODE")
            p["hometelephone"] = gks(row, "PERSONHOMEPHONE")
            p["worktelephone"] = gks(row, "PERSONWORKPHONE")
            p["mobiletelephone"] = gks(row, "PERSONCELLPHONE")
            p["emailaddress"] = gks(row, "PERSONEMAIL")
            flags = gks(row, "PERSONFLAGS")
            if gkb(row, "PERSONFOSTERER"): flags += ",fosterer"
            if gkb(row, "PERSONMEMBER"): flags += ",member"
            if gkb(row, "PERSONDONOR"): flags += ",donor"
            p["flags"] = flags
            p["comments"] = gks(row, "PERSONCOMMENTS")
            p["membershipexpires"] = gkd(dbo, row, "PERSONMEMBERSHIPEXPIRY")
            try:
                if checkduplicates:
                    dups = person.get_person_similar(dbo, p["emailaddress"], p["surname"], p["forenames"], p["address"])
                    if len(dups) > 0:
                        personid = dups[0]["ID"]
                        # Merge flags and any extra details
                        person.merge_flags(dbo, "import", personid, flags)
                        person.merge_person_details(dbo, "import", personid, p)
                if personid == 0:
                    personid = person.insert_person_from_form(dbo, utils.PostedData(p, dbo.locale), "import")
                    # Identify any PERSONADDITIONAL additional fields and create them
                    create_additional_fields(dbo, row, errors, rowno, "PERSONADDITIONAL", "person", personid)
            except Exception as e:
                al.error("row %d (%s), person: %s" % (rowno, str(row), str(e)), "csvimport.csvimport", dbo, sys.exc_info())
                errmsg = str(e)
                if type(e) == utils.ASMValidationError: errmsg = e.getMsg()
                errors.append( (rowno, str(row), "person: " + errmsg) )

        # Movement to tie animal/person together?
        movementid = 0
        if hasmovement and personid != 0 and animalid != 0 and gks(row, "MOVEMENTDATE") != "":
            m = {}
            m["person"] = str(personid)
            m["animal"] = str(animalid)
            movetype = gks(row, "MOVEMENTTYPE")
            if movetype == "": movetype = "1" # Default to adoption if not supplied
            m["type"] = str(movetype)
            m["movementdate"] = gkd(dbo, row, "MOVEMENTDATE", True)
            m["returndate"] = gkd(dbo, row, "MOVEMENTRETURNDATE")
            m["comments"] = gks(row, "MOVEMENTCOMMENTS")
            m["returncategory"] = str(configuration.default_entry_reason(dbo))
            try:
                movementid = movement.insert_movement_from_form(dbo, "import", utils.PostedData(m, dbo.locale))
            except Exception as e:
                al.error("row %d (%s), movement: %s" % (rowno, str(row), str(e)), "csvimport.csvimport", dbo, sys.exc_info())
                errmsg = str(e)
                if type(e) == utils.ASMValidationError: errmsg = e.getMsg()
                errors.append( (rowno, str(row), "movement: " + errmsg) )

        # Donation?
        if hasdonation and personid != 0 and gkc(row, "DONATIONAMOUNT") != 0:
            d = {}
            d["person"] = str(personid)
            d["animal"] = str(animalid)
            d["movement"] = str(movementid)
            d["amount"] = str(gkc(row, "DONATIONAMOUNT"))
            d["comments"] = gks(row, "DONATIONCOMMENTS")
            d["received"] = gkd(dbo, row, "DONATIONDATE", True)
            d["chequenumber"] = gks(row, "DONATIONCHECKNUMBER")
            d["type"] = gkl(dbo, row, "DONATIONTYPE", "donationtype", "DonationName", createmissinglookups)
            if d["type"] == "0":
                d["type"] = str(configuration.default_donation_type(dbo))
            d["payment"] = gkl(dbo, row, "DONATIONPAYMENT", "donationpayment", "PaymentName", createmissinglookups)
            if d["payment"] == "0":
                d["payment"] = "1"
            try:
                financial.insert_donation_from_form(dbo, "import", utils.PostedData(d, dbo.locale))
            except Exception as e:
                al.error("row %d (%s), donation: %s" % (rowno, str(row), str(e)), "csvimport.csvimport", dbo, sys.exc_info())
                errmsg = str(e)
                if type(e) == utils.ASMValidationError: errmsg = e.getMsg()
                errors.append( (rowno, str(row), "donation: " + errmsg) )
            if movementid != 0: movement.update_movement_donation(dbo, movementid)

        rowno += 1

    h = [ "<p>%d success, %d errors</p><table>" % (len(data) - len(errors), len(errors)) ]
    for rowno, row, err in errors:
        h.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (rowno, row, err))
    h.append("</table>")
    return "".join(h)

def csvexport_animals(dbo, animalids):
    """
    Export CSV data for the supplied comma separated list of animalids
    """
    l = dbo.locale
    rows = []
    for aid in animalids.split(","):
        row = collections.OrderedDict()
        a = animal.get_animal(dbo, utils.cint(aid))
        if a is None: continue
        row["ANIMALCODE"] = a["SHELTERCODE"]
        row["ANIMALNAME"] = a["ANIMALNAME"]
        row["ANIMALSEX"] = a["SEXNAME"]
        row["ANIMALTYPE"] = a["ANIMALTYPENAME"]
        row["ANIMALCOLOR"] = a["BASECOLOURNAME"]
        row["ANIMALBREED1"] = a["BREEDNAME1"]
        row["ANIMALBREED2"] = a["BREEDNAME2"]
        row["ANIMALDOB"] = i18n.python2display(l, a["DATEOFBIRTH"])
        row["ANIMALLOCATION"] = a["SHELTERLOCATIONNAME"]
        row["ANIMALUNIT"] = a["SHELTERLOCATIONUNIT"]
        row["ANIMALSPECIES"] = a["SPECIESNAME"]
        row["ANIMALCOMMENTS"] = a["ANIMALCOMMENTS"]
        row["ANIMALHIDDENDETAILS"] = a["HIDDENANIMALDETAILS"]
        row["ANIMALHEALTHPROBLEMS"] = a["HEALTHPROBLEMS"]
        row["ANIMALMARKINGS"] = a["MARKINGS"]
        row["ANIMALREASONFORENTRY"] = a["REASONFORENTRY"]
        row["ANIMALNEUTERED"] = a["NEUTERED"]
        row["ANIMALNEUTEREDDATE"] = i18n.python2display(l, a["NEUTEREDDATE"])
        row["ANIMALMICROCHIP"] = a["IDENTICHIPNUMBER"]
        row["ANIMALMICROCHIPDATE"] = i18n.python2display(l, a["IDENTICHIPDATE"])
        row["ANIMALENTRYDATE"] = i18n.python2display(l, a["DATEBROUGHTIN"])
        row["ANIMALDECEASEDDATE"] = i18n.python2display(l, a["DECEASEDDATE"])
        row["ANIMALNOTFORADOPTION"] = a["ISNOTAVAILABLEFORADOPTION"]
        row["ANIMALGOODWITHCATS"] = a["ISGOODWITHCATSNAME"]
        row["ANIMALGOODWITHDOGS"] = a["ISGOODWITHDOGSNAME"]
        row["ANIMALGOODWITHKIDS"] = a["ISGOODWITHCHILDRENNAME"]
        row["ANIMALHOUSETRAINED"] = a["ISHOUSETRAINEDNAME"]
        row["ORIGINALOWNERTITLE"] = a["ORIGINALOWNERTITLE"]
        row["ORIGINALOWNERINITIALS"] = a["ORIGINALOWNERINITIALS"]
        row["ORIGINALOWNERFIRSTNAME"] = a["ORIGINALOWNERFORENAMES"]
        row["ORIGINALOWNERLASTNAME"] = a["ORIGINALOWNERSURNAME"]
        row["ORIGINALOWNERADDRESS"] = a["ORIGINALOWNERADDRESS"]
        row["ORIGINALOWNERCITY"] = a["ORIGINALOWNERTOWN"]
        row["ORIGINALOWNERSTATE"] = a["ORIGINALOWNERCOUNTY"]
        row["ORIGINALOWNERZIPCODE"] = a["ORIGINALOWNERPOSTCODE"]
        row["ORIGINALOWNERHOMEPHONE"] = a["ORIGINALOWNERHOMETELEPHONE"]
        row["ORIGINALOWNERWORKPHONE"] = a["ORIGINALOWNERWORKTELEPHONE"]
        row["ORIGINALOWNERCELLPHONE"] = a["ORIGINALOWNERMOBILETELEPHONE"]
        row["ORIGINALOWNEREMAIL"] = a["ORIGINALOWNEREMAILADDRESS"]
        row["MOVEMENTTYPE"] = a["ACTIVEMOVEMENTTYPE"]
        row["MOVEMENTDATE"] = i18n.python2display(l, a["ACTIVEMOVEMENTDATE"])
        row["PERSONTITLE"] = a["CURRENTOWNERTITLE"]
        row["PERSONINITIALS"] = a["CURRENTOWNERINITIALS"]
        row["PERSONFIRSTNAME"] = a["CURRENTOWNERFORENAMES"]
        row["PERSONLASTNAME"] = a["CURRENTOWNERSURNAME"]
        row["PERSONADDRESS"] = a["CURRENTOWNERADDRESS"]
        row["PERSONCITY"] = a["CURRENTOWNERTOWN"]
        row["PERSONSTATE"] = a["CURRENTOWNERCOUNTY"]
        row["PERSONZIPCODE"] = a["CURRENTOWNERPOSTCODE"]
        row["PERSONFOSTERER"] = a["ACTIVEMOVEMENTTYPE"] == 2 and 1 or 0
        row["PERSONHOMEPHONE"] = a["CURRENTOWNERHOMETELEPHONE"]
        row["PERSONWORKPHONE"] = a["CURRENTOWNERWORKTELEPHONE"]
        row["PERSONCELLPHONE"] = a["CURRENTOWNERMOBILETELEPHONE"]
        row["PERSONEMAIL"] = a["CURRENTOWNEREMAILADDRESS"]
        rows.append(row)
    if len(rows) == 0: return ""
    keys = rows[0].keys()
    out = StringIO()
    dict_writer = csv.DictWriter(out, keys)
    dict_writer.writeheader()
    dict_writer.writerows(rows)
    return out.getvalue()

