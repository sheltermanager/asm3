
import asm3.additional
import asm3.al
import asm3.animal
import asm3.asynctask
import asm3.cachedisk
import asm3.configuration
import asm3.dbupdate
import asm3.financial
import asm3.i18n
import asm3.media
import asm3.medical
import asm3.movement
import asm3.person
import asm3.utils

from asm3.sitedefs import SERVICE_URL
from asm3.typehints import Any, Database, Dict, List

from datetime import datetime
import re
import sys

VALID_FIELDS = [
    "ANIMALCODE", "ANIMALNAME", "ANIMALSEX", "ANIMALTYPE", "ANIMALCOLOR", "ANIMALBREED1", "ANIMALBREED2", "ANIMALDOB", 
    "ANIMALLITTER", "ANIMALLOCATION", "ANIMALUNIT", "ANIMALJURISDICTION", 
    "ANIMALPICKUPLOCATION", "ANIMALPICKUPADDRESS", "ANIMALSPECIES", "ANIMALAGE", 
    "ANIMALDECEASEDDATE", "ANIMALDECEASEDREASON", "ANIMALDECEASEDNOTES", "ANIMALEUTHANIZED", 
    "ANIMALCOMMENTS", "ANIMALDESCRIPTION", "ANIMALMARKINGS", "ANIMALNEUTERED", "ANIMALNEUTEREDDATE", "ANIMALMICROCHIP", "ANIMALMICROCHIPDATE", 
    "ANIMALENTRYDATE", "ANIMALENTRYTIME", "ANIMALENTRYCATEGORY", "ANIMALENTRYTYPE", "ANIMALFLAGS", "ANIMALWARNING",
    "ANIMALREASONFORENTRY", "ANIMALHIDDENDETAILS", "ANIMALNOTFORADOPTION", "ANIMALNONSHELTER", "ANIMALTRANSFER",
    "ANIMALGOODWITHCATS", "ANIMALGOODWITHDOGS", "ANIMALGOODWITHKIDS", "ANIMALGOODWITHELDERLY", "ANIMALGOODONLEAD",
    "ANIMALHOUSETRAINED", "ANIMALCRATETRAINED", "ANIMALENERGYLEVEL", "ANIMALHEALTHPROBLEMS", "ANIMALIMAGE",
    "CLINICAPPOINTMENTFOR", "CLINICAPPOINTMENTTYPE", "CLINICAPPOINTMENTSTATUS", 
    "CLINICAPPOINTMENTDATE", "CLINICAPPOINTMENTTIME", "CLINICARRIVEDDATE", "CLINICARRIVEDTIME", 
    "CLINICWITHVETDATE", "CLINICWITHVETTIME", "CLINICCOMPLETEDDATE", "CLINICCOMPLETEDDATE", 
    "CLINICAPPOINTMENTISVAT", "CLINICAPPOINTMENTVATRATE", "CLINICAPPOINTMENTVATAMOUNT", "CLINICAPPOINTMENTREASON", "CLINICAPPOINTMENTREASON", "CLINICAPPOINTMENTCOMMENTS", "CLINICAMOUNT", 
    "CITATIONDATE", "CITATIONNUMBER", "CITATIONTYPE", "FINEAMOUNT", "FINEDUEDATE", "FINEPAIDDATE", "CITATIONCOMMENTS",
    "COSTDATE", "COSTTYPE", "COSTAMOUNT", "COSTDESCRIPTION",
    "VACCINATIONTYPE", "VACCINATIONDUEDATE", "VACCINATIONGIVENDATE", "VACCINATIONEXPIRESDATE", "VACCINATIONRABIESTAG",
    "VACCINATIONMANUFACTURER", "VACCINATIONBATCHNUMBER", "VACCINATIONCOMMENTS", 
    "VOUCHERNAME", "VOUCHERVETNAME", "VOUCHERVETADDRESS", "VOUCHERVETTOWN", "VOUCHERVETCOUNTY", "VOUCHERVETPOSTCODE", "VOUCHERDATEISSUED", "VOUCHERDATEPRESENTED", "VOUCHERDATEEXPIRED", "VOUCHERVALUE", "VOUCHERCODE", "VOUCHERCOMMENTS", 
    "TESTTYPE", "TESTDUEDATE", "TESTPERFORMEDDATE", "TESTRESULT", "TESTCOMMENTS",
    "MEDICALNAME", "MEDICALDOSAGE", "MEDICALGIVENDATE", "MEDICALCOMMENTS",
    "ORIGINALOWNERTITLE", "ORIGINALOWNERINITIALS", "ORIGINALOWNERFIRSTNAME",
    "ORIGINALOWNERLASTNAME", "ORIGINALOWNERADDRESS", "ORIGINALOWNERCITY",
    "ORIGINALOWNERSTATE", "ORIGINALOWNERZIPCODE", "ORIGINALOWNERJURISDICTION", "ORIGINALOWNERHOMEPHONE",
    "ORIGINALOWNERWORKPHONE", "ORIGINALOWNERCELLPHONE", "ORIGINALOWNEREMAIL", "ORIGINALOWNERWARNING", 
    "DONATIONDATE", "DONATIONAMOUNT", "DONATIONFEE", "DONATIONCHECKNUMBER", "DONATIONCOMMENTS", "DONATIONTYPE", "DONATIONPAYMENT", "DONATIONGIFTAID",
    "INCIDENTDATE", "INCIDENTTIME", "INCIDENTTYPE", "INCIDENTNOTES", "DISPATCHADDRESS", "DISPATCHCITY", "DISPATCHSTATE", "DISPATCHZIPCODE", "DISPATCHACO", "DISPATCHDATE", "DISPATCHTIME", "INCIDENTRESPONDEDDATE", "INCIDENTFOLLOWUPDATE", "INCIDENTCOMPLETEDDATE", "INCIDENTCOMPLETEDTIME", "INCIDENTCOMPLETEDTYPE"
    "INCIDENTANIMALSPECIES", "INCIDENTANIMALDESCRIPTION", "INCIDENTANIMALSEX",
    "INVESTIGATIONDATE", "INVESTIGATIONNOTES",
    "LICENSETYPE", "LICENSENUMBER", "LICENSEFEE", "LICENSEISSUEDATE", "LICENSEEXPIRESDATE", "LICENSECOMMENTS",
    "LOANDATE", "TRAPNUMBER", "TRAPTYPE", "DEPOSITAMOUNT", "DEPOSITRETURNDATE", "RETURNDUEDATE", "RETURNDATE", "TRAPLOANCOMMENTS",
    "LOGDATE", "LOGTIME", "LOGTYPE", "LOGCOMMENTS",
    "PERSONCODE", "PERSONDATEOFBIRTH", "PERSONIDNUMBER",
    "PERSONDATEOFBIRTH2", "PERSONIDNUMBER2",
    "PERSONTITLE", "PERSONINITIALS", "PERSONFIRSTNAME", "PERSONLASTNAME", "PERSONNAME",
    "PERSONTITLE2", "PERSONINITIALS2", "PERSONFIRSTNAME2", "PERSONLASTNAME2",
    "PERSONADDRESS", "PERSONCITY", "PERSONSTATE",
    "PERSONZIPCODE", "PERSONJURISDICTION", "PERSONFOSTERER", "PERSONDONOR",
    "PERSONFLAGS", "PERSONCOMMENTS", "PERSONWARNING", "PERSONFOSTERCAPACITY",
    "PERSONHOMEPHONE", "PERSONWORKPHONE", "PERSONCELLPHONE", "PERSONEMAIL",
    "PERSONWORKPHONE2", "PERSONCELLPHONE2", "PERSONEMAIL2",
    "PERSONGDPRCONTACT", "PERSONCLASS",
    "PERSONMEMBER", "PERSONMEMBERSHIPNUMBER", "PERSONMEMBERSHIPEXPIRY",
    "PERSONMATCHACTIVE", "PERSONMATCHADDED", "PERSONMATCHEXPIRES",
    "PERSONMATCHSEX", "PERSONMATCHSIZE", "PERSONMATCHCOLOR", "PERSONMATCHAGEFROM", "PERSONMATCHAGETO", 
    "PERSONMATCHTYPE", "PERSONMATCHSPECIES", "PERSONMATCHBREED1", "PERSONMATCHBREED2", 
    "PERSONMATCHGOODWITHCATS", "PERSONMATCHGOODWITHDOGS", "PERSONMATCHGOODWITHCHILDREN", "PERSONMATCHGOODWITHELDERLY", 
    "PERSONMATCHHOUSETRAINED", "PERSONMATCHCRATETRAINED", "PERSONMATCHGOODTRAVELLER", "PERSONMATCHGOODONLEAD", "PERSONMATCHENERGYLEVEL", 
    "PERSONMATCHCOMMENTSCONTAIN",
    "DIARYDATE", "DIARYFOR", "DIARYSUBJECT", "DIARYNOTE", 
    "STOCKLEVELNAME", "STOCKLEVELDESCRIPTION", "STOCKLEVELBARCODE", "STOCKLEVELLOCATIONNAME", "STOCKLEVELUNITNAME", "STOCKLEVELTOTAL", 
    "STOCKLEVELBALANCE", "STOCKLEVELLOW", "STOCKLEVELEXPIRY", "STOCKLEVELBATCHNUMBER", "STOCKLEVELCOST", "STOCKLEVELUNITPRICE"
]

def gkc(m: Dict, f: str) -> int:
    """ reads field f from map m, assuming a currency amount and returning 
        an integer """
    if f not in m: return 0
    try:
        # Remove non-numeric characters
        v = re.sub(r'[^\d\-\.]+', '', str(m[f]))
        fl = float(v)
        fl *= 100
        return int(fl)
    except:
        return 0

def gks(m: Dict, f: str) -> str:
    """ reads field f from map m, returning a string. 
        string is empty if key not present """
    if f not in m: return ""
    return str(m[f])

def gkd(dbo: Database, m: Dict, f: str, usetoday: bool = False) -> str:
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
    # Now split it by either / or - or .
    b = lv.split("/")
    if lv.find("-") != -1: b = lv.split("-")
    if lv.find(".") != -1: b = lv.split(".")
    # We should have three date bits now
    if len(b) != 3:
        # We don't have a valid date, if use today is on return that
        if usetoday:
            return asm3.i18n.python2display(dbo.locale, dbo.now())
        else:
            return ""
    else:
        try:
            # Which of our 3 bits is the year?
            if asm3.utils.cint(b[0]) > 1900:
                # it's Y/M/D
                d = datetime(asm3.utils.cint(b[0]), asm3.utils.cint(b[1]), asm3.utils.cint(b[2]))
            elif dbo.locale == "en" or dbo.locale == "en_CA":
                # Assume it's M/D/Y for US and Canada
                d = datetime(asm3.utils.cint(b[2]), asm3.utils.cint(b[0]), asm3.utils.cint(b[1]))
            else:
                # Assume it's D/M/Y
                d = datetime(asm3.utils.cint(b[2]), asm3.utils.cint(b[1]), asm3.utils.cint(b[0]))
            return asm3.i18n.python2display(dbo.locale, d)
        except:
            # We've got an invalid date - return today
            if usetoday:
                return asm3.i18n.python2display(dbo.locale, dbo.now())
            else:
                return ""

def gkb(m: Dict, f: str) -> bool:
    """ reads field f from map m, returning a boolean. 
        boolean is false if key not present. Interprets
        anything but blank, 0 or N as yes """
    if f not in m: return False
    if m[f] == "" or m[f] == "0" or m[f].upper().startswith("N"): return False
    return True

def gkbi(m: Dict, f: str) -> str:
    """ reads boolean field f from map m, returning 1 for yes or 0 for no """
    if gkb(m,f):
        return "1"
    else:
        return "0"

def gkbc(m: Dict, f: str) -> str:
    """ reads boolean field f from map m, returning a fake checkbox 
        field of blank for no, "on" for yes """
    if gkb(m,f):
        return "on"
    else:
        return ""

def gkynu(m: Dict, f: str) -> str:
    """ reads field f from map m, returning a tri-state
        switch. Returns 2 (unknown) for a blank field
        Input should start with Y/N/U or 0/1/2 """
    if f not in m: return 2
    if m[f].upper().startswith("A") or m[f] == "-1": return "-1" # (any) for match good with
    if m[f].upper().startswith("Y") or m[f] == "0": return "0"
    if m[f].upper().startswith("N") or m[f] == "1": return "1"
    if m[f].find("5") != -1: return "5" # Good with kids over 5
    if m[f].find("12") !=-1: return "12" # Good with kids over 12
    return "2"

def gkbr(dbo: Database, m: Dict, f: str, speciesid: int, create: bool) -> str:
    """ reads lookup field f from map m, returning a str(int) that
        corresponds to a lookup match for BreedName in breed.
        if create is True, adds a row to the table if it doesn't
        find a match and then returns str(newid)
        speciesid is the linked species for any newly created breed
        returns "0" if key not present, or if no match was found and create is off """
    if f not in m: return "0"
    lv = m[f]
    matchid = dbo.query_int("SELECT ID FROM breed WHERE LOWER(BreedName) = ?", [ lv.strip().lower().replace("'", "`")] )
    if matchid == 0 and create and lv.strip() != "":
        nextid = dbo.get_id("breed")
        sql = "INSERT INTO breed (ID, SpeciesID, BreedName) VALUES (?,?,?)"
        dbo.execute(sql, (nextid, speciesid, lv.replace("'", "`")))
        return str(nextid)
    return str(matchid)

def gkl(dbo: Database, m: Dict, f: str, table: str, namefield: str, create: bool) -> str:
    """ reads lookup field f from map m, returning a str(int) that
        corresponds to a lookup match for namefield in table.
        if create is True, adds a row to the table if it doesn't
        find a match then returns str(newid)
        returns "0" if key not present, or if no match was found and create is off,
        or the value was an empty string """
    if f not in m: return "0" # column not present
    lv = m[f]
    if lv.strip() == "": return "0" # value is empty string
    matchid = dbo.query_int("SELECT ID FROM %s WHERE LOWER(%s) = ?" % (table, namefield), [ lv.strip().lower().replace("'", "`") ])
    if matchid == 0 and create and lv.strip() != "":
        nextid = dbo.insert(table, {
            namefield:  lv
        }, setRecordVersion=False, setCreated=False, writeAudit=False)
        return str(nextid)
    return str(matchid)

def gksx(m: Dict, f: str) -> str:
    """ 
    Reads a value for Sex from field f in map m
    """
    if f not in m: return ""
    x = m[f].lower()
    if x.startswith("f"): return "0"
    elif x.startswith("m"): return "1"
    elif x.startswith("u"): return "2"
    elif x.startswith("a"): return "-1"
    else: return ""

def create_additional_fields(dbo: Database, row: Dict, errors: List, rowno: int, csvkey: str = "ANIMALADDITIONAL", linktype: str = "animal", linkid: int = 0) -> None:
    """ Identifies and create any additional fields that may have been specified in
        the csv file with csvkey<fieldname> 
        This is used during merge duplicates too as it only sets additional fields if a value
        has been supplied in the file.
    """
    for a in asm3.additional.get_field_definitions(dbo, linktype):
        v = gks(row, csvkey + str(a.fieldname).upper())
        if v != "":
            try:
                dbo.delete("additional", "LinkID=%s AND AdditionalFieldID=%s" % (linkid, a.ID))
                dbo.insert("additional", {
                    "LinkType":             a.linktype,
                    "LinkID":               linkid,
                    "AdditionalFieldID":    a.id,
                    "Value":                v
                }, generateID=False)
            except Exception as e:
                errors.append( (rowno, str(row), str(e)) )

def row_error(errors: List, rowtype: str, rowno: int, row: Dict, e: Any, dbo: Database, exinfo: Any):
    """ 
    Handles error messages during import 
    errors: List of errors to append to
    rowtype: The area of processing for the row (eg: animal)
    rowno: The row number
    row: The row data itself
    e: The exception thrown
    exinfo: execution info for logging
    """
    errmsg = str(e)
    if isinstance(e, asm3.utils.ASMValidationError): errmsg = e.getMsg()
    # If ANIMALIMAGE contains a data-uri, squash it for legibility
    if "ANIMALIMAGE" in row and row["ANIMALIMAGE"].startswith("data"):
        row["ANIMALIMAGE"] = "data:,"
    asm3.al.error("row %d %s: (%s): %s" % (rowno, rowtype, str(row), errmsg), "csvimport.row_error", dbo, exinfo)
    import traceback
    print(traceback.format_exc())
    errors.append( (rowno, str(row), errmsg) )

