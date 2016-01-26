#!/usr/bin/python

import additional
import animal
import animalcontrol
import configuration
import dbfs
import financial
import html
import log
import lookups
import media
import medical
import movement
import person
import publish
import users
import utils
import zipfile
from i18n import _, format_currency_no_symbol, format_time, now, python2display, yes_no
from sitedefs import BASE_URL, QR_IMG_SRC
from cStringIO import StringIO

def org_tags(dbo, username):
    """
    Generates a list of tags from the organisation and user info
    """
    u = users.get_users(dbo, username)
    realname = ""
    email = ""
    sig = ""
    if len(u) > 0:
        u = u[0]
        realname = utils.nulltostr(u["REALNAME"])
        email = utils.nulltostr(u["EMAILADDRESS"])
        sig = utils.nulltostr(u["SIGNATURE"])
    tags = {
        "ORGANISATION"          : configuration.organisation(dbo),
        "ORGANISATIONADDRESS"   : configuration.organisation_address(dbo),
        "ORGANISATIONTELEPHONE" : configuration.organisation_telephone(dbo),
        "DATE"                  : python2display(dbo.locale, now(dbo.timezone)),
        "USERNAME"              : username,
        "USERREALNAME"          : realname,
        "USEREMAILADDRESS"      : email,
        "USERSIGNATURE"         : "<img src=\"" + sig + "\" >",
        "USERSIGNATURESRC"      : sig
    }
    return tags

def additional_yesno(l, af):
    """
    Returns the yes/no value for an additional field. If it has a LOOKUPVALUES
    set, we use the value the user set.
    """
    if af["LOOKUPVALUES"] is not None and af["LOOKUPVALUES"].strip() != "":
        values = af["LOOKUPVALUES"].split("|")
        for v in values:
            if af["VALUE"] is None:
                if v.strip().startswith("0"):
                    return v[v.find("=")+1:]
            else:
                if v.strip().startswith(af["VALUE"]):
                    return v[v.find("=")+1:]
    else:
        return yes_no(l, af["VALUE"] == "1")

def br(s):
    """ Returns s with linebreaks turned to <br/> tags """
    if s is None: return ""
    s = s.replace("\r\n", "<br/>").replace("\n", "<br/>")
    return s

def fw(s):
    """ Returns the first word of a string """
    if s is None: return ""
    if s.find(" ") == -1: return s
    return s.split(" ")[0]

