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
import person
import users
import utils
import zipfile
from i18n import _, format_currency_no_symbol, now, python2display, yes_no
from sitedefs import BASE_URL, QR_IMG_SRC
from cStringIO import StringIO

def org_tags(dbo, username):
    """
    Generates a list of tags from the organisation and user info
    """
    u = users.get_users(dbo, username)
    realname = ""
    email = ""
    if len(u) > 0:
        u = u[0]
        realname = u["REALNAME"]
        email = u["EMAILADDRESS"]
    tags = {
        "ORGANISATION"          : configuration.organisation(dbo),
        "ORGANISATIONADDRESS"   : configuration.organisation_address(dbo),
        "ORGANISATIONTELEPHONE" : configuration.organisation_telephone(dbo),
        "DATE"                  : python2display(dbo.locale, now(dbo.timezone)),
        "USERNAME"              : username,
        "USERREALNAME"          : realname,
        "USEREMAILADDRESS"      : email
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
    displaydob = python2display(l, a["DATEOFBIRTH"])
    displayage = a["ANIMALAGE"]
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
        "LOCATIONUNIT"          : a["SHELTERLOCATIONUNIT"],
        "DISPLAYLOCATION"       : a["DISPLAYLOCATION"],
        "COATTYPE"              : a["COATTYPENAME"],
        "HEALTHPROBLEMS"        : a["HEALTHPROBLEMS"],
        "HEALTHPROBLEMSBR"      : br(a["HEALTHPROBLEMS"]),
        "ANIMALCREATEDBY"       : a["CREATEDBY"],
        "ANIMALCREATEDDATE"     : python2display(l, a["CREATEDDATE"]),
        "DATEBROUGHTIN"         : python2display(l, a["DATEBROUGHTIN"]),
        "DATEOFBIRTH"           : python2display(l, a["DATEOFBIRTH"]),
        "AGEGROUP"              : a["AGEGROUP"],
        "DISPLAYDOB"            : displaydob,
        "DISPLAYAGE"            : displayage,
        "ESTIMATEDDOB"          : estimate,
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
        "COMBITESTDATE"         : a["COMBITESTED"] == 1 and python2display(l, a["COMBITESTDATE"]) or "",
        "FIVLTESTDATE"          : a["COMBITESTED"] == 1 and python2display(l, a["COMBITESTDATE"]) or "",
        "COMBITESTRESULT"       : a["COMBITESTED"] == 1 and a["COMBITESTRESULTNAME"] or "",
        "FIVTESTRESULT"         : a["COMBITESTED"] == 1 and a["COMBITESTRESULTNAME"] or "",
        "FIVRESULT"             : a["COMBITESTED"] == 1 and a["COMBITESTRESULTNAME"] or "",
        "FLVTESTRESULT"         : a["COMBITESTED"] == 1 and a["FLVRESULTNAME"] or "",
        "FLVRESULT"             : a["COMBITESTED"] == 1 and a["FLVRESULTNAME"] or "",
        "HEARTWORMTESTED"       : a["HEARTWORMTESTEDNAME"],
        "HEARTWORMTESTDATE"     : a["HEARTWORMTESTED"] == 1 and python2display(l, a["HEARTWORMTESTDATE"]) or "",
        "HEARTWORMTESTRESULT"   : a["HEARTWORMTESTED"] == 1 and a["HEARTWORMTESTRESULTNAME"] or "",
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
        "AGE"                   : a["ANIMALAGE"],
        "ACCEPTANCENUMBER"      : a["ACCEPTANCENUMBER"],
        "LITTERID"              : a["ACCEPTANCENUMBER"],
        "DECEASEDDATE"          : python2display(l, a["DECEASEDDATE"]),
        "DECEASEDNOTES"         : a["PTSREASON"],
        "DECEASEDCATEGORY"      : a["PTSREASONNAME"],
        "SHORTSHELTERCODE"      : a["SHORTCODE"],
        "MOSTRECENTENTRY"       : python2display(l, a["MOSTRECENTENTRYDATE"]),
        "TIMEONSHELTER"         : a["TIMEONSHELTER"],
        "WEBMEDIAFILENAME"      : a["WEBSITEMEDIANAME"],
        "WEBSITEIMAGECOUNT"     : a["WEBSITEIMAGECOUNT"],
        "WEBSITEMEDIANAME"      : a["WEBSITEMEDIANAME"],
        "WEBSITEVIDEOURL"       : a["WEBSITEVIDEOURL"],
        "WEBSITEVIDEONOTES"     : a["WEBSITEVIDEONOTES"],
        "WEBMEDIANOTES"         : a["WEBSITEMEDIANOTES"],
        "WEBSITEMEDIANOTES"     : a["WEBSITEMEDIANOTES"],
        "DOCUMENTIMGLINK"       : "<img height=\"200\" src=\"" + html.img_src(a, "animal") + "\" >",
        "DOCUMENTIMGTHUMBLINK"  : "<img src=\"" + html.thumbnail_img_src(a, "animalthumb") + "\" />",
        "DOCUMENTQRLINK"        : "<img src=\"%s\" />" % qr,
        "ANIMALONSHELTER"       : yes_no(l, a["ARCHIVED"] == 0),
        "ANIMALISRESERVED"      : yes_no(l, a["HASACTIVERESERVE"] == 1),
        "ADOPTIONID"            : a["ACTIVEMOVEMENTADOPTIONNUMBER"],
        "ADOPTIONNUMBER"        : a["ACTIVEMOVEMENTADOPTIONNUMBER"],
        "INSURANCENUMBER"       : a["ACTIVEMOVEMENTINSURANCENUMBER"],
        "RESERVATIONDATE"       : python2display(l, a["ACTIVEMOVEMENTRESERVATIONDATE"]),
        "RESERVATIONSTATUS"     : a["RESERVATIONSTATUSNAME"],
        "RETURNDATE"            : python2display(l, a["ACTIVEMOVEMENTRETURNDATE"]),
        "ADOPTIONDATE"          : python2display(l, a["ACTIVEMOVEMENTDATE"]),
        "FOSTEREDDATE"          : python2display(l, a["ACTIVEMOVEMENTDATE"]),
        "TRANSFERDATE"          : python2display(l, a["ACTIVEMOVEMENTDATE"]),
        "TRIALENDDATE"          : python2display(l, a["ACTIVEMOVEMENTTRIALENDDATE"]),
        "MOVEMENTDATE"          : python2display(l, a["ACTIVEMOVEMENTDATE"]),
        "MOVEMENTTYPE"          : a["ACTIVEMOVEMENTTYPENAME"],
        "ADOPTIONDONATION"      : format_currency_no_symbol(l, a["ACTIVEMOVEMENTDONATION"]),
        "ADOPTIONCREATEDBY"     : a["ACTIVEMOVEMENTCREATEDBY"],
        "ADOPTIONCREATEDBYNAME" : a["ACTIVEMOVEMENTCREATEDBYNAME"],
        "ADOPTIONCREATEDDATE"   : python2display(l, a["ACTIVEMOVEMENTCREATEDDATE"]),
        "ADOPTIONLASTCHANGEDBY" : a["ACTIVEMOVEMENTLASTCHANGEDBY"],
        "ADOPTIONLASTCHANGEDDATE" : python2display(l, a["ACTIVEMOVEMENTLASTCHANGEDDATE"])
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
    add = additional.get_additional_fields(dbo, int(a["ID"]), "animal")
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
    vaccasc = medical.get_vaccinations(dbo, int(a["ID"]), not include_incomplete_vacc)
    vaccdesc = medical.get_vaccinations(dbo, int(a["ID"]), not include_incomplete_vacc, medical.DESCENDING_REQUIRED)
    for idx in range(1, 101):
        tags["VACCINATIONNAME" + str(idx)] = ""
        tags["VACCINATIONREQUIRED" + str(idx)] = ""
        tags["VACCINATIONGIVEN" + str(idx)] = ""
        tags["VACCINATIONEXPIRES" + str(idx)] = ""
        tags["VACCINATIONBATCH" + str(idx)] = ""
        tags["VACCINATIONMANUFACTURER" + str(idx)] = ""
        tags["VACCINATIONCOST" + str(idx)] = ""
        tags["VACCINATIONCOMMENTS" + str(idx)] = ""
        tags["VACCINATIONDESCRIPTION" + str(idx)] = ""
        tags["VACCINATIONNAMELAST" + str(idx)] = ""
        tags["VACCINATIONREQUIREDLAST" + str(idx)] = ""
        tags["VACCINATIONGIVENLAST" + str(idx)] = ""
        tags["VACCINATIONEXPIRESLAST" + str(idx)] = ""
        tags["VACCINATIONBATCHLAST" + str(idx)] = ""
        tags["VACCINATIONMANUFACTURERLAST" + str(idx)] = ""
        tags["VACCINATIONCOSTLAST" + str(idx)] = ""
        tags["VACCINATIONCOMMENTSLAST" + str(idx)] = ""
        tags["VACCINATIONDESCRIPTIONLAST" + str(idx)] = ""
    idx = 1
    for v in vaccasc:
        tags["VACCINATIONNAME" + str(idx)] = v["VACCINATIONTYPE"]
        tags["VACCINATIONREQUIRED" + str(idx)] = python2display(l, v["DATEREQUIRED"])
        tags["VACCINATIONGIVEN" + str(idx)] = python2display(l, v["DATEOFVACCINATION"])
        tags["VACCINATIONEXPIRES" + str(idx)] = python2display(l, v["DATEEXPIRES"])
        tags["VACCINATIONBATCH" + str(idx)] = v["BATCHNUMBER"]
        tags["VACCINATIONMANUFACTURER" + str(idx)] = v["MANUFACTURER"]
        tags["VACCINATIONCOST" + str(idx)] = format_currency_no_symbol(l, v["COST"])
        tags["VACCINATIONCOMMENTS" + str(idx)] = v["COMMENTS"]
        tags["VACCINATIONDESCRIPTION" + str(idx)] = v["VACCINATIONDESCRIPTION"]
        idx += 1
    idx = 1
    uniquetypes = {}
    recentgiven = {}
    for v in vaccdesc:
        tags["VACCINATIONNAMELAST" + str(idx)] = v["VACCINATIONTYPE"]
        tags["VACCINATIONREQUIREDLAST" + str(idx)] = python2display(l, v["DATEREQUIRED"])
        tags["VACCINATIONGIVENLAST" + str(idx)] = python2display(l, v["DATEOFVACCINATION"])
        tags["VACCINATIONEXPIRESLAST" + str(idx)] = python2display(l, v["DATEEXPIRES"])
        tags["VACCINATIONBATCHLAST" + str(idx)] = v["BATCHNUMBER"]
        tags["VACCINATIONMANUFACTURERLAST" + str(idx)] = v["MANUFACTURER"]
        tags["VACCINATIONCOSTLAST" + str(idx)] = format_currency_no_symbol(l, v["COST"])
        tags["VACCINATIONCOMMENTSLAST" + str(idx)] = v["COMMENTS"]
        tags["VACCINATIONDESCRIPTIONLAST" + str(idx)] = v["VACCINATIONDESCRIPTION"]
        idx += 1
        # If this is the first of this type of vacc we've seen, make
        # some keys based on its name.
        if not uniquetypes.has_key(v["VACCINATIONTYPE"]):
            vname = v["VACCINATIONTYPE"].upper().replace(" ", "").replace("/", "")
            uniquetypes[v["VACCINATIONTYPE"]] = v
            tags["VACCINATIONNAME" + vname] = v["VACCINATIONTYPE"]
            tags["VACCINATIONREQUIRED" + vname] = python2display(l, v["DATEREQUIRED"])
            tags["VACCINATIONGIVEN" + vname] = python2display(l, v["DATEOFVACCINATION"])
            tags["VACCINATIONEXPIRES" + vname] = python2display(l, v["DATEEXPIRES"])
            tags["VACCINATIONBATCH" + vname] = v["BATCHNUMBER"]
            tags["VACCINATIONMANUFACTURER" + vname] = v["MANUFACTURER"]
            tags["VACCINATIONCOST" + vname] = format_currency_no_symbol(l, v["COST"])
            tags["VACCINATIONCOMMENTS" + vname] = v["COMMENTS"]
            tags["VACCINATIONDESCRIPTION" + vname] = v["VACCINATIONDESCRIPTION"]
        # If this is the first of this type of vacc we've seen that's been given
        # make some keys based on its name
        if not recentgiven.has_key(v["VACCINATIONTYPE"]) and v["DATEOFVACCINATION"] is not None:
            vname = v["VACCINATIONTYPE"].upper().replace(" ", "").replace("/", "")
            recentgiven[v["VACCINATIONTYPE"]] = v
            tags["VACCINATIONNAMERECENT" + vname] = v["VACCINATIONTYPE"]
            tags["VACCINATIONREQUIREDRECENT" + vname] = python2display(l, v["DATEREQUIRED"])
            tags["VACCINATIONGIVENRECENT" + vname] = python2display(l, v["DATEOFVACCINATION"])
            tags["VACCINATIONEXPIRESRECENT" + vname] = python2display(l, v["DATEEXPIRES"])
            tags["VACCINATIONBATCHRECENT" + vname] = v["BATCHNUMBER"]
            tags["VACCINATIONMANUFACTURERRECENT" + vname] = v["MANUFACTURER"]
            tags["VACCINATIONCOSTRECENT" + vname] = format_currency_no_symbol(l, v["COST"])
            tags["VACCINATIONCOMMENTSRECENT" + vname] = v["COMMENTS"]
            tags["VACCINATIONDESCRIPTIONRECENT" + vname] = v["VACCINATIONDESCRIPTION"]

    # Tests
    testasc = medical.get_tests(dbo, int(a["ID"]), not include_incomplete_vacc)
    testdesc = medical.get_tests(dbo, int(a["ID"]), not include_incomplete_vacc, medical.DESCENDING_REQUIRED)
    for idx in range(1, 101):
        tags["TESTNAME" + str(idx)] = ""
        tags["TESTRESULT" + str(idx)] = ""
        tags["TESTREQUIRED" + str(idx)] = ""
        tags["TESTGIVEN" + str(idx)] = ""
        tags["TESTCOST" + str(idx)] = ""
        tags["TESTCOMMENTS" + str(idx)] = ""
        tags["TESTDESCRIPTION" + str(idx)] = ""
        tags["TESTNAMELAST" + str(idx)] = ""
        tags["TESTREQUIREDLAST" + str(idx)] = ""
        tags["TESTGIVENLAST" + str(idx)] = ""
        tags["TESTCOSTLAST" + str(idx)] = ""
        tags["TESTCOMMENTSLAST" + str(idx)] = ""
        tags["TESTDESCRIPTIONLAST" + str(idx)] = ""
    idx = 1
    for t in testasc:
        tags["TESTNAME" + str(idx)] = t["TESTNAME"]
        tags["TESTRESULT" + str(idx)] = t["RESULTNAME"]
        tags["TESTREQUIRED" + str(idx)] = python2display(l, t["DATEREQUIRED"])
        tags["TESTGIVEN" + str(idx)] = python2display(l, t["DATEOFTEST"])
        tags["TESTCOST" + str(idx)] = format_currency_no_symbol(l, t["COST"])
        tags["TESTCOMMENTS" + str(idx)] = t["COMMENTS"]
        tags["TESTDESCRIPTION" + str(idx)] = t["TESTDESCRIPTION"]
        idx += 1
    idx = 1
    uniquetypes = {}
    recentgiven = {}
    for t in testdesc:
        tags["TESTNAMELAST" + str(idx)] = t["TESTNAME"]
        tags["TESTRESULTLAST" + str(idx)] = t["RESULTNAME"]
        tags["TESTREQUIREDLAST" + str(idx)] = python2display(l, t["DATEREQUIRED"])
        tags["TESTGIVENLAST" + str(idx)] = python2display(l, t["DATEOFTEST"])
        tags["TESTCOSTLAST" + str(idx)] = format_currency_no_symbol(l, t["COST"])
        tags["TESTCOMMENTSLAST" + str(idx)] = t["COMMENTS"]
        tags["TESTDESCRIPTIONLAST" + str(idx)] = t["TESTDESCRIPTION"]
        idx += 1
        # If this is the first of this type of test we've seen, make
        # some keys based on its name.
        if not uniquetypes.has_key(t["TESTNAME"]):
            tname = t["TESTNAME"].upper().replace(" ", "").replace("/", "")
            uniquetypes[t["TESTNAME"]] = t
            tags["TESTNAME" + tname] = t["TESTNAME"]
            tags["TESTRESULT" + tname] = t["RESULTNAME"]
            tags["TESTREQUIRED" + tname] = python2display(l, t["DATEREQUIRED"])
            tags["TESTGIVEN" + tname] = python2display(l, t["DATEOFTEST"])
            tags["TESTCOST" + tname] = format_currency_no_symbol(l, t["COST"])
            tags["TESTCOMMENTS" + tname] = t["COMMENTS"]
            tags["TESTDESCRIPTION" + tname] = t["TESTDESCRIPTION"]
        # If this is the first of this type of test we've seen that's been given
        # make some keys based on its name
        if not recentgiven.has_key(t["TESTNAME"]) and t["DATEOFTEST"] is not None:
            tname = t["TESTNAME"].upper().replace(" ", "").replace("/", "")
            recentgiven[t["TESTNAME"]] = t
            tags["TESTNAMERECENT" + tname] = t["TESTNAME"]
            tags["TESTRESULTRECENT" + tname] = t["RESULTNAME"]
            tags["TESTREQUIREDRECENT" + tname] = python2display(l, t["DATEREQUIRED"])
            tags["TESTGIVENRECENT" + tname] = python2display(l, t["DATEOFTEST"])
            tags["TESTCOSTRECENT" + tname] = format_currency_no_symbol(l, t["COST"])
            tags["TESTCOMMENTSRECENT" + tname] = t["COMMENTS"]
            tags["TESTDESCRIPTIONRECENT" + tname] = t["TESTDESCRIPTION"]

    # Medical
    medasc = medical.get_regimens(dbo, int(a["ID"]), not include_incomplete_medical)
    meddesc = medical.get_regimens(dbo, int(a["ID"]), not include_incomplete_medical, medical.DESCENDING_REQUIRED)
    for idx in range(1, 101):
        tags["MEDICALNAME" + str(idx)] = ""
        tags["MEDICALCOMMENTS" + str(idx)] = ""
        tags["MEDICALFREQUENCY" + str(idx)] = ""
        tags["MEDICALNUMBEROFTREATMENTS" + str(idx)] = ""
        tags["MEDICALSTATUS" + str(idx)] = ""
        tags["MEDICALDOSAGE" + str(idx)] = ""
        tags["MEDICALSTARTDATE" + str(idx)] = ""
        tags["MEDICALTREATMENTSGIVEN" + str(idx)] = ""
        tags["MEDICALTREATMENTSREMAINING" + str(idx)] = ""
        tags["MEDICALCOST" + str(idx)] = ""
        tags["MEDICALNAMELAST" + str(idx)] = ""
        tags["MEDICALCOMMENTSLAST" + str(idx)] = ""
        tags["MEDICALFREQUENCYLAST" + str(idx)] = ""
        tags["MEDICALNUMBEROFTREATMENTSLAST" + str(idx)] = ""
        tags["MEDICALSTATUSLAST" + str(idx)] = ""
        tags["MEDICALDOSAGELAST" + str(idx)] = ""
        tags["MEDICALSTARTDATELAST" + str(idx)] = ""
        tags["MEDICALTREATMENTSGIVENLAST" + str(idx)] = ""
        tags["MEDICALTREATMENTSREMAININGLAST" + str(idx)] = ""
        tags["MEDICALNEXTTREATMENTDUE" + str(idx)] = ""
        tags["MEDICALLASTTREATMENTGIVEN" + str(idx)] = ""
        tags["MEDICALCOSTLAST" + str(idx)] = ""
    idx = 1
    for m in medasc:
        tags["MEDICALNAME" + str(idx)] = m["TREATMENTNAME"]
        tags["MEDICALCOMMENTS" + str(idx)] = m["COMMENTS"]
        tags["MEDICALFREQUENCY" + str(idx)] = m["NAMEDFREQUENCY"]
        tags["MEDICALNUMBEROFTREATMENTS" + str(idx)] = m["NAMEDNUMBEROFTREATMENTS"]
        tags["MEDICALSTATUS" + str(idx)] = m["NAMEDSTATUS"]
        tags["MEDICALDOSAGE" + str(idx)] = m["DOSAGE"]
        tags["MEDICALSTARTDATE" + str(idx)] = python2display(l, m["STARTDATE"])
        tags["MEDICALTREATMENTSGIVEN" + str(idx)] = str(m["TREATMENTSGIVEN"])
        tags["MEDICALTREATMENTSREMAINING" + str(idx)] = str(m["TREATMENTSREMAINING"])
        tags["MEDICALNEXTTREATMENTDUE" + str(idx)] = python2display(l, m["NEXTTREATMENTDUE"])
        tags["MEDICALLASTTREATMENTGIVEN" + str(idx)] = python2display(l, m["LASTTREATMENTGIVEN"])
        tags["MEDICALCOST" + str(idx)] = format_currency_no_symbol(l, m["COST"])
        idx += 1
    idx = 1
    uniquetypes = {}
    recentgiven = {}
    for m in meddesc:
        tags["MEDICALNAMELAST" + str(idx)] = m["TREATMENTNAME"]
        tags["MEDICALCOMMENTSLAST" + str(idx)] = m["COMMENTS"]
        tags["MEDICALFREQUENCYLAST" + str(idx)] = m["NAMEDFREQUENCY"]
        tags["MEDICALNUMBEROFTREATMENTSLAST" + str(idx)] = m["NAMEDNUMBEROFTREATMENTS"]
        tags["MEDICALSTATUSLAST" + str(idx)] = m["NAMEDSTATUS"]
        tags["MEDICALDOSAGELAST" + str(idx)] = m["DOSAGE"]
        tags["MEDICALSTARTDATELAST" + str(idx)] = python2display(l, m["STARTDATE"])
        tags["MEDICALTREATMENTSGIVENLAST" + str(idx)] = str(m["TREATMENTSGIVEN"])
        tags["MEDICALTREATMENTSREMAININGLAST" + str(idx)] = str(m["TREATMENTSREMAINING"])
        tags["MEDICALNEXTTREATMENTDUELAST" + str(idx)] = python2display(l, m["NEXTTREATMENTDUE"])
        tags["MEDICALLASTTREATMENTGIVENLAST" + str(idx)] = python2display(l, m["LASTTREATMENTGIVEN"])
        tags["MEDICALCOSTLAST" + str(idx)] = format_currency_no_symbol(l, m["COST"])
        idx += 1
        # If this is the first of this type of med we've seen, make
        # some keys based on its name.
        if not uniquetypes.has_key(m["TREATMENTNAME"]):
            tname = m["TREATMENTNAME"].upper().replace(" ", "").replace("/", "")
            uniquetypes[m["TREATMENTNAME"]] = m
            tags["MEDICALNAME" + tname] = m["TREATMENTNAME"]
            tags["MEDICALCOMMENTS" + tname] = m["COMMENTS"]
            tags["MEDICALFREQUENCY" + tname] = m["NAMEDFREQUENCY"]
            tags["MEDICALNUMBEROFTREATMENTS" + tname] = m["NAMEDNUMBEROFTREATMENTS"]
            tags["MEDICALSTATUS" + tname] = m["NAMEDSTATUS"]
            tags["MEDICALDOSAGE" + tname] = m["DOSAGE"]
            tags["MEDICALSTARTDATE" + tname] = python2display(l, m["STARTDATE"])
            tags["MEDICALTREATMENTSGIVEN" + tname] = str(m["TREATMENTSGIVEN"])
            tags["MEDICALTREATMENTSREMAINING" + tname] = str(m["TREATMENTSREMAINING"])
            tags["MEDICALNEXTTREATMENTDUE" + tname] = python2display(l, m["NEXTTREATMENTDUE"])
            tags["MEDICALLASTTREATMENTGIVEN" + tname] = python2display(l, m["LASTTREATMENTGIVEN"])
            tags["MEDICALCOST" + tname] = format_currency_no_symbol(l, m["COST"])
        # If this is the first of this type of med we've seen that's complete
        if not recentgiven.has_key(m["TREATMENTNAME"]) and m["STATUS"] == 2:
            tname = m["TREATMENTNAME"].upper().replace(" ", "").replace("/", "")
            recentgiven[m["TREATMENTNAME"]] = m
            tags["MEDICALNAMERECENT" + tname] = m["TREATMENTNAME"]
            tags["MEDICALCOMMENTSRECENT" + tname] = m["COMMENTS"]
            tags["MEDICALFREQUENCYRECENT" + tname] = m["NAMEDFREQUENCY"]
            tags["MEDICALNUMBEROFTREATMENTSRECENT" + tname] = m["NAMEDNUMBEROFTREATMENTS"]
            tags["MEDICALSTATUSRECENT" + tname] = m["NAMEDSTATUS"]
            tags["MEDICALDOSAGERECENT" + tname] = m["DOSAGE"]
            tags["MEDICALSTARTDATERECENT" + tname] = python2display(l, m["STARTDATE"])
            tags["MEDICALTREATMENTSGIVENRECENT" + tname] = str(m["TREATMENTSGIVEN"])
            tags["MEDICALTREATMENTSREMAININGRECENT" + tname] = str(m["TREATMENTSREMAINING"])
            tags["MEDICALNEXTTREATMENTDUERECENT" + tname] = python2display(l, m["NEXTTREATMENTDUE"])
            tags["MEDICALLASTTREATMENTGIVENRECENT" + tname] = python2display(l, m["LASTTREATMENTGIVEN"])
            tags["MEDICALCOSTRECENT" + tname] = format_currency_no_symbol(l, m["COST"])

    # Diet
    dietasc = animal.get_diets(dbo, int(a["ID"]))
    dietdesc = animal.get_diets(dbo, int(a["ID"]), animal.DESCENDING)
    for idx in range(1, 101):
        tags["DIETNAME" + str(idx)] = ""
        tags["DIETDESCRIPTION" + str(idx)] = ""
        tags["DIETDATESTARTED" + str(idx)] = ""
        tags["DIETCOMMENTS" + str(idx)] = ""
        tags["DIETNAMELAST" + str(idx)] = ""
        tags["DIETDESCRIPTIONLAST" + str(idx)] = ""
        tags["DIETDATESTARTEDLAST" + str(idx)] = ""
        tags["DIETCOMMENTSLAST" + str(idx)] = ""
    idx = 1
    for d in dietasc:
        tags["DIETNAME" + str(idx)] = d["DIETNAME"]
        tags["DIETDESCRIPTION" + str(idx)] = d["DIETDESCRIPTION"]
        tags["DIETDATESTARTED" + str(idx)] = python2display(l, d["DATESTARTED"])
        tags["DIETCOMMENTS" + str(idx)] = d["COMMENTS"]
        idx += 1
    idx = 1
    for d in dietdesc:
        tags["DIETNAMELAST" + str(idx)] = d["DIETNAME"]
        tags["DIETDESCRIPTIONLAST" + str(idx)] = d["DIETDESCRIPTION"]
        tags["DIETDATESTARTEDLAST" + str(idx)] = python2display(l, d["DATESTARTED"])
        tags["DIETCOMMENTSLAST" + str(idx)] = d["COMMENTS"]
        idx += 1

    # Donations
    donasc = financial.get_animal_donations(dbo, int(a["ID"]))
    dondesc = financial.get_animal_donations(dbo, int(a["ID"]), financial.DESCENDING)
    for idx in range(1, 101):
        tags["RECEIPTNUM" + str(idx)] = ""
        tags["DONATIONTYPE" + str(idx)] = ""
        tags["DONATIONPAYMENTTYPE" + str(idx)] = ""
        tags["DONATIONDATE" + str(idx)] = ""
        tags["DONATIONDATEDUE" + str(idx)] = ""
        tags["DONATIONAMOUNT" + str(idx)] = ""
        tags["DONATIONCOMMENTS" + str(idx)] = ""
        tags["DONATIONGIFTAID" + str(idx)] = ""
        tags["RECEIPTNUMLAST" + str(idx)] = ""
        tags["DONATIONTYPELAST" + str(idx)] = ""
        tags["DONATIONDATELAST" + str(idx)] = ""
        tags["DONATIONDATEDUELAST" + str(idx)] = ""
        tags["DONATIONAMOUNTLAST" + str(idx)] = ""
        tags["DONATIONCOMMENTSLAST" + str(idx)] = ""
        tags["DONATIONGIFTAIDLAST" + str(idx)] = ""
        tags["PAYMENTTYPE" + str(idx)] = ""
        tags["PAYMENTMETHOD" + str(idx)] = ""
        tags["PAYMENTDATE" + str(idx)] = ""
        tags["PAYMENTDATEDUE" + str(idx)] = ""
        tags["PAYMENTAMOUNT" + str(idx)] = ""
        tags["PAYMENTCOMMENTS" + str(idx)] = ""
        tags["PAYMENTTYPELAST" + str(idx)] = ""
        tags["PAYMENTMETHODLAST" + str(idx)] = ""
        tags["PAYMENTDATELAST" + str(idx)] = ""
        tags["PAYMENTDATEDUELAST" + str(idx)] = ""
        tags["PAYMENTAMOUNTLAST" + str(idx)] = ""
        tags["PAYMENTCOMMENTSLAST" + str(idx)] = ""
        tags["PAYMENTGIFTAIDLAST" + str(idx)] = ""

    idx = 1
    for d in donasc:
        tags["RECEIPTNUM" + str(idx)] = utils.padleft(d["ID"], 8)
        tags["DONATIONTYPE" + str(idx)] = d["DONATIONNAME"]
        tags["DONATIONPAYMENTTYPE" + str(idx)] = d["PAYMENTNAME"]
        tags["DONATIONDATE" + str(idx)] = python2display(l, d["DATE"])
        tags["DONATIONDATEDUE" + str(idx)] = python2display(l, d["DATEDUE"])
        tags["DONATIONAMOUNT" + str(idx)] = format_currency_no_symbol(l, d["DONATION"])
        tags["DONATIONCOMMENTS" + str(idx)] = d["COMMENTS"]
        tags["DONATIONGIFTAID" + str(idx)] = d["ISGIFTAID"] == 1 and _("Yes", l) or _("No", l)
        tags["PAYMENTTYPE" + str(idx)] = d["DONATIONNAME"]
        tags["PAYMENTMETHOD" + str(idx)] = d["PAYMENTNAME"]
        tags["PAYMENTDATE" + str(idx)] = python2display(l, d["DATE"])
        tags["PAYMENTDATEDUE" + str(idx)] = python2display(l, d["DATEDUE"])
        tags["PAYMENTAMOUNT" + str(idx)] = format_currency_no_symbol(l, d["DONATION"])
        tags["PAYMENTCOMMENTS" + str(idx)] = d["COMMENTS"]
        tags["PAYMENTGIFTAID" + str(idx)] = d["ISGIFTAID"] == 1 and _("Yes", l) or _("No", l)

    idx = 1
    uniquetypes = {}
    recentrec = {}
    for d in dondesc:
        tags["RECEIPTNUMLAST" + str(idx)] = utils.padleft(d["ID"], 8)
        tags["DONATIONTYPELAST" + str(idx)] = d["DONATIONNAME"]
        tags["DONATIONPAYMENTTYPELAST" + str(idx)] = d["PAYMENTNAME"]
        tags["DONATIONDATELAST" + str(idx)] = python2display(l, d["DATE"])
        tags["DONATIONDATEDUELAST" + str(idx)] = python2display(l, d["DATEDUE"])
        tags["DONATIONAMOUNTLAST" + str(idx)] = format_currency_no_symbol(l, d["DONATION"])
        tags["DONATIONCOMMENTSLAST" + str(idx)] = d["COMMENTS"]
        tags["DONATIONGIFTAIDLAST" + str(idx)] = d["ISGIFTAID"] == 1 and _("Yes", l) or _("No", l)
        tags["PAYMENTTYPELAST" + str(idx)] = d["DONATIONNAME"]
        tags["PAYMENTMETHODLAST" + str(idx)] = d["PAYMENTNAME"]
        tags["PAYMENTDATELAST" + str(idx)] = python2display(l, d["DATE"])
        tags["PAYMENTDATEDUELAST" + str(idx)] = python2display(l, d["DATEDUE"])
        tags["PAYMENTAMOUNTLAST" + str(idx)] = format_currency_no_symbol(l, d["DONATION"])
        tags["PAYMENTCOMMENTSLAST" + str(idx)] = d["COMMENTS"]
        tags["PAYMENTGIFTAIDLAST" + str(idx)] = d["ISGIFTAID"] == 1 and _("Yes", l) or _("No", l)

        idx += 1
        # If this is the first of this type of donation we've seen, make
        # some keys based on its name.
        if not uniquetypes.has_key(d["DONATIONNAME"]):
            dname = d["DONATIONNAME"].upper().replace(" ", "").replace("/", "")
            uniquetypes[d["DONATIONNAME"]] = d
            tags["RECEIPTNUM" + dname] = utils.padleft(d["ID"], 8)
            tags["DONATIONTYPE" + dname] = d["DONATIONNAME"]
            tags["DONATIONPAYMENTTYPE" + dname] = d["PAYMENTNAME"]
            tags["DONATIONDATE" + dname] = python2display(l, d["DATE"])
            tags["DONATIONDATEDUE" + dname] = python2display(l, d["DATEDUE"])
            tags["DONATIONAMOUNT" + dname] = format_currency_no_symbol(l, d["DONATION"])
            tags["DONATIONCOMMENTS" + dname] = d["COMMENTS"]
            tags["DONATIONGIFTAID" + dname] = d["ISGIFTAID"] == 1 and _("Yes", l) or _("No", l)
            tags["PAYMENTTYPE" + dname] = d["DONATIONNAME"]
            tags["PAYMENTMETHOD" + dname] = d["PAYMENTNAME"]
            tags["PAYMENTDATE" + dname] = python2display(l, d["DATE"])
            tags["PAYMENTDATEDUE" + dname] = python2display(l, d["DATEDUE"])
            tags["PAYMENTAMOUNT" + dname] = format_currency_no_symbol(l, d["DONATION"])
            tags["PAYMENTCOMMENTS" + dname] = d["COMMENTS"]
            tags["PAYMENTGIFTAID" + dname] = d["ISGIFTAID"] == 1 and _("Yes", l) or _("No", l)
        # If this is the first of this type of donation we've seen that's received
        if not recentrec.has_key(d["DONATIONNAME"]) and d["DATE"] is not None:
            dname = d["DONATIONNAME"].upper().replace(" ", "").replace("/", "")
            recentrec[d["DONATIONNAME"]] = d
            tags["RECEIPTNUMRECENT" + dname] = utils.padleft(d["ID"], 8)
            tags["DONATIONTYPERECENT" + dname] = d["DONATIONNAME"]
            tags["DONATIONPAYMENTTYPERECENT" + dname] = d["PAYMENTNAME"]
            tags["DONATIONDATERECENT" + dname] = python2display(l, d["DATE"])
            tags["DONATIONDATEDUERECENT" + dname] = python2display(l, d["DATEDUE"])
            tags["DONATIONAMOUNTRECENT" + dname] = format_currency_no_symbol(l, d["DONATION"])
            tags["DONATIONCOMMENTSRECENT" + dname] = d["COMMENTS"]
            tags["DONATIONGIFTAIDRECENT" + dname] = d["ISGIFTAID"] == 1 and _("Yes", l) or _("No", l)
            tags["PAYMENTTYPERECENT" + dname] = d["DONATIONNAME"]
            tags["PAYMENTMETHODRECENT" + dname] = d["PAYMENTNAME"]
            tags["PAYMENTDATERECENT" + dname] = python2display(l, d["DATE"])
            tags["PAYMENTDATEDUERECENT" + dname] = python2display(l, d["DATEDUE"])
            tags["PAYMENTAMOUNTRECENT" + dname] = format_currency_no_symbol(l, d["DONATION"])
            tags["PAYMENTCOMMENTSRECENT" + dname] = d["COMMENTS"]
            tags["PAYMENTGIFTAIDRECENT" + dname] = d["ISGIFTAID"] == 1 and _("Yes", l) or _("No", l)

    # Costs
    costasc = animal.get_costs(dbo, int(a["ID"]))
    costdesc = animal.get_costs(dbo, int(a["ID"]), animal.DESCENDING)
    for idx in range(1, 101):
        tags["COSTTYPE" + str(idx)] = ""
        tags["COSTDATE" + str(idx)] = ""
        tags["COSTDATEPAID" + str(idx)] = ""
        tags["COSTAMOUNT" + str(idx)] = ""
        tags["COSTDESCRIPTION" + str(idx)] = ""
        tags["COSTTYPELAST" + str(idx)] = ""
        tags["COSTDATELAST" + str(idx)] = ""
        tags["COSTDATEPAIDLAST" + str(idx)] = ""
        tags["COSTAMOUNTLAST" + str(idx)] = ""
        tags["COSTDESCRIPTIONLAST" + str(idx)] = ""

    idx = 1
    for c in costasc:
        tags["COSTTYPE" + str(idx)] = c["COSTTYPENAME"]
        tags["COSTDATE" + str(idx)] = python2display(l, c["COSTDATE"])
        tags["COSTDATEPAID" + str(idx)] = python2display(l, c["COSTPAIDDATE"])
        tags["COSTAMOUNT" + str(idx)] = format_currency_no_symbol(l, c["COSTAMOUNT"])
        tags["COSTDESCRIPTION" + str(idx)] = c["DESCRIPTION"]

    idx = 1
    uniquetypes = {}
    recentrec = {}
    for c in costdesc:
        tags["COSTTYPELAST" + str(idx)] = c["COSTTYPENAME"]
        tags["COSTDATELAST" + str(idx)] = python2display(l, c["COSTDATE"])
        tags["COSTDATEPAIDLAST" + str(idx)] = python2display(l, c["COSTPAIDDATE"])
        tags["COSTAMOUNTLAST" + str(idx)] = format_currency_no_symbol(l, c["COSTAMOUNT"])
        tags["COSTDESCRIPTIONLAST" + str(idx)] = c["DESCRIPTION"]

        idx += 1
        # If this is the first of this type of cost we've seen, make
        # some keys based on its name.
        if not uniquetypes.has_key(c["COSTTYPENAME"]):
            cname = c["COSTTYPENAME"].upper().replace(" ", "").replace("/", "")
            uniquetypes[c["COSTTYPENAME"]] = c
            tags["COSTTYPE" + cname] = c["COSTTYPENAME"]
            tags["COSTDATE" + cname] = python2display(l, c["COSTDATE"])
            tags["COSTDATEPAID" + cname] = python2display(l, c["COSTPAIDDATE"])
            tags["COSTAMOUNT" + cname] = format_currency_no_symbol(l, c["COSTAMOUNT"])
            tags["COSTDESCRIPTION" + cname] = c["DESCRIPTION"]
        # If this is the first of this type of cost we've seen that's received
        if not recentrec.has_key(c["COSTTYPENAME"]) and c["COSTPAIDDATE"] is not None:
            cname = c["COSTTYPENAME"].upper().replace(" ", "").replace("/", "")
            recentrec[c["COSTTYPENAME"]] = c
            tags["COSTTYPERECENT" + cname] = c["COSTTYPENAME"]
            tags["COSTDATERECENT" + cname] = python2display(l, c["COSTDATE"])
            tags["COSTDATEPAIDRECENT" + cname] = python2display(l, c["COSTPAIDDATE"])
            tags["COSTAMOUNTRECENT" + cname] = format_currency_no_symbol(l, c["COSTAMOUNT"])
            tags["COSTDESCRIPTIONRECENT" + cname] = c["DESCRIPTION"]

    # Logs
    logasc = log.get_logs(dbo, log.ANIMAL, int(a["ID"]), 0, log.ASCENDING)
    logdesc = log.get_logs(dbo, log.ANIMAL, int(a["ID"]), 0, log.DESCENDING)
    for idx in range(1, 101):
        tags["LOGNAME" + str(idx)] = ""
        tags["LOGDATE" + str(idx)] = ""
        tags["LOGCOMMENTS" + str(idx)] = ""
        tags["LOGNAMELAST" + str(idx)] = ""
        tags["LOGDATELAST" + str(idx)] = ""
        tags["LOGCOMMENTSLAST" + str(idx)] = ""
    idx = 1
    for o in logasc:
        tags["LOGNAME" + str(idx)] = o["LOGTYPENAME"]
        tags["LOGDATE" + str(idx)] = python2display(l, o["DATE"])
        tags["LOGCOMMENTS" + str(idx)] = o["COMMENTS"]
        idx += 1
    idx = 1
    uniquetypes = {}
    for o in logdesc:
        tags["LOGNAMELAST" + str(idx)] = o["LOGTYPENAME"]
        tags["LOGDATELAST" + str(idx)] = python2display(l, o["DATE"])
        tags["LOGCOMMENTSLAST" + str(idx)] = o["COMMENTS"]
        idx += 1
        # If this is the first of this type of log we've seen, make
        # some keys based on its name.
        if not uniquetypes.has_key(o["LOGTYPENAME"]):
            lname = o["LOGTYPENAME"].upper().replace(" ", "").replace("/", "")
            uniquetypes[o["LOGTYPENAME"]] = o
            tags["LOGNAME" + lname] = o["LOGTYPENAME"]
            tags["LOGDATE" + lname] = python2display(l, o["DATE"])
            tags["LOGCOMMENTS" + lname] = o["COMMENTS"]
            tags["LOGNAMERECENT" + lname] = o["LOGTYPENAME"]
            tags["LOGDATERECENT" + lname] = python2display(l, o["DATE"])
            tags["LOGCOMMENTSRECENT" + lname] = o["COMMENTS"]

    return tags

def donation_tags(dbo, donations):
    """
    Generates a list of tags from a donation result.
    donations: a list of donation records
    """
    l = dbo.locale
    tags = {}
    totals = { "due": 0, "received": 0 }
    def add_to_tags(i, p): 
        x = { 
            "DONATIONID"+i          : str(p["ID"]),
            "RECEIPTNUM"+i          : utils.padleft(p["ID"], 8),
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
            "PAYMENTCREATEDBY"+i    : p["CREATEDBY"],
            "PAYMENTCREATEDBYNAME"+i: p["CREATEDBY"],
            "PAYMENTCREATEDDATE"+i  : python2display(l, p["CREATEDDATE"]),
            "PAYMENTLASTCHANGEDBY"+i: p["LASTCHANGEDBY"],
            "PAYMENTLASTCHANGEDBYNAME"+i : p["LASTCHANGEDBY"],
            "PAYMENTLASTCHANGEDDATE"+i : python2display(l, p["LASTCHANGEDDATE"])
        }
        tags.update(x)
        if i == "": return # Don't add a total for the compatibility row
        if p["DATE"] is not None: totals["received"] += p["DONATION"]
        if p["DATE"] is None: totals["due"] += p["DONATION"]
    add_to_tags("", donations[0]) 
    for i, d in enumerate(donations):
        add_to_tags(str(i+1), d)
    tags["PAYMENTTOTALDUE"] = format_currency_no_symbol(l, totals["due"])
    tags["PAYMENTTOTALRECEIVED"] = format_currency_no_symbol(l, totals["received"])
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
        "IDCHECK"               : (p["IDCHECK"] == 1 and _("Yes", l) or _("No", l)),
        "HOMECHECKEDBYNAME"     : p["HOMECHECKEDBYNAME"],
        "HOMECHECKEDBYEMAIL"    : p["HOMECHECKEDBYEMAIL"],
        "HOMECHECKEDBYHOMETELEPHONE": p["HOMECHECKEDBYHOMETELEPHONE"],
        "HOMECHECKEDBYMOBILETELEPHONE": p["HOMECHECKEDBYMOBILETELEPHONE"],
        "HOMECHECKEDBYCELLTELEPHONE": p["HOMECHECKEDBYMOBILETELEPHONE"],
        "MEMBERSHIPNUMBER"      : p["MEMBERSHIPNUMBER"],
        "MEMBERSHIPEXPIRYDATE"  : python2display(l, p["MEMBERSHIPEXPIRYDATE"])
    }

    # Additional fields
    add = additional.get_additional_fields(dbo, int(p["ID"]), "person")
    for af in add:
        val = af["VALUE"]
        if af["FIELDTYPE"] == additional.YESNO:
            val = additional_yesno(l, af)
        tags[af["FIELDNAME"].upper()] = val

    # Trap loans
    trapasc = animalcontrol.get_person_traploans(dbo, int(p["ID"]), animalcontrol.ASCENDING)
    trapdesc = animalcontrol.get_person_traploans(dbo, int(p["ID"]), animalcontrol.DESCENDING)
    for idx in range(1, 101):
        tags["TRAPTYPENAME" + str(idx)] = ""
        tags["TRAPLOANDATE" + str(idx)] = ""
        tags["TRAPDEPOSITAMOUNT" + str(idx)] = ""
        tags["TRAPDEPOSITRETURNDATE" + str(idx)] = ""
        tags["TRAPNUMBER" + str(idx)] = ""
        tags["TRAPRETURNDUEDATE" + str(idx)] = ""
        tags["TRAPRETURNDATE" + str(idx)] = ""
        tags["TRAPCOMMENTS" + str(idx)] = ""
    idx = 1
    for t in trapasc:
        tags["TRAPTYPENAME" + str(idx)] = t["TRAPTYPENAME"]
        tags["TRAPLOANDATE" + str(idx)] = python2display(l, t["LOANDATE"])
        tags["TRAPDEPOSITAMOUNT" + str(idx)] = format_currency_no_symbol(l, t["DEPOSITAMOUNT"])
        tags["TRAPDEPOSITRETURNDATE" + str(idx)] = python2display(l, t["DEPOSITRETURNDATE"])
        tags["TRAPNUMBER" + str(idx)] = t["TRAPNUMBER"]
        tags["TRAPRETURNDUEDATE" + str(idx)] = python2display(l, t["RETURNDUEDATE"])
        tags["TRAPRETURNDATE" + str(idx)] = python2display(l, t["RETURNDATE"])
        tags["TRAPCOMMENTS" + str(idx)] = t["COMMENTS"]
        idx += 1
    idx = 1
    uniquetypes = {}
    for t in trapdesc:
        tags["TRAPTYPENAMELAST" + str(idx)] = t["TRAPTYPENAME"]
        tags["TRAPLOANDATELAST" + str(idx)] = python2display(l, t["LOANDATE"])
        tags["TRAPDEPOSITAMOUNTLAST" + str(idx)] = format_currency_no_symbol(l, t["DEPOSITAMOUNT"])
        tags["TRAPDEPOSITRETURNDATELAST" + str(idx)] = python2display(l, t["DEPOSITRETURNDATE"])
        tags["TRAPNUMBERLAST" + str(idx)] = t["TRAPNUMBER"]
        tags["TRAPRETURNDUEDATELAST" + str(idx)] = python2display(l, t["RETURNDUEDATE"])
        tags["TRAPRETURNDATELAST" + str(idx)] = python2display(l, t["RETURNDATE"])
        tags["TRAPCOMMENTSLAST" + str(idx)] = t["COMMENTS"]
        idx += 1
        # If this is the first of this type of traploan we've seen, make
        # some keys based on its name.
        if not uniquetypes.has_key(t["TRAPTYPENAME"]):
            tname = t["TRAPTYPENAME"].upper().replace(" ", "").replace("/", "")
            uniquetypes[t["TRAPTYPENAME"]] = t
            tags["TRAPTYPENAME" + tname] = t["TRAPTYPENAME"]
            tags["TRAPLOANDATE" + tname] = python2display(l, t["LOANDATE"])
            tags["TRAPDEPOSITAMOUNT" + tname] = format_currency_no_symbol(l, t["DEPOSITAMOUNT"])
            tags["TRAPDEPOSITRETURNDATE" + tname] = python2display(l, t["DEPOSITRETURNDATE"])
            tags["TRAPNUMBER" + tname] = t["TRAPNUMBER"]
            tags["TRAPRETURNDUEDATE" + tname] = python2display(l, t["RETURNDUEDATE"])
            tags["TRAPRETURNDATE" + tname] = python2display(l, t["RETURNDATE"])
            tags["TRAPCOMMENTS" + tname] = t["COMMENTS"]

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
        tags = append_tags(tags, person_tags(dbo, person.get_person(dbo, int(a["CURRENTOWNERID"]))))
    elif a["RESERVEDOWNERID"] is not None and a["RESERVEDOWNERID"] != 0:
        tags = append_tags(tags, person_tags(dbo, person.get_person(dbo, int(a["RESERVEDOWNERID"]))))
    if a["ACTIVEMOVEMENTID"] is not None and a["ACTIVEMOVEMENTID"] != 0:
        md = financial.get_movement_donation(dbo, a["ACTIVEMOVEMENTID"])
        if md is not None and md > 0: 
            tags = append_tags(tags, donation_tags(dbo, [md,]))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, template, tags, im)

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
    tags = person_tags(dbo, person.get_person(dbo, int(d["OWNERID"])))
    if d["ANIMALID"] is not None and d["ANIMALID"] != 0:
        tags = append_tags(tags, animal_tags(dbo, animal.get_animal(dbo, d["ANIMALID"])))
    tags = append_tags(tags, donation_tags(dbo, dons))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, template, tags)