def csvimport(dbo: Database, csvdata: bytes, encoding: str = "utf-8-sig", user: str = "", 
              createmissinglookups: bool = False, cleartables: bool = False, 
              checkduplicates: bool = True, prefixanimalcodes: bool = False, 
              entrytoday: bool = False, htmlresults: bool = True, dryrun: bool = False) -> str:
    """
    Imports csvdata (bytes string, encoded with encoding)
    createmissinglookups: If a lookup value is given that's not in our data, add it
    cleartables: Clear down the animal, owner and adoption tables before import
    checkduplicates: Try to attach to existing records if they exist, there is no scenario really
        where this should be false, unless you want to force new records but have no ability to
        attach extra records to these imported ones.
    prefixanimalcodes: Add a prefix to shelter codes to avoid clashes with the existing records
    entrytoday: Set ANIMALENTRYDATE to today - useful for importing animals being transferred in
    htmlresults: Return the results as an HTML table. If false, returns a JSON document
    dryrun: Perform all checks and validation, but do not create or update any records
    """
    if user == "":
        user = "import"
    else:
        user = "import/%s" % user

    rows = asm3.utils.csv_parse( asm3.utils.bytes2str(csvdata, encoding=encoding) )

    # Make sure we have a valid header
    if len(rows) == 0:
        asm3.asynctask.set_last_error(dbo, "Your CSV file is empty")
        return

    onevalid = False
    hasanimal = False
    hasanimalname = False
    hascitation = False
    hasclinic = False
    hasequipmentloan = False
    hasmed = False
    hasmedicalname = False
    hasmedicalgivendate = False
    hastest = False
    hastestduedate = False
    hasvacc = False
    hasvaccduedate = False
    hasincident = False
    hasincidentdate = False
    hasinvestigation = False
    hasperson = False
    haspersonlastname = False
    haspersonname = False
    haslicence = False
    haslicencenumber = False
    hascost = False
    hascostamount = False
    haslog = False
    haslogcomments = False
    hasmovement = False
    hasmovementdate = False
    hasdonation = False
    hasdonationamount = False
    hasoriginalowner = False
    hasoriginalownerlastname = False
    hascurrentvet = False
    hascurrentvetlastname = False
    hasdiary = False
    hasvoucher = False
    hasstocklevel = False
    hasstocklevelname = False
    hasstockleveltotal = False
    hasstocklevelbalance = False

    cols = rows[0].keys()
    for col in cols:
        if col in VALID_FIELDS: onevalid = True
        if col.startswith("ANIMAL"): hasanimal = True
        if col == "ANIMALNAME": hasanimalname = True
        if col.startswith("ORIGINALOWNER"): hasoriginalowner = True
        if col.startswith("CITATION"): hascitation = True
        if col.startswith("CLINIC"): hasclinic = True
        if col.startswith("CURRENTVET"): hascurrentvet = True
        if col.startswith("CURRENTVETLASTNAME"): hascurrentvetlastname = True
        if col.startswith("LOANDATE"): hasequipmentloan = True
        if col.startswith("VACCINATION"): hasvacc = True
        if col == "VACCINATIONDUEDATE": hasvaccduedate = True
        if col.startswith("TEST"): hastest = True
        if col == "TESTDUEDATE": hastestduedate = True
        if col.startswith("MEDICAL"): hasmed = True
        if col == "MEDICALGIVENDATE": hasmedicalgivendate = True
        if col == "MEDICALNAME": hasmedicalname = True
        if col.startswith("INCIDENT"): hasincident = True
        if col == "INCIDENTDATE": hasincidentdate = True
        if col.startswith("INVESTIGATION"): hasinvestigation = True
        if col.startswith("LICENSE"): haslicence = True
        if col == "LICENSENUMBER": haslicencenumber = True
        if col.startswith("COST"): hascost = True
        if col == "COSTAMOUNT": hascostamount = True
        if col.startswith("LOG"): haslog = True
        if col == "LOGCOMMENTS": haslogcomments = True
        if col == "ORIGINALOWNERLASTNAME": hasoriginalownerlastname = True
        if col.startswith("PERSON"): hasperson = True
        if col == "PERSONLASTNAME": haspersonlastname = True
        if col == "PERSONNAME": haspersonname = True
        if col.startswith("MOVEMENT"): hasmovement = True
        if col == "MOVEMENTDATE": hasmovementdate = True
        if col.startswith("DONATION"): hasdonation = True
        if col == "DONATIONAMOUNT": hasdonationamount = True
        if col == "DIARYDATE": hasdiary = True
        if col.startswith("VOUCHER"): hasvoucher = True
        if col.startswith("STOCKLEVEL"): hasstocklevel = True
        if col.startswith("STOCKLEVELNAME"): hasstocklevelname = True
        if col.startswith("STOCKLEVELTOTAL"): hasstockleveltotal = True
        if col.startswith("STOCKLEVELBALANCE"): hasstocklevelbalance = True

    rules = [
        ( not onevalid, "Your CSV file did not contain any fields that ASM recognises" ),
        ( hasanimal and not hasanimalname, "Your CSV file has animal fields, but no ANIMALNAME column" ),
        ( hasperson and not haspersonlastname and not haspersonname, "Your CSV file has person fields, but no PERSONNAME or PERSONLASTNAME column" ),
        ( hascurrentvet and not hascurrentvetlastname, "Your CSV file has current vet fields, but no CURRENTVETLASTNAME column" ),
        ( hasoriginalowner and not hasoriginalownerlastname, "Your CSV file has original owner fields, but no ORIGINALOWNERLASTNAME column" ),
        ( hasmovement and not hasmovementdate, "Your CSV file has movement fields, but no MOVEMENTDATE column" ),
        ( hasdonation and not hasdonationamount, "Your CSV file has donation fields, but no DONATIONAMOUNT column" ),
        ( hasdonation and not (haspersonlastname or haspersonname), "Your CSV file has donation fields, but no person to apply the donation to" ),
        ( hasmed and not (hasmedicalname or hasmedicalgivendate), "Your CSV file has medical fields, but no MEDICALNAME or MEDICALGIVENDATE columns" ),
        ( hasmed and not hasanimal, "Your CSV file has medical fields, but no animal to apply them to" ),
        ( hasvacc and not hasvaccduedate, "Your CSV file has vaccination fields, but no VACCINATIONDUEDATE column" ),
        ( hasvacc and not hasanimal, "Your CSV file has vaccination fields, but no animal to apply them to" ),
        ( hastest and not hastestduedate, "Your CSV file has test fields, but no TESTDUEDATE column" ),
        ( hastest and not hasanimal, "Your CSV file has test fields, but no animal to apply them to" ),
        ( hascost and not hasanimal, "Your CSV file has cost fields, but no animal to apply them to" ),
        ( hascost and not hascostamount, "Your CSV file has cost fields, but no COSTAMOUNT column" ),
        ( hasdiary and not hasanimal and not hasperson and not hasincident, "Your CSV file has diary fields, but no animal, person or incident to apply them to"),
        ( haslog and not hasanimal, "Your CSV file has log fields, but no animal to apply them to" ),
        ( haslog and not haslogcomments, "Your CSV file has log fields, but no LOGCOMMENTS column" ),
        ( hasincident and not hasincidentdate, "Your CSV file has incident fields, but no INCIDENTDATE column" ),
        ( hasincident and not hasperson, "Your CSV file has incident fields, but no person to set as the caller" ),
        ( haslicence and not haslicencenumber, "Your CSV file has license fields, but no LICENSENUMBER column" ),
        ( haslicence and not (haspersonlastname or haspersonname), "Your CSV file has license fields, but no person to apply the license to" ),
        ( hasstocklevel and not hasstocklevelname, "Your CSV file has stock level fields, but no STOCKLEVELNAME column" ),
        ( hasstocklevel and not hasstockleveltotal, "Your CSV file has stock level fields, but no STOCKLEVELTOTAL column" ),
        ( hasstocklevel and not hasstocklevelbalance, "Your CSV file has stock level fields, but no STOCKLEVELBALANCE column" )
    ]
    for cond, msg in rules:
        if cond:
            asm3.asynctask.set_last_error(dbo, msg)
            return asm3.asynctask.get_last_error(dbo)

    asm3.al.debug("reading CSV data, found %d rows" % len(rows), "csvimport.csvimport", dbo)

    # If we're clearing down tables first, do it now
    if cleartables and not dryrun:
        asm3.al.warn("Resetting the database by removing all non-lookup data", "csvimport.csvimport", dbo)
        asm3.dbupdate.reset_db(dbo)

    # Now that we've read them in, go through all the rows
    # and start importing.
    errors = []
    rowno = 1
    animalcodes = {}
    asm3.asynctask.set_progress_max(dbo, len(rows))
    for row in rows:

        asm3.al.debug("import csv: row %d of %d" % (rowno, len(rows)), "csvimport.csvimport", dbo)
        asm3.asynctask.increment_progress_value(dbo)

        # Should we stop?
        if asm3.asynctask.get_cancel(dbo): break

        # Do we have animal data to read?
        animalid = 0
        nonshelter = False
        originalownerid = 0
        if hasanimal and gks(row, "ANIMALNAME") != "":
            animalcode = gks(row, "ANIMALCODE")
            # If we're prefixing animal codes, we insert a prefix. The prefix is repeatable
            # based on the position in the file. This means that codes in a file can't clash with
            # normal codes in the database, but if you import the exact same file again, you'll
            # get a repeatable code and it will update the same record.
            if prefixanimalcodes:
                if animalcode in animalcodes:
                    animalcode = animalcodes[animalcode]
                else:
                    pcode = f"CSV{rowno:04}.{animalcode}"
                    animalcodes[animalcode] = pcode
                    animalcode = pcode
            a = {}
            a["animalname"] = gks(row, "ANIMALNAME")
            a["sheltercode"] = animalcode
            a["shortcode"] = animalcode
            a["litterid"] = gks(row, "ANIMALLITTER")
            if gks(row, "ANIMALSEX") == "": 
                a["sex"] = "2" # Default unknown if not set
            else:
                a["sex"] = gksx(row, "ANIMALSEX")
            a["basecolour"] = gkl(dbo, row, "ANIMALCOLOR", "basecolour", "BaseColour", createmissinglookups)
            if a["basecolour"] == "0":
                a["basecolour"] = str(asm3.configuration.default_colour(dbo))
            a["species"] = gkl(dbo, row, "ANIMALSPECIES", "species", "SpeciesName", createmissinglookups)
            if a["species"] == "0":
                a["species"] = str(asm3.configuration.default_species(dbo))
            a["animaltype"] = gkl(dbo, row, "ANIMALTYPE", "animaltype", "AnimalType", createmissinglookups)
            if a["animaltype"] == "0":
                a["animaltype"] = str(asm3.configuration.default_type(dbo))
            a["breed1"] = gkbr(dbo, row, "ANIMALBREED1", a["species"], createmissinglookups)
            if a["breed1"] == "0":
                a["breed1"] = str(asm3.configuration.default_breed(dbo))
            a["breed2"] = gkbr(dbo, row, "ANIMALBREED2", a["species"], createmissinglookups)
            if a["breed2"] != "0" and a["breed2"] != a["breed1"]:
                a["crossbreed"] = "on"
            a["size"] = gkl(dbo, row, "ANIMALSIZE", "lksize", "Size", False)
            if gks(row, "ANIMALSIZE") == "": 
                a["size"] = str(asm3.configuration.default_size(dbo))
            a["weight"] = gks(row, "ANIMALWEIGHT")
            a["internallocation"] = gkl(dbo, row, "ANIMALLOCATION", "internallocation", "LocationName", createmissinglookups)
            if a["internallocation"] == "0":
                a["internallocation"] = str(asm3.configuration.default_location(dbo))
            a["jurisdiction"] = gkl(dbo, row, "ANIMALJURISDICTION", "jurisdiction", "JurisdictionName", createmissinglookups)
            if a["jurisdiction"] == "0":
                a["jurisdiction"] = str(asm3.configuration.default_jurisdiction(dbo))
            a["pickuplocation"] = gkl(dbo, row, "ANIMALPICKUPLOCATION", "pickuplocation", "LocationName", createmissinglookups)
            if a["pickuplocation"] != "0":
                a["pickedup"] = "on"
            a["pickupaddress"] = gks(row, "ANIMALPICKUPADDRESS")
            if a["pickupaddress"] != "":
                a["pickedup"] = "on"
            a["entrytype"] = gkl(dbo, row, "ANIMALENTRYTYPE", "lksentrytype", "EntryTypeName", False)
            if a["entrytype"] == "0":
                a["entrytype"] = str(asm3.configuration.default_entry_type(dbo))
            a["entryreason"] = gkl(dbo, row, "ANIMALENTRYCATEGORY", "entryreason", "ReasonName", createmissinglookups)
            if a["entryreason"] == "0":
                a["entryreason"] = str(asm3.configuration.default_entry_reason(dbo))
            a["unit"] = gks(row, "ANIMALUNIT")
            a["comments"] = gks(row, "ANIMALCOMMENTS") or gks(row, "ANIMALDESCRIPTION")
            a["markings"] = gks(row, "ANIMALMARKINGS")
            a["hiddenanimaldetails"] = gks(row, "ANIMALHIDDENDETAILS")
            a["popupwarning"] = gks(row, "ANIMALWARNING")
            a["healthproblems"] = gks(row, "ANIMALHEALTHPROBLEMS")
            a["notforadoption"] = gkbi(row, "ANIMALNOTFORADOPTION")
            a["nonshelter"] = gkbc(row, "ANIMALNONSHELTER")
            nonshelter = a["nonshelter"] == "on"
            a["transferin"] = gkbc(row, "ANIMALTRANSFER")
            a["housetrained"] = gkynu(row, "ANIMALHOUSETRAINED")
            a["cratetrained"] = gkynu(row, "ANIMALCRATETRAINED")
            a["goodwithcats"] = gkynu(row, "ANIMALGOODWITHCATS")
            a["goodwithdogs"] = gkynu(row, "ANIMALGOODWITHDOGS")
            a["goodwithkids"] = gkynu(row, "ANIMALGOODWITHKIDS")
            a["goodwithelderly"] = gkynu(row, "ANIMALGOODWITHELDERLY")
            a["goodonlead"] = gkynu(row, "ANIMALGOODONLEAD")
            a["goodtraveller"] = gkynu(row, "ANIMALGOODTRAVELLER")
            a["energylevel"] = gks(row, "ANIMALENERGYLEVEL")
            a["reasonforentry"] = gks(row, "ANIMALREASONFORENTRY")
            a["estimatedage"] = gks(row, "ANIMALAGE")
            a["dateofbirth"] = gkd(dbo, row, "ANIMALDOB")
            if gks(row, "ANIMALDOB") == "" and a["estimatedage"] != "":
                a["dateofbirth"] = "" # if we had an age and dob was blank, prefer the age
            a["datebroughtin"] = gkd(dbo, row, "ANIMALENTRYDATE", True)
            a["timebroughtin"] = gks(row, "ANIMALENTRYTIME")
            if entrytoday: 
                a["datebroughtin"] = asm3.i18n.python2display(dbo.locale, dbo.today())
            a["deceaseddate"] = gkd(dbo, row, "ANIMALDECEASEDDATE")
            a["ptsreason"] = gks(row, "ANIMALDECEASEDNOTES")
            a["puttosleep"] = gkbc(row, "ANIMALEUTHANIZED")
            a["deathcategory"] = gkl(dbo, row, "ANIMALDECEASEDREASON", "deathreason", "ReasonName", createmissinglookups)
            if a["deathcategory"] == "0":
                a["deathcategory"] = str(asm3.configuration.default_death_reason(dbo))
            a["neutered"] = gkbc(row, "ANIMALNEUTERED")
            a["neutereddate"] = gkd(dbo, row, "ANIMALNEUTEREDDATE")
            if a["neutereddate"] != "": a["neutered"] = "on"
            a["microchipnumber"] = gks(row, "ANIMALMICROCHIP")
            if a["microchipnumber"] != "": a["microchipped"] = "on"
            a["microchipdate"] = gkd(dbo, row, "ANIMALMICROCHIPDATE")
            a["tattoonumber"] = gks(row, "ANIMALTATTOO")
            if a["tattoonumber"] != "": a["tattoo"] = "on"
            a["tattoodate"] = gkd(dbo, row, "ANIMALTATTOODATE")
            a["flags"] = gks(row, "ANIMALFLAGS")
            a["declawed"] = gkbc(row, "ANIMALDECLAWED")
            a["specialneeds"] = gkbc(row, "ANIMALHASSPECIALNEEDS")
            a["coattype"] = gkl(dbo, row, "ANIMALCOATTYPE", "lkcoattype", "CoatType", createmissinglookups)
            # image data if any was supplied
            imagedata = gks(row, "ANIMALIMAGE")
            if imagedata != "":
                if imagedata.startswith("http"):
                    # It's a URL, get the image from the remote server
                    r = asm3.utils.get_url_bytes(imagedata, timeout=5000, exceptions=False)
                    if r["status"] == 200:
                        asm3.al.debug("retrieved image from %s (%s bytes)" % (imagedata, len(r["response"])), "csvimport.csvimport", dbo)
                        imagedata = "data:image/jpeg;base64,%s" % asm3.utils.base64encode(r["response"])
                    else:
                        row_error(errors, "animal", rowno, row, "error reading image from '%s': %s" % (imagedata, r), dbo, sys.exc_info())
                        continue
                elif imagedata.startswith("data:image"):
                    # It's a base64 encoded data URI - do nothing as attach_file requires it
                    pass
                else:
                    # We don't know what it is, don't try and do anything with it
                    row_error(errors, "animal", rowno, row, "WARN: unrecognised image content, ignoring", dbo, sys.exc_info())
                    imagedata = ""
            # pdf data if any was supplied
            pdfdata = gks(row, "ANIMALPDFDATA")
            pdfname = gks(row, "ANIMALPDFNAME")
            if pdfdata != "":
                if pdfdata.startswith("http"):
                    # It's a URL, get the PDF from the remote server
                    r = asm3.utils.get_url_bytes(pdfdata, timeout=5000, exceptions=False)
                    if r["status"] == 200:
                        asm3.al.debug("retrieved PDF from %s (%s bytes)" % (pdfdata, len(r["response"])), "csvimport.csvimport", dbo)
                        pdfdata = "data:application/pdf;base64,%s" % asm3.utils.base64encode(r["response"])
                    else:
                        row_error(errors, "animal", rowno, row, "error reading pdf from '%s': %s" % (pdfdata, r), dbo, sys.exc_info())
                        continue
                elif pdfdata.startswith("data:"):
                    # It's a base64 encoded data URI - do nothing as attach_file requires it
                    pass
                else:
                    # We don't know what it is, don't try and do anything with it
                    row_error(errors, "animal", rowno, row, "WARN: unrecognised PDF content, ignoring", dbo, sys.exc_info())
                    pdfdata = ""
                if pdfdata != "" and pdfname == "":
                    row_error(errors, "animal", rowno, row, "ANIMALPDFNAME must be set for data", dbo, sys.exc_info())
                    continue

            # media data if any was supplied
            htmldata = gks(row, "ANIMALHTMLDATA")
            htmlname = gks(row, "ANIMALHTMLNAME")
            if htmldata != "":
                if htmldata.startswith("http"):
                    # It's a URL, get the PDF from the remote server
                    r = asm3.utils.get_url_bytes(htmldata, timeout=5000, exceptions=False)
                    if r["status"] == 200:
                        asm3.al.debug("retrieved HTML document from %s (%s bytes)" % (htmldata, len(r["response"])), "csvimport.csvimport", dbo)
                        htmldata = "data:text/html;base64,%s" % asm3.utils.base64encode(r["response"])
                    else:
                        row_error(errors, "animal", rowno, row, "error reading html data from '%s': %s" % (htmldata, r), dbo, sys.exc_info())
                        continue
                elif htmldata.startswith("data:"):
                    # It's a base64 encoded data URI - do nothing as attach_file requires it
                    pass
                else:
                    # We don't know what it is, don't try and do anything with it
                    row_error(errors, "animal", rowno, row, "WARN: unrecognised HTML content, ignoring", dbo, sys.exc_info())
                    htmldata = ""
                if htmldata != "" and htmlname == "":
                    row_error(errors, "animal", rowno, row, "ANIMALHTMLNAME must be set for data", dbo, sys.exc_info())
                    continue

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
                p["jurisdiction"] = gkl(dbo, row, "ORIGINALOWNERJURISDICTION", "jurisdiction", "JurisdictionName", createmissinglookups)
                if p["jurisdiction"] == "0":
                    p["jurisdiction"] = str(asm3.configuration.default_jurisdiction(dbo))
                p["hometelephone"] = gks(row, "ORIGINALOWNERHOMEPHONE")
                p["worktelephone"] = gks(row, "ORIGINALOWNERWORKPHONE")
                p["mobiletelephone"] = gks(row, "ORIGINALOWNERCELLPHONE")
                p["emailaddress"] = gks(row, "ORIGINALOWNEREMAIL")
                p["flags"] = gks(row, "ORIGINALOWNERFLAGS")
                p["popupwarning"] = gks(row, "ORIGINALOWNERWARNING")
                try:
                    originalownerid = 0
                    if checkduplicates:
                        dups = asm3.person.get_person_similar(dbo, p["emailaddress"], p["mobiletelephone"], p["surname"], p["forenames"], p["address"])
                        if len(dups) > 0:
                            originalownerid = dups[0]["ID"]
                    if originalownerid == 0:
                        originalownerid = asm3.person.insert_person_from_form(dbo, asm3.utils.PostedData(p, dbo.locale), user, geocode=False)
                    # Identify any ORIGINALOWNERADDITIONAL additional fields and create/merge them
                    if originalownerid > 0:
                        if not dryrun: create_additional_fields(dbo, row, errors, rowno, "ORIGINALOWNERADDITIONAL", "person", originalownerid)
                    if "transferin" in a and a["transferin"] == "on":
                        a["broughtinby"] = str(originalownerid) # set original owner as transferor for transfers in
                    elif "nonshelter" in a and a["nonshelter"] == "on": # set nsowner for non-shelter animals
                        a["nsowner"] = str(originalownerid)
                    else:
                        a["originalowner"] = str(originalownerid)
                except Exception as e:
                    row_error(errors, "originalowner", rowno, row, e, dbo, sys.exc_info())
            # If a current vet is specified, create a person record
            # for them and attach it to the animal as currentvet
            if gks(row, "CURRENTVETLASTNAME") != "":
                p = {}
                p["title"] = gks(row, "CURRENTVETTITLE")
                p["initials"] = gks(row, "CURRENTVETINITIALS")
                p["forenames"] = gks(row, "CURRENTVETFIRSTNAME")
                p["surname"] = gks(row, "CURRENTVETLASTNAME")
                p["address"] = gks(row, "CURRENTVETADDRESS")
                p["town"] = gks(row, "CURRENTVETCITY")
                p["county"] = gks(row, "CURRENTVETSTATE")
                p["postcode"] = gks(row, "CURRENTVETZIPCODE")
                p["jurisdiction"] = gkl(dbo, row, "CURRENTVETJURISDICTION", "jurisdiction", "JurisdictionName", createmissinglookups)
                if p["jurisdiction"] == "0":
                    p["jurisdiction"] = str(asm3.configuration.default_jurisdiction(dbo))
                p["hometelephone"] = gks(row, "CURRENTVETHOMEPHONE")
                p["worktelephone"] = gks(row, "CURRENTVETWORKPHONE")
                p["mobiletelephone"] = gks(row, "CURRENTVETCELLPHONE")
                p["emailaddress"] = gks(row, "CURRENTVETEMAIL")
                p["flags"] = gks(row, "CURRENTVETFLAGS")
                try:
                    cvid = 0
                    if checkduplicates:
                        dups = asm3.person.get_person_similar(dbo, p["emailaddress"], p["mobiletelephone"], p["surname"], p["forenames"], p["address"])
                        if len(dups) > 0:
                            cvid = dups[0]["ID"]
                            a["currentvet"] = str(cvid)
                    if "currentvet" not in a:
                        if not dryrun: 
                            cvid = asm3.person.insert_person_from_form(dbo, asm3.utils.PostedData(p, dbo.locale), user, geocode=False)
                            a["currentvet"] = str(cvid)
                    # If both a current vet and neutering date has been given, set the neutering vet
                    if "currentvet" in a and "neutereddate" in a and a["neutereddate"] != "":
                        a["neuteringvet"] = a["currentvet"]
                    # Identify any CURRENTVETADDITIONAL additional fields and create/merge them
                    if cvid > 0: create_additional_fields(dbo, row, errors, rowno, "CURRENTVETADDITIONAL", "person", cvid)
                except Exception as e:
                    row_error(errors, "currentvet", rowno, row, e, dbo, sys.exc_info())
            try:
                if checkduplicates:
                    dup = asm3.animal.get_animal_sheltercode(dbo, a["sheltercode"])
                    if dup is not None:
                        # We already have an animal record with this code, update it
                        animalid = dup.ID
                        # If the weight has been changed, it may need to be logged if the
                        # option is on. We run it here before merge_animal_details updates it so that
                        # it can check the previous weight to see if it is different 
                        if gks(row, "ANIMALWEIGHT") != "": 
                            asm3.animal.insert_weight_log(dbo, user, animalid, asm3.utils.cfloat(gks(row, "ANIMALWEIGHT")), dup.WEIGHT)
                        # The code above will set internallocation to the default if not supplied, assuming we're going to create
                        # a new animal. If no actual location was given in the file, we remove that default location
                        # value now to prevent merge_animal_details overwriting the existing value on the record. #1516
                        if gks(row, "ANIMALLOCATION") == "": a["internallocation"] = "0"
                        # Overwrite newly supplied fields if they are present and have a value
                        asm3.animal.merge_animal_details(dbo, user, dup.ID, a, force=True)
                        # Update flags if present
                        if a["flags"] != "":
                            asm3.animal.update_flags(dbo, user, dup.ID, a["flags"].split(","))
                if animalid == 0 and not dryrun:
                    animalid, dummy = asm3.animal.insert_animal_from_form(dbo, asm3.utils.PostedData(a, dbo.locale), user)
                    # Add any flags that were set
                    if a["flags"] != "":
                        asm3.animal.update_flags(dbo, user, animalid, a["flags"].split(","))
                # Identify any ANIMALADDITIONAL additional fields and create/merge them
                if not dryrun: create_additional_fields(dbo, row, errors, rowno, "ANIMALADDITIONAL", "animal", animalid)
                # If we have some image data, add it to the animal
                if len(imagedata) > 0 and not dryrun:
                    imagepost = asm3.utils.PostedData({ "filename": "image.jpg", "filetype": "image/jpeg", "filedata": imagedata }, dbo.locale)
                    asm3.media.attach_file_from_form(dbo, user, asm3.media.ANIMAL, animalid, asm3.media.MEDIASOURCE_CSVIMPORT, imagepost)
                # If we have some PDF data, add that to the animal
                if len(pdfdata) > 0 and not dryrun:
                    pdfpost = asm3.utils.PostedData({ "filename": pdfname, "filetype": "application/pdf", "filedata": pdfdata }, dbo.locale)
                    asm3.media.attach_file_from_form(dbo, user, asm3.media.ANIMAL, animalid, asm3.media.MEDIASOURCE_CSVIMPORT, pdfpost)
                # If we have some HTML data, add that to the animal
                if len(htmldata) > 0 and not dryrun:
                    htmlpost = asm3.utils.PostedData({ "filename": htmlname, "filetype": "text/html", "filedata": htmldata }, dbo.locale)
                    asm3.media.attach_file_from_form(dbo, user, asm3.media.ANIMAL, animalid, asm3.media.MEDIASOURCE_CSVIMPORT, htmlpost)
            except Exception as e:
                row_error(errors, "animal", rowno, row, e, dbo, sys.exc_info())

        # Person data?
        personid = 0
        if hasperson:
            if gks(row, "PERSONLASTNAME") != "" or gks(row, "PERSONNAME") != "":
                p = {}
                p["ownercode"] = gks(row, "PERSONCODE")
                p["ownertype"] = gks(row, "PERSONCLASS")
                if p["ownertype"] not in ("1", "2", "3"): 
                    p["ownertype"] = "1"
                if gks(row, "PERSONLASTNAME2") != "":
                    p["ownertype"] = "3"
                p["title"] = gks(row, "PERSONTITLE")
                p["title2"] = gks(row, "PERSONTITLE2")
                p["initials"] = gks(row, "PERSONINITIALS")
                p["initials2"] = gks(row, "PERSONINITIALS2")
                p["forenames"] = gks(row, "PERSONFIRSTNAME")
                p["forenames2"] = gks(row, "PERSONFIRSTNAME2")
                p["surname"] = gks(row, "PERSONLASTNAME")
                p["surname2"] = gks(row, "PERSONLASTNAME2")
                # If we have a person name, all upto the last space is first names,
                # everything after the last name
                if gks(row, "PERSONNAME") != "":
                    pname = gks(row, "PERSONNAME")
                    if pname.find(" ") != -1:
                        p["forenames"] = pname[0:pname.rfind(" ")]
                        p["surname"] = pname[pname.rfind(" ")+1:]
                    else:
                        p["surname"] = pname
                p["dateofbirth"] = gkd(dbo, row, "PERSONDATEOFBIRTH")
                p["dateofbirth2"] = gkd(dbo, row, "PERSONDATEOFBIRTH2")
                p["idnumber"] = gks(row, "PERSONIDNUMBER")
                p["idnumber2"] = gks(row, "PERSONIDNUMBER2")
                p["address"] = gks(row, "PERSONADDRESS")
                p["town"] = gks(row, "PERSONCITY")
                p["county"] = gks(row, "PERSONSTATE")
                p["postcode"] = gks(row, "PERSONZIPCODE")
                p["jurisdiction"] = gkl(dbo, row, "PERSONJURISDICTION", "jurisdiction", "JurisdictionName", createmissinglookups)
                if p["jurisdiction"] == "0":
                    p["jurisdiction"] = str(asm3.configuration.default_jurisdiction(dbo))
                p["hometelephone"] = gks(row, "PERSONHOMEPHONE")
                p["hometelephone2"] = gks(row, "PERSONHOMEPHONE2")
                p["worktelephone"] = gks(row, "PERSONWORKPHONE")
                p["worktelephone2"] = gks(row, "PERSONWORKPHONE2")
                p["mobiletelephone"] = gks(row, "PERSONCELLPHONE")
                p["mobiletelephone2"] = gks(row, "PERSONCELLPHONE2")
                p["emailaddress"] = gks(row, "PERSONEMAIL")
                p["emailaddress2"] = gks(row, "PERSONEMAIL2")
                p["gdprcontactoptin"] = gks(row, "PERSONGDPRCONTACTOPTIN")
                flags = gks(row, "PERSONFLAGS")
                if gkb(row, "PERSONFOSTERER"): flags += ",fosterer"
                if gkb(row, "PERSONMEMBER"): flags += ",member"
                if gkb(row, "PERSONDONOR"): flags += ",donor"
                p["flags"] = flags
                p["comments"] = gks(row, "PERSONCOMMENTS")
                p["popupwarning"] = gks(row, "PERSONWARNING")
                p["membershipnumber"] = gks(row, "PERSONMEMBERSHIPNUMBER")
                p["membershipexpires"] = gkd(dbo, row, "PERSONMEMBERSHIPEXPIRY")
                p["matchactive"] = gkbi(row, "PERSONMATCHACTIVE")
                p["fostercapacity"] = gks(row,"PERSONFOSTERCAPACITY")
                if p["matchactive"] == "1":
                    if "PERSONMATCHADDED" in cols: p["matchadded"] = gkd(dbo, row, "PERSONMATCHADDED")
                    if "PERSONMATCHEXPIRES" in cols: p["matchexpires"] = gkd(dbo, row, "PERSONMATCHEXPIRES")
                    if "PERSONMATCHSEX" in cols: p["matchsex"] = gksx(row, "PERSONMATCHSEX")
                    if "PERSONMATCHSIZE" in cols: p["matchsize"] = gkl(dbo, row, "PERSONMATCHSIZE", "lksize", "Size", False)
                    if "PERSONMATCHCOLOR" in cols: p["matchcolour"] = gkl(dbo, row, "PERSONMATCHCOLOR", "basecolour", "BaseColour", createmissinglookups)
                    if "PERSONMATCHAGEFROM" in cols: p["agedfrom"] = gks(row, "PERSONMATCHAGEFROM")
                    if "PERSONMATCHAGETO" in cols: p["agedto"] = gks(row, "PERSONMATCHAGETO")
                    if "PERSONMATCHTYPE" in cols: p["matchanimaltype"] = gkl(dbo, row, "PERSONMATCHTYPE", "animaltype", "AnimalType", createmissinglookups)
                    if "PERSONMATCHSPECIES" in cols: p["matchspecies"] = gkl(dbo, row, "PERSONMATCHSPECIES", "species", "SpeciesName", createmissinglookups)
                    if "PERSONMATCHBREED1" in cols: p["matchbreed"] = gkbr(dbo, row, "PERSONMATCHBREED1", p["matchspecies"], createmissinglookups)
                    if "PERSONMATCHBREED2" in cols: p["matchbreed2"] = gkbr(dbo, row, "PERSONMATCHBREED2", p["matchspecies"], createmissinglookups)
                    if "PERSONMATCHGOODWITHCATS" in cols: p["matchgoodwithcats"] = gkynu(row, "PERSONMATCHGOODWITHCATS")
                    if "PERSONMATCHGOODWITHDOGS" in cols: p["matchgoodwithdogs"] = gkynu(row, "PERSONMATCHGOODWITHDOGS")
                    if "PERSONMATCHGOODWITHCHILDREN" in cols: p["matchgoodwithchildren"] = gkynu(row, "PERSONMATCHGOODWITHCHILDREN")
                    if "PERSONMATCHGOODWITHELDERLY" in cols: p["matchgoodwithelderly"] = gkynu(row, "PERSONMATCHGOODWITHELDERLY")
                    if "PERSONMATCHGOODONLEAD" in cols: p["matchgoodonlead"] = gkynu(row, "PERSONMATCHGOODONLEAD")
                    if "PERSONMATCHGOODTRAVELLER" in cols: p["matchgoodtraveller"] = gkynu(row, "PERSONMATCHGOODTRAVELLER")
                    if "PERSONMATCHHOUSETRAINED" in cols: p["matchhousetrained"] = gkynu(row, "PERSONMATCHHOUSETRAINED")
                    if "PERSONMATCHCRATETRAINED" in cols: p["matchcratetrained"] = gkynu(row, "PERSONMATCHCRATETRAINED")
                    if "PERSONMATCHENERGYLEVEL" in cols: p["matchenergylevel"] = gkynu(row, "PERSONMATCHENERGYLEVEL")
                    if "PERSONMATCHCOMMENTSCONTAIN" in cols: p["matchcommentscontain"] = gks(row, "PERSONMATCHCOMMENTSCONTAIN")
                
                imagedata = gks(row, "PERSONIMAGE")
                if imagedata != "":
                    if imagedata.startswith("http"):
                        # It's a URL, get the image from the remote server
                        r = asm3.utils.get_url_bytes(imagedata, timeout=5000, exceptions=False)
                        if r["status"] == 200:
                            asm3.al.debug("retrieved image from %s (%s bytes)" % (imagedata, len(r["response"])), "csvimport.csvimport", dbo)
                            imagedata = "data:image/jpeg;base64,%s" % asm3.utils.base64encode(r["response"])
                        else:
                            row_error(errors, "person", rowno, row, "error reading image from '%s': %s" % (imagedata, r), dbo, sys.exc_info())
                            continue
                    elif imagedata.startswith("data:image"):
                        # It's a base64 encoded data URI - do nothing as attach_file requires it
                        pass
                    else:
                        # We don't know what it is, don't try and do anything with it
                        row_error(errors, "person", rowno, row, "WARN: unrecognised image content, ignoring", dbo, sys.exc_info())
                        imagedata = ""
                # pdf data if any was supplied
                pdfdata = gks(row, "PERSONPDFDATA")
                pdfname = gks(row, "PERSONPDFNAME")
                if pdfdata != "":
                    if pdfdata.startswith("http"):
                        # It's a URL, get the PDF from the remote server
                        r = asm3.utils.get_url_bytes(pdfdata, timeout=5000, exceptions=False)
                        if r["status"] == 200:
                            asm3.al.debug("retrieved PDF from %s (%s bytes)" % (pdfdata, len(r["response"])), "csvimport.csvimport", dbo)
                            pdfdata = "data:application/pdf;base64,%s" % asm3.utils.base64encode(r["response"])
                        else:
                            row_error(errors, "person", rowno, row, "error reading pdf from '%s': %s" % (pdfdata, r), dbo, sys.exc_info())
                            continue
                    elif pdfdata.startswith("data:"):
                        # It's a base64 encoded data URI - do nothing as attach_file requires it
                        pass
                    else:
                        # We don't know what it is, don't try and do anything with it
                        row_error(errors, "person", rowno, row, "WARN: unrecognised PDF content, ignoring", dbo, sys.exc_info())
                        pdfdata = ""
                    if pdfdata != "" and pdfname == "":
                        row_error(errors, "person", rowno, row, "PERSONPDFNAME must be set for data", dbo, sys.exc_info())
                        continue
                        
                try:
                    if checkduplicates:
                        personid = asm3.person.get_person_id_for_code(dbo, p["ownercode"])
                        if personid == 0:
                            dups = asm3.person.get_person_similar(dbo, p["emailaddress"], p["mobiletelephone"], p["surname"], p["forenames"], p["address"])
                            if len(dups) > 0:
                                personid = dups[0].ID
                        if personid != 0 and not dryrun:
                            # Merge flags and any extra details
                            asm3.person.merge_flags(dbo, user, personid, flags)
                            asm3.person.merge_gdpr_flags(dbo, user, personid, p["gdprcontactoptin"])
                            # If we deduplicated on the email address, and address details are
                            # present, assume that they are newer than the ones we had and update them
                            # (we do this by setting force=True parameter to merge_person_details,
                            # otherwise we do a regular merge which only fills in any blanks)
                            force = dbo.query_string("SELECT EmailAddress FROM owner WHERE ID=?", [personid]) == p["emailaddress"]
                            asm3.person.merge_person_details(dbo, user, personid, p, force=force)
                    if personid == 0 and not dryrun:
                        personid = asm3.person.insert_person_from_form(dbo, asm3.utils.PostedData(p, dbo.locale), user, geocode=False)
                    # Identify any PERSONADDITIONAL additional fields and create/merge them
                    if not dryrun: create_additional_fields(dbo, row, errors, rowno, "PERSONADDITIONAL", "person", personid)
                    # If we have some image data, add it to the person
                    if len(imagedata) > 0 and not dryrun:
                        imagepost = asm3.utils.PostedData({ "filename": "image.jpg", "filetype": "image/jpeg", "filedata": imagedata }, dbo.locale)
                        asm3.media.attach_file_from_form(dbo, user, asm3.media.PERSON, personid, asm3.media.MEDIASOURCE_CSVIMPORT, imagepost)
                    # If we have some PDF data, add that to the person
                    if len(pdfdata) > 0 and not dryrun:
                        pdfpost = asm3.utils.PostedData({ "filename": pdfname, "filetype": "application/pdf", "filedata": pdfdata }, dbo.locale)
                        asm3.media.attach_file_from_form(dbo, user, asm3.media.PERSON, personid, asm3.media.MEDIASOURCE_CSVIMPORT, pdfpost)
                except Exception as e:
                    row_error(errors, "person", rowno, row, e, dbo, sys.exc_info())

        # Movement to tie animal/person together?
        movementid = 0
        if hasmovement and animalid != 0 and gks(row, "MOVEMENTDATE") != "":
            m = {}
            m["person"] = str(personid)
            m["animal"] = str(animalid)
            movetype = gks(row, "MOVEMENTTYPE")
            if movetype == "": movetype = "1" # Default to adoption if not supplied
            m["type"] = str(movetype)
            if movetype == "0":
                m["reservationdate"] = gkd(dbo, row, "MOVEMENTDATE", True)
                m["reservationcancelled"] = gkd(dbo, row, "MOVEMENTRETURNDATE")
            else:
                m["movementdate"] = gkd(dbo, row, "MOVEMENTDATE", True)
                m["returndate"] = gkd(dbo, row, "MOVEMENTRETURNDATE")
            m["comments"] = gks(row, "MOVEMENTCOMMENTS")
            m["returncategory"] = str(asm3.configuration.default_entry_reason(dbo))
            try:
                if dryrun:
                    asm3.movement.validate_movement_form_data(dbo, user, asm3.utils.PostedData(m, dbo.locale))
                else:
                    movementid = asm3.movement.insert_movement_from_form(dbo, user, asm3.utils.PostedData(m, dbo.locale))
            except Exception as e:
                row_error(errors, "movement", rowno, row, e, dbo, sys.exc_info())

        # Donation?
        if hasdonation and personid != 0 and gkc(row, "DONATIONAMOUNT") != 0:
            d = {}
            d["person"] = str(personid)
            d["animal"] = str(animalid)
            d["movement"] = str(movementid)
            d["amount"] = str(gkc(row, "DONATIONAMOUNT"))
            d["fee"] = str(gkc(row, "DONATIONFEE"))
            d["comments"] = gks(row, "DONATIONCOMMENTS")
            d["received"] = gkd(dbo, row, "DONATIONDATE", True)
            d["chequenumber"] = gks(row, "DONATIONCHECKNUMBER")
            d["type"] = gkl(dbo, row, "DONATIONTYPE", "donationtype", "DonationName", createmissinglookups)
            if d["type"] == "0":
                d["type"] = str(asm3.configuration.default_donation_type(dbo))
            d["giftaid"] = gkbc(row, "DONATIONGIFTAID")
            d["payment"] = gkl(dbo, row, "DONATIONPAYMENT", "donationpayment", "PaymentName", createmissinglookups)
            if d["payment"] == "0":
                d["payment"] = "1"
            try:
                if not dryrun: asm3.financial.insert_donation_from_form(dbo, user, asm3.utils.PostedData(d, dbo.locale))
            except Exception as e:
                row_error(errors, "payment", rowno, row, e, dbo, sys.exc_info())
            if movementid != 0: asm3.movement.update_movement_donation(dbo, movementid)

        # Incident?
        incidentid = 0
        if hasincident and personid != 0 and gks(row, "INCIDENTDATE") != "":
            d = {}
            d["incidentdate"] = gkd(dbo, row, "INCIDENTDATE", True)
            d["incidenttime"] = gks(row, "INCIDENTTIME")
            d["incidenttype"] = gkl(dbo, row, "INCIDENTTYPE", "incidenttype", "IncidentName", createmissinglookups)
            if d["incidenttype"] == "0":
                d["incidenttype"] = str(asm3.configuration.default_incident(dbo))
            d["calldate"] = d["incidentdate"]
            d["callnotes"] = gks(row, "INCIDENTNOTES")
            d["caller"] = str(personid)
            d["dispatchaddress"] = gks(row, "DISPATCHADDRESS")
            d["dispatchtown"] = gks(row, "DISPATCHCITY")
            d["dispatchcounty"] = gks(row, "DISPATCHSTATE")
            d["dispatchpostcode"] = gks(row, "DISPATCHZIPCODE")
            d["species"] = gkl(dbo, row, "INCIDENTANIMALSPECIES", "species", "SpeciesName", createmissinglookups)
            d["sex"] = gksx(row, "INCIDENTANIMALSEX")
            d["dispatchedaco"] = gks(row, "DISPATCHACO")
            d["dispatchdate"] = gkd(dbo, row, "DISPATCHDATE")
            d["dispatchtime"] = gks(row, "DISPATCHTIME")
            d["respondeddate"] = gkd(dbo, row, "INCIDENTRESPONDEDDATE")
            d["followupdate"] = gkd(dbo, row, "INCIDENTFOLLOWUPDATE")
            d["completeddate"] = gkd(dbo, row, "INCIDENTCOMPLETEDDATE")
            d["completedtime"] = gks(row, "INCIDENTCOMPLETEDTIME")
            d["completedtype"] = gkl(dbo, row, "INCIDENTCOMPLETEDTYPE", "incidentcompleted", "CompletedName", True)
            try:
                if not dryrun: incidentid = asm3.animalcontrol.insert_animalcontrol_from_form(dbo, asm3.utils.PostedData(d, dbo.locale), user, geocode=False)
            except Exception as e:
                row_error(errors, "incident", rowno, row, e, dbo, sys.exc_info())
        
        # Citation
        if hascitation and personid != 0 and gkd(dbo, row, "CITATIONDATE") != "":
            c = {}
            c["person"] = str(personid)
            c["incident"] = "0"
            c["type"] = gkl(dbo, row, "CITATIONTYPE", "citationtype", "CitationName", createmissinglookups)
            c["citationnumber"] = gks(row, "CITATIONNUMBER")
            c["citationdate"] = gkd(dbo, row, "CITATIONDATE")
            c["fineamount"] = str(gkc(row, "FINEAMOUNT"))
            c["finedue"] = gkd(dbo, row, "FINEDUEDATE")
            c["finepaid"] = gkd(dbo, row, "FINEPAIDDATE")
            c["comments"] = gks(row, "CITATIONCOMMENTS")
            if not dryrun: asm3.financial.insert_citation_from_form(dbo, user, asm3.utils.PostedData(c, dbo.locale))
        
        # Clinic appointments
        if hasclinic and personid != 0 and gkd(dbo, row, "CLINICAPPOINTMENTDATE") != "":
            c = {}
            c["animal"] = "0"
            c["person"] = str(personid)
            c["type"] = gkl(dbo, row, "CLINICAPPOINTMENTTYPE", "lkclinictype", "ClinicTypeName", createmissinglookups)
            c["for"] = gks(row, "CLINICAPPOINTMENTFOR")
            c["apptdate"] = gkd(dbo, row, "CLINICAPPOINTMENTDATE")
            c["appttime"] = gks(row, "CLINICAPPOINTMENTTIME")

            c["status"] = asm3.utils.cint(row["CLINICAPPOINTMENTSTATUS"])

            c["arriveddate"] = gkd(dbo, row, "CLINICARRIVEDDATE")
            c["arrivedtime"] = gks(row, "CLINICARRIVEDTIME")

            c["withvetdate"] = gkd(dbo, row, "CLINICWITHVETDATE")
            c["withvettime"] = gks(row, "CLINICWITHVETTIME")

            c["completedate"] = gkd(dbo, row, "CLINICCOMPLETEDDATE")
            c["completetime"] = gks(row, "CLINICCOMPLETEDDATE")

            c["reason"] = gks(row, "CLINICAPPOINTMENTREASON")
            c["comments"] = gks(row, "CLINICAPPOINTMENTCOMMENTS")
            c["amount"] = asm3.utils.cint(row["CLINICAMOUNT"])

            c["vat"] = asm3.utils.cint(row["CLINICAPPOINTMENTISVAT"])

            c["vatrate"] = asm3.utils.cfloat(row["CLINICAPPOINTMENTVATRATE"])

            c["vatamount"] = asm3.utils.cint(row["CLINICAPPOINTMENTVATAMOUNT"])

            if not dryrun: asm3.clinic.insert_appointment_from_form(dbo, user, asm3.utils.PostedData(c, dbo.locale))
        
        # Diary note
        if hasdiary:
            d = {}
            d["diarydate"] = gkd(dbo, row, "DIARYDATE")
            d["diaryfor"] = gks(row, "DIARYFOR")
            d["subject"] = gks(row, "DIARYSUBJECT")
            d["note"] = gks(row, "DIARYNOTE")

            if d["diarydate"] == "" or dryrun:
                pass
            elif animalid != 0:
                asm3.diary.insert_diary_from_form(dbo, user, asm3.diary.ANIMAL, animalid, asm3.utils.PostedData(d, dbo.locale))
            elif incidentid != 0:
                asm3.diary.insert_diary_from_form(dbo, user, asm3.diary.ANIMALCONTROL, incidentid, asm3.utils.PostedData(d, dbo.locale))
            else:
                asm3.diary.insert_diary_from_form(dbo, user, asm3.diary.PERSON, personid, asm3.utils.PostedData(d, dbo.locale))

        # Equipment loans
        if hasequipmentloan and personid != 0 and gkd(dbo, row, "LOANDATE") != "":
            t = {}
            t["person"] = str(personid)
            t["type"] = gkl(dbo, row, "TRAPTYPE", "traptype", "TrapTypeName", createmissinglookups)
            t["loandate"] = gkd(dbo, row, "LOANDATE")
            t["depositamount"] = str(gkc(row, "DEPOSITAMOUNT"))
            t["depositreturndate"] = gkd(dbo, row, "DEPOSITRETURNDATE")
            t["trapnumber"] = gks(row, "TRAPNUMBER")
            t["returnduedate"] = gkd(dbo, row, "RETURNDUEDATE")
            t["returndate"] = gkd(dbo, row, "RETURNDATE")
            t["comments"] = gks(row, "TRAPLOANCOMMENTS")

            if not dryrun: asm3.animalcontrol.insert_traploan_from_form(dbo, user, asm3.utils.PostedData(t, dbo.locale))

        # Vaccination
        if hasvacc and animalid != 0 and gks(row, "VACCINATIONDUEDATE") != "":
            v = {}
            v["animal"] = str(animalid)
            v["type"] = gkl(dbo, row, "VACCINATIONTYPE", "vaccinationtype", "VaccinationType", createmissinglookups)
            if v["type"] == "0":
                v["type"] = str(asm3.configuration.default_vaccination_type(dbo))
            v["required"] = gkd(dbo, row, "VACCINATIONDUEDATE", True)
            v["given"] = gkd(dbo, row, "VACCINATIONGIVENDATE")
            v["expires"] = gkd(dbo, row, "VACCINATIONEXPIRESDATE")
            v["batchnumber"] = gks(row, "VACCINATIONBATCHNUMBER")
            v["manufacturer"] = gks(row, "VACCINATIONMANUFACTURER")
            v["rabiestag"] = gks(row, "VACCINATIONRABIESTAG")
            v["comments"] = gks(row, "VACCINATIONCOMMENTS")
            try:
                if not dryrun: asm3.medical.insert_vaccination_from_form(dbo, user, asm3.utils.PostedData(v, dbo.locale))
            except Exception as e:
                row_error(errors, "vaccination", rowno, row, e, dbo, sys.exc_info())

        # Test
        if hastest and animalid != 0 and gks(row, "TESTDUEDATE") != "":
            v = {}
            v["animal"] = str(animalid)
            v["type"] = gkl(dbo, row, "TESTTYPE", "testtype", "TestName", createmissinglookups)
            v["result"] = gkl(dbo, row, "TESTRESULT", "testresult", "ResultName", createmissinglookups)
            v["required"] = gkd(dbo, row, "TESTDUEDATE", True)
            v["given"] = gkd(dbo, row, "TESTPERFORMEDDATE")
            v["comments"] = gks(row, "TESTCOMMENTS")
            try:
                if not dryrun: asm3.medical.insert_test_from_form(dbo, user, asm3.utils.PostedData(v, dbo.locale))
            except Exception as e:
                row_error(errors, "test", rowno, row, e, dbo, sys.exc_info())

        # Medical
        if hasmed and animalid != 0 and gks(row, "MEDICALGIVENDATE") != "" and gks(row, "MEDICALNAME") != "":
            m = {}
            m["animal"] = str(animalid)
            m["medicaltype"] = gkl(dbo, row, "MEDICALTYPE", "lksmedicaltype", "MedicalTypeName", createmissinglookups)
            m["treatmentname"] = gks(row, "MEDICALNAME")
            m["dosage"] = gks(row, "MEDICALDOSAGE")
            m["startdate"] = gkd(dbo, row, "MEDICALGIVENDATE")
            m["comments"] = gks(row, "MEDICALCOMMENTS")
            m["singlemulti"] = "0" # single treatment
            m["status"] = "2" # completed
            try:
                if not dryrun: asm3.medical.insert_regimen_from_form(dbo, user, asm3.utils.PostedData(m, dbo.locale))
            except Exception as e:
                row_error(errors, "medical", rowno, row, e, dbo, sys.exc_info())

        # Costs
        if hascost and animalid != 0 and gkc(row, "COSTAMOUNT") > 0:
            c = {}
            c["animalid"] = str(animalid)
            c["type"] = gkl(dbo, row, "COSTTYPE", "costtype", "CostTypeName", createmissinglookups)
            c["costdate"] = gkd(dbo, row, "COSTDATE", True)
            c["cost"] = str(gkc(row, "COSTAMOUNT"))
            c["description"] = gks(row, "COSTDESCRIPTION")
            try:
                if not dryrun: asm3.animal.insert_cost_from_form(dbo, user, asm3.utils.PostedData(c, dbo.locale))
            except Exception as e:
                row_error(errors, "cost", rowno, row, e, dbo, sys.exc_info())

        # Investigation
        if hasinvestigation and personid != 0 and gks(row, "INVESTIGATIONNOTES") != "":
            i = {}
            i["personid"] = str(personid)
            i["date"] = gkd(dbo, row, "INVESTIGATIONDATE", True)
            i["notes"] = gks(row, "INVESTIGATIONNOTES")
            try:
                if not dryrun: asm3.person.insert_investigation_from_form(dbo, user, asm3.utils.PostedData(i, dbo.locale))
            except Exception as e:
                row_error(errors, "investigation", rowno, row, e, dbo, sys.exc_info())
        
        # Logs
        if haslog and (animalid != 0 or personid != 0) and gks(row, "LOGCOMMENTS") != "":
            l = {}
            l["type"] = gkl(dbo, row, "LOGTYPE", "logtype", "LogTypeName", createmissinglookups)
            l["logdate"] = gkd(dbo, row, "LOGDATE", True)
            l["logtime"] = gks(row, "LOGTIME")
            l["entry"] = gks(row, "LOGCOMMENTS")

            if animalid != 0:
                linktype = asm3.log.ANIMAL
                linkid = animalid
            else:
                linktype = asm3.log.PERSON
                linkid = personid

            try:
                if not dryrun: asm3.log.insert_log_from_form(dbo, user, linktype, linkid, asm3.utils.PostedData(l, dbo.locale))
            except Exception as e:
                row_error(errors, "log", rowno, row, e, dbo, sys.exc_info())

        # License (PERSON columns)
        if haslicence and personid != 0 and gks(row, "LICENSENUMBER") != "":
            l = {}
            l["person"] = str(personid)
            l["animal"] = str(animalid)
            l["type"] = gkl(dbo, row, "LICENSETYPE", "licencetype", "LicenceTypeName", createmissinglookups)
            if l["type"] == "0": l["type"] = 1
            l["number"] = gks(row, "LICENSENUMBER")
            l["fee"] = str(gkc(row, "LICENSEFEE"))
            l["issuedate"] = gkd(dbo, row, "LICENSEISSUEDATE")
            l["expirydate"] = gkd(dbo, row, "LICENSEEXPIRESDATE")
            l["comments"] = gks(row, "LICENSECOMMENTS")
            try:
                if not dryrun: asm3.financial.insert_licence_from_form(dbo, user, asm3.utils.PostedData(l, dbo.locale))
            except Exception as e:
                row_error(errors, "license", rowno, row, e, dbo, sys.exc_info())

        # License (ORIGINALOWNER columns for non-shelter animals)
        if haslicence and originalownerid != 0 and nonshelter and gks(row, "LICENSENUMBER") != "":
            l = {}
            l["person"] = str(originalownerid)
            l["animal"] = str(animalid)
            l["type"] = gkl(dbo, row, "LICENSETYPE", "licencetype", "LicenceTypeName", createmissinglookups)
            if l["type"] == "0": l["type"] = 1
            l["number"] = gks(row, "LICENSENUMBER")
            l["fee"] = str(gkc(row, "LICENSEFEE"))
            l["issuedate"] = gkd(dbo, row, "LICENSEISSUEDATE")
            l["expirydate"] = gkd(dbo, row, "LICENSEEXPIRESDATE")
            l["comments"] = gks(row, "LICENSECOMMENTS")
            try:
                if not dryrun: asm3.financial.insert_licence_from_form(dbo, user, asm3.utils.PostedData(l, dbo.locale))
            except Exception as e:
                row_error(errors, "license", rowno, row, e, dbo, sys.exc_info())
        
        # Voucher 
        if hasvoucher and personid != 0 and gkd(dbo, row, "VOUCHERDATEISSUED") != "":
            v = {}
            v["person"] = str(personid)
            v["animal"] = "0"
            v["type"] = gkl(dbo, row, "VOUCHERNAME", "voucher", "VoucherName", createmissinglookups)
            v["vouchercode"] = gks(row, "VOUCHERCODE")
            v["issued"] = gkd(dbo, row, "VOUCHERDATEISSUED")
            v["expires"] = gkd(dbo, row, "VOUCHERDATEEXPIRED")
            v["presented"] = gkd(dbo, row, "VOUCHERDATEPRESENTED")
            v["vet"] = "0"
            v["amount"] = asm3.utils.cint(row["VOUCHERVALUE"])
            v["comments"] = gks(row, "VOUCHERCOMMENTS")

            try:
                if not dryrun: asm3.financial.insert_voucher_from_form(dbo, user, asm3.utils.PostedData(v, dbo.locale))
            except Exception as e:
                row_error(errors, "voucher", rowno, row, e, dbo, sys.exc_info())
        
        # Stocklevel 
        if hasstocklevel:
            s = {}
            s["name"] = gks(row, "STOCKLEVELNAME")
            s["productlist"] = "0"
            s["description"] = gks(row, "STOCKLEVELDESCRIPTION")
            s["barcode"] = gks(row, "STOCKLEVELBARCODE")
            s["location"] = gkl(dbo, row, "STOCKLEVELLOCATIONNAME", "stocklocation", "LocationName", createmissinglookups)
            s["unitname"] = gks(row, "STOCKLEVELUNITNAME")
            s["total"] = asm3.utils.cfloat(row["STOCKLEVELTOTAL"])
            s["balance"] = asm3.utils.cfloat(row["STOCKLEVELBALANCE"])
            if 'STOCKLEVELLOW' not in row.keys():
                row["STOCKLEVELLOW"] = 0
            s["low"] = asm3.utils.cfloat(row["STOCKLEVELLOW"])
            s["expiry"] = gkd(dbo, row, "STOCKLEVELEXPIRY")
            s["batchnumber"] = gks(row, "STOCKLEVELBATCHNUMBER")
            if 'STOCKLEVELCOST' not in row.keys():
                row["STOCKLEVELCOST"] = 0
            s["cost"] = asm3.utils.cint(row["STOCKLEVELCOST"])
            if 'STOCKLEVELUNITPRICE' not in row.keys():
                row["STOCKLEVELUNITPRICE"] = 0
            s["unitprice"] = asm3.utils.cint(row["STOCKLEVELUNITPRICE"])
            s["usagedate"] = asm3.i18n.python2display(dbo.locale, dbo.today())
            s["usagetype"] = asm3.configuration.product_movement_usage_type(dbo)
            s["comments"] = asm3.i18n._("Imported from CSV", dbo.locale)

            try:
                if not dryrun: asm3.stock.insert_stocklevel_from_form(dbo, asm3.utils.PostedData(s, dbo.locale), user)
            except Exception as e:
                row_error(errors, "stocklevel", rowno, row, e, dbo, sys.exc_info())

        rowno += 1
    
    if htmlresults:
        h = [ "<p>%d success, %d errors</p><table>" % (len(rows) - len(errors), len(errors)) ]
        for rowno, row, err in errors:
            h.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (rowno, row, err))
        h.append("</table>")
        return "".join(h)
    else:
        return asm3.utils.json({ "rows": len(rows), "success": len(rows)-len(errors), "errors": errors })