def animal_tags(dbo, a):
    """
    Generates a list of tags from an animal result (the deep type from
    calling animal.get_animal)
    """
    l = dbo.locale
    qr = QR_IMG_SRC % { "url": BASE_URL + "/animal?id=%d" % a["ID"], "size": "150x150" }
    animalage = a["ANIMALAGE"]
    if not animalage is None and animalage.endswith("."): animalage = animalage[0:len(animalage)-1]
    timeonshelter = a["TIMEONSHELTER"]
    if timeonshelter.endswith("."): timeonshelter = timeonshelter[0:len(timeonshelter)-1]
    displaydob = python2display(l, a["DATEOFBIRTH"])
    displayage = animalage
    estimate = ""
    if a["ESTIMATEDDOB"] == 1: 
        displaydob = a["AGEGROUP"]
        displayage = a["AGEGROUP"]
        estimate = _("estimate", l)

    tags = { 
        "ANIMALNAME"            : a["ANIMALNAME"],
        "ANIMALTYPENAME"        : a["ANIMALTYPENAME"],
        "BASECOLOURNAME"        : a["BASECOLOURNAME"],
        "BASECOLORNAME"         : a["BASECOLOURNAME"],
        "BREEDNAME"             : a["BREEDNAME"],
        "INTERNALLOCATION"      : a["SHELTERLOCATIONNAME"],
        "LOCATIONNAME"          : a["SHELTERLOCATIONNAME"],
        "LOCATIONDESCRIPTION"   : a["SHELTERLOCATIONDESCRIPTION"],
        "LOCATIONUNIT"          : a["SHELTERLOCATIONUNIT"],
        "DISPLAYLOCATION"       : a["DISPLAYLOCATION"],
        "COATTYPE"              : a["COATTYPENAME"],
        "HEALTHPROBLEMS"        : a["HEALTHPROBLEMS"],
        "HEALTHPROBLEMSBR"      : br(a["HEALTHPROBLEMS"]),
        "ANIMALCREATEDBY"       : a["CREATEDBY"],
        "ANIMALCREATEDDATE"     : python2display(l, a["CREATEDDATE"]),
        "DATEBROUGHTIN"         : python2display(l, a["DATEBROUGHTIN"]),
        "TIMEBROUGHTIN"         : format_time(a["DATEBROUGHTIN"]),
        "DATEOFBIRTH"           : python2display(l, a["DATEOFBIRTH"]),
        "AGEGROUP"              : a["AGEGROUP"],
        "DISPLAYDOB"            : displaydob,
        "DISPLAYAGE"            : displayage,
        "ESTIMATEDDOB"          : estimate,
        "HOLDUNTILDATE"         : python2display(l, a["HOLDUNTILDATE"]),
        "ANIMALID"              : str(a["ID"]),
        "FEE"                   : format_currency_no_symbol(l, a["FEE"]),
        "IDENTICHIPNUMBER"      : a["IDENTICHIPNUMBER"],
        "IDENTICHIPPED"         : a["IDENTICHIPPEDNAME"],
        "IDENTICHIPPEDDATE"     : python2display(l, a["IDENTICHIPDATE"]),
        "MICROCHIPNUMBER"       : a["IDENTICHIPNUMBER"],
        "MICROCHIPPED"          : a["IDENTICHIPPEDNAME"],
        "MICROCHIPDATE"         : python2display(l, a["IDENTICHIPDATE"]),
        "MICROCHIPMANUFACTURER" : lookups.get_microchip_manufacturer(l, a["IDENTICHIPNUMBER"]),
        "TATTOO"                : a["TATTOONAME"],
        "TATTOODATE"            : python2display(l, a["TATTOODATE"]),
        "TATTOONUMBER"          : a["TATTOONUMBER"],
        "COMBITESTED"           : a["COMBITESTEDNAME"],
        "FIVLTESTED"            : a["COMBITESTEDNAME"],
        "COMBITESTDATE"         : utils.iif(a["COMBITESTED"] == 1, python2display(l, a["COMBITESTDATE"]), ""),
        "FIVLTESTDATE"          : utils.iif(a["COMBITESTED"] == 1, python2display(l, a["COMBITESTDATE"]), ""),
        "COMBITESTRESULT"       : utils.iif(a["COMBITESTED"] == 1, a["COMBITESTRESULTNAME"], ""),
        "FIVTESTRESULT"         : utils.iif(a["COMBITESTED"] == 1, a["COMBITESTRESULTNAME"], ""),
        "FIVRESULT"             : utils.iif(a["COMBITESTED"] == 1, a["COMBITESTRESULTNAME"], ""),
        "FLVTESTRESULT"         : utils.iif(a["COMBITESTED"] == 1, a["FLVRESULTNAME"], ""),
        "FLVRESULT"             : utils.iif(a["COMBITESTED"] == 1, a["FLVRESULTNAME"], ""),
        "HEARTWORMTESTED"       : a["HEARTWORMTESTEDNAME"],
        "HEARTWORMTESTDATE"     : utils.iif(a["HEARTWORMTESTED"] == 1, python2display(l, a["HEARTWORMTESTDATE"]), ""),
        "HEARTWORMTESTRESULT"   : utils.iif(a["HEARTWORMTESTED"] == 1, a["HEARTWORMTESTRESULTNAME"], ""),
        "HIDDENANIMALDETAILS"   : a["HIDDENANIMALDETAILS"],
        "HIDDENANIMALDETAILSBR" : br(a["HIDDENANIMALDETAILS"]),
        "ANIMALLASTCHANGEDBY"   : a["LASTCHANGEDBY"],
        "ANIMALLASTCHANGEDDATE" : python2display(l, a["LASTCHANGEDDATE"]),
        "MARKINGS"              : a["MARKINGS"],
        "MARKINGSBR"            : br(a["MARKINGS"]),
        "DECLAWED"              : a["DECLAWEDNAME"],
        "RABIESTAG"             : a["RABIESTAG"],
        "GOODWITHCATS"          : a["ISGOODWITHCATSNAME"],
        "GOODWITHDOGS"          : a["ISGOODWITHDOGSNAME"],
        "GOODWITHCHILDREN"      : a["ISGOODWITHCHILDRENNAME"],
        "HOUSETRAINED"          : a["ISHOUSETRAINEDNAME"],
        "NAMEOFPERSONBROUGHTANIMALIN" : a["BROUGHTINBYOWNERNAME"],
        "ADDRESSOFPERSONBROUGHTANIMALIN" : a["BROUGHTINBYOWNERADDRESS"],
        "TOWNOFPERSONBROUGHTANIMALIN" : a["BROUGHTINBYOWNERTOWN"],
        "COUNTYOFPERSONBROUGHTANIMALIN": a["BROUGHTINBYOWNERCOUNTY"],
        "POSTCODEOFPERSONBROUGHTIN": a["BROUGHTINBYOWNERPOSTCODE"],
        "CITYOFPERSONBROUGHTANIMALIN" : a["BROUGHTINBYOWNERTOWN"],
        "STATEOFPERSONBROUGHTANIMALIN": a["BROUGHTINBYOWNERCOUNTY"],
        "ZIPCODEOFPERSONBROUGHTIN": a["BROUGHTINBYOWNERPOSTCODE"],
        "BROUGHTINBYNAME"     : a["BROUGHTINBYOWNERNAME"],
        "BROUGHTINBYADDRESS"  : a["BROUGHTINBYOWNERADDRESS"],
        "BROUGHTINBYTOWN"     : a["BROUGHTINBYOWNERTOWN"],
        "BROUGHTINBYCOUNTY"   : a["BROUGHTINBYOWNERCOUNTY"],
        "BROUGHTINBYPOSTCODE" : a["BROUGHTINBYOWNERPOSTCODE"],
        "BROUGHTINBYCITY"     : a["BROUGHTINBYOWNERTOWN"],
        "BROUGHTINBYSTATE"    : a["BROUGHTINBYOWNERCOUNTY"],
        "BROUGHTINBYZIPCODE"  : a["BROUGHTINBYOWNERPOSTCODE"],
        "BROUGHTINBYHOMEPHONE" : a["BROUGHTINBYHOMETELEPHONE"],
        "BROUGHTINBYPHONE"    : a["BROUGHTINBYHOMETELEPHONE"],
        "BROUGHTINBYWORKPHONE" : a["BROUGHTINBYWORKTELEPHONE"],
        "BROUGHTINBYMOBILEPHONE" : a["BROUGHTINBYMOBILETELEPHONE"],
        "BROUGHTINBYCELLPHONE" : a["BROUGHTINBYMOBILETELEPHONE"],
        "BROUGHTINBYEMAIL"    : a["BROUGHTINBYEMAILADDRESS"],
        "BONDEDANIMAL1NAME"     : a["BONDEDANIMAL1NAME"],
        "BONDEDANIMAL1CODE"     : a["BONDEDANIMAL1CODE"],
        "BONDEDANIMAL2NAME"     : a["BONDEDANIMAL2NAME"],
        "BONDEDANIMAL2CODE"     : a["BONDEDANIMAL2CODE"],
        "NAMEOFOWNERSVET"       : a["OWNERSVETNAME"],
        "NAMEOFCURRENTVET"      : a["CURRENTVETNAME"],
        "HASSPECIALNEEDS"       : a["HASSPECIALNEEDSNAME"],
        "NEUTERED"              : a["NEUTEREDNAME"],
        "FIXED"                 : a["NEUTEREDNAME"],
        "ALTERED"               : a["NEUTEREDNAME"],
        "NEUTEREDDATE"          : python2display(l, a["NEUTEREDDATE"]),
        "FIXEDDATE"             : python2display(l, a["NEUTEREDDATE"]),
        "ALTEREDDATE"           : python2display(l, a["NEUTEREDDATE"]),
        "ORIGINALOWNERNAME"     : a["ORIGINALOWNERNAME"],
        "ORIGINALOWNERADDRESS"  : a["ORIGINALOWNERADDRESS"],
        "ORIGINALOWNERTOWN"     : a["ORIGINALOWNERTOWN"],
        "ORIGINALOWNERCOUNTY"   : a["ORIGINALOWNERCOUNTY"],
        "ORIGINALOWNERPOSTCODE" : a["ORIGINALOWNERPOSTCODE"],
        "ORIGINALOWNERCITY"     : a["ORIGINALOWNERTOWN"],
        "ORIGINALOWNERSTATE"    : a["ORIGINALOWNERCOUNTY"],
        "ORIGINALOWNERZIPCODE"  : a["ORIGINALOWNERPOSTCODE"],
        "ORIGINALOWNERHOMEPHONE" : a["ORIGINALOWNERHOMETELEPHONE"],
        "ORIGINALOWNERPHONE"    : a["ORIGINALOWNERHOMETELEPHONE"],
        "ORIGINALOWNERWORKPHONE" : a["ORIGINALOWNERWORKTELEPHONE"],
        "ORIGINALOWNERMOBILEPHONE" : a["ORIGINALOWNERMOBILETELEPHONE"],
        "ORIGINALOWNERCELLPHONE" : a["ORIGINALOWNERMOBILETELEPHONE"],
        "ORIGINALOWNEREMAIL"    : a["ORIGINALOWNEREMAILADDRESS"],
        "CURRENTOWNERNAME"     : a["CURRENTOWNERNAME"],
        "CURRENTOWNERADDRESS"  : a["CURRENTOWNERADDRESS"],
        "CURRENTOWNERTOWN"     : a["CURRENTOWNERTOWN"],
        "CURRENTOWNERCOUNTY"   : a["CURRENTOWNERCOUNTY"],
        "CURRENTOWNERPOSTCODE" : a["CURRENTOWNERPOSTCODE"],
        "CURRENTOWNERCITY"     : a["CURRENTOWNERTOWN"],
        "CURRENTOWNERSTATE"    : a["CURRENTOWNERCOUNTY"],
        "CURRENTOWNERZIPCODE"  : a["CURRENTOWNERPOSTCODE"],
        "CURRENTOWNERHOMEPHONE" : a["CURRENTOWNERHOMETELEPHONE"],
        "CURRENTOWNERPHONE"    : a["CURRENTOWNERHOMETELEPHONE"],
        "CURRENTOWNERWORKPHONE" : a["CURRENTOWNERWORKTELEPHONE"],
        "CURRENTOWNERMOBILEPHONE" : a["CURRENTOWNERMOBILETELEPHONE"],
        "CURRENTOWNERCELLPHONE" : a["CURRENTOWNERMOBILETELEPHONE"],
        "CURRENTOWNEREMAIL"     : a["CURRENTOWNEREMAILADDRESS"],
        "CURRENTVETNAME"        : a["CURRENTVETNAME"],
        "CURRENTVETADDRESS"     : a["CURRENTVETADDRESS"],
        "CURRENTVETTOWN"        : a["CURRENTVETTOWN"],
        "CURRENTVETCOUNTY"      : a["CURRENTVETCOUNTY"],
        "CURRENTVETPOSTCODE"    : a["CURRENTVETPOSTCODE"],
        "CURRENTVETCITY"        : a["CURRENTVETTOWN"],
        "CURRENTVETSTATE"       : a["CURRENTVETCOUNTY"],
        "CURRENTVETZIPCODE"     : a["CURRENTVETPOSTCODE"],
        "CURRENTVETPHONE"       : a["CURRENTVETWORKTELEPHONE"],
        "OWNERSVETNAME"         : a["OWNERSVETNAME"],
        "OWNERSVETADDRESS"      : a["OWNERSVETADDRESS"],
        "OWNERSVETTOWN"         : a["OWNERSVETTOWN"],
        "OWNERSVETCOUNTY"       : a["OWNERSVETCOUNTY"],
        "OWNERSVETPOSTCODE"     : a["OWNERSVETPOSTCODE"],
        "OWNERSVETCITY"         : a["OWNERSVETTOWN"],
        "OWNERSVETSTATE"        : a["OWNERSVETCOUNTY"],
        "OWNERSVETZIPCODE"      : a["OWNERSVETPOSTCODE"],
        "OWNERSVETPHONE"        : a["OWNERSVETWORKTELEPHONE"],
        "RESERVEDOWNERNAME"     : a["RESERVEDOWNERNAME"],
        "RESERVEDOWNERADDRESS"  : a["RESERVEDOWNERADDRESS"],
        "RESERVEDOWNERTOWN"     : a["RESERVEDOWNERTOWN"],
        "RESERVEDOWNERCOUNTY"   : a["RESERVEDOWNERCOUNTY"],
        "RESERVEDOWNERPOSTCODE" : a["RESERVEDOWNERPOSTCODE"],
        "RESERVEDOWNERCITY"     : a["RESERVEDOWNERTOWN"],
        "RESERVEDOWNERSTATE"    : a["RESERVEDOWNERCOUNTY"],
        "RESERVEDOWNERZIPCODE"  : a["RESERVEDOWNERPOSTCODE"],
        "RESERVEDOWNERHOMEPHONE" : a["RESERVEDOWNERHOMETELEPHONE"],
        "RESERVEDOWNERPHONE"    : a["RESERVEDOWNERHOMETELEPHONE"],
        "RESERVEDOWNERWORKPHONE" : a["RESERVEDOWNERWORKTELEPHONE"],
        "RESERVEDOWNERMOBILEPHONE" : a["RESERVEDOWNERMOBILETELEPHONE"],
        "RESERVEDOWNERCELLPHONE" : a["RESERVEDOWNERMOBILETELEPHONE"],
        "RESERVEDOWNEREMAIL"    : a["RESERVEDOWNEREMAILADDRESS"],
        "ENTRYCATEGORY"         : a["ENTRYREASONNAME"],
        "REASONFORENTRY"        : a["REASONFORENTRY"],
        "REASONFORENTRYBR"      : br(a["REASONFORENTRY"]),
        "REASONNOTBROUGHTBYOWNER" : a["REASONNO"],
        "SEX"                   : a["SEXNAME"],
        "SIZE"                  : a["SIZENAME"],
        "WEIGHT"                : utils.nulltostr(a["WEIGHT"]),
        "SPECIESNAME"           : a["SPECIESNAME"],
        "ANIMALCOMMENTS"        : a["ANIMALCOMMENTS"],
        "ANIMALCOMMENTSBR"      : br(a["ANIMALCOMMENTS"]),
        "SHELTERCODE"           : a["SHELTERCODE"],
        "AGE"                   : animalage,
        "ACCEPTANCENUMBER"      : a["ACCEPTANCENUMBER"],
        "LITTERID"              : a["ACCEPTANCENUMBER"],
        "DECEASEDDATE"          : python2display(l, a["DECEASEDDATE"]),
        "DECEASEDNOTES"         : a["PTSREASON"],
        "DECEASEDCATEGORY"      : a["PTSREASONNAME"],
        "SHORTSHELTERCODE"      : a["SHORTCODE"],
        "MOSTRECENTENTRY"       : python2display(l, a["MOSTRECENTENTRYDATE"]),
        "TIMEONSHELTER"         : timeonshelter,
        "WEBMEDIAFILENAME"      : a["WEBSITEMEDIANAME"],
        "WEBSITEIMAGECOUNT"     : a["WEBSITEIMAGECOUNT"],
        "WEBSITEMEDIANAME"      : a["WEBSITEMEDIANAME"],
        "WEBSITEVIDEOURL"       : a["WEBSITEVIDEOURL"],
        "WEBSITEVIDEONOTES"     : a["WEBSITEVIDEONOTES"],
        "WEBMEDIANOTES"         : a["WEBSITEMEDIANOTES"],
        "WEBSITEMEDIANOTES"     : a["WEBSITEMEDIANOTES"],
        "DOCUMENTIMGLINK"       : "<img height=\"200\" src=\"" + html.doc_img_src(a, "animal") + "\" >",
        "DOCUMENTIMGTHUMBLINK"  : "<img src=\"" + html.thumbnail_img_src(a, "animalthumb") + "\" />",
        "DOCUMENTQRLINK"        : "<img src=\"%s\" />" % qr,
        "ANIMALONSHELTER"       : yes_no(l, a["ARCHIVED"] == 0),
        "ANIMALONFOSTER"        : yes_no(l, a["ACTIVEMOVEMENTTYPE"] == movement.FOSTER),
        "ANIMALPERMANENTFOSTER" : yes_no(l, a["HASPERMANENTFOSTER"] == 1),
        "ANIMALATRETAILER"      : yes_no(l, a["ACTIVEMOVEMENTTYPE"] == movement.RETAILER),
        "ANIMALISADOPTABLE"     : utils.iif(publish.is_adoptable(dbo, a["ID"]), _("Yes", l), _("No", l)),
        "ANIMALISRESERVED"      : yes_no(l, a["HASACTIVERESERVE"] == 1),
        "ADOPTIONSTATUS"        : publish.get_adoption_status(dbo, a),
        "ADOPTIONID"            : a["ACTIVEMOVEMENTADOPTIONNUMBER"],
        "OUTCOMEDATE"           : utils.iif(a["DECEASEDDATE"] is None, python2display(l, a["ACTIVEMOVEMENTDATE"]), python2display(l, a["DECEASEDDATE"])),
        "OUTCOMETYPE"           : utils.iif(a["ARCHIVED"] == 1, a["DISPLAYLOCATIONNAME"], "")
    }

    # Set original owner to be current owner on non-shelter animals
    if a["NONSHELTERANIMAL"] == 1 and a["ORIGINALOWNERNAME"] is not None and a["ORIGINALOWNERNAME"] != "":
        tags["CURRENTOWNERNAME"] = a["ORIGINALOWNERNAME"]
        tags["CURRENTOWNERADDRESS"] = a["ORIGINALOWNERADDRESS"]
        tags["CURRENTOWNERTOWN"] = a["ORIGINALOWNERTOWN"]
        tags["CURRENTOWNERCOUNTY"] = a["ORIGINALOWNERCOUNTY"]
        tags["CURRENTOWNERPOSTCODE"] = a["ORIGINALOWNERPOSTCODE"]
        tags["CURRENTOWNERCITY"] = a["ORIGINALOWNERTOWN"]
        tags["CURRENTOWNERSTATE"] = a["ORIGINALOWNERCOUNTY"]
        tags["CURRENTOWNERZIPCODE"] = a["ORIGINALOWNERPOSTCODE"]
        tags["CURRENTOWNERHOMEPHONE"] = a["ORIGINALOWNERHOMETELEPHONE"]
        tags["CURRENTOWNERPHONE"] = a["ORIGINALOWNERHOMETELEPHONE"]
        tags["CURRENTOWNERWORKPHONE"] = a["ORIGINALOWNERWORKTELEPHONE"]
        tags["CURRENTOWNERMOBILEPHONE"] = a["ORIGINALOWNERMOBILETELEPHONE"]
        tags["CURRENTOWNERCELLPHONE"] = a["ORIGINALOWNERMOBILETELEPHONE"]
        tags["CURRENTOWNEREMAIL"] = a["ORIGINALOWNEREMAILADDRESS"]

    # If the animal doesn't have a current owner, but does have an open
    # movement with a future date on it, look up the owner and use that 
    # instead so that we can still generate paperwork for future adoptions.
    if a["CURRENTOWNERID"] is None or a["CURRENTOWNERID"] == 0:
        latest = animal.get_latest_movement(dbo, a["ID"])
        if latest is not None:
            p = person.get_person(dbo, latest["OWNERID"])
            if p is not None:
                tags["CURRENTOWNERNAME"] = p["OWNERNAME"]
                tags["CURRENTOWNERADDRESS"] = p["OWNERADDRESS"]
                tags["CURRENTOWNERTOWN"] = p["OWNERTOWN"]
                tags["CURRENTOWNERCOUNTY"] = p["OWNERCOUNTY"]
                tags["CURRENTOWNERPOSTCODE"] = p["OWNERPOSTCODE"]
                tags["CURRENTOWNERCITY"] = p["OWNERTOWN"]
                tags["CURRENTOWNERSTATE"] = p["OWNERCOUNTY"]
                tags["CURRENTOWNERZIPCODE"] = p["OWNERPOSTCODE"]
                tags["CURRENTOWNERHOMEPHONE"] = p["HOMETELEPHONE"]
                tags["CURRENTOWNERPHONE"] = p["HOMETELEPHONE"]
                tags["CURRENTOWNERWORKPHONE"] = p["WORKTELEPHONE"]
                tags["CURRENTOWNERMOBILEPHONE"] = p["MOBILETELEPHONE"]
                tags["CURRENTOWNERCELLPHONE"] = p["MOBILETELEPHONE"]
                tags["CURRENTOWNEREMAIL"] = p["EMAILADDRESS"]

    # Additional fields
    add = additional.get_additional_fields(dbo, a["ID"], "animal")
    for af in add:
        val = af["VALUE"]
        if af["FIELDTYPE"] == additional.YESNO:
            val = additional_yesno(l, af)
        if af["FIELDTYPE"] == additional.MONEY:
            val = format_currency_no_symbol(l, af["VALUE"])
        tags[af["FIELDNAME"].upper()] = val

    include_incomplete_vacc = configuration.include_incomplete_vacc_doc(dbo)
    include_incomplete_medical = configuration.include_incomplete_medical_doc(dbo)
    
    # Vaccinations
    d = {
        "VACCINATIONNAME":          "VACCINATIONTYPE",
        "VACCINATIONREQUIRED":      "d:DATEREQUIRED",
        "VACCINATIONGIVEN":         "d:DATEOFVACCINATION",
        "VACCINATIONEXPIRES":       "d:DATEEXPIRES",
        "VACCINATIONBATCH":         "BATCHNUMBER",
        "VACCINATIONMANUFACTURER":  "MANUFACTURER",
        "VACCINATIONCOST":          "c:COST",
        "VACCINATIONCOMMENTS":      "COMMENTS",
        "VACCINATIONDESCRIPTION":   "VACCINATIONDESCRIPTION"
    }
    tags.update(table_tags(dbo, d, medical.get_vaccinations(dbo, a["ID"], not include_incomplete_vacc), "VACCINATIONTYPE", "DATEOFVACCINATION"))
    tags["ANIMALISVACCINATED"] = utils.iif(medical.get_vaccinated(dbo, a["ID"]), _("Yes", l), _("No", l))

    # Tests
    d = {
        "TESTNAME":                 "TESTNAME",
        "TESTRESULT":               "RESULTNAME",
        "TESTREQUIRED":             "d:DATEREQUIRED",
        "TESTGIVEN":                "d:DATEOFTEST",
        "TESTCOST":                 "c:COST",
        "TESTCOMMENTS":             "COMMENTS",
        "TESTDESCRIPTION":          "TESTDESCRIPTION"
    }
    tags.update(table_tags(dbo, d, medical.get_tests(dbo, a["ID"], not include_incomplete_vacc), "TESTNAME", "DATEOFTEST"))

    # Medical
    d = {
        "MEDICALNAME":              "TREATMENTNAME",
        "MEDICALCOMMENTS":          "COMMENTS",
        "MEDICALFREQUENCY":         "NAMEDFREQUENCY",
        "MEDICALNUMBEROFTREATMENTS": "NAMEDNUMBEROFTREATMENTS",
        "MEDICALSTATUS":            "NAMEDSTATUS",
        "MEDICALDOSAGE":            "DOSAGE",
        "MEDICALSTARTDATE":         "d:STARTDATE",
        "MEDICALTREATMENTSGIVEN":   "TREATMENTSGIVEN",
        "MEDICALTREATMENTSREMAINING": "TREATMENTSREMAINING",
        "MEDICALNEXTTREATMENTDUE":  "d:NEXTTREATMENTDUE",
        "MEDICALLASTTREATMENTGIVEN": "d:LASTTREATMENTGIVEN",
        "MEDICALCOST":              "c:COST"
    }
    tags.update(table_tags(dbo, d, medical.get_regimens(dbo, a["ID"], not include_incomplete_medical), "TREATMENTNAME", "STATUS"))

    # Diet
    d = {
        "DIETNAME":                 "DIETNAME",
        "DIETDESCRIPTION":          "DIETDESCRIPTION",
        "DIETDATESTARTED":          "d:DATESTARTED",
        "DIETCOMMENTS":             "COMMENTS"
    }
    tags.update(table_tags(dbo, d, animal.get_diets(dbo, a["ID"]), "DIETNAME", "DATESTARTED"))

    # Donations (only add if this animal doesn't have an active movement)
    d = {
        "RECEIPTNUM":               "RECEIPTNUMBER",
        "DONATIONTYPE":             "DONATIONNAME",
        "DONATIONPAYMENTTYPE":      "PAYMENTNAME",
        "DONATIONDATE":             "d:DATE",
        "DONATIONDATEDUE":          "d:DATEDUE",
        "DONATIONAMOUNT":           "c:DONATION",
        "DONATIONCOMMENTS":         "COMMENTS",
        "DONATIONGIFTAID":          "y:ISGIFTAID",
        "PAYMENTTYPE":              "DONATIONNAME",
        "PAYMENTMETHOD":            "PAYMENTNAME",
        "PAYMENTDATE":              "d:DATE",
        "PAYMENTDATEDUE":           "d:DATEDUE",
        "PAYMENTAMOUNT":            "c:DONATION",
        "PAYMENTCOMMENTS":          "COMMENTS",
        "PAYMENTGIFTAID":           "y:ISGIFTAID",
        "PAYMENTVAT":               "y:ISVAT",
        "PAYMENTTAX":               "y:ISVAT",
        "PAYMENTVATRATE":           "f:VATRATE",
        "PAYMENTTAXRATE":           "f:VATRATE",
        "PAYMENTVATAMOUNT":         "c:VATAMOUNT",
        "PAYMENTTAXAMOUNT":         "c:VATAMOUNT"
    }
    if a["ACTIVEMOVEMENTID"] is None or a["ACTIVEMOVEMENTID"] == 0:
        tags.update(table_tags(dbo, d, financial.get_animal_donations(dbo, a["ID"]), "DONATIONNAME", "DATE"))

    # Costs
    d = {
        "COSTTYPE":                 "COSTTYPENAME",
        "COSTDATE":                 "d:COSTDATE",
        "COSTDATEPAID":             "d:COSTPAIDDATE",
        "COSTAMOUNT":               "c:COSTAMOUNT",
        "COSTDESCRIPTION":          "DESCRIPTION"
    }
    tags.update(table_tags(dbo, d, animal.get_costs(dbo, a["ID"]), "COSTTYPENAME", "COSTPAIDDATE"))

    # Logs
    d = {
        "LOGNAME":                  "LOGTYPENAME",
        "LOGDATE":                  "d:DATE",
        "LOGCOMMENTS":              "COMMENTS",
        "LOGCREATEDBY":             "CREATEDBY"
    }
    tags.update(table_tags(dbo, d, log.get_logs(dbo, log.ANIMAL, a["ID"], 0, log.ASCENDING), "LOGTYPENAME", "DATE"))

    return tags