def csvimport_paypal(dbo: Database, csvdata: bytes, donationtypeid: int, donationpaymentid: int, flags: str, 
                     user: str = "", encoding: str = "utf-8-sig") -> str:
    """
    Imports a PayPal CSV file of transactions.
    Returns an HTML error report.
    """
    def v(r, n, n2 = "", n3 = "", n4 = "", n5 = ""):
        """ 
        Read values n(x) from a dictionary r depending on which is present, 
        if none are present empty string is returned 
        """
        if n in r: return r[n]
        if n2 != "" and n2 in r: return r[n2]
        if n3 != "" and n3 in r: return r[n3]
        if n4 != "" and n4 in r: return r[n4]
        if n5 != "" and n5 in r: return r[n5]
        return ""
    
    def curr(s):
        """
        Takes the currency string s from a PayPal CSV and return it as an SM int/currency value.
        Can cope with . or , as the decimal marker. Negative amounts will remain negative.
        """
        s = s.replace(",", ".")
        return asm3.utils.cint(asm3.utils.cfloat(s) * 100) 

    if user == "":
        user = "import"
    else:
        user = "import/%s" % user

    rows = asm3.utils.csv_parse( asm3.utils.bytes2str(csvdata, encoding=encoding) )
    print(rows[0])

    errors = []
    rowno = 1
    asm3.asynctask.set_progress_max(dbo, len(rows))

    if len(rows) == 0:
        asm3.asynctask.set_last_error(dbo, "CSV file is empty")
        return

    REQUIRED_FIELDS = [ "Date", "Currency", "Gross", "Fee", "Net", "From Email Address", "Status", "Type" ]
    for rf in REQUIRED_FIELDS:
        if rf not in rows[0]:
            asm3.asynctask.set_last_error(dbo, "This CSV file does not look like a PayPal CSV (missing %s)" % rf)
            return

    for r in rows:

        # Skip blank rows
        if len(r) == 0: continue

        # Should we stop?
        if asm3.asynctask.get_cancel(dbo): break

        asm3.al.debug("import paypal csv: row %d of %d" % (rowno, len(rows)), "csvimport.csvimport_paypal", dbo)
        asm3.asynctask.increment_progress_value(dbo)

        if r["Status"] != "Completed":
            asm3.al.debug("skipping: Status='%s' (!= Completed), Type='%s'" % (r["Status"], r["Type"]), "csvimport.csvimport_paypal", dbo)
            continue

        if r["Type"].find("Payment") == -1:
            asm3.al.debug("skipping: Status='%s', Type='%s' (!Payment)" % (r["Status"], r["Type"]), "csvimport.csvimport_paypal", dbo)
            continue

        # Parse name (use all up to last space for first names if only Name exists)
        name = v(r, "Name")
        firstname = v(r, "First Name")
        lastname = v(r, "Last Name")
        if name != "" and firstname == "" and lastname == "":
            if name.find(" ") != -1:
                firstname =name[0:name.rfind(" ")]
                lastname =name[name.rfind(" ")+1:]
            else:
                lastname = name

        # Person data
        personid = 0
        p = {}
        p["ownertype"] = "1"
        p["forenames"] = firstname
        p["surname"] = lastname
        p["address"] = v(r, "Address Line 1", "Street Address 1")
        p["town"] = v(r, "Town/City", "Town", "City")
        p["county"] = v(r, "County", "State", "Province", "Region", "State/Province/Region/County/Territory/Prefecture/Republic")
        p["postcode"] = v(r, "Postcode", "Zip Code", "Zip/Postal Code")
        p["hometelephone"] = v(r, "Contact Phone Number", "Phone Number")
        p["emailaddress"] = v(r, "From Email Address")
        p["flags"] = flags
        try:
            dups = asm3.person.get_person_similar(dbo, p["emailaddress"], p["hometelephone"], p["surname"], p["forenames"], p["address"])
            if len(dups) > 0:
                personid = dups[0]["ID"]
                # Merge flags and any extra details
                asm3.person.merge_flags(dbo, user, personid, flags)
                asm3.person.merge_person_details(dbo, user, personid, p)
            if personid == 0:
                personid = asm3.person.insert_person_from_form(dbo, asm3.utils.PostedData(p, dbo.locale), user, geocode=False)
        except Exception as e:
            row_error(errors, "person", rowno, r, e, dbo, sys.exc_info())

        # Sort out which payment type is being used. Look for a user-added column called "ASM Payment Type"
        # if it doesn't exist, is blank or we couldn't find a match in the donation type table 
        # then we fall back to the one the user chose during import.
        sdonationtypeid = v(r, "ASM Payment Type")
        if sdonationtypeid != "":
            sdonationtypeid = dbo.query_str("SELECT ID FROM donationtype WHERE DonationName=?", [sdonationtypeid])
        if sdonationtypeid == "":
            sdonationtypeid = str(donationtypeid)

        # Donation info
        gross = curr(v(r, "Gross"))
        net = curr(v(r, "Net"))
        fee = abs(curr(v(r, "Fee"))) # Fee is a negative amount 
        if net > gross: gross = net # I've seen PayPal files where net/gross are the wrong way around
        if personid != 0 and net > 0:
            pdate = asm3.i18n.display2python(dbo.locale, v(r, "Date")) # parse the date (we do this to fix 2 digit years, which I've also seen)
            if pdate is None: pdate = dbo.today() # use today if parsing failed
            d = {}
            d["person"] = str(personid)
            d["animal"] = "0"
            d["movement"] = "0"
            d["amount"] = str(gross)
            d["fee"] = str(fee)
            d["chequenumber"] = str(v(r, "Transaction ID"))
            comments = "PayPal ID: %s \nItem: %s %s \nCurrency: %s \nGross: %s \nFee: %s \nNet: %s \nSubject: %s \nNote: %s" % \
                ( v(r, "Transaction ID"), v(r, "Item ID", "Item Number"), v(r, "Item Title"), v(r, "Currency"), 
                v(r, "Gross"), v(r, "Fee"), v(r, "Net"), v(r, "Subject"), v(r, "Note") )
            d["comments"] = comments
            d["received"] = asm3.i18n.python2display(dbo.locale, pdate)
            d["type"] = sdonationtypeid
            d["payment"] = str(donationpaymentid)
            try:
                asm3.financial.insert_donation_from_form(dbo, user, asm3.utils.PostedData(d, dbo.locale))
            except Exception as e:
                row_error(errors, "payment", rowno, r, e, dbo, sys.exc_info())

        rowno += 1

    h = [ "<p>%d success, %d errors</p><table>" % (len(rows) - len(errors), len(errors)) ]
    for rowno, row, err in errors:
        h.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (rowno, row, err))
    h.append("</table>")
    return "".join(h)