def animalcontrol_tags(dbo, ac):
    """
    Generates a list of tags from an animalcontrol incident.
    ac: An animalcontrol incident record
    """
    l = dbo.locale
    tags = {
        "INCIDENTDATE":         python2display(l, ac["INCIDENTDATETIME"]),
        "INCIDENTTIME":         format_time(ac["INCIDENTDATETIME"]),
        "INCIDENTTYPENAME":     utils.nulltostr(ac["INCIDENTNAME"]),
        "CALLDATE":             python2display(l, ac["CALLDATETIME"]),
        "CALLTIME":             format_time(ac["CALLDATETIME"]),
        "CALLNOTES":            ac["CALLNOTES"],
        "CALLTAKER":            ac["CALLTAKER"],
        "DISPATCHDATE":         python2display(l, ac["DISPATCHDATETIME"]),
        "DISPATCHTIME":         format_time(ac["DISPATCHDATETIME"]),
        "DISPATCHADDRESS":      ac["DISPATCHADDRESS"],
        "DISPATCHTOWN":         ac["DISPATCHTOWN"],
        "DISPATCHCITY":         ac["DISPATCHTOWN"],
        "DISPATCHCOUNTY":       ac["DISPATCHCOUNTY"],
        "DISPATCHSTATE":        ac["DISPATCHCOUNTY"],
        "DISPATCHPOSTCODE":     ac["DISPATCHPOSTCODE"],
        "DISPATCHZIPCODE":      ac["DISPATCHPOSTCODE"],
        "DISPATCHEDACO":        ac["DISPATCHEDACO"],
        "PICKUPLOCATIONNAME":   utils.nulltostr(ac["LOCATIONNAME"]),
        "RESPONDEDDATE":        python2display(l, ac["RESPONDEDDATETIME"]),
        "RESPONDEDTIME":        format_time(ac["RESPONDEDDATETIME"]),
        "FOLLOWUPDATE":         python2display(l, ac["FOLLOWUPDATETIME"]),
        "FOLLOWUPTIME":         format_time(ac["FOLLOWUPDATETIME"]),
        "COMPLETEDDATE":        python2display(l, ac["COMPLETEDDATE"]),
        "COMPLETEDTYPENAME":    utils.nulltostr(ac["COMPLETEDNAME"]),
        "ANIMALDESCRIPTION":    ac["ANIMALDESCRIPTION"],
        "SPECIESNAME":          utils.nulltostr(ac["SPECIESNAME"]),
        "SEX":                  utils.nulltostr(ac["SEXNAME"]),
        "AGEGROUP":             utils.nulltostr(ac["AGEGROUP"]),
        "CALLERNAME":           utils.nulltostr(ac["CALLERNAME"]),
        "CALLERHOMETELEPHONE":  utils.nulltostr(ac["HOMETELEPHONE"]),
        "CALLERWORKTELEPHONE":  utils.nulltostr(ac["WORKTELEPHONE"]),
        "CALLERMOBILETELEPHONE": utils.nulltostr(ac["MOBILETELEPHONE"]),
        "CALLERCELLTELEPHONE":  utils.nulltostr(ac["MOBILETELEPHONE"]),
        "SUSPECTNAME":          utils.nulltostr(ac["SUSPECTNAME"]),
        "SUSPECTADDRESS":       utils.nulltostr(ac["SUSPECTADDRESS"]),
        "SUSPECTTOWN":          utils.nulltostr(ac["SUSPECTTOWN"]),
        "SUSPECTCITY":          utils.nulltostr(ac["SUSPECTTOWN"]),
        "SUSPECTCOUNTY":        utils.nulltostr(ac["SUSPECTCOUNTY"]),
        "SUSPECTSTATE":         utils.nulltostr(ac["SUSPECTCOUNTY"]),
        "SUSPECTPOSTCODE":      utils.nulltostr(ac["SUSPECTPOSTCODE"]),
        "SUSPECTZIPCODE":       utils.nulltostr(ac["SUSPECTPOSTCODE"]),
        "SUSPECT1NAME":         utils.nulltostr(ac["OWNERNAME1"]),
        "SUSPECT2NAME":         utils.nulltostr(ac["OWNERNAME2"]),
        "SUSPECT3NAME":         utils.nulltostr(ac["OWNERNAME3"]),
        "VICTIMNAME":           utils.nulltostr(ac["VICTIMNAME"])
    }

    # Additional fields
    add = additional.get_additional_fields(dbo, ac["ID"], "incident")
    for af in add:
        val = af["VALUE"]
        if af["FIELDTYPE"] == additional.YESNO:
            val = additional_yesno(l, af)
        tags[af["FIELDNAME"].upper()] = val

    # Citations
    d = {
        "CITATIONNAME":         "CITATIONNAME",
        "CITATIONDATE":         "d:CITATIONDATE",
        "COMMENTS":             "COMMENTS",
        "FINEAMOUNT":           "c:FINEAMOUNT",
        "FINEDUEDATE":          "d:FINEDUEDATE",
        "FINEPAIDDATE":         "d:FINEPAIDDATE"
    }
    tags.update(table_tags(dbo, d, financial.get_incident_citations(dbo, ac["ID"]), "CITATIONNAME", "CITATIONDATE"))

    # Logs
    d = {
        "INCIDENTLOGNAME":            "LOGTYPENAME",
        "INCIDENTLOGDATE":            "d:DATE",
        "INCIDENTLOGCOMMENTS":        "COMMENTS",
        "INCIDENTLOGCREATEDBY":       "CREATEDBY"
    }
    tags.update(table_tags(dbo, d, log.get_logs(dbo, log.ANIMALCONTROL, ac["ID"], 0, log.ASCENDING), "LOGTYPENAME", "DATE"))

    return tags