def csvimport_stripe(dbo: Database, csvdata: bytes, donationtypeid: int, donationpaymentid: int, flags: str, 
                     user: str = "", encoding: str = "utf-8-sig") -> str:
    """
    Imports a Stripe CSV file of transactions.
    Returns an HTML error report.
    """
    def v(r: Dict, n: str) -> str:
        """ Reads r[n], returning empty string if n does not exist in r """
        if n in r: return r[n]
        return ""

    if user == "":
        user = "import"
    else:
        user = "import/%s" % user

    rows = asm3.utils.csv_parse( asm3.utils.bytes2str(csvdata, encoding=encoding) )
    print(rows[0])

    errors = []
    rowno = 1
    asm3.asynctask.set_progress_max(dbo, len(rows))

    if len(rows) == 0:
        asm3.asynctask.set_last_error(dbo, "CSV file is empty")
        return

    REQUIRED_FIELDS = [ "id", "Status", "Currency", "Amount", "Fee", "Converted Amount", "Converted Currency", 
        "Card Name", "Card Last4", "Card Brand", 
        "Card Address Line1", "Card Address City", "Card Address State", "Card Address Zip", 
        "Card Address Country", "Customer Email" ]

    for rf in REQUIRED_FIELDS:
        if rf not in rows[0]:
            asm3.asynctask.set_last_error(dbo, "This CSV file does not look like a Stripe CSV (missing %s)" % rf)
            return

    for r in rows:

        # Skip blank rows
        if len(r) == 0: continue

        # Should we stop?
        if asm3.asynctask.get_cancel(dbo): break

        asm3.al.debug("import stripe csv: row %d of %d" % (rowno, len(rows)), "csvimport.csvimport_stripe", dbo)
        asm3.asynctask.increment_progress_value(dbo)

        if r["Status"] != "Paid":
            asm3.al.debug("skipping: Status='%s' (!= Paid)" % (r["Status"]), "csvimport.csvimport_paypal", dbo)
            continue

        # Parse name (use all up to last space for first names if only Name exists)
        firstname = ""
        lastname = ""
        name = r["Card Name"]
        if name != "":
            if name.find(" ") != -1:
                firstname =name[0:name.rfind(" ")]
                lastname =name[name.rfind(" ")+1:]
            else:
                lastname = name

        # Person data
        personid = 0
        p = {}
        p["ownertype"] = "1"
        p["forenames"] = firstname
        p["surname"] = lastname
        p["address"] = r["Card Address Line1"]
        p["town"] = r["Card Address City"]
        p["county"] = r["Card Address State"]
        p["postcode"] = r["Card Address Zip"]
        p["country"] = r["Card Address Country"]
        p["emailaddress"] = r["Customer Email"]
        p["flags"] = flags
        try:
            dups = asm3.person.get_person_similar(dbo, p["emailaddress"], "", p["surname"], p["forenames"], p["address"])
            if len(dups) > 0:
                personid = dups[0]["ID"]
                # Merge flags and any extra details
                asm3.person.merge_flags(dbo, user, personid, flags)
                asm3.person.merge_person_details(dbo, user, personid, p)
            if personid == 0:
                personid = asm3.person.insert_person_from_form(dbo, asm3.utils.PostedData(p, dbo.locale), user, geocode=False)
        except Exception as e:
            row_error(errors, "person", rowno, r, e, dbo, sys.exc_info())

        # Sort out which payment type is being used. Look for a user-added column called "ASM Payment Type"
        # if it doesn't exist, is blank or we couldn't find a match in the donation type table 
        # then we fall back to the one the user chose during import.
        sdonationtypeid = v(r, "ASM Payment Type")
        if sdonationtypeid != "":
            sdonationtypeid = dbo.query_str("SELECT ID FROM donationtype WHERE DonationName=?", [sdonationtypeid])
        if sdonationtypeid == "":
            sdonationtypeid = str(donationtypeid)
        # Donation info
        gross = asm3.utils.cint(asm3.utils.cfloat(r["Converted Amount"]) * 100)
        if gross == 0: asm3.utils.cint(asm3.utils.cfloat(r["Amount"]) * 100)
        fee = asm3.utils.cint(asm3.utils.cfloat(r["Fee"]) * 100)
        if personid != 0 and gross > 0:
            pdate = asm3.i18n.parse_date("%Y-%m-%d %H:%M", r["Created (UTC)"])
            if pdate is None: pdate = dbo.today() # use today if parsing failed
            d = {}
            d["person"] = str(personid)
            d["animal"] = "0"
            d["movement"] = "0"
            d["amount"] = str(gross - fee)
            d["fee"] = str(fee)
            d["chequenumber"] = str(r["id"])
            comments = "Stripe ID: %s \nItem: %s \nCurrency: %s \nAmount: %s \nFee: %s \nConverted: %s %s \nCard: %s %s" % \
                (r["id"], r["Description"], r["Currency"], r["Amount"], r["Fee"], r["Converted Amount"], r["Converted Currency"], r["Card Last4"], r["Card Brand"])
            d["comments"] = comments
            d["received"] = asm3.i18n.python2display(dbo.locale, pdate)
            d["type"] = sdonationtypeid
            d["payment"] = str(donationpaymentid)
            try:
                asm3.financial.insert_donation_from_form(dbo, user, asm3.utils.PostedData(d, dbo.locale))
            except Exception as e:
                row_error(errors, "payment", rowno, r, e, dbo, sys.exc_info())

        rowno += 1

    h = [ "<p>%d success, %d errors</p><table>" % (len(rows) - len(errors), len(errors)) ]
    for rowno, row, err in errors:
        h.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (rowno, row, err))
    h.append("</table>")
    return "".join(h)