def donation_tags(dbo, donations):
    """
    Generates a list of tags from a donation result.
    donations: a list of donation records
    """
    l = dbo.locale
    tags = {}
    totals = { "due": 0, "received": 0, "vat": 0, "total": 0, "taxrate": 0.0 }
    def add_to_tags(i, p): 
        x = { 
            "DONATIONID"+i          : str(p["ID"]),
            "RECEIPTNUM"+i          : p["RECEIPTNUMBER"],
            "DONATIONTYPE"+i        : p["DONATIONNAME"],
            "DONATIONPAYMENTTYPE"+i : p["PAYMENTNAME"],
            "DONATIONDATE"+i        : python2display(l, p["DATE"]),
            "DONATIONDATEDUE"+i     : python2display(l, p["DATEDUE"]),
            "DONATIONAMOUNT"+i      : format_currency_no_symbol(l, p["DONATION"]),
            "DONATIONCOMMENTS"+i    : p["COMMENTS"],
            "DONATIONCOMMENTSFW"+i  : fw(p["COMMENTS"]),
            "DONATIONGIFTAID"+i     : p["ISGIFTAIDNAME"],
            "DONATIONCREATEDBY"+i   : p["CREATEDBY"],
            "DONATIONCREATEDBYNAME"+i:  p["CREATEDBY"],
            "DONATIONCREATEDDATE"+i : python2display(l, p["CREATEDDATE"]),
            "DONATIONLASTCHANGEDBY"+i : p["LASTCHANGEDBY"],
            "DONATIONLASTCHANGEDBYNAME"+i : p["LASTCHANGEDBY"],
            "DONATIONLASTCHANGEDDATE"+i : python2display(l, p["LASTCHANGEDDATE"]),
            "PAYMENTID"+i           : str(p["ID"]),
            "PAYMENTTYPE"+i         : p["DONATIONNAME"],
            "PAYMENTMETHOD"+i       : p["PAYMENTNAME"],
            "PAYMENTDATE"+i         : python2display(l, p["DATE"]),
            "PAYMENTDATEDUE"+i      : python2display(l, p["DATEDUE"]),
            "PAYMENTAMOUNT"+i       : format_currency_no_symbol(l, p["DONATION"]),
            "PAYMENTCOMMENTS"+i     : p["COMMENTS"],
            "PAYMENTCOMMENTSFW"+i   : fw(p["COMMENTS"]),
            "PAYMENTGIFTAID"+i      : p["ISGIFTAIDNAME"],
            "PAYMENTVAT"+i          : utils.iif(p["ISVAT"] == 1, _("Yes", l), _("No", l)),
            "PAYMENTTAX"+i          : utils.iif(p["ISVAT"] == 1, _("Yes", l), _("No", l)),
            "PAYMENTVATRATE"+i      : "%0.2f" % utils.cfloat(p["VATRATE"]),
            "PAYMENTTAXRATE"+i      : "%0.2f" % utils.cfloat(p["VATRATE"]),
            "PAYMENTVATAMOUNT"+i    : format_currency_no_symbol(l, p["VATAMOUNT"]),
            "PAYMENTTAXAMOUNT"+i    : format_currency_no_symbol(l, p["VATAMOUNT"]),
            "PAYMENTCREATEDBY"+i    : p["CREATEDBY"],
            "PAYMENTCREATEDBYNAME"+i: p["CREATEDBY"],
            "PAYMENTCREATEDDATE"+i  : python2display(l, p["CREATEDDATE"]),
            "PAYMENTLASTCHANGEDBY"+i: p["LASTCHANGEDBY"],
            "PAYMENTLASTCHANGEDBYNAME"+i : p["LASTCHANGEDBY"],
            "PAYMENTLASTCHANGEDDATE"+i : python2display(l, p["LASTCHANGEDDATE"])
        }
        tags.update(x)
        if i == "": return # Don't add a total for the compatibility row
        if p["VATRATE"] > totals["taxrate"]:
            totals["taxrate"] = p["VATRATE"]
        if p["DATE"] is not None: 
            totals["received"] += p["DONATION"]
            totals["vat"] += p["VATAMOUNT"]
            totals["total"] += p["VATAMOUNT"] + p["DONATION"]
        if p["DATE"] is None: 
            totals["due"] += p["DONATION"]
    # Add a copy of the donation tags without an index for compatibility
    if len(donations) > 0:
        add_to_tags("", donations[0]) 
    for i, d in enumerate(donations):
        add_to_tags(str(i+1), d)
    tags["PAYMENTTOTALDUE"] = format_currency_no_symbol(l, totals["due"])
    tags["PAYMENTTOTALRECEIVED"] = format_currency_no_symbol(l, totals["received"])
    tags["PAYMENTTOTALVATRATE"] = "%0.2f" % totals["taxrate"]
    tags["PAYMENTTOTALTAXRATE"] = "%0.2f" % totals["taxrate"]
    tags["PAYMENTTOTALVAT"] = format_currency_no_symbol(l, totals["vat"])
    tags["PAYMENTTOTALTAX"] = format_currency_no_symbol(l, totals["vat"])
    tags["PAYMENTTOTAL"] = format_currency_no_symbol(l, totals["total"])
    return tags

def licence_tags(dbo, li):
    """
    Generates a list of tags from a licence result 
    (from anything using financial.get_licence_query)
    """
    l = dbo.locale
    tags = {
        "LICENCETYPENAME":      li["LICENCETYPENAME"],
        "LICENCENUMBER":        li["LICENCENUMBER"],
        "LICENCEFEE":           li["LICENCEFEE"],
        "LICENCEISSUED":        python2display(l, li["ISSUEDATE"]),
        "LICENCEEXPIRES":       python2display(l, li["EXPIRYDATE"]),
        "LICENCECOMMENTS":      li["COMMENTS"],
        "LICENSETYPENAME":      li["LICENCETYPENAME"],
        "LICENSENUMBER":        li["LICENCENUMBER"],
        "LICENSEFEE":           li["LICENCEFEE"],
        "LICENSEISSUED":        python2display(l, li["ISSUEDATE"]),
        "LICENSEEXPIRES":       python2display(l, li["EXPIRYDATE"]),
        "LICENSECOMMENTS":      li["COMMENTS"]
    }
    return tags

def movement_tags(dbo, m):
    """
    Generates a list of tags from a movement result
    (anything using movement.get_movement_query)
    """
    l = dbo.locale
    tags = {
        "MOVEMENTTYPE":                 m["MOVEMENTNAME"],
        "MOVEMENTDATE":                 python2display(l, m["MOVEMENTDATE"]),
        "MOVEMENTNUMBER":               m["ADOPTIONNUMBER"],
        "ADOPTIONNUMBER":               m["ADOPTIONNUMBER"],
        "ADOPTIONDONATION":             format_currency_no_symbol(l, m["DONATION"]),
        "MOVEMENTPAYMENTTOTAL":         format_currency_no_symbol(l, m["DONATION"]),
        "INSURANCENUMBER":              m["INSURANCENUMBER"],
        "RETURNDATE":                   python2display(l, m["RETURNDATE"]),
        "RETURNNOTES":                  m["REASONFORRETURN"],
        "RETURNREASON":                 utils.iif(m["RETURNDATE"] is not None, m["RETURNEDREASONNAME"], ""),
        "RESERVATIONDATE":              m["RESERVATIONDATE"],
        "RESERVATIONCANCELLEDDATE":     m["RESERVATIONCANCELLEDDATE"],
        "RESERVATIONSTATUS":            m["RESERVATIONSTATUSNAME"],
        "MOVEMENTISTRIAL":              utils.iif(m["ISTRIAL"] == 1, _("Yes", l), _("No", l)),
        "MOVEMENTISPERMANENTFOSTER":    utils.iif(m["ISPERMANENTFOSTER"] == 1, _("Yes", l), _("No", l)),
        "TRIALENDDATE":                 python2display(l, m["TRIALENDDATE"]),
        "MOVEMENTCOMMENTS":             m["COMMENTS"],
        "MOVEMENTCREATEDBY":            m["CREATEDBY"],
        "MOVEMENTLASTCHANGEDBY":        m["LASTCHANGEDBY"],
        "MOVEMENTCREATEDDATE":          python2display(l, m["CREATEDDATE"]),
        "MOVEMENTLASTCHANGEDDATE":      python2display(l, m["LASTCHANGEDDATE"]),
        "ADOPTIONCREATEDBY":            m["CREATEDBY"],
        "ADOPTIONLASTCHANGEDBY":        m["LASTCHANGEDBY"],
        "ADOPTIONCREATEDDATE":          python2display(l, m["CREATEDDATE"]),
        "ADOPTIONLASTCHANGEDDATE":      python2display(l, m["LASTCHANGEDDATE"]),
        "ADOPTIONDATE":                 utils.iif(m["MOVEMENTTYPE"] == movement.ADOPTION, python2display(l, m["MOVEMENTDATE"]), ""),
        "FOSTEREDDATE":                 utils.iif(m["MOVEMENTTYPE"] == movement.FOSTER, python2display(l, m["MOVEMENTDATE"]), ""),
        "TRANSFERDATE":                 utils.iif(m["MOVEMENTTYPE"] == movement.TRANSFER, python2display(l, m["MOVEMENTDATE"]), ""),
        "TRIALENDDATE":                 utils.iif(m["MOVEMENTTYPE"] == movement.ADOPTION, python2display(l, m["TRIALENDDATE"]), "")
    }
    return tags    