def csvexport_animals(dbo: Database, dataset: str, animalids: str = "", where: str = "", includemedia: str = "photo") -> str:
    """
    Export CSV data for a set of animals.
    dataset: The named set of data to use
    animalids: If dataset == selshelter, a comma separated list of animals to export
    where: If dataset == where, a where clause to the animal table (without the keyword WHERE)
    includemedia: photo: output base64 encoded version of the primary photo for each animal
                  all: output base64 encoded version of all media for each animal
    Returns an html link to the exported file to download.
    """
    l = dbo.locale
    q = ""
    out = asm3.utils.stringio()
    
    if dataset == "all": q = "SELECT ID FROM animal ORDER BY ID"
    elif dataset == "shelter": q = "SELECT ID FROM animal WHERE Archived=0 ORDER BY ID"
    elif dataset == "nonshelter": q = "SELECT ID FROM animal WHERE NonShelterAnimal=1 ORDER BY ID"
    elif dataset == "selshelter": q = "SELECT ID FROM animal WHERE ID IN (%s) ORDER BY ID" % animalids
    elif dataset == "where": q = "SELECT ID FROM animal WHERE %s ORDER BY ID" % where.replace(";", "")
    
    ids = dbo.query(q)

    keys = [ "ANIMALID", "ANIMALCODE", "ANIMALLITTER", "ANIMALNAME", "ANIMALSEX", "ANIMALTYPE", "ANIMALWEIGHT", "ANIMALCOLOR", "ANIMALBREED1",
        "ANIMALBREED2", "ANIMALDOB", "ANIMALLOCATION", "ANIMALUNIT", "ANIMALSPECIES", "ANIMALDESCRIPTION", "ANIMALWARNING", 
        "ANIMALHIDDENDETAILS", "ANIMALHEALTHPROBLEMS", "ANIMALMARKINGS", "ANIMALREASONFORENTRY", "ANIMALNEUTERED",
        "ANIMALNEUTEREDDATE", "ANIMALMICROCHIP", "ANIMALMICROCHIPDATE", "ANIMALENTRYDATE", 
        "ANIMALDECEASEDDATE", "ANIMALDECEASEDREASON", "ANIMALDECEASEDNOTES", "ANIMALEUTHANIZED", 
        "ANIMALJURISDICTION", "ANIMALPICKUPLOCATION", "ANIMALPICKUPADDRESS", "ANIMALENTRYCATEGORY",
        "ANIMALNOTFORADOPTION", "ANIMALNONSHELTER", "ANIMALTRANSFER",
        "ANIMALGOODWITHCATS", "ANIMALGOODWITHDOGS", "ANIMALGOODWITHKIDS", "ANIMALHOUSETRAINED", 
        "ANIMALIMAGE", "ANIMALPDFNAME", "ANIMALPDFDATA", "ANIMALHTMLNAME", "ANIMALHTMLDATA", 
        "COSTDATE", "COSTTYPE", "COSTAMOUNT", "COSTDESCRIPTION",
        "CURRENTVETTITLE", "CURRENTVETINITIALS", "CURRENTVETFIRSTNAME",
        "CURRENTVETLASTNAME", "CURRENTVETADDRESS", "CURRENTVETCITY", "CURRENTVETSTATE", "CURRENTVETZIPCODE",
        "CURRENTVETHOMEPHONE", "CURRENTVETWORKPHONE", "CURRENTVETCELLPHONE", "CURRENTVETEMAIL", 
        "LOGDATE", "LOGTIME", "LOGTYPE", "LOGCOMMENTS", 
        "ORIGINALOWNERTITLE", "ORIGINALOWNERINITIALS", "ORIGINALOWNERFIRSTNAME",
        "ORIGINALOWNERLASTNAME", "ORIGINALOWNERADDRESS", "ORIGINALOWNERCITY", "ORIGINALOWNERSTATE", "ORIGINALOWNERZIPCODE",
        "ORIGINALOWNERHOMEPHONE", "ORIGINALOWNERWORKPHONE", "ORIGINALOWNERCELLPHONE", "ORIGINALOWNEREMAIL", "ORIGINALOWNERWARNING", 
        "MOVEMENTTYPE", "MOVEMENTDATE", 
        "PERSONTITLE", "PERSONINITIALS", "PERSONFIRSTNAME", "PERSONLASTNAME", "PERSONADDRESS", "PERSONCITY",
        "PERSONSTATE", "PERSONZIPCODE", "PERSONFOSTERER", "PERSONHOMEPHONE", "PERSONWORKPHONE", "PERSONCELLPHONE", "PERSONEMAIL",
        "PERSONCOMMENTS", "PERSONWARNING", 
        "TESTTYPE", "TESTRESULT", "TESTDUEDATE", "TESTPERFORMEDDATE", "TESTCOMMENTS",
        "VACCINATIONTYPE", "VACCINATIONDUEDATE", "VACCINATIONGIVENDATE", "VACCINATIONEXPIRESDATE", "VACCINATIONRABIESTAG",
        "VACCINATIONMANUFACTURER", "VACCINATIONBATCHNUMBER", "VACCINATIONCOMMENTS", 
        "MEDICALNAME", "MEDICALDOSAGE", "MEDICALGIVENDATE", "MEDICALCOMMENTS", "MEDICALTYPE" ]
    
    def tocsv(row: Dict) -> str:
        r = []
        for k in keys:
            if k in row: 
                r.append("\"%s\"" % str(row[k]).replace("\"", "\"\""))
            else:
                r.append("\"\"")
        return ",".join(r) + "\n"

    def nn(s: str) -> str:
        if s is None: return ""
        return s

    firstrow = True
    asm3.asynctask.set_progress_max(dbo, len(ids))
    for aid in ids:

        # Should we stop?
        if asm3.asynctask.get_cancel(dbo): break

        if firstrow:
            firstrow = False
            out.write(",".join(keys) + "\n")

        row = {}
        a = asm3.animal.get_animal(dbo, aid.ID)
        if a is None: continue

        asm3.asynctask.increment_progress_value(dbo)

        row["ANIMALID"] = aid.ID
        row["ANIMALCODE"] = a["SHELTERCODE"]
        row["ANIMALLITTER"] = a["ACCEPTANCENUMBER"]
        row["ANIMALNAME"] = a["ANIMALNAME"]
        row["ANIMALSEX"] = a["SEXNAME"]
        row["ANIMALTYPE"] = a["ANIMALTYPENAME"]
        row["ANIMALCOLOR"] = a["BASECOLOURNAME"]
        row["ANIMALBREED1"] = a["BREEDNAME1"]
        row["ANIMALBREED2"] = a["BREEDNAME2"]
        row["ANIMALDOB"] = asm3.i18n.python2display(l, a["DATEOFBIRTH"])
        row["ANIMALSIZE"] = a["SIZENAME"]
        row["ANIMALWEIGHT"] = a["WEIGHT"]
        row["ANIMALLOCATION"] = a["SHELTERLOCATIONNAME"]
        row["ANIMALUNIT"] = a["SHELTERLOCATIONUNIT"]
        row["ANIMALSPECIES"] = a["SPECIESNAME"]
        row["ANIMALDESCRIPTION"] = a["ANIMALCOMMENTS"]
        row["ANIMALHIDDENDETAILS"] = a["HIDDENANIMALDETAILS"]
        row["ANIMALHEALTHPROBLEMS"] = a["HEALTHPROBLEMS"]
        row["ANIMALMARKINGS"] = a["MARKINGS"]
        row["ANIMALWARNING"] = a["POPUPWARNING"]
        row["ANIMALREASONFORENTRY"] = a["REASONFORENTRY"]
        row["ANIMALENTRYCATEGORY"] = a["ENTRYREASONNAME"]
        row["ANIMALENTRYTYPE"] = a["ENTRYTYPENAME"]
        row["ANIMALJURISDICTION"] = a["JURISDICTIONNAME"]
        row["ANIMALPICKUPLOCATION"] = asm3.utils.iif(a["ISPICKUP"] == 1, a["PICKUPLOCATIONNAME"], "")
        row["ANIMALPICKUPADDRESS"] = a["PICKUPADDRESS"]
        row["ANIMALNEUTERED"] = a["NEUTERED"]
        row["ANIMALNEUTEREDDATE"] = asm3.i18n.python2display(l, a["NEUTEREDDATE"])
        row["ANIMALMICROCHIP"] = a["IDENTICHIPNUMBER"]
        row["ANIMALMICROCHIPDATE"] = asm3.i18n.python2display(l, a["IDENTICHIPDATE"])
        row["ANIMALENTRYDATE"] = asm3.i18n.python2display(l, a["DATEBROUGHTIN"])
        row["ANIMALDECEASEDDATE"] = asm3.i18n.python2display(l, a["DECEASEDDATE"])
        row["ANIMALDECEASEDREASON"] = asm3.utils.iif(a["DECEASEDDATE"] is not None, a["PTSREASONNAME"], "")
        row["ANIMALDECEASEDNOTES"] = a["PTSREASON"]
        row["ANIMALEUTHANIZED"] = a["PUTTOSLEEP"]
        row["ANIMALNOTFORADOPTION"] = a["ISNOTAVAILABLEFORADOPTION"]
        row["ANIMALNONSHELTER"] = a["NONSHELTERANIMAL"]
        row["ANIMALTRANSFER"] = a["ISTRANSFER"]
        row["ANIMALGOODWITHCATS"] = a["ISGOODWITHCATSNAME"]
        row["ANIMALGOODWITHDOGS"] = a["ISGOODWITHDOGSNAME"]
        row["ANIMALGOODWITHKIDS"] = a["ISGOODWITHCHILDRENNAME"]
        row["ANIMALHOUSETRAINED"] = a["ISHOUSETRAINEDNAME"]
        row["CURRENTVETTITLE"] = ""
        row["CURRENTVETINITIALS"] = ""
        row["CURRENTVETFIRSTNAME"] = nn(a["CURRENTVETFORENAMES"])
        row["CURRENTVETLASTNAME"] = nn(a["CURRENTVETSURNAME"])
        row["CURRENTVETADDRESS"] = nn(a["CURRENTVETADDRESS"])
        row["CURRENTVETCITY"] = nn(a["CURRENTVETTOWN"])
        row["CURRENTVETSTATE"] = nn(a["CURRENTVETCOUNTY"])
        row["CURRENTVETZIPCODE"] = nn(a["CURRENTVETPOSTCODE"])
        row["CURRENTVETHOMEPHONE"] = ""
        row["CURRENTVETWORKPHONE"] = nn(a["CURRENTVETWORKTELEPHONE"])
        row["CURRENTVETCELLPHONE"] = ""
        row["CURRENTVETEMAIL"] = nn(a["CURRENTVETEMAILADDRESS"])
        row["ORIGINALOWNERTITLE"] = nn(a["ORIGINALOWNERTITLE"])
        row["ORIGINALOWNERINITIALS"] = nn(a["ORIGINALOWNERINITIALS"])
        row["ORIGINALOWNERFIRSTNAME"] = nn(a["ORIGINALOWNERFORENAMES"])
        row["ORIGINALOWNERLASTNAME"] = nn(a["ORIGINALOWNERSURNAME"])
        row["ORIGINALOWNERADDRESS"] = nn(a["ORIGINALOWNERADDRESS"])
        row["ORIGINALOWNERCITY"] = nn(a["ORIGINALOWNERTOWN"])
        row["ORIGINALOWNERSTATE"] = nn(a["ORIGINALOWNERCOUNTY"])
        row["ORIGINALOWNERZIPCODE"] = nn(a["ORIGINALOWNERPOSTCODE"])
        row["ORIGINALOWNERHOMEPHONE"] = nn(a["ORIGINALOWNERHOMETELEPHONE"])
        row["ORIGINALOWNERWORKPHONE"] = nn(a["ORIGINALOWNERWORKTELEPHONE"])
        row["ORIGINALOWNERCELLPHONE"] = nn(a["ORIGINALOWNERMOBILETELEPHONE"])
        row["ORIGINALOWNEREMAIL"] = nn(a["ORIGINALOWNEREMAILADDRESS"])
        row["ORIGINALOWNERWARNING"] = nn(a["ORIGINALOWNERPOPUPWARNING"])
        row["MOVEMENTTYPE"] = a["ACTIVEMOVEMENTTYPE"]
        row["MOVEMENTDATE"] = asm3.i18n.python2display(l, a["ACTIVEMOVEMENTDATE"])
        row["PERSONTITLE"] = nn(a["CURRENTOWNERTITLE"])
        row["PERSONINITIALS"] = nn(a["CURRENTOWNERINITIALS"])
        row["PERSONFIRSTNAME"] = nn(a["CURRENTOWNERFORENAMES"])
        row["PERSONLASTNAME"] = nn(a["CURRENTOWNERSURNAME"])
        row["PERSONADDRESS"] = nn(a["CURRENTOWNERADDRESS"])
        row["PERSONCITY"] = nn(a["CURRENTOWNERTOWN"])
        row["PERSONSTATE"] = nn(a["CURRENTOWNERCOUNTY"])
        row["PERSONZIPCODE"] = nn(a["CURRENTOWNERPOSTCODE"])
        row["PERSONFOSTERER"] = asm3.utils.iif(a["ACTIVEMOVEMENTTYPE"] == 2, "1", "0")
        row["PERSONHOMEPHONE"] = nn(a["CURRENTOWNERHOMETELEPHONE"])
        row["PERSONWORKPHONE"] = nn(a["CURRENTOWNERWORKTELEPHONE"])
        row["PERSONCELLPHONE"] = nn(a["CURRENTOWNERMOBILETELEPHONE"])
        row["PERSONEMAIL"] = nn(a["CURRENTOWNEREMAILADDRESS"])
        row["PERSONCOMMENTS"] = nn(a["CURRENTOWNERCOMMENTS"])
        row["PERSONWARNING"] = nn(a["CURRENTOWNERPOPUPWARNING"])
        if a["WEBSITEIMAGECOUNT"] > 0 and includemedia == "photo":
            # dummy, mdata = asm3.media.get_image_file_data(dbo, "animal", a["ID"])
            # row["ANIMALIMAGE"] = "data:image/jpg;base64,%s" % asm3.utils.base64encode(mdata)
            row["ANIMALIMAGE"] = "%s?account=%s&method=animal_image&animalid=%s" % (SERVICE_URL, dbo.name(), a["ID"])
        out.write(tocsv(row))

        if includemedia == "photos":
            for m in asm3.media.get_media(dbo, asm3.media.ANIMAL, a["ID"]):
                if m["MEDIANAME"].endswith(".jpg"):
                    row = {}
                    row["ANIMALCODE"] = a["SHELTERCODE"]
                    row["ANIMALNAME"] = a["ANIMALNAME"]
                    #row["ANIMALIMAGE"] = "data:image/jpg;base64,%s" % asm3.utils.base64encode(mdata)
                    row["ANIMALIMAGE"] = "%s?account=%s&method=media_file&mediaid=%s" % (SERVICE_URL, dbo.name(), m["ID"])
                    out.write(tocsv(row))

        if includemedia == "all":
            for m in asm3.media.get_media(dbo, asm3.media.ANIMAL, a["ID"]):
                if m["MEDIANAME"].endswith(".jpg") or m["MEDIANAME"].endswith(".pdf") or m["MEDIANAME"].endswith(".html"):
                    row = {}
                    row["ANIMALCODE"] = a["SHELTERCODE"]
                    row["ANIMALNAME"] = a["ANIMALNAME"]
                    if m["MEDIANAME"].endswith(".jpg"):
                        #row["ANIMALIMAGE"] = "data:image/jpg;base64,%s" % asm3.utils.base64encode(mdata)
                        row["ANIMALIMAGE"] = "%s?account=%s&method=media_file&mediaid=%s" % (SERVICE_URL, dbo.name(), m["ID"])
                    elif m["MEDIANAME"].endswith(".pdf"):
                        row["ANIMALPDFNAME"] = m["MEDIANOTES"]
                        if row["ANIMALPDFNAME"].strip() == "": row["ANIMALPDFNAME"] = "doc.pdf"
                        #row["ANIMALPDFDATA"] = "data:application/pdf;base64,%s" % asm3.utils.base64encode(mdata)
                        row["ANIMALPDFDATA"] = "%s?account=%s&method=media_file&mediaid=%s" % (SERVICE_URL, dbo.name(), m["ID"])
                    elif m["MEDIANAME"].endswith(".html"):
                        row["ANIMALHTMLNAME"] = m["MEDIANOTES"]
                        if row["ANIMALHTMLNAME"].strip() == "": row["ANIMALHTMLNAME"] = "doc.html"
                        #row["ANIMALHTMLDATA"] = "data:text/html;base64,%s" % asm3.utils.base64encode(mdata)
                        row["ANIMALHTMLDATA"] = "%s?account=%s&method=media_file&mediaid=%s" % (SERVICE_URL, dbo.name(), m["ID"])
                    out.write(tocsv(row))

        for v in asm3.medical.get_vaccinations(dbo, a["ID"]):
            row = {}
            row["VACCINATIONTYPE"] = v["VACCINATIONTYPE"]
            row["VACCINATIONDUEDATE"] = asm3.i18n.python2display(l, v["DATEREQUIRED"])
            row["VACCINATIONGIVENDATE"] = asm3.i18n.python2display(l, v["DATEOFVACCINATION"])
            row["VACCINATIONEXPIRESDATE"] = asm3.i18n.python2display(l, v["DATEEXPIRES"])
            row["VACCINATIONMANUFACTURER"] = v["MANUFACTURER"]
            row["VACCINATIONBATCHNUMBER"] = v["BATCHNUMBER"]
            row["VACCINATIONRABIESTAG"] = v["RABIESTAG"]
            row["VACCINATIONCOMMENTS"] = v["COMMENTS"]
            row["ANIMALCODE"] = a["SHELTERCODE"]
            row["ANIMALNAME"] = a["ANIMALNAME"]
            out.write(tocsv(row))

        for t in asm3.medical.get_tests(dbo, a["ID"]):
            row = {}
            row["TESTTYPE"] = t["TESTNAME"]
            row["TESTRESULT"] = t["RESULTNAME"]
            row["TESTDUEDATE"] = asm3.i18n.python2display(l, t["DATEREQUIRED"])
            row["TESTPERFORMEDDATE"] = asm3.i18n.python2display(l, t["DATEOFTEST"])
            row["TESTCOMMENTS"] = t["COMMENTS"]
            row["ANIMALCODE"] = a["SHELTERCODE"]
            row["ANIMALNAME"] = a["ANIMALNAME"]
            out.write(tocsv(row))

        for m in asm3.medical.get_regimens(dbo, a["ID"], True):
            row = {}
            row["MEDICALNAME"] = m["TREATMENTNAME"]
            row["MEDICALDOSAGE"] = m["DOSAGE"]
            row["MEDICALGIVENDATE"] = asm3.i18n.python2display(l, m["STARTDATE"])
            row["MEDICALCOMMENTS"] = m["COMMENTS"]
            row["MEDICALTYPE"] = m["MEDICALTYPENAME"]
            row["ANIMALCODE"] = a["SHELTERCODE"]
            row["ANIMALNAME"] = a["ANIMALNAME"]
            out.write(tocsv(row))

        for c in asm3.animal.get_costs(dbo, a["ID"]):
            row = {} 
            row["COSTDATE"] = asm3.i18n.python2display(l, c["COSTDATE"])
            row["COSTTYPE"] = c["COSTTYPENAME"]
            row["COSTAMOUNT"] = asm3.utils.cint(c["COSTAMOUNT"]) / 100.0
            row["COSTDESCRIPTION"] = c["DESCRIPTION"]
            row["ANIMALCODE"] = a["SHELTERCODE"]
            row["ANIMALNAME"] = a["ANIMALNAME"]
            out.write(tocsv(row))

        for g in asm3.log.get_logs(dbo, asm3.log.ANIMAL, a["ID"]):
            row = {}
            row["LOGDATE"] = asm3.i18n.python2display(l, g["DATE"])
            row["LOGTIME"] = asm3.i18n.format_time(g["DATE"])
            row["LOGTYPE"] = g["LOGTYPENAME"]
            row["LOGCOMMENTS"] = g["COMMENTS"]
            row["ANIMALCODE"] = a["SHELTERCODE"]
            row["ANIMALNAME"] = a["ANIMALNAME"]
            out.write(tocsv(row))

        del a
        del row

    # Generate a disk cache key and store the data in the cache so it can be retrieved for the next hour
    key = asm3.utils.uuid_str()
    asm3.cachedisk.put(key, dbo.name(), out.getvalue(), 3600)
    h = '<p>%s <a target="_blank" href="csvexport_animals_ex?get=%s"><b>%s</b></p>' % ( \
        asm3.i18n._("Export complete ({0} entries).", l).format(len(ids)), key, asm3.i18n._("Download File", l) )
    return h