def person_tags(dbo, p):
    """
    Generates a list of tags from a person result (the deep type from
    calling person.get_person)
    """
    l = dbo.locale
    tags = { 
        "OWNERID"               : str(p["ID"]),
        "OWNERCODE"             : p["OWNERCODE"],
        "OWNERTITLE"            : p["OWNERTITLE"],
        "TITLE"                 : p["OWNERTITLE"],
        "OWNERINITIALS"         : p["OWNERINITIALS"],
        "INITIALS"              : p["OWNERINITIALS"],
        "OWNERFORENAMES"        : p["OWNERFORENAMES"],
        "FORENAMES"             : p["OWNERFORENAMES"],
        "OWNERFIRSTNAMES"       : p["OWNERFORENAMES"],
        "FIRSTNAMES"            : p["OWNERFORENAMES"],
        "OWNERSURNAME"          : p["OWNERSURNAME"],
        "SURNAME"               : p["OWNERSURNAME"],
        "OWNERLASTNAME"         : p["OWNERSURNAME"],
        "LASTNAME"              : p["OWNERSURNAME"],
        "OWNERNAME"             : p["OWNERNAME"],
        "NAME"                  : p["OWNERNAME"],
        "OWNERADDRESS"          : p["OWNERADDRESS"],
        "ADDRESS"               : p["OWNERADDRESS"],
        "OWNERTOWN"             : p["OWNERTOWN"],
        "TOWN"                  : p["OWNERTOWN"],
        "OWNERCOUNTY"           : p["OWNERCOUNTY"],
        "COUNTY"                : p["OWNERCOUNTY"],
        "OWNERCITY"             : p["OWNERTOWN"],
        "CITY"                  : p["OWNERTOWN"],
        "OWNERSTATE"            : p["OWNERCOUNTY"],
        "STATE"                 : p["OWNERCOUNTY"],
        "OWNERPOSTCODE"         : p["OWNERPOSTCODE"],
        "POSTCODE"              : p["OWNERPOSTCODE"],
        "OWNERZIPCODE"          : p["OWNERPOSTCODE"],
        "ZIPCODE"               : p["OWNERPOSTCODE"],
        "HOMETELEPHONE"         : p["HOMETELEPHONE"],
        "WORKTELEPHONE"         : p["WORKTELEPHONE"],
        "MOBILETELEPHONE"       : p["MOBILETELEPHONE"],
        "CELLTELEPHONE"         : p["MOBILETELEPHONE"],
        "EMAILADDRESS"          : p["EMAILADDRESS"],
        "OWNERCOMMENTS"         : p["COMMENTS"],
        "COMMENTS"              : p["COMMENTS"],
        "OWNERCREATEDBY"        : p["CREATEDBY"],
        "OWNERCREATEDBYNAME"    : p["CREATEDBY"],
        "OWNERCREATEDDATE"      : python2display(l, p["CREATEDDATE"]),
        "OWNERLASTCHANGEDBY"    : p["LASTCHANGEDBY"],
        "OWNERLASTCHANGEDBYNAME" : p["LASTCHANGEDBY"],
        "OWNERLASTCHANGEDDATE"  : python2display(l, p["LASTCHANGEDDATE"]),
        "IDCHECK"               : utils.iif(p["IDCHECK"] == 1, _("Yes", l), _("No", l)),
        "HOMECHECKEDBYNAME"     : p["HOMECHECKEDBYNAME"],
        "HOMECHECKEDBYEMAIL"    : p["HOMECHECKEDBYEMAIL"],
        "HOMECHECKEDBYHOMETELEPHONE": p["HOMECHECKEDBYHOMETELEPHONE"],
        "HOMECHECKEDBYMOBILETELEPHONE": p["HOMECHECKEDBYMOBILETELEPHONE"],
        "HOMECHECKEDBYCELLTELEPHONE": p["HOMECHECKEDBYMOBILETELEPHONE"],
        "MEMBERSHIPNUMBER"      : p["MEMBERSHIPNUMBER"],
        "MEMBERSHIPEXPIRYDATE"  : python2display(l, p["MEMBERSHIPEXPIRYDATE"])
    }

    # Additional fields
    add = additional.get_additional_fields(dbo, p["ID"], "person")
    for af in add:
        val = af["VALUE"]
        if af["FIELDTYPE"] == additional.YESNO:
            val = additional_yesno(l, af)
        tags[af["FIELDNAME"].upper()] = val

    # Citations
    d = {
        "CITATIONNAME":         "CITATIONNAME",
        "CITATIONDATE":         "d:CITATIONDATE",
        "COMMENTS":             "COMMENTS",
        "FINEAMOUNT":           "c:FINEAMOUNT",
        "FINEDUEDATE":          "d:FINEDUEDATE",
        "FINEPAIDDATE":         "d:FINEPAIDDATE"
    }
    tags.update(table_tags(dbo, d, financial.get_person_citations(dbo, p["ID"]), "CITATIONNAME", "CITATIONDATE"))

    # Logs
    d = {
        "PERSONLOGNAME":            "LOGTYPENAME",
        "PERSONLOGDATE":            "d:DATE",
        "PERSONLOGCOMMENTS":        "COMMENTS",
        "PERSONLOGCREATEDBY":       "CREATEDBY"
    }
    tags.update(table_tags(dbo, d, log.get_logs(dbo, log.PERSON, p["ID"], 0, log.ASCENDING), "LOGTYPENAME", "DATE"))

    # Trap loans
    d = {
        "TRAPTYPENAME":             "TRAPTYPENAME",
        "TRAPLOANDATE":             "d:LOANDATE",
        "TRAPDEPOSITAMOUNT":        "c:DEPOSITAMOUNT",
        "TRAPDEPOSITRETURNDATE":    "d:DEPOSITRETURNDATE",
        "TRAPNUMBER":               "TRAPNUMBER",
        "TRAPRETURNDUEDATE":        "d:RETURNDUEDATE",
        "TRAPRETURNDATE":           "d:RETURNDATE",
        "TRAPCOMMENTS":             "COMMENTS"
    }
    tags.update(table_tags(dbo, d, animalcontrol.get_person_traploans(dbo, p["ID"], animalcontrol.ASCENDING), "TRAPTYPENAME", "RETURNDATE"))

    return tags

def append_tags(tags1, tags2):
    """
    Adds two dictionaries of tags together and returns
    a new dictionary containing both sets.
    """
    tags = {}
    tags.update(tags1)
    tags.update(tags2)
    return tags

def table_get_value(l, row, k):
    """
    Returns row[k], looking for a type prefix in k -
    c: currency, d: date
    """
    if k.find("d:") != -1: 
        s = python2display(l, row[k.replace("d:", "")])
    elif k.find("c:") != -1:
        s = format_currency_no_symbol(l, row[k.replace("c:", "")])
    elif k.find("y:") != -1:
        s = utils.iif(row[k.replace("y:", "")] == 1, _("Yes", l), _("No", l))
    elif k.find("f:") != -1:
        s = "%0.2f" % utils.cfloat(row[k.replace("f:", "")])
    else:
        s = str(row[k])
    return s

def table_tags(dbo, d, rows, typefield = "", recentdatefield = ""):
    """
    For a collection of table rows, generates the LAST/RECENT and indexed tags.

    d: A dictionary of tag names to field expressions. If the field is
       preceded with d:, it is formatted as a date, c: a currency
       eg: { "VACCINATIONNAME" : "VACCINATIONTYPE", "VACCINATIONREQUIRED", "d:DATEREQUIRED" }

    typefield: The name of the field in rows that contains the type for
       creating tags with the type as a suffix

    recentdatefield: The name of the field in rows that contains the date
        the last thing was received/given for RECENT tags.

    rows: The table rows
    """
    l = dbo.locale
    tags = {}

    # Create the indexed rows
    for i, r in enumerate(rows, 1):
        for k, v in d.iteritems():
            tags[k + str(i)] = table_get_value(l, r, v)

    uniquetypes = {}
    recentgiven = {}

    # Go backwards through rows
    for i, r in enumerate(reversed(rows), 1):

        # Create reversed index tags
        for k, v in d.iteritems():
            tags[k + "LAST" + str(i)] = table_get_value(l, r, v)

        # Type suffixed tags
        if typefield != "":
            t = r[typefield]
            # Is this the first of this type we've seen?
            # If so, create the tags with type as a suffix
            if not uniquetypes.has_key(t):
                uniquetypes[t] = r
                t = t.upper().replace(" ", "").replace("/", "")
                for k, v in d.iteritems():
                    tags[k + t] = table_get_value(l, r, v)

        # Recent suffixed tags
        if recentdatefield != "":
            # STATUS is an edge case for medical rows only - all the
            # others have some kind of date
            if recentdatefield == "STATUS":
                t = r[typefield]
                # Is this the first type with STATUS==2 we've seen?
                # If so, create the tags with recent as a suffix.
                if not recentgiven.has_key(t) and r[recentdatefield] == 2:
                    recentgiven[t] = r
                    t = t.upper().replace(" ", "").replace("/", "")
                    for k, v in d.iteritems():
                        tags[k + "RECENT" + t] = table_get_value(l, r, v)
            else:
                t = r[typefield]
                # Is this the first type with a date we've seen?
                # If so, create the tags with recent as a suffix
                if not recentgiven.has_key(t) and r[recentdatefield] is not None:
                    recentgiven[t] = r
                    t = t.upper().replace(" ", "").replace("/", "")
                    for k, v in d.iteritems():
                        tags[k + "RECENT" + t] = table_get_value(l, r, v)
    return tags

def substitute_tags_plain(searchin, tags):
    """
    Substitutes the dictionary of tags in "tags" for any found in
    "searchin". This is a convenience method for plain text substitution
    with << >> opener/closers and no XML escaping.
    """
    return substitute_tags(searchin, tags, False, "<<", ">>")