def csvexport_people(dbo: Database, dataset: str, flags: str = "", where: str = "", includemedia: str = "photo") -> str:
    """
    Export CSV data for a set of people.
    dataset: The named set of data to use
    where: If dataset == where, a where clause to the owner table (without the keyword WHERE)
    includemedia: photo: output base64 encoded version of the primary photo for each person
                  all: output base64 encoded version of all media for each person
    Returns an html link to the exported file to download.
    """
    l = dbo.locale
    q = ""
    out = asm3.utils.stringio()
    
    if dataset == "all": q = "SELECT ID FROM owner ORDER BY ID"
    elif dataset == "flaggedpeople":
        q = "SELECT ID FROM owner WHERE "
        flagargs = []
        for flag in flags.split(","):
            flagargs.append("AdditionalFlags LIKE '%" + flag + "|%'")
        q += (" OR ").join(flagargs)
    elif dataset == "where": q = "SELECT ID FROM owner WHERE %s ORDER BY ID" % where.replace(";", "")
    
    pids = dbo.query(q)

    keys = [ "PERSONCODE", "PERSONDATEOFBIRTH", "PERSONIDNUMBER",
        "PERSONDATEOFBIRTH2", "PERSONIDNUMBER2",
        "PERSONTITLE", "PERSONINITIALS", "PERSONFIRSTNAME", "PERSONLASTNAME",
        "PERSONTITLE2", "PERSONINITIALS2", "PERSONFIRSTNAME2", "PERSONLASTNAME2",
        "PERSONADDRESS", "PERSONCITY", "PERSONSTATE",
        "PERSONZIPCODE", "PERSONJURISDICTION", "PERSONFOSTERER", "PERSONDONOR",
        "PERSONFLAGS", "PERSONCOMMENTS", "PERSONWARNING", "PERSONFOSTERCAPACITY",
        "PERSONHOMEPHONE", "PERSONWORKPHONE", "PERSONCELLPHONE", "PERSONEMAIL",
        "PERSONHOMEPHONE2", "PERSONWORKPHONE2", "PERSONCELLPHONE2", "PERSONEMAIL2",
        "PERSONGDPRCONTACT", "PERSONCLASS",
        "PERSONMEMBER", "PERSONMEMBERSHIPNUMBER", "PERSONMEMBERSHIPEXPIRY",
        "PERSONMATCHACTIVE", "PERSONMATCHADDED", "PERSONMATCHEXPIRES",
        "PERSONMATCHSEX", "PERSONMATCHSIZE", "PERSONMATCHCOLOR", "PERSONMATCHAGEFROM", "PERSONMATCHAGETO", 
        "PERSONMATCHTYPE", "PERSONMATCHSPECIES", "PERSONMATCHBREED1", "PERSONMATCHBREED2", 
        "PERSONMATCHGOODWITHCATS", "PERSONMATCHGOODWITHDOGS", "PERSONMATCHGOODWITHCHILDREN", "PERSONMATCHGOODWITHELDERLY", 
        "PERSONMATCHHOUSETRAINED", "PERSONMATCHCRATETRAINED", "PERSONMATCHGOODTRAVELLER", "PERSONMATCHGOODONLEAD", "PERSONMATCHENERGYLEVEL", 
        "PERSONMATCHCOMMENTSCONTAIN",
        "PERSONIMAGE", "PERSONPDFNAME", "PERSONPDFDATA", "PERSONHTMLNAME", "PERSONHTMLDATA",
        "LOGDATE", "LOGTIME", "LOGTYPE", "LOGCOMMENTS",
        "ANIMALCODE", "ANIMALNAME", 
        "LICENSENUMBER", "LICENSETYPE", "LICENSEFEE", "LICENSEISSUEDATE", "LICENSEEXPIRESDATE", "LICENSECOMMENTS",
        "INVESTIGATIONDATE", "INVESTIGATIONNOTES",
        "CITATIONDATE", "CITATIONNUMBER", "CITATIONTYPE", "FINEAMOUNT", "FINEDUEDATE", "FINEPAIDDATE", "CITATIONCOMMENTS",
        "LOANDATE", "TRAPTYPE", "TRAPNUMBER", "DEPOSITAMOUNT", "DEPOSITRETURNDATE", "RETURNDUEDATE", "RETURNDATE", "TRAPLOANCOMMENTS",
        "DONATIONNAME", "DONATIONDATE", "DONATIONAMOUNT", "PAYMENTNAME", "PAYMENTISGIFTAID", "PAYMENTFREQUENCY", "PAYMENTRECEIPTNUMBER", "PAYMENTCHEQUENUMBER", "PAYMENTFEE", "PAYMENTISVAT", "PAYMENTVATRATE", "PAYMENTVATAMOUNT", "PAYMENTCOMMENTS",
        "VOUCHERNAME", "VOUCHERVETNAME", "VOUCHERVETADDRESS", "VOUCHERVETTOWN", "VOUCHERVETCOUNTY", "VOUCHERVETPOSTCODE", "VOUCHERDATEISSUED", "VOUCHERDATEPRESENTED", "VOUCHERDATEEXPIRED", "VOUCHERVALUE", "VOUCHERCODE", "VOUCHERCOMMENTS", 
        "DIARYDATE", "DIARYFOR", "DIARYSUBJECT", "DIARYNOTE",
        "CLINICAPPOINTMENTFOR", "CLINICAPPOINTMENTTYPE", "CLINICAPPOINTMENTSTATUS", 
        "CLINICAPPOINTMENTDATE", "CLINICAPPOINTMENTTIME",     "CLINICARRIVEDDATE", "CLINICARRIVEDTIME", 
        "CLINICWITHVETDATE", "CLINICWITHVETTIME", "CLINICCOMPLETEDDATE", "CLINICCOMPLETEDDATE", 
        "CLINICAPPOINTMENTISVAT", "CLINICAPPOINTMENTVATRATE", "CLINICAPPOINTMENTVATAMOUNT", "CLINICAPPOINTMENTREASON", "CLINICAPPOINTMENTREASON", "CLINICAPPOINTMENTCOMMENTS", "CLINICAMOUNT", 
        "DIARYDATE", "DIARYFOR", "DIARYSUBJECT", "DIARYNOTE" ]
    
    def tocsv(row: Dict) -> str:
        r = []
        for k in keys:
            if k in row: 
                r.append("\"%s\"" % str(row[k]).replace("\"", "\"\""))
            else:
                r.append("\"\"")
        return ",".join(r) + "\n"

    def nn(s: str) -> str:
        if s is None: return ""
        return s

    firstrow = True
    asm3.asynctask.set_progress_max(dbo, len(pids))
    for pid in pids:

        # Should we stop?
        if asm3.asynctask.get_cancel(dbo): break

        if firstrow:
            firstrow = False
            out.write(",".join(keys) + "\n")

        row = {}
        #p = asm3.person.get_person(dbo, pid["ID"])
        p = dbo.query("SELECT * FROM owner WHERE ID = %s" % (pid["ID"]) )
        if p is None: continue
        p = p[0]
        asm3.asynctask.increment_progress_value(dbo)

        row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
        row["PERSONDATEOFBIRTH"] = asm3.i18n.python2display(l, nn(p["DATEOFBIRTH"]))
        row["PERSONDATEOFBIRTH2"] = asm3.i18n.python2display(l, nn(p["DATEOFBIRTH2"]))
        row["PERSONTITLE"] = nn(p["OWNERTITLE"])
        row["PERSONINITIALS"] = nn(p["OWNERINITIALS"])
        row["PERSONFIRSTNAME"] = nn(p["OWNERFORENAMES"])
        row["PERSONLASTNAME"] = nn(p["OWNERSURNAME"])
        row["PERSONTITLE2"] = nn(p["OWNERTITLE2"])
        row["PERSONINITIALS2"] = nn(p["OWNERINITIALS2"])
        row["PERSONFIRSTNAME2"] = nn(p["OWNERFORENAMES2"])
        row["PERSONLASTNAME2"] = nn(p["OWNERSURNAME2"])
        row["PERSONADDRESS"] = nn(p["OWNERADDRESS"])
        row["PERSONCITY"] = nn(p["OWNERTOWN"])
        row["PERSONSTATE"] = nn(p["OWNERCOUNTY"])
        row["PERSONZIPCODE"] = nn(p["OWNERPOSTCODE"])
        row["PERSONHOMEPHONE"] = nn(p["HOMETELEPHONE"])
        row["PERSONWORKPHONE"] = nn(p["WORKTELEPHONE"])
        row["PERSONCELLPHONE"] = nn(p["MOBILETELEPHONE"])
        row["PERSONEMAIL"] = nn(p["EMAILADDRESS"])
        row["PERSONWORKPHONE2"] = nn(p["WORKTELEPHONE2"])
        row["PERSONCELLPHONE2"] = nn(p["MOBILETELEPHONE2"])
        row["PERSONEMAIL2"] = nn(p["EMAILADDRESS2"])
        row["PERSONGDPRCONTACT"] = nn(p["GDPRCONTACTOPTIN"])
        row["PERSONCLASS"] = asm3.utils.cint(p["OWNERTYPE"])
        row["PERSONMEMBER"] = asm3.utils.cint(p["ISMEMBER"])
        row["PERSONMEMBERSHIPNUMBER"] = nn(p["MEMBERSHIPNUMBER"])
        row["PERSONMEMBERSHIPEXPIRY"] = asm3.i18n.python2display(l, p["MEMBERSHIPEXPIRYDATE"])
        row["PERSONMATCHACTIVE"] = asm3.utils.cint(p["MATCHACTIVE"])
        row["PERSONMATCHADDED"] = asm3.i18n.python2display(l, p["MATCHADDED"])
        row["PERSONMATCHEXPIRES"] = asm3.i18n.python2display(l, p["MATCHEXPIRES"])
        row["PERSONMATCHSEX"] = asm3.utils.cint(p["MATCHSEX"])
        row["PERSONMATCHSIZE"] = asm3.utils.cint(p["MATCHSIZE"])
        row["PERSONMATCHCOLOR"] = asm3.utils.cint(p["MATCHCOLOUR"])
        row["PERSONMATCHAGEFROM"] = asm3.utils.cfloat(p["MATCHAGEFROM"])
        row["PERSONMATCHAGETO"] = asm3.utils.cfloat(p["MATCHAGETO"])
        row["PERSONMATCHTYPE"] = asm3.utils.cint(p["MATCHANIMALTYPE"])
        row["PERSONMATCHSPECIES"] = asm3.utils.cint(p["MATCHSPECIES"])
        row["PERSONMATCHBREED1"] = asm3.utils.cint(p["MATCHBREED"])
        row["PERSONMATCHBREED2"] = asm3.utils.cint(p["MATCHBREED2"])
        row["PERSONMATCHGOODWITHCATS"] = asm3.utils.cint(p["MATCHGOODWITHCATS"])
        row["PERSONMATCHGOODWITHDOGS"] = asm3.utils.cint(p["MATCHGOODWITHDOGS"])
        row["PERSONMATCHGOODWITHCHILDREN"] = asm3.utils.cint(p["MATCHGOODWITHCHILDREN"])
        row["PERSONMATCHGOODWITHELDERLY"] = asm3.utils.cint(p["MATCHGOODWITHELDERLY"])
        row["PERSONMATCHGOODONLEAD"] = asm3.utils.cint(p["MATCHGOODONLEAD"])
        row["PERSONMATCHGOODTRAVELLER"] = asm3.utils.cint(p["MATCHGOODTRAVELLER"])
        row["PERSONMATCHHOUSETRAINED"] = asm3.utils.cint(p["MATCHHOUSETRAINED"])
        row["PERSONMATCHCRATETRAINED"] = asm3.utils.cint(p["MATCHCRATETRAINED"])
        row["PERSONMATCHENERGYLEVEL"] = asm3.utils.cint(p["MATCHENERGYLEVEL"])
        row["PERSONMATCHCOMMENTSCONTAIN"] = nn(p["MATCHCOMMENTSCONTAIN"])
        row["PERSONCOMMENTS"] = nn(p["COMMENTS"])
        row["PERSONWARNING"] = nn(p["POPUPWARNING"])
        out.write(tocsv(row))

        if includemedia != "none":
            media = asm3.media.get_image_media(dbo, asm3.media.PERSON, p["ID"])
            if includemedia == "photo":
                for m in media:
                    if m["WEBSITEPHOTO"] == 1:
                        row["PERSONIMAGE"] = "%s?account=%s&method=media_image&mediaid=%s" % (SERVICE_URL, dbo.name(), m["ID"])
                        break
                out.write(tocsv(row))
            elif includemedia == "photos":
                for m in media:
                    if m["MEDIANAME"].endswith(".jpg"):
                        row = {}
                        row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
                        row["PERSONIMAGE"] = "%s?account=%s&method=media_file&mediaid=%s" % (SERVICE_URL, dbo.name(), m["ID"])
                        out.write(tocsv(row))
            elif includemedia == "all":
                for m in asm3.media.get_media(dbo, asm3.media.PERSON, p["ID"]):
                    if m["MEDIANAME"].endswith(".jpg") or m["MEDIANAME"].endswith(".pdf") or m["MEDIANAME"].endswith(".html"):
                        row = {}
                        row["PERSONCODE"] ="XP-" + nn(p["OWNERCODE"])
                        if m["MEDIANAME"].endswith(".jpg"):
                            row["PERSONIMAGE"] = "%s?account=%s&method=media_file&mediaid=%s" % (SERVICE_URL, dbo.name(), m["ID"])
                        elif m["MEDIANAME"].endswith(".pdf"):
                            row["PERSONPDFNAME"] = m["MEDIANOTES"]
                            if row["PERSONPDFNAME"].strip() == "": row["PERSONPDFNAME"] = "doc.pdf"
                            row["PERSONPDFDATA"] = "%s?account=%s&method=media_file&mediaid=%s" % (SERVICE_URL, dbo.name(), m["ID"])
                        elif m["MEDIANAME"].endswith(".html"):
                            row["PERSONHTMLNAME"] = m["MEDIANOTES"]
                            if row["PERSONHTMLNAME"].strip() == "": row["PERSONHTMLNAME"] = "doc.html"
                            row["PERSONHTMLDATA"] = "%s?account=%s&method=media_file&mediaid=%s" % (SERVICE_URL, dbo.name(), m["ID"])
                        out.write(tocsv(row))

        for n in asm3.diary.get_diaries(dbo, asm3.diary.PERSON, p["ID"]):
            row = {}
            row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
            row["DIARYDATE"] = asm3.i18n.python2display(l, n["DIARYDATETIME"])
            row["DIARYFOR"] = nn(n["DIARYFORNAME"])
            row["DIARYSUBJECT"] = nn(n["SUBJECT"])
            row["DIARYNOTE"] = nn(n["NOTE"])
            out.write(tocsv(row))
        
        for g in asm3.log.get_logs(dbo, asm3.log.PERSON, p["ID"]):
            row = {}
            row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
            row["LOGDATE"] = asm3.i18n.python2display(l, g["DATE"])
            row["LOGTIME"] = asm3.i18n.format_time(g["DATE"])
            row["LOGTYPE"] = nn(g["LOGTYPENAME"])
            row["LOGCOMMENTS"] = nn(g["COMMENTS"])
            out.write(tocsv(row))
        
        for li in dbo.query(asm3.financial.get_licence_query(dbo) + " WHERE ol.OwnerID = " + str(p["ID"])):
            row = {}
            row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
            row["LICENSENUMBER"] = nn(li["LICENCENUMBER"])
            row["ANIMALCODE"] = nn(li["SHELTERCODE"])
            row["LICENSETYPE"] = nn(li["LICENCETYPENAME"])
            row["LICENSEFEE"] = asm3.utils.cint(li["LICENCEFEE"])
            row["LICENSEISSUEDATE"] = asm3.i18n.python2display(l, li["ISSUEDATE"])
            row["LICENSEEXPIRESDATE"] = asm3.i18n.python2display(l, li["EXPIRYDATE"])
            row["LICENSECOMMENTS"] = nn(li["COMMENTS"])
            out.write(tocsv(row))
        
        for i in asm3.person.get_investigation(dbo, p["ID"]):
            row = {}
            row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
            row["INVESTIGATIONDATE"] = asm3.i18n.python2display(l, i["DATE"])
            row["INVESTIGATIONNOTES"] = nn(i["NOTES"])
            out.write(tocsv(row))
       
        for c in dbo.query(asm3.financial.get_citation_query(dbo) + " WHERE oc.OwnerID = " + str(p["ID"])):
            row = {}
            row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
            row["CITATIONDATE"] = asm3.i18n.python2display(l, c["CITATIONDATE"])
            row["CITATIONNUMBER"] = nn(c["CITATIONNUMBER"])
            row["CITATIONTYPE"] = nn(c["CITATIONNAME"])
            row["FINEAMOUNT"] = asm3.utils.cint(c["FINEAMOUNT"])
            row["FINEDUEDATE"] = asm3.i18n.python2display(l, c["FINEDUEDATE"])
            row["FINEPAIDDATE"] = asm3.i18n.python2display(l, c["FINEPAIDDATE"])
            row["CITATIONCOMMENTS"] = nn(c["COMMENTS"])
            out.write(tocsv(row))
        
        for t in dbo.query(asm3.animalcontrol.get_traploan_query(dbo) + " WHERE ot.OwnerID = " + str(p["ID"])):
            row = {}
            row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
            row["TRAPTYPE"] = nn(t["TRAPTYPENAME"])
            row["TRAPNUMBER"] = nn(t["TRAPNUMBER"])
            row["LOANDATE"] = asm3.i18n.python2display(l, t["LOANDATE"])
            row["DEPOSITAMOUNT"] = asm3.utils.cint(t["DEPOSITAMOUNT"])
            row["DEPOSITRETURNDATE"] = asm3.i18n.python2display(l, t["DEPOSITRETURNDATE"])
            row["RETURNDUEDATE"] = asm3.i18n.python2display(l, t["RETURNDUEDATE"])
            row["RETURNDATE"] = asm3.i18n.python2display(l, t["RETURNDATE"])
            row["TRAPLOANCOMMENTS"] = nn(t["COMMENTS"])
            out.write(tocsv(row))
        
        for d in dbo.query(asm3.financial.get_donation_query(dbo) + " WHERE od.OwnerID = " + str(p["ID"])):
            row = {}
            row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
            row["DONATIONNAME"] = nn(d["DONATIONNAME"])
            row["DONATIONDATE"] = asm3.i18n.python2display(l, d["DATE"])
            row["DONATIONAMOUNT"] = asm3.utils.cint(d["DONATION"])
            row["PAYMENTNAME"] = nn(d["PAYMENTNAME"])
            row["PAYMENTISGIFTAID"] = nn(d["ISGIFTAIDNAME"])
            row["PAYMENTFREQUENCY"] = nn(d["FREQUENCYNAME"])
            row["PAYMENTRECEIPTNUMBER"] = nn(d["RECEIPTNUMBER"])
            row["PAYMENTCHEQUENUMBER"] = nn(d["CHEQUENUMBER"])
            row["PAYMENTFEE"] = asm3.utils.cint(d["FEE"])
            row["PAYMENTISVAT"] = asm3.utils.cint(d["ISVAT"])
            row["PAYMENTVATRATE"] = asm3.utils.cfloat(d["VATRATE"])
            row["PAYMENTVATAMOUNT"] = asm3.utils.cint(d["VATAMOUNT"])
            row["PAYMENTCOMMENTS"] = nn(d["COMMENTS"])
            out.write(tocsv(row))
        
        for v in dbo.query(asm3.financial.get_voucher_query(dbo) + " WHERE ov.OwnerID = " + str(p["ID"])):
            row = {}
            row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
            row["ANIMALCODE"] = nn(v["SHELTERCODE"])
            row["ANIMALNAME"] = nn(v["ANIMALNAME"])
            row["VOUCHERNAME"] = nn(v["VOUCHERNAME"])
            row["VOUCHERVETNAME"] = nn(v["VETNAME"])
            row["VOUCHERVETADDRESS"] = nn(v["VETADDRESS"])
            row["VOUCHERVETTOWN"] = nn(v["VETTOWN"])
            row["VOUCHERVETCOUNTY"] = nn(v["VETCOUNTY"])
            row["VOUCHERVETPOSTCODE"] = nn(v["VETPOSTCODE"])
            row["VOUCHERDATEISSUED"] = asm3.i18n.python2display(l, v["DATEISSUED"])
            row["VOUCHERDATEPRESENTED"] = asm3.i18n.python2display(l, v["DATEPRESENTED"])
            row["VOUCHERDATEEXPIRED"] = asm3.i18n.python2display(l, v["DATEEXPIRED"])
            row["VOUCHERVALUE"] = asm3.utils.cint(v["VALUE"])
            row["VOUCHERCODE"] = nn(v["VOUCHERCODE"])
            row["VOUCHERCOMMENTS"] = nn(v["COMMENTS"])
            out.write(tocsv(row))
        
        for a in dbo.query(asm3.clinic.get_clinic_appointment_query(dbo) + " WHERE ca.OwnerID = " + str(p["ID"])):
            row = {}
            row["PERSONCODE"] = "XP-" + nn(p["OWNERCODE"])
            row["ANIMALCODE"] = nn(a["SHELTERCODE"])
            row["CLINICAPPOINTMENTFOR"] = nn(a["APPTFOR"])
            row["CLINICAPPOINTMENTTYPE"] = nn(a["CLINICTYPENAME"])
            row["CLINICAPPOINTMENTSTATUS"] = nn(a["CLINICSTATUSNAME"])
            row["CLINICAPPOINTMENTDATE"] = asm3.i18n.python2display(l, a["DATETIME"])
            row["CLINICAPPOINTMENTTIME"] = asm3.i18n.format_time(a["DATETIME"])
            row["CLINICARRIVEDDATE"] = asm3.i18n.python2display(l, a["ARRIVEDDATETIME"])
            row["CLINICARRIVEDTIME"] = asm3.i18n.format_time(a["ARRIVEDDATETIME"])
            row["CLINICWITHVETDATE"] = asm3.i18n.python2display(l, a["WITHVETDATETIME"])
            row["CLINICWITHVETTIME"] = asm3.i18n.format_time(a["WITHVETDATETIME"])
            row["CLINICCOMPLETEDDATE"] = asm3.i18n.python2display(l, a["COMPLETEDDATETIME"])
            row["CLINICCOMPLETEDTIME"] = asm3.i18n.format_time(a["COMPLETEDDATETIME"])
            row["CLINICAPPOINTMENTISVAT"] = asm3.utils.cint(a["ISVAT"])
            row["CLINICAPPOINTMENTVATRATE"] = asm3.utils.cfloat(a["VATRATE"])
            row["CLINICAPPOINTMENTVATAMOUNT"] = asm3.utils.cfloat(a["VATAMOUNT"])
            row["CLINICAPPOINTMENTREASON"] = nn(a["REASONFORAPPOINTMENT"])
            row["CLINICAPPOINTMENTCOMMENTS"] = nn(a["COMMENTS"])
            row["CLINICAMOUNT"] = nn(a["AMOUNT"])
            out.write(tocsv(row))

        del p
        del row

    # Generate a disk cache key and store the data in the cache so it can be retrieved for the next hour
    key = asm3.utils.uuid_str()
    asm3.cachedisk.put(key, dbo.name(), out.getvalue(), 3600)
    h = '<p>%s <a target="_blank" href="csvexport_people_ex?get=%s"><b>%s</b></p>' % ( \
        asm3.i18n._("Export complete ({0} entries).", l).format(len(pids)), key, asm3.i18n._("Download File", l) )
    return h