def substitute_tags(searchin, tags, use_xml_escaping = True, opener = "&lt;&lt;", closer = "&gt;&gt;"):
    """
    Substitutes the dictionary of tags in "tags" for any found
    in "searchin". opener and closer denote the start of a tag,
    if use_xml_escaping is set to true, then tags are XML escaped when
    output and opener/closer are escaped.
    """
    if not use_xml_escaping:
        opener = opener.replace("&lt;", "<").replace("&gt;", ">")
        closer = closer.replace("&lt;", "<").replace("&gt;", ">")

    s = searchin
    sp = s.find(opener)
    while sp != -1:
        ep = s.find(closer, sp + len(opener))
        if ep != -1:
            matchtag = s[sp + len(opener):ep].upper()
            newval = ""
            if tags.has_key(matchtag):
                newval = tags[matchtag]
                if newval is not None:
                    newval = str(newval)
                    # Escape xml entities unless the replacement tag is an image
                    # or it contains HTML entities or <br tags
                    if use_xml_escaping and \
                       not newval.lower().startswith("<img") and \
                       not newval.lower().find("&#") != -1 and \
                       not newval.lower().find("<br/>") != -1:
                        newval = newval.replace("&", "&amp;")
                        newval = newval.replace("<", "&lt;")
                        newval = newval.replace(">", "&gt;")
            s = s[0:sp] + str(newval) + s[ep + len(closer):]
            sp = s.find(opener, sp)
        else:
            # No end marker for this tag, stop processing
            break
    return s

def substitute_template(dbo, template, tags, imdata = None):
    """
    Reads the template specified by dbfs id "template" and substitutes
    according to the tags in "tags". Returns the built file.
    imdata is the preferred image for the record and since html uses
    URLs, only applies to ODT templates.
    """
    templatedata = dbfs.get_string_id(dbo, template)
    templatename = dbfs.get_name_for_id(dbo, template)
    if templatename.endswith(".html"):
        # Translate any user signature placeholder
        templatedata = templatedata.replace("signature:user", "&lt;&lt;UserSignatureSrc&gt;&gt;")
        return substitute_tags(templatedata, tags)
    elif templatename.endswith(".odt"):
        try:
            odt = StringIO(templatedata)
            zf = zipfile.ZipFile(odt, "r")
            # Load the content.xml file and substitute the tags
            content = zf.open("content.xml").read()
            content = substitute_tags(content, tags)
            # Write the replacement file
            zo = StringIO()
            zfo = zipfile.ZipFile(zo, "w")
            for info in zf.infolist():
                if info.filename == "content.xml":
                    zfo.writestr("content.xml", content)
                elif imdata is not None and (info.file_size == 2897 or info.file_size == 7701):
                    # If the image is the old placeholder.jpg or our default nopic.jpg, substitute for the record image
                    zfo.writestr(info.filename, imdata)
                else:
                    zfo.writestr(info.filename, zf.open(info.filename).read())
            zf.close()
            zfo.close()
            # Return the zip data
            return zo.getvalue()
        except Exception,zderr:
            raise utils.ASMError("Failed generating odt document: %s" % str(zderr))

def generate_animal_doc(dbo, template, animalid, username):
    """
    Generates an animal document from a template using animal keys and
    (if a currentowner is available) person keys
    template: The path/name of the template to use
    animalid: The animal to generate for
    """
    a = animal.get_animal(dbo, animalid)
    im = media.get_image_file_data(dbo, "animal", animalid)[1]
    if a is None: raise utils.ASMValidationError("%d is not a valid animal ID" % animalid)
    tags = animal_tags(dbo, a)
    if a["CURRENTOWNERID"] is not None and a["CURRENTOWNERID"] != 0:
        tags = append_tags(tags, person_tags(dbo, person.get_person(dbo, a["CURRENTOWNERID"])))
    elif a["RESERVEDOWNERID"] is not None and a["RESERVEDOWNERID"] != 0:
        tags = append_tags(tags, person_tags(dbo, person.get_person(dbo, a["RESERVEDOWNERID"])))
    if a["ACTIVEMOVEMENTID"] is not None and a["ACTIVEMOVEMENTID"] != 0:
        m = movement.get_movement(dbo, a["ACTIVEMOVEMENTID"])
        md = financial.get_movement_donations(dbo, a["ACTIVEMOVEMENTID"])
        if m is not None and len(m) > 0:
            tags = append_tags(tags, movement_tags(dbo, m))
        if len(md) > 0: 
            tags = append_tags(tags, donation_tags(dbo, md))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, template, tags, im)

def generate_animalcontrol_doc(dbo, template, acid, username):
    """
    Generates an animal control incident document from a template
    template: The path/name of the template to use
    acid:     The incident id to generate for
    """
    ac = animalcontrol.get_animalcontrol(dbo, acid)
    if ac is None: raise utils.ASMValidationError("%d is not a valid incident ID" % acid)
    tags = animalcontrol_tags(dbo, ac)
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, template, tags)

def generate_person_doc(dbo, template, personid, username):
    """
    Generates a person document from a template
    template: The path/name of the template to use
    personid: The person to generate for
    """
    p = person.get_person(dbo, personid)
    im = media.get_image_file_data(dbo, "person", personid)[1]
    if p is None: raise utils.ASMValidationError("%d is not a valid person ID" % personid)
    tags = person_tags(dbo, p)
    tags = append_tags(tags, org_tags(dbo, username))
    m = movement.get_person_movements(dbo, personid)
    if len(m) > 0: 
        tags = append_tags(tags, movement_tags(dbo, m[0]))
        tags = append_tags(tags, animal_tags(dbo, animal.get_animal(dbo, m[0]["ANIMALID"])))
    return substitute_template(dbo, template, tags, im)

def generate_donation_doc(dbo, template, donationids, username):
    """
    Generates a donation document from a template
    template: The path/name of the template to use
    donationids: A list of ids to generate for
    """
    dons = financial.get_donations_by_ids(dbo, donationids)
    if len(dons) == 0: 
        raise utils.ASMValidationError("%s does not contain any valid donation IDs" % donationids)
    d = dons[0]
    tags = person_tags(dbo, person.get_person(dbo, d["OWNERID"]))
    if d["ANIMALID"] is not None and d["ANIMALID"] != 0:
        tags = append_tags(tags, animal_tags(dbo, animal.get_animal(dbo, d["ANIMALID"])))
    if d["MOVEMENTID"] is not None and d["MOVEMENTID"] != 0:
        tags = append_tags(tags, movement_tags(dbo, movement.get_movement(dbo, d["MOVEMENTID"])))
    tags = append_tags(tags, donation_tags(dbo, dons))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, template, tags)

def generate_licence_doc(dbo, template, licenceid, username):
    """
    Generates a licence document from a template
    template: The path/name of the template to use
    licenceid: The licence to generate for
    """
    l = financial.get_licence(dbo, licenceid)
    if l is None:
        raise utils.ASMValidationError("%d is not a valid licence ID" % licenceid)
    tags = person_tags(dbo, person.get_person(dbo, l["OWNERID"]))
    if l["ANIMALID"] is not None and l["ANIMALID"] != 0:
        tags = append_tags(tags, animal_tags(dbo, animal.get_animal(dbo, l["ANIMALID"])))
    tags = append_tags(tags, licence_tags(dbo, l))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, template, tags)

def generate_movement_doc(dbo, template, movementid, username):
    """
    Generates a movement document from a template
    template: The path/name of the template to use
    movementid: The movement to generate for
    """
    m = movement.get_movement(dbo, movementid)
    if m is None:
        raise utils.ASMValidationError("%d is not a valid movement ID" % movementid)
    tags = animal_tags(dbo, animal.get_animal(dbo, m["ANIMALID"]))
    if m["OWNERID"] is not None and m["OWNERID"] != 0:
        tags = append_tags(tags, person_tags(dbo, person.get_person(dbo, m["OWNERID"])))
    tags = append_tags(tags, movement_tags(dbo, m))
    tags = append_tags(tags, donation_tags(dbo, financial.get_movement_donations(dbo, movementid)))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, template, tags)

