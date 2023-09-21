
import asm3.additional
import asm3.al
import asm3.animal
import asm3.animalcontrol
import asm3.clinic
import asm3.configuration
import asm3.event
import asm3.financial
import asm3.html
import asm3.log
import asm3.lookups
import asm3.lostfound
import asm3.media
import asm3.medical
import asm3.movement
import asm3.person
import asm3.publishers.base
import asm3.template
import asm3.users
import asm3.utils
import asm3.waitinglist
from asm3.i18n import _, date_diff_days, format_currency, format_currency_no_symbol, format_diff, format_diff_single, format_time, now, python2display, python2displaytime, yes_no
from asm3.typehints import bytes_or_str, Database, Dict, List, ResultRow, Results, Tags, Tuple

import zipfile

def org_tags(dbo: Database, username: str) -> Tags:
    """
    Generates a list of tags from the organisation and user info
    """
    u = asm3.users.get_users(dbo, username)
    realname = ""
    email = ""
    sig = ""
    if len(u) > 0:
        u = u[0]
        realname = asm3.utils.nulltostr(u["REALNAME"])
        email = asm3.utils.nulltostr(u["EMAILADDRESS"])
        sig = asm3.utils.nulltostr(u["SIGNATURE"])
    orgname = asm3.configuration.organisation(dbo)
    orgaddress = asm3.configuration.organisation_address(dbo)
    orgtown = asm3.configuration.organisation_town(dbo)
    orgcounty = asm3.configuration.organisation_county(dbo)
    orgpostcode = asm3.configuration.organisation_postcode(dbo)
    orgtel = asm3.configuration.organisation_telephone(dbo)
    orgemail = asm3.configuration.email(dbo)
    tags = {
        "ORGANISATION"          : orgname,
        "ORGANISATIONADDRESS"   : orgaddress,
        "ORGANISATIONTOWN"      : orgtown,
        "ORGANISATIONCOUNTY"    : orgcounty,
        "ORGANISATIONPOSTCODE"  : orgpostcode,
        "ORGANISATIONTELEPHONE" : orgtel,
        "ORGANISATIONEMAIL"     : orgemail,
        "ORGANIZATION"          : orgname,
        "ORGANIZATIONADDRESS"   : orgaddress,
        "ORGANIZATIONCITY"      : orgtown,
        "ORGANIZATIONSTATE"     : orgcounty,
        "ORGANIZATIONZIPCODE"   : orgpostcode,
        "ORGANIZATIONTELEPHONE" : orgtel,
        "ORGANIZATIONEMAIL"     : orgemail,
        "DATE"                  : python2display(dbo.locale, now(dbo.timezone)),
        "SIGNATURE"             : '<img src="signature:placeholder" width="150px" />',
        "SIGNATURE100"          : '<img src="signature:placeholder" width="100px" />',
        "SIGNATURE150"          : '<img src="signature:placeholder" width="150px" />',
        "SIGNATURE200"          : '<img src="signature:placeholder" width="200px" />',
        "SIGNATURE300"          : '<img src="signature:placeholder" width="300px" />',
        "DATABASE"              : dbo.database,
        "USERNAME"              : username,
        "USERREALNAME"          : realname,
        "USEREMAILADDRESS"      : email,
        "USERSIGNATURE"         : '<img src="%s" width="150px" />' % sig,
        "USERSIGNATURE100"      : '<img src="%s" width="100px" />' % sig,
        "USERSIGNATURE150"      : '<img src="%s" width="150px" />' % sig,
        "USERSIGNATURE200"      : '<img src="%s" width="200px" />' % sig,
        "USERSIGNATURE300"      : '<img src="%s" width="300px" />' % sig,
        "USERSIGNATURESRC"      : sig
    }
    return tags

def additional_yesno(l: str, af: ResultRow) -> str:
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

def weight_display(dbo: Database, wv: float) -> str:
    """ formats the weight value wv for display (either kg or lb/oz) """
    kg = asm3.utils.cfloat(wv)
    lbf = asm3.utils.cfloat(wv)
    lb = asm3.utils.cint(wv)
    oz = asm3.utils.cint((kg - lb) * 16.0)
    l = dbo.locale
    if asm3.configuration.show_weight_in_lbs(dbo):
        return "%s %s %s %s" % ( lb, _("lb", l), oz, _("oz", l) )
    elif asm3.configuration.show_weight_in_lbs_fraction(dbo):
        return "%s %s" % (lbf, _("lb", l))
    else:
        return "%s %s" % (kg, _("kg", l))

def br(s: str) -> str:
    """ Returns s with linebreaks turned to <br/> tags """
    if s is None: return ""
    s = s.replace("\r\n", "<br/>").replace("\n", "<br/>")
    return s

def fw(s: str) -> str:
    """ Returns the first word of a string """
    if s is None: return ""
    if s.find(" ") == -1: return s
    return s.split(" ")[0]

def separate_results(rows: Results, f: str) -> Results:
    """ Given a list of result rows, looks at field f and produces
        a list containing a new list of result rows for each
        unique value of f. 
    """
    types = {}
    result = []
    for x in rows:
        if x[f] not in types:
            types[x[f]] = ""
    for k in types.keys():
        orows = []
        for x in rows:
            if x[f] == k:
                orows.append(x)
        result.append(orows)
    return result

def additional_field_tags(dbo: Database, fields: Results, prefix: str = "", depth: int = 2) -> Tags:
    """ Process additional fields and returns them as tags
        depth - the level of the recursion for resolving additional person links in an additional person
    """
    l = dbo.locale
    tags = {}
    for af in fields:
        val = af["VALUE"]
        if val is None: val = ""
        if af["FIELDTYPE"] == asm3.additional.YESNO:
            val = additional_yesno(l, af)
        if af["FIELDTYPE"] == asm3.additional.MONEY:
            val = format_currency_no_symbol(l, af["VALUE"])
        if af["FIELDTYPE"] == asm3.additional.ANIMAL_LOOKUP:
            val = af["ANIMALNAME"]
        if asm3.additional.is_person_fieldtype(af["FIELDTYPE"]):
            val = af["OWNERNAME"]
            p = asm3.person.get_person(dbo, asm3.utils.cint(af["VALUE"]))
            if p is not None: tags = append_tags(tags, additional_field_person_tags(dbo, p, prefix, af["FIELDNAME"].upper(), depth))
        tags[prefix + af["FIELDNAME"].upper()] = val
    return tags

def additional_field_person_tags(dbo: Database, p: ResultRow, prefix: str, fieldname: str, depth: int) -> Tags:
    """
    Generate a tag dictionary for a person record (person, sponsor, vet)
    p - person record
    prefix - the tag prefix to use
    fieldname - the name of the additional field
    depth - the recursion level for resolving additional person records in this person
    """
    l = dbo.locale
    tags = {
        prefix + fieldname + "NAME":            p["OWNERNAME"],
        prefix + fieldname + "TITLE":           p["OWNERTITLE"],
        prefix + fieldname + "TITLE2":          p["OWNERTITLE2"],
        prefix + fieldname + "FIRSTNAME":       p["OWNERFORENAMES"],
        prefix + fieldname + "FIRSTNAME2":      p["OWNERFORENAMES2"],
        prefix + fieldname + "FORENAMES":       p["OWNERFORENAMES"],
        prefix + fieldname + "FORENAMES2":      p["OWNERFORENAMES2"],
        prefix + fieldname + "LASTNAME":        p["OWNERSURNAME"],
        prefix + fieldname + "LASTNAME2":       p["OWNERSURNAME2"],
        prefix + fieldname + "SURNAME":         p["OWNERSURNAME"],
        prefix + fieldname + "SURNAME2":        p["OWNERSURNAME2"],
        prefix + fieldname + "OWNERADDRESS":    p["OWNERADDRESS"],
        prefix + fieldname + "ADDRESS":         p["OWNERADDRESS"],
        prefix + fieldname + "TOWN":            p["OWNERTOWN"],
        prefix + fieldname + "COUNTRY":         p["OWNERCOUNTRY"],
        prefix + fieldname + "POSTCODE":        p["OWNERPOSTCODE"],
        prefix + fieldname + "ZIPCODE":         p["OWNERPOSTCODE"],
        prefix + fieldname + "CITY":            p["OWNERTOWN"],
        prefix + fieldname + "STATE":           p["OWNERCOUNTY"],
        prefix + fieldname + "HOMEPHONE":       p["HOMETELEPHONE"],
        prefix + fieldname + "PHONE":           p["HOMETELEPHONE"],
        prefix + fieldname + "WORKPHONE":       p["WORKTELEPHONE"],
        prefix + fieldname + "WORKPHONE2":      p["WORKTELEPHONE2"],
        prefix + fieldname + "MOBILEPHONE":     p["MOBILETELEPHONE"],
        prefix + fieldname + "MOBILEPHONE2":    p["MOBILETELEPHONE2"],
        prefix + fieldname + "CELLPHONE":       p["MOBILETELEPHONE"],
        prefix + fieldname + "CELLPHONE2":      p["MOBILETELEPHONE2"],
        prefix + fieldname + "EMAIL":           p["EMAILADDRESS"],
        prefix + fieldname + "EMAIL2":          p["EMAILADDRESS2"],
        prefix + fieldname + "OWNERDATEOFBIRTH": python2display(l, p["DATEOFBIRTH"]),
        prefix + fieldname + "OWNERDATEOFBIRTH2": python2display(l, p["DATEOFBIRTH2"]),
        prefix + fieldname + "IDNUMBER":        p["IDENTIFICATIONNUMBER"],
        prefix + fieldname + "IDNUMBER2":       p["IDENTIFICATIONNUMBER2"],
        prefix + fieldname + "JURISDICTION":    p["JURISDICTIONNAME"]
    }
    if depth > 0:
        tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, p["ID"], "person"), prefix + fieldname, depth - 1))
    return tags

def animal_tags_publisher(dbo: Database, a: ResultRow, includeAdditional=True) -> Tags:
    """
    Convenience method for getting animal tags when used by a publisher - 
    very little apart from additional fields are required and we can save
    database calls for each asm3.animal.
    """
    return animal_tags(dbo, a, includeAdditional=includeAdditional, includeCosts=False, includeDiet=True, \
        includeDonations=False, includeFutureOwner=False, includeIsVaccinated=True, includeLitterMates=False, \
        includeLogs=False, includeMedical=False, includeTransport=False)

def animal_tags(dbo: Database, a: ResultRow, includeAdditional=True, includeCosts=True, includeDiet=True, includeDonations=True, \
        includeFutureOwner=True, includeIsVaccinated=True, includeLitterMates=True, includeLogs=True, \
        includeLicence=True, includeMedical=True, includeTransport=True) -> Tags:
    """
    Generates a list of tags from an animal result (the deep type from calling asm3.animal.get_animal)
    """
    l = dbo.locale
    
    # calculate the age instead of using stored value in case animal is off shelter
    animalage = format_diff_single(l, date_diff_days(a["DATEOFBIRTH"], dbo.today()))
    if animalage and animalage.endswith("."): 
        animalage = animalage[0:len(animalage)-1]

    # animal age but with the years and months
    animalageym = format_diff(l, date_diff_days(a["DATEOFBIRTH"], dbo.today()))
    if animalageym and animalageym.endswith("."): 
        animalageym = animalageym[0:len(animalageym)-1]
   
    # strip full stop from the end of time on shelter
    timeonshelter = a["TIMEONSHELTER"]
    if timeonshelter and timeonshelter.endswith("."): 
        timeonshelter = timeonshelter[0:len(timeonshelter)-1]

    # calculate displaydob/age based on whether age is an estimate
    displaydob = python2display(l, a["DATEOFBIRTH"])
    displayage = animalage
    estimate = ""
    if a["ESTIMATEDDOB"] == 1: 
        displaydob = a["AGEGROUP"]
        displayage = a["AGEGROUP"]
        estimate = _("estimate", l)

    # make a list of names for the BONDEDNAMES, BONDEDCODES and BONDEDMICROCHIPS tokens
    bondednames = [ a["ANIMALNAME"] ]
    if a["BONDEDANIMAL1NAME"]: bondednames.append(a["BONDEDANIMAL1NAME"])
    if a["BONDEDANIMAL2NAME"]: bondednames.append(a["BONDEDANIMAL2NAME"])
    bondedcodes = [ a["SHELTERCODE"] ]
    if a["BONDEDANIMAL1CODE"]: bondedcodes.append(a["BONDEDANIMAL1CODE"])
    if a["BONDEDANIMAL2CODE"]: bondedcodes.append(a["BONDEDANIMAL2CODE"])
    bondedmicrochips = [ a["IDENTICHIPNUMBER"] ]
    if a["BONDEDANIMAL1IDENTICHIPNUMBER"]: bondedmicrochips.append(a["BONDEDANIMAL1IDENTICHIPNUMBER"])
    if a["BONDEDANIMAL2IDENTICHIPNUMBER"]: bondedmicrochips.append(a["BONDEDANIMAL2IDENTICHIPNUMBER"])

    tags = { 
        "ANIMALNAME"            : a["ANIMALNAME"],
        "BONDEDNAMES"           : " / ".join(bondednames),
        "BONDEDCODES"           : " / ".join(bondedcodes),
        "BONDEDMICROCHIPS"      : " / ".join(bondedmicrochips),
        "ANIMALTYPENAME"        : a["ANIMALTYPENAME"],
        "BASECOLOURNAME"        : a["BASECOLOURNAME"],
        "BASECOLORNAME"         : a["BASECOLOURNAME"],
        "BREEDNAME"             : a["BREEDNAME"],
        "INTERNALLOCATION"      : a["SHELTERLOCATIONNAME"],
        "LOCATIONNAME"          : a["SHELTERLOCATIONNAME"],
        "LOCATIONDESCRIPTION"   : a["SHELTERLOCATIONDESCRIPTION"],
        "LOCATIONUNIT"          : a["SHELTERLOCATIONUNIT"],
        "DISPLAYLOCATION"       : a["DISPLAYLOCATION"],
        "UNITSPONSOR"           : "UNITSPONSOR" in a and a["UNITSPONSOR"] or "",
        "COATTYPE"              : a["COATTYPENAME"],
        "HEALTHPROBLEMS"        : a["HEALTHPROBLEMS"],
        "HEALTHPROBLEMSBR"      : a["HEALTHPROBLEMS"],
        "ANIMALCREATEDBY"       : a["CREATEDBY"],
        "ANIMALCREATEDDATE"     : python2display(l, a["CREATEDDATE"]),
        "DATEBROUGHTIN"         : python2display(l, a["DATEBROUGHTIN"]),
        "TIMEBROUGHTIN"         : format_time(a["DATEBROUGHTIN"], "%H:%M"),
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
        "MICROCHIPNUMBER2"      : a["IDENTICHIP2NUMBER"],
        "MICROCHIPPED"          : a["IDENTICHIPPEDNAME"],
        "MICROCHIPDATE"         : python2display(l, a["IDENTICHIPDATE"]),
        "MICROCHIPDATE2"        : python2display(l, a["IDENTICHIP2DATE"]),
        "MICROCHIPMANUFACTURER" : asm3.lookups.get_microchip_manufacturer(l, a["IDENTICHIPNUMBER"]),
        "MICROCHIPMANUFACTURER2": asm3.lookups.get_microchip_manufacturer(l, a["IDENTICHIP2NUMBER"]),
        "TATTOO"                : a["TATTOONAME"],
        "TATTOODATE"            : python2display(l, a["TATTOODATE"]),
        "TATTOONUMBER"          : a["TATTOONUMBER"],
        "COMBITESTED"           : a["COMBITESTEDNAME"],
        "FIVLTESTED"            : a["COMBITESTEDNAME"],
        "COMBITESTDATE"         : asm3.utils.iif(a["COMBITESTED"] == 1, python2display(l, a["COMBITESTDATE"]), ""),
        "FIVLTESTDATE"          : asm3.utils.iif(a["COMBITESTED"] == 1, python2display(l, a["COMBITESTDATE"]), ""),
        "COMBITESTRESULT"       : asm3.utils.iif(a["COMBITESTED"] == 1, a["COMBITESTRESULTNAME"], ""),
        "FIVTESTRESULT"         : asm3.utils.iif(a["COMBITESTED"] == 1, a["COMBITESTRESULTNAME"], ""),
        "FIVRESULT"             : asm3.utils.iif(a["COMBITESTED"] == 1, a["COMBITESTRESULTNAME"], ""),
        "FLVTESTRESULT"         : asm3.utils.iif(a["COMBITESTED"] == 1, a["FLVRESULTNAME"], ""),
        "FLVRESULT"             : asm3.utils.iif(a["COMBITESTED"] == 1, a["FLVRESULTNAME"], ""),
        "HEARTWORMTESTED"       : a["HEARTWORMTESTEDNAME"],
        "HEARTWORMTESTDATE"     : asm3.utils.iif(a["HEARTWORMTESTED"] == 1, python2display(l, a["HEARTWORMTESTDATE"]), ""),
        "HEARTWORMTESTRESULT"   : asm3.utils.iif(a["HEARTWORMTESTED"] == 1, a["HEARTWORMTESTRESULTNAME"], ""),
        "HIDDENCOMMENTS"        : a["HIDDENANIMALDETAILS"],
        "HIDDENCOMMENTSBR"      : a["HIDDENANIMALDETAILS"],
        "HIDDENANIMALDETAILS"   : a["HIDDENANIMALDETAILS"],
        "HIDDENANIMALDETAILSBR" : a["HIDDENANIMALDETAILS"],
        "ANIMALLASTCHANGEDBY"   : a["LASTCHANGEDBY"],
        "ANIMALLASTCHANGEDDATE" : python2display(l, a["LASTCHANGEDDATE"]),
        "MARKINGS"              : a["MARKINGS"],
        "MARKINGSBR"            : a["MARKINGS"],
        "WARNING"               : a["POPUPWARNING"],
        "DECLAWED"              : a["DECLAWEDNAME"],
        "RABIESTAG"             : a["RABIESTAG"],
        "GOODWITHCATS"          : a["ISGOODWITHCATSNAME"],
        "GOODWITHDOGS"          : a["ISGOODWITHDOGSNAME"],
        "GOODWITHCHILDREN"      : a["ISGOODWITHCHILDRENNAME"],
        "HOUSETRAINED"          : a["ISHOUSETRAINEDNAME"],
        "DISPLAYCATSIFGOODWITH" : asm3.utils.iif(a["ISGOODWITHCATS"] == 0, _("Cats", l), ""),
        "DISPLAYDOGSIFGOODWITH" : asm3.utils.iif(a["ISGOODWITHDOGS"] == 0, _("Dogs", l), ""),
        "DISPLAYCHILDRENIFGOODWITH" : asm3.utils.iif(a["ISGOODWITHCHILDREN"] == 0, _("Children", l), ""),
        "DISPLAYCATSIFBADWITH" : asm3.utils.iif(a["ISGOODWITHCATS"] == 1, _("Cats", l), ""),
        "DISPLAYDOGSIFBADWITH" : asm3.utils.iif(a["ISGOODWITHDOGS"] == 1, _("Dogs", l), ""),
        "DISPLAYCHILDRENIFBADWITH" : asm3.utils.iif(a["ISGOODWITHCHILDREN"] == 1, _("Children", l), ""),
        "DISPLAYXIFCAT"         : asm3.utils.iif(a["SPECIESID"] == 2, "X", ""),
        "DISPLAYXIFDOG"         : asm3.utils.iif(a["SPECIESID"] == 1, "X", ""),
        "DISPLAYXIFRABBIT"      : asm3.utils.iif(a["SPECIESID"] == 7, "X", ""),
        "DISPLAYXIFMALE"        : asm3.utils.iif(a["SEX"] == 1, "X", ""),
        "DISPLAYXIFFEMALE"      : asm3.utils.iif(a["SEX"] == 0, "X", ""),
        "DISPLAYXIFNEUTERED"    : asm3.utils.iif(a["NEUTERED"] == 1, "X", ""),
        "DISPLAYXIFNOTNEUTERED" : asm3.utils.iif(a["NEUTERED"] == 0, "X", ""),
        "DISPLAYXIFENTIREMALE"  : asm3.utils.iif(a["SEX"] == 1 and a["NEUTERED"] == 0, "X", ""),
        "DISPLAYXIFENTIREFEMALE": asm3.utils.iif(a["SEX"] == 0 and a["NEUTERED"] == 0, "X", ""),
        "DISPLAYXIFFIXEDMALE"   : asm3.utils.iif(a["SEX"] == 1 and a["NEUTERED"] == 1, "X", ""),
        "DISPLAYXIFFIXEDFEMALE" : asm3.utils.iif(a["SEX"] == 0 and a["NEUTERED"] == 1, "X", ""),
        "DISPLAYXIFPEDIGREE"    : asm3.utils.iif(a["CROSSBREED"] == 0, "X", ""),
        "DISPLAYXIFCROSSBREED"  : asm3.utils.iif(a["CROSSBREED"] == 1, "X", ""),
        "PICKUPLOCATIONNAME"    : asm3.utils.iif(a["ISPICKUP"] == 1, asm3.utils.nulltostr(a["PICKUPLOCATIONNAME"]), ""),
        "PICKUPADDRESS"         : asm3.utils.iif(a["ISPICKUP"] == 1, asm3.utils.nulltostr(a["PICKUPADDRESS"]), ""),
        "ANIMALJURISDICTION"    : a["JURISDICTIONNAME"],
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
        "BROUGHTINBYJURISDICTION" : a["BROUGHTINBYJURISDICTION"],
        "BONDEDANIMAL1NAME"     : a["BONDEDANIMAL1NAME"],
        "BONDEDANIMAL1CODE"     : a["BONDEDANIMAL1CODE"],
        "BONDEDANIMAL1MICROCHIP": a["BONDEDANIMAL1IDENTICHIPNUMBER"],
        "BONDEDANIMAL2NAME"     : a["BONDEDANIMAL2NAME"],
        "BONDEDANIMAL2CODE"     : a["BONDEDANIMAL2CODE"],
        "BONDEDANIMAL2MICROCHIP": a["BONDEDANIMAL2IDENTICHIPNUMBER"],
        "NAMEOFOWNERSVET"       : a["OWNERSVETNAME"],
        "NAMEOFCURRENTVET"      : a["CURRENTVETNAME"],
        "HASSPECIALNEEDS"       : a["HASSPECIALNEEDSNAME"],
        "NEUTERED"              : a["NEUTEREDNAME"],
        "FIXED"                 : a["NEUTEREDNAME"],
        "ALTERED"               : a["NEUTEREDNAME"],
        "NEUTEREDDATE"          : python2display(l, a["NEUTEREDDATE"]),
        "FIXEDDATE"             : python2display(l, a["NEUTEREDDATE"]),
        "ALTEREDDATE"           : python2display(l, a["NEUTEREDDATE"]),
        "NEUTERINGVETNAME"      : a["NEUTERINGVETNAME"],
        "NEUTERINGVETADDRESS"   : a["NEUTERINGVETADDRESS"],
        "NEUTERINGVETTOWN"      : a["NEUTERINGVETTOWN"],
        "NEUTERINGVETCOUNTY"    : a["NEUTERINGVETCOUNTY"],
        "NEUTERINGVETPOSTCODE"  : a["NEUTERINGVETPOSTCODE"],
        "NEUTERINGVETCITY"      : a["NEUTERINGVETTOWN"],
        "NEUTERINGVETSTATE"     : a["NEUTERINGVETCOUNTY"],
        "NEUTERINGVETZIPCODE"   : a["NEUTERINGVETPOSTCODE"],
        "NEUTERINGVETPHONE"     : a["NEUTERINGVETWORKTELEPHONE"],
        "NEUTERINGVETEMAIL"     : a["NEUTERINGVETEMAILADDRESS"],
        "NEUTERINGVETLICENSE"   : a["NEUTERINGVETLICENCENUMBER"],
        "NEUTERINGVETLICENCE"   : a["NEUTERINGVETLICENCENUMBER"],
        "COORDINATORNAME"       : a["ADOPTIONCOORDINATORNAME"],
        "COORDINATORHOMEPHONE"  : a["ADOPTIONCOORDINATORHOMETELEPHONE"],
        "COORDINATORWORKPHONE"  : a["ADOPTIONCOORDINATORWORKTELEPHONE"],
        "COORDINATORMOBILEPHONE" : a["ADOPTIONCOORDINATORMOBILETELEPHONE"],
        "COORDINATORCELLPHONE"  : a["ADOPTIONCOORDINATORMOBILETELEPHONE"],
        "COORDINATOREMAIL"      : a["ADOPTIONCOORDINATOREMAILADDRESS"],
        "ORIGINALOWNERTITLE"    : a["ORIGINALOWNERTITLE"],
        "ORIGINALOWNERNAME"     : a["ORIGINALOWNERNAME"],
        "ORIGINALOWNERFIRSTNAME": a["ORIGINALOWNERFORENAMES"],
        "ORIGINALOWNERFORENAMES": a["ORIGINALOWNERFORENAMES"],
        "ORIGINALOWNERLASTNAME" : a["ORIGINALOWNERSURNAME"],
        "ORIGINALOWNERSURNAME"  : a["ORIGINALOWNERSURNAME"],
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
        "ORIGINALOWNERIDNUMBER" : a["ORIGINALOWNERIDNUMBER"],
        "ORIGINALOWNERJURISDICTION" : a["ORIGINALOWNERJURISDICTION"],
        "CURRENTOWNERNAME"     : a["CURRENTOWNERNAME"],
        "CURRENTOWNERTITLE"     : a["CURRENTOWNERTITLE"],
        "CURRENTOWNERFIRSTNAME": a["CURRENTOWNERFORENAMES"],
        "CURRENTOWNERFORENAMES": a["CURRENTOWNERFORENAMES"],
        "CURRENTOWNERLASTNAME" : a["CURRENTOWNERSURNAME"],
        "CURRENTOWNERSURNAME"  : a["CURRENTOWNERSURNAME"],
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
        "CURRENTOWNERIDNUMBER"  : a["CURRENTOWNERIDNUMBER"],
        "CURRENTOWNERJURISDICTION" : a["CURRENTOWNERJURISDICTION"],
        "CURRENTVETNAME"        : a["CURRENTVETNAME"],
        "CURRENTVETADDRESS"     : a["CURRENTVETADDRESS"],
        "CURRENTVETTOWN"        : a["CURRENTVETTOWN"],
        "CURRENTVETCOUNTY"      : a["CURRENTVETCOUNTY"],
        "CURRENTVETPOSTCODE"    : a["CURRENTVETPOSTCODE"],
        "CURRENTVETCITY"        : a["CURRENTVETTOWN"],
        "CURRENTVETSTATE"       : a["CURRENTVETCOUNTY"],
        "CURRENTVETZIPCODE"     : a["CURRENTVETPOSTCODE"],
        "CURRENTVETPHONE"       : a["CURRENTVETWORKTELEPHONE"],
        "CURRENTVETEMAIL"       : a["CURRENTVETEMAILADDRESS"],
        "CURRENTVETLICENSE"     : a["CURRENTVETLICENCENUMBER"],
        "CURRENTVETLICENCE"     : a["CURRENTVETLICENCENUMBER"],
        "OWNERSVETNAME"         : a["OWNERSVETNAME"],
        "OWNERSVETADDRESS"      : a["OWNERSVETADDRESS"],
        "OWNERSVETTOWN"         : a["OWNERSVETTOWN"],
        "OWNERSVETCOUNTY"       : a["OWNERSVETCOUNTY"],
        "OWNERSVETPOSTCODE"     : a["OWNERSVETPOSTCODE"],
        "OWNERSVETCITY"         : a["OWNERSVETTOWN"],
        "OWNERSVETSTATE"        : a["OWNERSVETCOUNTY"],
        "OWNERSVETZIPCODE"      : a["OWNERSVETPOSTCODE"],
        "OWNERSVETPHONE"        : a["OWNERSVETWORKTELEPHONE"],
        "OWNERSVETEMAIL"        : a["OWNERSVETEMAILADDRESS"],
        "OWNERSVETLICENSE"      : a["OWNERSVETLICENCENUMBER"],
        "OWNERSVETLICENCE"      : a["OWNERSVETLICENCENUMBER"],
        "RESERVEDOWNERNAME"     : a["RESERVEDOWNERNAME"],
        "RESERVEDOWNERTITLE"    : a["RESERVEDOWNERTITLE"],
        "RESERVEDOWNERFIRSTNAME" : a["RESERVEDOWNERFORENAMES"],
        "RESERVEDOWNERFORENAMES" : a["RESERVEDOWNERFORENAMES"],
        "RESERVEDOWNERLASTNAME" : a["RESERVEDOWNERSURNAME"],
        "RESERVEDOWNERSURNAME"  : a["RESERVEDOWNERSURNAME"],
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
        "RESERVEDOWNERIDNUMBER"  : a["RESERVEDOWNERIDNUMBER"],
        "RESERVEDOWNERJURISDICTION" : a["RESERVEDOWNERJURISDICTION"],
        "ENTRYCATEGORY"         : a["ENTRYREASONNAME"],
        "MOSTRECENTENTRYCATEGORY" : a["ENTRYREASONNAME"],
        "REASONFORENTRY"        : a["REASONFORENTRY"],
        "REASONFORENTRYBR"      : a["REASONFORENTRY"],
        "REASONNOTBROUGHTBYOWNER" : a["REASONNO"],
        "SEX"                   : a["SEXNAME"],
        "SIZE"                  : a["SIZENAME"],
        "WEIGHT"                : asm3.utils.nulltostr(a["WEIGHT"]),
        "DISPLAYWEIGHT"         : weight_display(dbo, a["WEIGHT"]),
        "SPECIESNAME"           : a["SPECIESNAME"],
        "ANIMALFLAGS"           : asm3.utils.nulltostr(a["ADDITIONALFLAGS"]).replace("|", ", "),
        "ANIMALCOMMENTS"        : a["ANIMALCOMMENTS"],
        "ANIMALCOMMENTSBR"      : a["ANIMALCOMMENTS"],
        "DESCRIPTION"           : a["ANIMALCOMMENTS"],
        "DESCRIPTIONATTR"       : asm3.utils.truncate(a["ANIMALCOMMENTS"].replace("\n", " ").replace("\"", "''")),
        "DESCRIPTIONBR"         : a["ANIMALCOMMENTS"],
        "SHELTERCODE"           : a["SHELTERCODE"],
        "AGE"                   : animalage,
        "AGEYM"                 : animalageym,
        "ACCEPTANCENUMBER"      : a["ACCEPTANCENUMBER"],
        "LITTERID"              : a["ACCEPTANCENUMBER"],
        "DECEASEDDATE"          : python2display(l, a["DECEASEDDATE"]),
        "DECEASEDNOTES"         : a["PTSREASON"],
        "DECEASEDCATEGORY"      : a["PTSREASONNAME"],
        "SHORTSHELTERCODE"      : a["SHORTCODE"],
        "MOSTRECENTENTRY"       : python2display(l, a["MOSTRECENTENTRYDATE"]),
        "MOSTRECENTENTRYDATE"   : python2display(l, a["MOSTRECENTENTRYDATE"]),
        "TIMEONSHELTER"         : timeonshelter,
        "DAYSONSHELTER"         : str(a["DAYSONSHELTER"]),
        "WEBMEDIAFILENAME"      : a["WEBSITEMEDIANAME"],
        "WEBSITEIMAGECOUNT"     : a["WEBSITEIMAGECOUNT"],
        "WEBSITEMEDIANAME"      : a["WEBSITEMEDIANAME"],
        "WEBSITEVIDEOURL"       : a["WEBSITEVIDEOURL"],
        "WEBSITEVIDEONOTES"     : a["WEBSITEVIDEONOTES"],
        "WEBMEDIANOTES"         : a["WEBSITEMEDIANOTES"],
        "WEBSITEMEDIANOTES"     : a["WEBSITEMEDIANOTES"],
        "DOCUMENTIMGSRC"        : asm3.html.doc_img_src(dbo, a),
        "DOCUMENTIMGLINK"       : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK200"    : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK300"    : "<img height=\"300\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK400"    : "<img height=\"400\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK500"    : "<img height=\"500\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGTHUMBSRC"   : asm3.html.thumbnail_img_src(dbo, a, "animalthumb"),
        "DOCUMENTIMGTHUMBLINK"  : "<img src=\"" + asm3.html.thumbnail_img_src(dbo, a, "animalthumb") + "\" />",
        "DOCUMENTQRLINK"        : "<img src=\"%s\" />" % asm3.html.qr_animal_img_record_src(a.ID),
        "DOCUMENTQRLINK200"     : "<img src=\"%s\" />" % asm3.html.qr_animal_img_record_src(a.ID, "200x200"),
        "DOCUMENTQRLINK150"     : "<img src=\"%s\" />" % asm3.html.qr_animal_img_record_src(a.ID, "150x150"),
        "DOCUMENTQRLINK100"     : "<img src=\"%s\" />" % asm3.html.qr_animal_img_record_src(a.ID, "100x100"),
        "DOCUMENTQRLINK50"      : "<img src=\"%s\" />" % asm3.html.qr_animal_img_record_src(a.ID, "50x50"),
        "DOCUMENTQRSHARE"       : "<img src=\"%s\" />" % asm3.html.qr_animal_img_share_src(dbo, a.ID),
        "DOCUMENTQRSHARE200"    : "<img src=\"%s\" />" % asm3.html.qr_animal_img_share_src(dbo, a.ID, "200x200"),
        "DOCUMENTQRSHARE150"    : "<img src=\"%s\" />" % asm3.html.qr_animal_img_share_src(dbo, a.ID, "150x150"),
        "DOCUMENTQRSHARE100"    : "<img src=\"%s\" />" % asm3.html.qr_animal_img_share_src(dbo, a.ID, "100x100"),
        "DOCUMENTQRSHARE50"     : "<img src=\"%s\" />" % asm3.html.qr_animal_img_share_src(dbo, a.ID, "50x50"),
        "ADOPTIONSTATUS"        : asm3.publishers.base.get_adoption_status(dbo, a),
        "ANIMALISADOPTABLE"     : asm3.utils.iif(asm3.publishers.base.is_animal_adoptable(dbo, a), _("Yes", l), _("No", l)),
        "DATEAVAILABLEFORADOPTION": python2display(l, a["DATEAVAILABLEFORADOPTION"]),
        "ANIMALONSHELTER"       : yes_no(l, a["ARCHIVED"] == 0),
        "ANIMALONFOSTER"        : yes_no(l, a["ACTIVEMOVEMENTTYPE"] == asm3.movement.FOSTER),
        "ANIMALPERMANENTFOSTER" : yes_no(l, a["HASPERMANENTFOSTER"] == 1),
        "ANIMALATRETAILER"      : yes_no(l, a["ACTIVEMOVEMENTTYPE"] == asm3.movement.RETAILER),
        "ANIMALISRESERVED"      : yes_no(l, a["HASACTIVERESERVE"] == 1),
        "RESERVATIONDATE"       : python2display(l, a["RESERVATIONDATE"]),
        "ADOPTIONID"            : a["ACTIVEMOVEMENTADOPTIONNUMBER"],
        "OUTCOMEDATE"           : asm3.utils.iif(a["DECEASEDDATE"] is None, python2display(l, a["ACTIVEMOVEMENTDATE"]), python2display(l, a["DECEASEDDATE"])),
        "OUTCOMETYPE"           : asm3.utils.iif(a["ARCHIVED"] == 1, a["DISPLAYLOCATIONNAME"], "")
    }

    # Set original owner to be current owner on non-shelter animals
    if a["NONSHELTERANIMAL"] == 1 and a["ORIGINALOWNERNAME"] is not None and a["ORIGINALOWNERNAME"] != "":
        tags["CURRENTOWNERID"] = a["ORIGINALOWNERID"]
        tags["CURRENTOWNERNAME"] = a["ORIGINALOWNERNAME"]
        tags["CURRENTOWNERTITLE"] = a["ORIGINALOWNERTITLE"]
        tags["CURRENTOWNERFIRSTNAME"] = a["ORIGINALOWNERFORENAMES"]
        tags["CURRENTOWNERFORENAMES"] = a["ORIGINALOWNERFORENAMES"]
        tags["CURRENTOWNERLASTNAME"] = a["ORIGINALOWNERSURNAME"]
        tags["CURRENTOWNERSURNAME"] = a["ORIGINALOWNERSURNAME"]
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
        tags["CURRENTOWNERJURISDICTION"] = a["ORIGINALOWNERJURISDICTION"]

    # If the animal doesn't have a current owner, but does have an open
    # movement with a future date on it, look up the owner and use that 
    # instead so that we can still generate paperwork for future adoptions.
    if includeFutureOwner and a["CURRENTOWNERID"] is None or a["CURRENTOWNERID"] == 0:
        latest = asm3.movement.get_animal_movements(dbo, a["ID"])
        if len(latest) > 0:
            latest = latest[0]
            if latest["MOVEMENTDATE"] is not None and latest["RETURNDATE"] is None:
                p = asm3.person.get_person(dbo, latest["OWNERID"])
                a["CURRENTOWNERID"] = latest["OWNERID"]
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

            # If the latest movement is an adoption return, update the MOSTRECENTENTRYCATEGORY field
            if latest["MOVEMENTTYPE"] == 1 and latest["RETURNDATE"] is not None:
                tags["MOSTRECENTENTRYCATEGORY"] = latest["RETURNEDREASONNAME"]

    # Additional fields
    if includeAdditional:
        tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, a["ID"], "animal")))
        if a["ORIGINALOWNERID"] and a["ORIGINALOWNERID"] > 0:
            tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, a["ORIGINALOWNERID"], "person"), "ORIGINALOWNER"))
        if a["BROUGHTINBYOWNERID"] and a["BROUGHTINBYOWNERID"] > 0:
            tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, a["BROUGHTINBYOWNERID"], "person"), "BROUGHTINBY"))
        if a["CURRENTOWNERID"] and a["CURRENTOWNERID"] > 0:
            tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, a["CURRENTOWNERID"], "person"), "CURRENTOWNER"))
        if a["CURRENTVETID"] and a["CURRENTVETID"] > 0:
            tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, a["CURRENTVETID"], "person"), "CURRENTVET"))

    # Is vaccinated indicator
    if includeIsVaccinated:    
        tags["ANIMALISVACCINATED"] = asm3.utils.iif(asm3.medical.get_vaccinated(dbo, a["ID"]), _("Yes", l), _("No", l))

    # Last licence number
    if includeLicence:
        licences = asm3.financial.get_animal_licences(dbo, a["ID"], asm3.financial.DESCENDING)
        if len(licences) > 0:
            tags["LICENCENUMBER"] = licences[0]["LICENCENUMBER"]
            tags["LICENSENUMBER"] = licences[0]["LICENCENUMBER"]

    if includeMedical:
        iic = asm3.configuration.include_incomplete_medical_doc(dbo)
        # Vaccinations
        d = {
            "VACCINATIONNAME":          "VACCINATIONTYPE",
            "VACCINATIONREQUIRED":      "d:DATEREQUIRED",
            "VACCINATIONGIVEN":         "d:DATEOFVACCINATION",
            "VACCINATIONEXPIRES":       "d:DATEEXPIRES",
            "VACCINATIONBATCH":         "BATCHNUMBER",
            "VACCINATIONMANUFACTURER":  "MANUFACTURER",
            "VACCINATIONRABIESTAG":     "RABIESTAG",
            "VACCINATIONCOST":          "c:COST",
            "VACCINATIONCOMMENTS":      "COMMENTS",
            "VACCINATIONDESCRIPTION":   "VACCINATIONDESCRIPTION",
            "VACCINATIONADMINISTERINGVETNAME":      "ADMINISTERINGVETNAME",
            "VACCINATIONADMINISTERINGVETLICENCE":   "ADMINISTERINGVETLICENCE",
            "VACCINATIONADMINISTERINGVETLICENSE":   "ADMINISTERINGVETLICENCE",
            "VACCINATIONADMINISTERINGVETADDRESS":   "ADMINISTERINGVETADDRESS",
            "VACCINATIONADMINISTERINGVETTOWN":      "ADMINISTERINGVETTOWN",
            "VACCINATIONADMINISTERINGVETCITY":      "ADMINISTERINGVETTOWN",
            "VACCINATIONADMINISTERINGVETCOUNTY":    "ADMINISTERINGVETCOUNTY",
            "VACCINATIONADMINISTERINGVETSTATE":     "ADMINISTERINGVETCOUNTY",
            "VACCINATIONADMINISTERINGVETPOSTCODE":  "ADMINISTERINGVETPOSTCODE",
            "VACCINATIONADMINISTERINGVETZIPCODE":   "ADMINISTERINGVETPOSTCODE",
            "VACCINATIONADMINISTERINGVETEMAIL":     "ADMINISTERINGVETEMAIL"
        }
        vaccinations = asm3.medical.get_vaccinations(dbo, a["ID"], not iic)
        tags.update(table_tags(dbo, d, vaccinations, "VACCINATIONTYPE", "DATEREQUIRED", "DATEOFVACCINATION"))
        tags["ANIMALVACCINATIONS"] = html_table(l, vaccinations, (
            ( "VACCINATIONTYPE", _("Type", l) ),
            ( "DATEREQUIRED", _("Due", l)),
            ( "DATEOFVACCINATION", _("Given", l)),
            ( "DATEEXPIRES", _("Expires", l)),
            ( "ADMINISTERINGVETNAME", _("Vet", l)),
            ( "RABIESTAG", _("Rabies Tag", l) ),
            ( "MANUFACTURER", _("Manufacturer", l)),
            ( "BATCHNUMBER", _("Batch", l)),
            ( "COMMENTS", _("Comments", l)) 
        ))

        # Tests
        d = {
            "TESTNAME":                 "TESTNAME",
            "TESTRESULT":               "RESULTNAME",
            "TESTREQUIRED":             "d:DATEREQUIRED",
            "TESTGIVEN":                "d:DATEOFTEST",
            "TESTCOST":                 "c:COST",
            "TESTCOMMENTS":             "COMMENTS",
            "TESTDESCRIPTION":          "TESTDESCRIPTION",
            "TESTADMINISTERINGVETNAME":      "ADMINISTERINGVETNAME",
            "TESTADMINISTERINGVETLICENCE":   "ADMINISTERINGVETLICENCE",
            "TESTADMINISTERINGVETLICENSE":   "ADMINISTERINGVETLICENCE",
            "TESTADMINISTERINGVETADDRESS":   "ADMINISTERINGVETADDRESS",
            "TESTADMINISTERINGVETTOWN":      "ADMINISTERINGVETTOWN",
            "TESTADMINISTERINGVETCITY":      "ADMINISTERINGVETTOWN",
            "TESTADMINISTERINGVETCOUNTY":    "ADMINISTERINGVETCOUNTY",
            "TESTADMINISTERINGVETSTATE":     "ADMINISTERINGVETCOUNTY",
            "TESTADMINISTERINGVETPOSTCODE":  "ADMINISTERINGVETPOSTCODE",
            "TESTADMINISTERINGVETZIPCODE":   "ADMINISTERINGVETPOSTCODE",
            "TESTADMINISTERINGVETEMAIL":     "ADMINISTERINGVETEMAIL"
        }
        tests = asm3.medical.get_tests(dbo, a["ID"], not iic)
        for t in tests:
            if t.DATEOFTEST is None: t.RESULTNAME = "" # Do not show a result for ungiven tests
        tags.update(table_tags(dbo, d, tests, "TESTNAME", "DATEREQUIRED", "DATEOFTEST"))
        tags["ANIMALTESTS"] = html_table(l, tests, (
            ( "TESTNAME", _("Type", l) ),
            ( "DATEREQUIRED", _("Required", l)),
            ( "DATEOFTEST", _("Performed", l)),
            ( "ADMINISTERINGVETNAME", _("Vet", l)),
            ( "RESULTNAME", _("Result", l)),
            ( "COMMENTS", _("Comments", l)) 
        ))

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
            "MEDICALLASTTREATMENTCOMMENTS": "LASTTREATMENTCOMMENTS",
            "MEDICALCOST":              "c:COST"
        }
        medicals = asm3.medical.get_regimens(dbo, a["ID"], onlycomplete=not iic)
        tags.update(table_tags(dbo, d, medicals, "TREATMENTNAME", "NEXTTREATMENTDUE", "LASTTREATMENTGIVEN"))
        tags["ANIMALMEDICALS"] = html_table(l, medicals, (
            ( "STARTDATE", _("Start Date", l) ),
            ( "TREATMENTNAME", _("Treatment", l) ),
            ( "DOSAGE", _("Dosage", l) ),
            ( "NAMEDSTATUS", _("Status", l) ),
            ( "NAMEDGIVENREMAINING", _("Given", l) ),
            ( "LASTTREATMENTVETNAME", _("Vet", l) ),
            ( "LASTTREATMENTGIVEN", _("Date", l)),
            ( "NEXTTREATMENTDUE", _("Due", l)),
            ( "COMMENTS", _("Comments", l)) 
        ))

        activemedicals = asm3.medical.get_regimens(dbo, a["ID"], onlyactive=True)
        tags["ACTIVEANIMALMEDICALS"] = html_table(l, activemedicals, (
            ( "STARTDATE", _("Start Date", l) ),
            ( "TREATMENTNAME", _("Treatment", l) ),
            ( "DOSAGE", _("Dosage", l) ),
            ( "NAMEDSTATUS", _("Status", l) ),
            ( "NAMEDGIVENREMAINING", _("Given", l) ),
            ( "LASTTREATMENTVETNAME", _("Vet", l) ),
            ( "LASTTREATMENTGIVEN", _("Date", l)),
            ( "NEXTTREATMENTDUE", _("Due", l)),
            ( "COMMENTS", _("Comments", l)) 
        ))

    # Diet
    if includeDiet:
        d = {
            "DIETNAME":                 "DIETNAME",
            "DIETDESCRIPTION":          "DIETDESCRIPTION",
            "DIETDATESTARTED":          "d:DATESTARTED",
            "DIETCOMMENTS":             "COMMENTS"
        }
        tags.update(table_tags(dbo, d, asm3.animal.get_diets(dbo, a["ID"]), "DIETNAME", "DATESTARTED", "DATESTARTED"))

    # Donations
    if includeDonations:
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
            "PAYMENTAMOUNT":            "c:NET",
            "PAYMENTGROSS":             "c:GROSS",
            "PAYMENTNET":               "c:NET",
            "PAYMENTFEE":               "c:FEE",
            "PAYMENTCOMMENTS":          "COMMENTS",
            "PAYMENTGIFTAID":           "y:ISGIFTAID",
            "PAYMENTVAT":               "y:ISVAT",
            "PAYMENTTAX":               "y:ISVAT",
            "PAYMENTVATRATE":           "f:VATRATE",
            "PAYMENTTAXRATE":           "f:VATRATE",
            "PAYMENTVATAMOUNT":         "c:VATAMOUNT",
            "PAYMENTTAXAMOUNT":         "c:VATAMOUNT"
        }
        dons = asm3.financial.get_animal_donations(dbo, a["ID"])
        tags.update(table_tags(dbo, d, dons, "DONATIONNAME", "DATEDUE", "DATE"))

    # Transport
    if includeTransport:
        d = {
            "TRANSPORTTYPE":            "TRANSPORTTYPENAME",
            "TRANSPORTDRIVERNAME":      "DRIVEROWNERNAME", 
            "TRANSPORTPICKUPDATETIME":  "dt:PICKUPDATETIME",
            "TRANSPORTPICKUPDATE":      "d:PICKUPDATETIME",
            "TRANSPORTPICKUPTIME":      "t:PICKUPDATETIME",
            "TRANSPORTPICKUPNAME":      "PICKUPOWNERNAME", 
            "TRANSPORTPICKUPADDRESS":   "PICKUPADDRESS",
            "TRANSPORTPICKUPTOWN":      "PICKUPTOWN",
            "TRANSPORTPICKUPCITY":      "PICKUPTOWN",
            "TRANSPORTPICKUPCOUNTY":    "PICKUPCOUNTY",
            "TRANSPORTPICKUPSTATE":     "PICKUPCOUNTY",
            "TRANSPORTPICKUPZIPCODE":   "PICKUPPOSTCODE",
            "TRANSPORTPICKUPPOSTCODE":  "PICKUPPOSTCODE",
            "TRANSPORTPICKUPCOUNTRY":   "PICKUPCOUNTRY",
            "TRANSPORTPICKUPEMAIL":     "PICKUPEMAILADDRESS",
            "TRANSPORTPICKUPHOMEPHONE": "PICKUPHOMETELEPHONE",
            "TRANSPORTPICKUPWORKPHONE": "PICKUPWORKTELEPHONE",
            "TRANSPORTPICKUPMOBILEPHONE": "PICKUPMOBILETELEPHONE",
            "TRANSPORTPICKUPCELLPHONE": "PICKUPMOBILETELEPHONE",
            "TRANSPORTDROPOFFNAME":     "DROPOFFOWNERNAME", 
            "TRANSPORTDROPOFFDATETIME": "dt:DROPOFFDATETIME",
            "TRANSPORTDROPOFFDATE":     "d:DROPOFFDATETIME",
            "TRANSPORTDROPOFFTIME":     "t:DROPOFFDATETIME",
            "TRANSPORTDROPOFFADDRESS":  "DROPOFFADDRESS",
            "TRANSPORTDROPOFFTOWN":     "DROPOFFTOWN",
            "TRANSPORTDROPOFFCITY":     "DROPOFFTOWN",
            "TRANSPORTDROPOFFCOUNTY":   "DROPOFFCOUNTY",
            "TRANSPORTDROPOFFSTATE":    "DROPOFFCOUNTY",
            "TRANSPORTDROPOFFZIPCODE":  "DROPOFFPOSTCODE",
            "TRANSPORTDROPOFFPOSTCODE": "DROPOFFPOSTCODE",
            "TRANSPORTDROPOFFCOUNTRY":  "DROPOFFCOUNTRY",
            "TRANSPORTDROPOFFEMAIL":    "DROPOFFEMAILADDRESS",
            "TRANSPORTDROPOFFHOMEPHONE": "DROPOFFHOMETELEPHONE",
            "TRANSPORTDROPOFFWORKPHONE": "DROPOFFWORKTELEPHONE",
            "TRANSPORTDROPOFFMOBILEPHONE": "DROPOFFMOBILETELEPHONE",
            "TRANSPORTDROPOFFCELLPHONE": "DROPOFFMOBILETELEPHONE",
            "TRANSPORTMILES":           "MILES",
            "TRANSPORTCOST":            "c:COST",
            "TRANSPORTCOSTPAIDDATE":    "d:COSTPAIDDATE",
            "TRANSPORTCOMMENTS":        "COMMENTS"
        }
        tags.update(table_tags(dbo, d, asm3.movement.get_animal_transports(dbo, a["ID"]), "TRANSPORTTYPENAME", "PICKUPDATETIME", "DROPOFFDATETIME"))

    # Costs
    if includeCosts:
        d = {
            "COSTTYPE":                 "COSTTYPENAME",
            "COSTDATE":                 "d:COSTDATE",
            "COSTDATEPAID":             "d:COSTPAIDDATE",
            "COSTAMOUNT":               "c:COSTAMOUNT",
            "COSTDESCRIPTION":          "DESCRIPTION"
        }
        tags.update(table_tags(dbo, d, asm3.animal.get_costs(dbo, a["ID"]), "COSTTYPENAME", "COSTDATE", "COSTPAIDDATE"))

        # Cost totals
        totalvaccinations = dbo.query_int("SELECT SUM(Cost) FROM animalvaccination WHERE AnimalID = ?", [a["ID"]])
        totaltransports = dbo.query_int("SELECT SUM(Cost) FROM animaltransport WHERE AnimalID = ?", [a["ID"]])
        totaltests = dbo.query_int("SELECT SUM(Cost) FROM animaltest WHERE AnimalID = ?", [a["ID"]])
        totalmedicals = dbo.query_int("SELECT SUM(Cost) FROM animalmedical WHERE AnimalID = ?", [a["ID"]])
        totallines = dbo.query_int("SELECT SUM(CostAmount) FROM animalcost WHERE AnimalID = ?", [a["ID"]])
        totalcosts = totalvaccinations + totaltransports + totaltests + totalmedicals + totallines
        dailyboardingcost = a["DAILYBOARDINGCOST"] or 0
        daysonshelter = a["DAYSONSHELTER"] or 0
        currentboardingcost = dailyboardingcost * daysonshelter
        # Only add the current boarding cost to total if this is a shelter animal
        if a["ARCHIVED"] == 0: totalcosts += currentboardingcost
        costtags = {
            "TOTALVACCINATIONCOSTS": format_currency_no_symbol(l, totalvaccinations),
            "TOTALTRANSPORTCOSTS": format_currency_no_symbol(l, totaltransports),
            "TOTALTESTCOSTS": format_currency_no_symbol(l, totaltests),
            "TOTALMEDICALCOSTS": format_currency_no_symbol(l, totalmedicals),
            "TOTALLINECOSTS": format_currency_no_symbol(l, totallines),
            "DAILYBOARDINGCOST": format_currency_no_symbol(l, dailyboardingcost),
            "CURRENTBOARDINGCOST": format_currency_no_symbol(l, currentboardingcost),
            "TOTALCOSTS": format_currency_no_symbol(l, totalcosts)
        }
        tags = append_tags(tags, costtags)

    if includeLitterMates and a["ACCEPTANCENUMBER"] is not None and len(a["ACCEPTANCENUMBER"]) > 2:
        # Littermates
        lm = dbo.query("SELECT AnimalName, ShelterCode FROM animal " \
            "WHERE AcceptanceNumber = ? AND ID <> ? " \
            "ORDER BY AnimalName", [ a["ACCEPTANCENUMBER"], a["ID"] ])
        tags["LITTERMATES"] = html_table(l, lm, (
            ( "SHELTERCODE", _("Code", l)),
            ( "ANIMALNAME", _("Name", l))
        ))
        lma = dbo.query("SELECT AnimalName, ShelterCode FROM animal " \
            "WHERE AcceptanceNumber = ? AND ID <> ? AND Archived = 0 " \
            "ORDER BY AnimalName", [ a["ACCEPTANCENUMBER"], a["ID"] ])
        tags["ACTIVELITTERMATES"] = html_table(l, lma, (
            ( "SHELTERCODE", _("Code", l)),
            ( "ANIMALNAME", _("Name", l))
        ))

    if includeLogs:
        # Logs
        d = {
            "LOGNAME":                  "LOGTYPENAME",
            "LOGDATE":                  "d:DATE",
            "LOGTIME":                  "t:DATE",
            "LOGCOMMENTS":              "COMMENTS",
            "LOGCREATEDBY":             "CREATEDBY"
        }
        logs = asm3.log.get_logs(dbo, asm3.log.ANIMAL, a["ID"], 0, asm3.log.ASCENDING)
        tags.update(table_tags(dbo, d, logs, "LOGTYPENAME", "DATE", "DATE"))
        tags["ANIMALLOGS"] = html_table(l, logs, (
            ( "DATE", _("Date", l)),
            ( "LOGTYPENAME", _("Type", l)),
            ( "CREATEDBY", _("By", l)),
            ( "COMMENTS", _("Comments", l))
        ))
        # Generate an ANIMALLOGSTYPE for each type represented in the logs
        for logst in separate_results(logs, "LOGTYPENAME"):
            tags["ANIMALLOGS%s" % logst[0]["LOGTYPENAME"].replace(" ", "").upper()] = html_table(l, logst, (
                ( "DATE", _("Date", l)),
                ( "LOGTYPENAME", _("Type", l)),
                ( "CREATEDBY", _("By", l)),
                ( "COMMENTS", _("Comments", l))
            ))

    return tags

def animalcontrol_tags(dbo: Database, ac: ResultRow) -> Tags:
    """
    Generates a list of tags from an animalcontrol incident.
    ac: An animalcontrol incident record
    """
    l = dbo.locale
    tags = {
        "INCIDENTNUMBER":       asm3.utils.padleft(ac["ACID"], 6),
        "INCIDENTDATE":         python2display(l, ac["INCIDENTDATETIME"]),
        "INCIDENTTIME":         format_time(ac["INCIDENTDATETIME"], "%H:%M"),
        "INCIDENTTYPENAME":     asm3.utils.nulltostr(ac["INCIDENTNAME"]),
        "CALLDATE":             python2display(l, ac["CALLDATETIME"]),
        "CALLTIME":             format_time(ac["CALLDATETIME"], "%H:%M"),
        "CALLNOTES":            ac["CALLNOTES"],
        "CALLNOTESBR":          ac["CALLNOTES"],
        "CALLTAKER":            ac["CALLTAKER"],
        "DISPATCHDATE":         python2display(l, ac["DISPATCHDATETIME"]),
        "DISPATCHTIME":         format_time(ac["DISPATCHDATETIME"], "%H:%M"),
        "DISPATCHADDRESS":      ac["DISPATCHADDRESS"],
        "DISPATCHTOWN":         ac["DISPATCHTOWN"],
        "DISPATCHCITY":         ac["DISPATCHTOWN"],
        "DISPATCHCOUNTY":       ac["DISPATCHCOUNTY"],
        "DISPATCHSTATE":        ac["DISPATCHCOUNTY"],
        "DISPATCHPOSTCODE":     ac["DISPATCHPOSTCODE"],
        "DISPATCHZIPCODE":      ac["DISPATCHPOSTCODE"],
        "DISPATCHEDACO":        ac["DISPATCHEDACO"],
        "PICKUPLOCATIONNAME":   asm3.utils.nulltostr(ac["LOCATIONNAME"]),
        "INCIDENTJURISDICTION": asm3.utils.nulltostr(ac["JURISDICTIONNAME"]),
        "RESPONDEDDATE":        python2display(l, ac["RESPONDEDDATETIME"]),
        "RESPONDEDTIME":        format_time(ac["RESPONDEDDATETIME"], "%H:%M"),
        "FOLLOWUPDATE":         python2display(l, ac["FOLLOWUPDATETIME"]),
        "FOLLOWUPTIME":         format_time(ac["FOLLOWUPDATETIME"], "%H:%M"),
        "FOLLOWUPDATE2":         python2display(l, ac["FOLLOWUPDATETIME2"]),
        "FOLLOWUPTIME2":         format_time(ac["FOLLOWUPDATETIME2"], "%H:%M"),
        "FOLLOWUPDATE3":         python2display(l, ac["FOLLOWUPDATETIME3"]),
        "FOLLOWUPTIME3":         format_time(ac["FOLLOWUPDATETIME3"], "%H:%M"),
        "COMPLETEDDATE":        python2display(l, ac["COMPLETEDDATE"]),
        "COMPLETEDTYPENAME":    asm3.utils.nulltostr(ac["COMPLETEDNAME"]),
        "ANIMALDESCRIPTION":    ac["ANIMALDESCRIPTION"],
        "SPECIESNAME":          asm3.utils.nulltostr(ac["SPECIESNAME"]),
        "SEX":                  asm3.utils.nulltostr(ac["SEXNAME"]),
        "AGEGROUP":             asm3.utils.nulltostr(ac["AGEGROUP"]),
        "CALLERNAME":           asm3.utils.nulltostr(ac["CALLERNAME"]),
        "CALLERADDRESS":        asm3.utils.nulltostr(ac["CALLERADDRESS"]),
        "CALLERTOWN":           asm3.utils.nulltostr(ac["CALLERTOWN"]),
        "CALLERCITY":           asm3.utils.nulltostr(ac["CALLERTOWN"]),
        "CALLERCOUNTY":         asm3.utils.nulltostr(ac["CALLERCOUNTY"]),
        "CALLERSTATE":          asm3.utils.nulltostr(ac["CALLERCOUNTY"]),
        "CALLERPOSTCODE":       asm3.utils.nulltostr(ac["CALLERPOSTCODE"]),
        "CALLERZIPCODE":        asm3.utils.nulltostr(ac["CALLERPOSTCODE"]),
        "CALLERHOMETELEPHONE":  asm3.utils.nulltostr(ac["CALLERHOMETELEPHONE"]),
        "CALLERWORKTELEPHONE":  asm3.utils.nulltostr(ac["CALLERWORKTELEPHONE"]),
        "CALLERMOBILETELEPHONE": asm3.utils.nulltostr(ac["CALLERMOBILETELEPHONE"]),
        "CALLERCELLTELEPHONE":  asm3.utils.nulltostr(ac["CALLERMOBILETELEPHONE"]),
        "SUSPECTNAME":          asm3.utils.nulltostr(ac["SUSPECTNAME"]),
        "SUSPECTADDRESS":       asm3.utils.nulltostr(ac["SUSPECTADDRESS"]),
        "SUSPECTTOWN":          asm3.utils.nulltostr(ac["SUSPECTTOWN"]),
        "SUSPECTCITY":          asm3.utils.nulltostr(ac["SUSPECTTOWN"]),
        "SUSPECTCOUNTY":        asm3.utils.nulltostr(ac["SUSPECTCOUNTY"]),
        "SUSPECTSTATE":         asm3.utils.nulltostr(ac["SUSPECTCOUNTY"]),
        "SUSPECTPOSTCODE":      asm3.utils.nulltostr(ac["SUSPECTPOSTCODE"]),
        "SUSPECTZIPCODE":       asm3.utils.nulltostr(ac["SUSPECTPOSTCODE"]),
        "SUSPECTHOMETELEPHONE": asm3.utils.nulltostr(ac["SUSPECTHOMETELEPHONE"]),
        "SUSPECTWORKTELEPHONE": asm3.utils.nulltostr(ac["SUSPECTWORKTELEPHONE"]),
        "SUSPECTMOBILETELEPHONE": asm3.utils.nulltostr(ac["SUSPECTMOBILETELEPHONE"]),
        "SUSPECT1NAME":         asm3.utils.nulltostr(ac["OWNERNAME1"]),
        "SUSPECT2NAME":         asm3.utils.nulltostr(ac["OWNERNAME2"]),
        "SUSPECT3NAME":         asm3.utils.nulltostr(ac["OWNERNAME3"]),
        "VICTIMNAME":           asm3.utils.nulltostr(ac["VICTIMNAME"]),
        "VICTIMADDRESS":        asm3.utils.nulltostr(ac["VICTIMADDRESS"]),
        "VICTIMTOWN":           asm3.utils.nulltostr(ac["VICTIMTOWN"]),
        "VICTIMCITY":           asm3.utils.nulltostr(ac["VICTIMTOWN"]),
        "VICTIMCOUNTY":         asm3.utils.nulltostr(ac["VICTIMCOUNTY"]),
        "VICTIMSTATE":          asm3.utils.nulltostr(ac["VICTIMCOUNTY"]),
        "VICTIMPOSTCODE":       asm3.utils.nulltostr(ac["VICTIMPOSTCODE"]),
        "VICTIMHOMETELEPHONE":  asm3.utils.nulltostr(ac["VICTIMHOMETELEPHONE"]),
        "VICTIMWORKTELEPHONE":  asm3.utils.nulltostr(ac["VICTIMWORKTELEPHONE"]),
        "VICTIMMOBILETELEPHONE":  asm3.utils.nulltostr(ac["VICTIMMOBILETELEPHONE"]),
        "VICTIMCELLTELEPHONE":  asm3.utils.nulltostr(ac["VICTIMMOBILETELEPHONE"]),
        "DOCUMENTIMGSRC"        : asm3.html.doc_img_src(dbo, ac),
        "DOCUMENTIMGLINK"       : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, ac) + "\" >",
        "DOCUMENTIMGLINK200"    : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, ac) + "\" >",
        "DOCUMENTIMGLINK300"    : "<img height=\"300\" src=\"" + asm3.html.doc_img_src(dbo, ac) + "\" >",
        "DOCUMENTIMGLINK400"    : "<img height=\"400\" src=\"" + asm3.html.doc_img_src(dbo, ac) + "\" >",
        "DOCUMENTIMGLINK500"    : "<img height=\"500\" src=\"" + asm3.html.doc_img_src(dbo, ac) + "\" >"
    }

    # Linked animals
    d = {
        "ANIMALNAME":           "ANIMALNAME",
        "SHELTERCODE":          "SHELTERCODE",
        "SHORTCODE":            "SHORTCODE",
        "MICROCHIPNUMBER":      "IDENTICHIPNUMBER",
        "AGEGROUP":             "AGEGROUP",
        "ANIMALTYPENAME":       "ANIMALTYPENAME",
        "SPECIESNAME":          "SPECIESNAME",
        "SEX":                  "SEXNAME",
        "SIZE":                 "SIZENAME",
        "BREEDNAME":            "BREEDNAME",
        "BASECOLORNAME":        "BASECOLOURNAME",
        "BASECOLOURNAME":       "BASECOLOURNAME",
        "COATTYPE":             "COATTYPENAME",
        "DATEBROUGHTIN":        "d:DATEBROUGHTIN",
        "DECEASEDDATE":         "d:DECEASEDDATE"
    }
    tags.update(table_tags(dbo, d, asm3.animalcontrol.get_animalcontrol_animals(dbo, ac["ID"]), "SPECIESNAME", "DATEBROUGHTIN", "DATEBROUGHTIN"))

    # Additional fields
    tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, ac["ID"], "incident")))

    # Citations
    d = {
        "CITATIONNAME":         "CITATIONNAME",
        "CITATIONDATE":         "d:CITATIONDATE",
        "CITATIONCOMMENTS":     "COMMENTS",
        "FINEAMOUNT":           "c:FINEAMOUNT",
        "FINEDUEDATE":          "d:FINEDUEDATE",
        "FINEPAIDDATE":         "d:FINEPAIDDATE"
    }
    tags.update(table_tags(dbo, d, asm3.financial.get_incident_citations(dbo, ac["ID"]), "CITATIONNAME", "CITATIONDATE", "FINEPAIDDATE"))

    # Logs
    d = {
        "INCIDENTLOGNAME":            "LOGTYPENAME",
        "INCIDENTLOGDATE":            "d:DATE",
        "INCIDENTLOGTIME":            "t:DATE",
        "INCIDENTLOGCOMMENTS":        "COMMENTS",
        "INCIDENTLOGCREATEDBY":       "CREATEDBY"
    }
    logs = asm3.log.get_logs(dbo, asm3.log.ANIMALCONTROL, ac["ID"], 0, asm3.log.ASCENDING)
    tags.update(table_tags(dbo, d, logs, "LOGTYPENAME", "DATE", "DATE"))
    tags["INCIDENTLOGS"] = html_table(l, logs, (
        ( "DATE", _("Date", l)),
        ( "LOGTYPENAME", _("Type", l)),
        ( "CREATEDBY", _("By", l)),
        ( "COMMENTS", _("Comments", l))
    ))

    return tags

def donation_tags(dbo: Database, donations: Results) -> Tags:
    """
    Generates a list of tags from a donation result.
    donations: a list of donation records
    """
    l = dbo.locale
    tags = {}
    totals = { "due": 0, "gross": 0, "net": 0, "vat": 0, "taxrate": 0.0 }
    def add_to_tags(i, p): 
        x = { 
            "DONATIONID"+i          : str(p["ID"]),
            "RECEIPTNUM"+i          : p["RECEIPTNUMBER"],
            "CHECKNUM"+i            : p["CHEQUENUMBER"],
            "CHEQUENUM"+i           : p["CHEQUENUMBER"],
            "DONATIONTYPE"+i        : p["DONATIONNAME"],
            "DONATIONPAYMENTTYPE"+i : p["PAYMENTNAME"],
            "DONATIONDATE"+i        : python2display(l, p["DATE"]),
            "DONATIONDATEDUE"+i     : python2display(l, p["DATEDUE"]),
            "DONATIONQUANTITY"+i    : str(p["QUANTITY"]),
            "DONATIONUNITPRICE"+i   : format_currency_no_symbol(l, p["UNITPRICE"]),
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
            "PAYMENTQUANTITY"+i    : str(p["QUANTITY"]),
            "PAYMENTUNITPRICE"+i   : format_currency_no_symbol(l, p["UNITPRICE"]),
            "PAYMENTGROSS"+i        : format_currency_no_symbol(l, p["GROSS"]),
            "PAYMENTNET"+i          : format_currency_no_symbol(l, p["NET"]),
            "PAYMENTAMOUNT"+i       : format_currency_no_symbol(l, p["NET"]), 
            "PAYMENTFEE"+i          : format_currency_no_symbol(l, p["FEE"]),
            "PAYMENTCOMMENTS"+i     : p["COMMENTS"],
            "PAYMENTCOMMENTSFW"+i   : fw(p["COMMENTS"]),
            "PAYMENTGIFTAID"+i      : p["ISGIFTAIDNAME"],
            "PAYMENTVAT"+i          : asm3.utils.iif(p["ISVAT"] == 1, _("Yes", l), _("No", l)),
            "PAYMENTTAX"+i          : asm3.utils.iif(p["ISVAT"] == 1, _("Yes", l), _("No", l)),
            "PAYMENTVATRATE"+i      : "%0.2f" % asm3.utils.cfloat(p["VATRATE"]),
            "PAYMENTTAXRATE"+i      : "%0.2f" % asm3.utils.cfloat(p["VATRATE"]),
            "PAYMENTVATAMOUNT"+i    : format_currency_no_symbol(l, p["VATAMOUNT"]),
            "PAYMENTTAXAMOUNT"+i    : format_currency_no_symbol(l, p["VATAMOUNT"]),
            "PAYMENTCREATEDBY"+i    : p["CREATEDBY"],
            "PAYMENTCREATEDBYNAME"+i: p["CREATEDBY"],
            "PAYMENTCREATEDDATE"+i  : python2display(l, p["CREATEDDATE"]),
            "PAYMENTLASTCHANGEDBY"+i: p["LASTCHANGEDBY"],
            "PAYMENTLASTCHANGEDBYNAME"+i : p["LASTCHANGEDBY"],
            "PAYMENTLASTCHANGEDDATE"+i : python2display(l, p["LASTCHANGEDDATE"]),
            "PAYMENTANIMALNAME"+i   : p["ANIMALNAME"],
            "PAYMENTANIMALSHELTERCODE"+i : p["SHELTERCODE"],
            "PAYMENTANIMALSHORTCODE"+i : p["SHORTCODE"],
            "PAYMENTPERSONNAME"+i   : p["OWNERNAME"],
            "PAYMENTPERSONADDRESS"+i : p["OWNERADDRESS"],
            "PAYMENTPERSONTOWN"+i   : p["OWNERTOWN"],
            "PAYMENTPERSONCITY"+i   : p["OWNERTOWN"],
            "PAYMENTPERSONCOUNTY"+i  : p["OWNERCOUNTY"],
            "PAYMENTPERSONSTATE"+i  : p["OWNERCOUNTY"],
            "PAYMENTPERSONPOSTCODE"+i : p["OWNERPOSTCODE"],
            "PAYMENTPERSONZIPCODE"+i : p["OWNERPOSTCODE"]
        }
        tags.update(x)
        if i == "": return # Don't add a total for the compatibility row
        if p["VATRATE"] is not None and p["VATRATE"] > totals["taxrate"]:
            totals["taxrate"] = p["VATRATE"]
        if p["DATE"] is not None: 
            totals["vat"] += asm3.utils.cint(p["VATAMOUNT"])
            totals["net"] += asm3.utils.cint(p["NET"])
            totals["gross"] += asm3.utils.cint(p["GROSS"])
        if p["DATE"] is None: 
            totals["due"] += asm3.utils.cint(p["DONATION"])
    # Add a copy of the donation tags without an index for compatibility
    if len(donations) > 0:
        add_to_tags("", donations[0]) 
    for i, d in enumerate(donations):
        add_to_tags(str(i+1), d)
    tags["PAYMENTTOTALDUE"] = format_currency_no_symbol(l, totals["due"])
    tags["PAYMENTTOTALNET"] = format_currency_no_symbol(l, totals["net"])
    tags["PAYMENTTOTALRECEIVED"] = format_currency_no_symbol(l, totals["net"])
    tags["PAYMENTTOTALVATRATE"] = "%0.2f" % totals["taxrate"]
    tags["PAYMENTTOTALTAXRATE"] = "%0.2f" % totals["taxrate"]
    tags["PAYMENTTOTALVAT"] = format_currency_no_symbol(l, totals["vat"])
    tags["PAYMENTTOTALTAX"] = format_currency_no_symbol(l, totals["vat"])
    tags["PAYMENTTOTALGROSS"] = format_currency_no_symbol(l, totals["gross"])
    tags["PAYMENTTOTAL"] = format_currency_no_symbol(l, totals["gross"])
    return tags

def foundanimal_tags(dbo: Database, a: ResultRow) -> Tags:
    """
    Generates a list of tags from a foundanimal result (asm3.lostfound.get_foundanimal)
    """
    l = dbo.locale
    tags = {
        "ID":                       asm3.utils.padleft(a["ID"], 6),
        "DATEREPORTED":             python2display(l, a["DATEREPORTED"]),
        "DATEFOUND":                python2display(l, a["DATEFOUND"]),
        "DATERETURNED":             python2display(l, a["RETURNTOOWNERDATE"]),
        "AGEGROUP":                 a["AGEGROUP"],
        "FEATURES":                 a["DISTFEAT"],
        "AREAFOUND":                a["AREAFOUND"],
        "AREAPOSTCODE":             a["AREAPOSTCODE"],
        "COMMENTS":                 a["COMMENTS"],
        "SPECIESNAME":              a["SPECIESNAME"],
        "BREEDNAME":                a["BREEDNAME"],
        "BASECOLOURNAME":           a["BASECOLOURNAME"],
        "BASECOLORNAME":            a["BASECOLOURNAME"],
        "SEX":                      a["SEXNAME"],
        "DOCUMENTIMGLINK"       : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK200"    : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK300"    : "<img height=\"300\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK400"    : "<img height=\"400\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK500"    : "<img height=\"500\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >"
    }

    # Additional fields
    tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, a["ID"], "foundanimal")))

    # Logs
    d = {
        "LOGNAME":            "LOGTYPENAME",
        "LOGDATE":            "d:DATE",
        "LOGTIME":            "t:DATE",
        "LOGCOMMENTS":        "COMMENTS",
        "LOGCREATEDBY":       "CREATEDBY"
    }
    tags.update(table_tags(dbo, d, asm3.log.get_logs(dbo, asm3.log.FOUNDANIMAL, a["ID"], 0, asm3.log.ASCENDING), "LOGTYPENAME", "DATE", "DATE"))
    return tags

def lostanimal_tags(dbo: Database, a: ResultRow) -> Tags:
    """
    Generates a list of tags from a lostanimal result (asm3.lostfound.get_lostanimal)
    """
    l = dbo.locale
    tags = {
        "ID":                       asm3.utils.padleft(a["ID"], 6),
        "DATEREPORTED":             python2display(l, a["DATEREPORTED"]),
        "DATELOST":                 python2display(l, a["DATELOST"]),
        "DATEFOUND":                python2display(l, a["DATEFOUND"]),
        "AGEGROUP":                 a["AGEGROUP"],
        "FEATURES":                 a["DISTFEAT"],
        "AREALOST":                 a["AREALOST"],
        "AREAPOSTCODE":             a["AREAPOSTCODE"],
        "COMMENTS":                 a["COMMENTS"],
        "SPECIESNAME":              a["SPECIESNAME"],
        "BREEDNAME":                a["BREEDNAME"],
        "BASECOLOURNAME":           a["BASECOLOURNAME"],
        "BASECOLORNAME":            a["BASECOLOURNAME"],
        "SEX":                      a["SEXNAME"],
        "DOCUMENTIMGLINK"       : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK200"    : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK300"    : "<img height=\"300\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK400"    : "<img height=\"400\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK500"    : "<img height=\"500\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >"
    }

    # Additional fields
    tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, a["ID"], "lostanimal")))

    # Logs
    d = {
        "LOGNAME":            "LOGTYPENAME",
        "LOGDATE":            "d:DATE",
        "LOGTIME":            "t:DATE",
        "LOGCOMMENTS":        "COMMENTS",
        "LOGCREATEDBY":       "CREATEDBY"
    }
    tags.update(table_tags(dbo, d, asm3.log.get_logs(dbo, asm3.log.LOSTANIMAL, a["ID"], 0, asm3.log.ASCENDING), "LOGTYPENAME", "DATE", "DATE"))
    return tags

def licence_tags(dbo: Database, li: ResultRow) -> Tags:
    """
    Generates a list of tags from a licence result 
    (from anything using asm3.financial.get_licence_query)
    """
    l = dbo.locale
    tags = {
        "LICENCETYPENAME":      li["LICENCETYPENAME"],
        "LICENCENUMBER":        li["LICENCENUMBER"],
        "LICENCEFEE":           format_currency_no_symbol(l, li["LICENCEFEE"]),
        "LICENCEISSUED":        python2display(l, li["ISSUEDATE"]),
        "LICENCEEXPIRES":       python2display(l, li["EXPIRYDATE"]),
        "LICENCECOMMENTS":      li["COMMENTS"],
        "LICENSETYPENAME":      li["LICENCETYPENAME"],
        "LICENSENUMBER":        li["LICENCENUMBER"],
        "LICENSEFEE":           format_currency_no_symbol(l, li["LICENCEFEE"]),
        "LICENSEISSUED":        python2display(l, li["ISSUEDATE"]),
        "LICENSEEXPIRES":       python2display(l, li["EXPIRYDATE"]),
        "LICENSECOMMENTS":      li["COMMENTS"]
    }
    return tags

def movement_tags(dbo: Database, m: ResultRow) -> Tags:
    """
    Generates a list of tags from a movement result
    (anything using asm3.movement.get_movement_query)
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
        "RETURNREASON":                 asm3.utils.iif(m["RETURNDATE"] is not None, m["RETURNEDREASONNAME"], ""),
        "RETURNEDBYNAME":               m["RETURNEDBYOWNERNAME"],
        "RETURNEDBYFIRSTNAME":          m["RETURNEDBYOWNERFORENAMES"],
        "RETURNEDBYFORENAMES":          m["RETURNEDBYOWNERFORENAMES"],
        "RETURNEDBYSURNAME":            m["RETURNEDBYOWNERSURNAME"],
        "RETURNEDBYLASTNAME":           m["RETURNEDBYOWNERSURNAME"],
        "RETURNEDBYADDRESS":            m["RETURNEDBYOWNERADDRESS"],
        "RETURNEDBYTOWN":               m["RETURNEDBYOWNERTOWN"],
        "RETURNEDBYCITY":               m["RETURNEDBYOWNERTOWN"],
        "RETURNEDBYCOUNTY":             m["RETURNEDBYOWNERCOUNTY"],
        "RETURNEDBYSTATE":              m["RETURNEDBYOWNERCOUNTY"],
        "RETURNEDBYPOSTCODE":           m["RETURNEDBYOWNERPOSTCODE"],
        "RETURNEDBYZIPCODE":            m["RETURNEDBYOWNERPOSTCODE"],
        "RETURNEDBYHOMEPHONE":          m["RETURNEDBYHOMETELEPHONE"],
        "RETURNEDBYWORKPHONE":          m["RETURNEDBYWORKTELEPHONE"],
        "RETURNEDBYMOBILEPHONE":        m["RETURNEDBYMOBILETELEPHONE"],
        "RETURNEDBYCELLPHONE":          m["RETURNEDBYMOBILETELEPHONE"],
        "RETURNEDBYEMAIL":              m["RETURNEDBYEMAILADDRESS"],
        "RESERVATIONDATE":              m["RESERVATIONDATE"],
        "RESERVATIONCANCELLEDDATE":     m["RESERVATIONCANCELLEDDATE"],
        "RESERVATIONSTATUS":            m["RESERVATIONSTATUSNAME"],
        "MOVEMENTISTRIAL":              asm3.utils.iif(m["ISTRIAL"] == 1, _("Yes", l), _("No", l)),
        "MOVEMENTISPERMANENTFOSTER":    asm3.utils.iif(m["ISPERMANENTFOSTER"] == 1, _("Yes", l), _("No", l)),
        "MOVEMENTCOMMENTS":             m["COMMENTS"],
        "MOVEMENTCREATEDBY":            m["CREATEDBY"],
        "MOVEMENTLASTCHANGEDBY":        m["LASTCHANGEDBY"],
        "MOVEMENTCREATEDDATE":          python2display(l, m["CREATEDDATE"]),
        "MOVEMENTLASTCHANGEDDATE":      python2display(l, m["LASTCHANGEDDATE"]),
        "ADOPTIONCREATEDBY":            m["CREATEDBY"],
        "ADOPTIONLASTCHANGEDBY":        m["LASTCHANGEDBY"],
        "ADOPTIONCREATEDDATE":          python2display(l, m["CREATEDDATE"]),
        "ADOPTIONLASTCHANGEDDATE":      python2display(l, m["LASTCHANGEDDATE"]),
        "ADOPTIONDATE":                 asm3.utils.iif(m["MOVEMENTTYPE"] == asm3.movement.ADOPTION, python2display(l, m["MOVEMENTDATE"]), ""),
        "FOSTEREDDATE":                 asm3.utils.iif(m["MOVEMENTTYPE"] == asm3.movement.FOSTER, python2display(l, m["MOVEMENTDATE"]), ""),
        "TRANSFERDATE":                 asm3.utils.iif(m["MOVEMENTTYPE"] == asm3.movement.TRANSFER, python2display(l, m["MOVEMENTDATE"]), ""),
        "TRIALENDDATE":                 asm3.utils.iif(m["MOVEMENTTYPE"] == asm3.movement.ADOPTION, python2display(l, m["TRIALENDDATE"]), "")
    }
    dons = asm3.financial.get_movement_donations(dbo, m["ID"])
    tags["MOVEMENTPAYMENTS"] = html_table(l, dons, (
        ( "DATE", _("Date", l) ),
        ( "RECEIPTNUMBER", _("Receipt", l) ),
        ( "DONATIONNAME", _("Type", l) ),
        ( "PAYMENTNAME", _("Method", l) ),
        ( "DONATION", _("Amount", l) )
    ))
    if m.EVENTID is not None and m.EVENTID != 0:
        tags = append_tags(tags, event_tags(dbo, asm3.event.get_event(dbo, m.EVENTID)))
    # movement additional fields
    tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, m["ID"], "movement"), "MOVEMENT"))

    return tags

def clinic_tags(dbo: Database, c: ResultRow) -> Tags:
    """
    Generates a list of tags from a clinic result (asm3.clinic.get_appointment)
    """
    l = dbo.locale
    tags = {
        "ID":                   asm3.utils.padleft(c.ID, 6),
        "APPOINTMENTFOR"        : asm3.users.get_real_name(dbo, c.APPTFOR),
        "APPOINTMENTDATE"       : python2display(l, c.DATETIME),
        "APPOINTMENTTIME"       : format_time(c.DATETIME, "%H:%M"),
        "STATUS"                : c.CLINICSTATUSNAME,
        "ARRIVEDDATE"           : python2display(l, c.ARRIVEDDATETIME),
        "ARRIVEDTIME"           : format_time(c.ARRIVEDDATETIME, "%H:%M"),
        "WITHVETDATE"           : python2display(l, c.WITHVETDATETIME),
        "WITHVETTIME"           : format_time(c.WITHVETDATETIME, "%H:%M"),
        "COMPLETEDDATE"         : python2display(l, c.COMPLETEDDATETIME),
        "COMPLETEDTIME"         : format_time(c.COMPLETEDDATETIME, "%H:%M"),
        "REASONFORAPPOINTMENT"  : c.REASONFORAPPOINTMENT,
        "APPOINTMENTCOMMENTS"   : c.COMMENTS,
        "INVOICEAMOUNT"         : format_currency_no_symbol(l, c.AMOUNT),
        "INVOICEVATAMOUNT"      : format_currency_no_symbol(l, c.VATAMOUNT),
        "INVOICETAXAMOUNT"      : format_currency_no_symbol(l, c.VATAMOUNT),
        "INVOICEVATRATE"        : c.VATRATE,
        "INVOICETAXRATE"        : c.VATRATE,
        "INVOICETOTAL"          : format_currency_no_symbol(l, c.AMOUNT + c.VATAMOUNT),
    }

    # Invoice items
    d = {
        "CLINICINVOICEAMOUNT"       : "c:AMOUNT",
        "CLINICINVOICEDESCRIPTION"  : "DESCRIPTION"
    }
    tags.update(table_tags(dbo, d, asm3.clinic.get_invoice_items(dbo, c.ID)))
    return tags

def person_tags(dbo: Database, p: ResultRow, includeImg=False, includeDonations=False, includeVouchers=False) -> Tags:
    """
    Generates a list of tags from a person result (the deep type from
    calling asm3.person.get_person)
    """
    l = dbo.locale
    tags = { 
        "OWNERID"               : str(p["ID"]),
        "OWNERCODE"             : p["OWNERCODE"],
        "OWNERNAME"             : p["OWNERNAME"],
        "NAME"                  : p["OWNERNAME"],
        "OWNERTITLE"            : p["OWNERTITLE"],
        "TITLE"                 : p["OWNERTITLE"],
        "TITLE2"                : p["OWNERTITLE2"],
        "OWNERINITIALS"         : p["OWNERINITIALS"],
        "INITIALS"              : p["OWNERINITIALS"],
        "INITIALS2"             : p["OWNERINITIALS2"],
        "OWNERFORENAMES"        : p["OWNERFORENAMES"],
        "OWNERFIRSTNAMES"       : p["OWNERFORENAMES"],
        "FORENAMES"             : p["OWNERFORENAMES"],
        "FORENAMES2"            : p["OWNERFORENAMES2"],
        "FIRSTNAMES"            : p["OWNERFORENAMES"],
        "FIRSTNAMES2"           : p["OWNERFORENAMES2"],
        "OWNERSURNAME"          : p["OWNERSURNAME"],
        "OWNERLASTNAME"         : p["OWNERSURNAME"],
        "SURNAME"               : p["OWNERSURNAME"],
        "SURNAME2"              : p["OWNERSURNAME2"],
        "LASTNAME"              : p["OWNERSURNAME"],
        "LASTNAME2"             : p["OWNERSURNAME2"],
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
        "OWNERCOUNTRY"          : p["OWNERCOUNTRY"],
        "COUNTRY"               : p["OWNERCOUNTRY"],
        "HOMETELEPHONE"         : p["HOMETELEPHONE"],
        "WORKTELEPHONE"         : p["WORKTELEPHONE"],
        "WORKTELEPHONE2"        : p["WORKTELEPHONE2"],
        "MOBILETELEPHONE"       : p["MOBILETELEPHONE"],
        "MOBILETELEPHONE2"      : p["MOBILETELEPHONE2"],
        "CELLTELEPHONE"         : p["MOBILETELEPHONE"],
        "CELLTELEPHONE2"        : p["MOBILETELEPHONE2"],
        "EMAILADDRESS"          : p["EMAILADDRESS"],
        "EMAILADDRESS2"         : p["EMAILADDRESS2"],
        "OWNERDATEOFBIRTH"      : python2display(l, p["DATEOFBIRTH"]),
        "OWNERDATEOFBIRTH2"     : python2display(l, p["DATEOFBIRTH2"]),
        "IDNUMBER"              : p["IDENTIFICATIONNUMBER"],
        "IDNUMBER2"             : p["IDENTIFICATIONNUMBER2"],
        "JURISDICTION"          : p["JURISDICTIONNAME"],
        "OWNERJURISDICTION"     : p["JURISDICTIONNAME"],
        "SITE"                  : asm3.utils.nulltostr(p["SITENAME"]),
        "OWNERSITE"             : asm3.utils.nulltostr(p["SITENAME"]),
        "OWNERCOMMENTS"         : p["COMMENTS"],
        "OWNERWARNING"          : p["POPUPWARNING"],
        "OWNERFLAGS"            : asm3.utils.nulltostr(p["ADDITIONALFLAGS"]).replace("|", ", "),
        "OWNERCREATEDBY"        : p["CREATEDBY"],
        "OWNERCREATEDBYNAME"    : p["CREATEDBY"],
        "OWNERCREATEDDATE"      : python2display(l, p["CREATEDDATE"]),
        "OWNERLASTCHANGEDBY"    : p["LASTCHANGEDBY"],
        "OWNERLASTCHANGEDBYNAME" : p["LASTCHANGEDBY"],
        "OWNERLASTCHANGEDDATE"  : python2display(l, p["LASTCHANGEDDATE"]),
        "IDCHECK"               : asm3.utils.iif(p["IDCHECK"] == 1, _("Yes", l), _("No", l)),
        "HOMECHECKEDDATE"       : python2display(l, p["DATELASTHOMECHECKED"]),
        "HOMECHECKEDBYNAME"     : p["HOMECHECKEDBYNAME"],
        "HOMECHECKEDBYEMAIL"    : p["HOMECHECKEDBYEMAIL"],
        "HOMECHECKEDBYHOMETELEPHONE": p["HOMECHECKEDBYHOMETELEPHONE"],
        "HOMECHECKEDBYMOBILETELEPHONE": p["HOMECHECKEDBYMOBILETELEPHONE"],
        "HOMECHECKEDBYCELLTELEPHONE": p["HOMECHECKEDBYMOBILETELEPHONE"],
        "MEMBERSHIPNUMBER"      : p["MEMBERSHIPNUMBER"],
        "MEMBERSHIPEXPIRYDATE"  : python2display(l, p["MEMBERSHIPEXPIRYDATE"]),
        "OWNERLOOKINGFOR"       : asm3.person.lookingfor_summary(dbo, p["ID"])
    }

    if includeImg:
        tags["DOCUMENTIMGSRC"] = asm3.html.doc_img_src(dbo, p)
        tags["DOCUMENTIMGLINK"] = "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, p) + "\" >"
        tags["DOCUMENTIMGLINK200"] = "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, p) + "\" >"
        tags["DOCUMENTIMGLINK300"] = "<img height=\"300\" src=\"" + asm3.html.doc_img_src(dbo, p) + "\" >"
        tags["DOCUMENTIMGLINK400"] = "<img height=\"400\" src=\"" + asm3.html.doc_img_src(dbo, p) + "\" >"
        tags["DOCUMENTIMGLINK500"] = "<img height=\"500\" src=\"" + asm3.html.doc_img_src(dbo, p) + "\" >"

    # Donations
    if includeDonations:
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
            "PAYMENTAMOUNT":            "c:NET",
            "PAYMENTGROSS":             "c:GROSS",
            "PAYMENTNET":               "c:NET",
            "PAYMENTFEE":               "c:FEE",
            "PAYMENTCOMMENTS":          "COMMENTS",
            "PAYMENTGIFTAID":           "y:ISGIFTAID",
            "PAYMENTVAT":               "y:ISVAT",
            "PAYMENTTAX":               "y:ISVAT",
            "PAYMENTVATRATE":           "f:VATRATE",
            "PAYMENTTAXRATE":           "f:VATRATE",
            "PAYMENTVATAMOUNT":         "c:VATAMOUNT",
            "PAYMENTTAXAMOUNT":         "c:VATAMOUNT"
        }
        dons = asm3.financial.get_person_donations(dbo, p["ID"])
        tags.update(table_tags(dbo, d, dons, "DONATIONNAME", "DATEDUE", "DATE"))

    # Vouchers
    if includeVouchers:
        d = {
            "VOUCHERANIMALNAME":    "ANIMALNAME",
            "VOUCHERSHELTERCODE":   "SHELTERCODE",
            "VOUCHERTYPENAME":      "VOUCHERNAME",
            "VOUCHERCODE":          "VOUCHERCODE",
            "VOUCHERVALUE":         "c:VALUE",
            "VOUCHERISSUED":        "d:DATEISSUED",
            "VOUCHEREXPIRES":       "d:DATEEXPIRED",
            "VOUCHERREDEEMED":      "d:DATEPRESENTED",
            "VOUCHERCOMMENTS":      "COMMENTS"
        }
        vouc = asm3.financial.get_person_vouchers(dbo, p["ID"])
        tags.update(table_tags(dbo, d, vouc, "VOUCHERNAME", "DATEISSUED", "DATEPRESENTED"))

    # Additional fields
    tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, p["ID"], "person")))

    # Citations
    d = {
        "CITATIONNAME":         "CITATIONNAME",
        "CITATIONDATE":         "d:CITATIONDATE",
        "CITATIONCOMMENTS":     "COMMENTS",
        "FINEAMOUNT":           "c:FINEAMOUNT",
        "FINEDUEDATE":          "d:FINEDUEDATE",
        "FINEPAIDDATE":         "d:FINEPAIDDATE"
    }
    tags.update(table_tags(dbo, d, asm3.financial.get_person_citations(dbo, p["ID"]), "CITATIONNAME", "CITATIONDATE", "FINEPAIDDATE"))

    # Logs
    d = {
        "PERSONLOGNAME":            "LOGTYPENAME",
        "PERSONLOGDATE":            "d:DATE",
        "PERSONLOGTIME":            "t:DATE",
        "PERSONLOGCOMMENTS":        "COMMENTS",
        "PERSONLOGCREATEDBY":       "CREATEDBY"
    }
    tags.update(table_tags(dbo, d, asm3.log.get_logs(dbo, asm3.log.PERSON, p["ID"], 0, asm3.log.ASCENDING), "LOGTYPENAME", "DATE", "DATE"))

    # Trap loans
    d = {
        "TRAPTYPENAME":             "TRAPTYPENAME",
        "TRAPLOANDATE":             "d:LOANDATE",
        "TRAPDEPOSITAMOUNT":        "c:DEPOSITAMOUNT",
        "TRAPDEPOSITRETURNDATE":    "d:DEPOSITRETURNDATE",
        "TRAPNUMBER":               "TRAPNUMBER",
        "TRAPRETURNDUEDATE":        "d:RETURNDUEDATE",
        "TRAPRETURNDATE":           "d:RETURNDATE",
        "TRAPCOMMENTS":             "COMMENTS",
        "EQUIPMENTTYPENAME":        "TRAPTYPENAME",
        "EQUIPMENTLOANDATE":        "d:LOANDATE",
        "EQUIPMENTDEPOSITAMOUNT":   "c:DEPOSITAMOUNT",
        "EQUIPMENTDEPOSITRETURNDATE":"d:DEPOSITRETURNDATE",
        "EQUIPMENTNUMBER":          "TRAPNUMBER",
        "EQUIPMENTRETURNDUEDATE":   "d:RETURNDUEDATE",
        "EQUIPMENTRETURNDATE":      "d:RETURNDATE",
        "EQUIPMENTCOMMENTS":        "COMMENTS"
    }
    tags.update(table_tags(dbo, d, asm3.animalcontrol.get_person_traploans(dbo, p["ID"], asm3.animalcontrol.ASCENDING), "TRAPTYPENAME", "RETURNDUEDATE", "RETURNDATE"))

    return tags

def transport_tags(dbo: Database, transports: Results) -> Tags:
    """
    Generates a list of tags from a list of transports.
    transports: a list of transport records
    """
    l = dbo.locale
    tags = {}
    def add_to_tags(i, t): 
        x = { 
            "TRANSPORTID"+i:              str(t["ID"]),
            "TRANSPORTTYPE"+i:            t["TRANSPORTTYPENAME"],
            "TRANSPORTDRIVERNAME"+i:      t["DRIVEROWNERNAME"], 

            "TRANSPORTPICKUPNAME"+i:      t["PICKUPOWNERNAME"], 
            "TRANSPORTPICKUPDATETIME"+i:  python2display(l, t["PICKUPDATETIME"]),
            "TRANSPORTPICKUPDATE"+i:      python2display(l, t["PICKUPDATETIME"]),
            "TRANSPORTPICKUPTIME"+i:      format_time(t["PICKUPDATETIME"], "%H:%M"),
            "TRANSPORTPICKUPADDRESS"+i:   t["PICKUPADDRESS"],
            "TRANSPORTPICKUPTOWN"+i:      t["PICKUPTOWN"],
            "TRANSPORTPICKUPCITY"+i:      t["PICKUPTOWN"],
            "TRANSPORTPICKUPCOUNTY"+i:    t["PICKUPCOUNTY"],
            "TRANSPORTPICKUPSTATE"+i:     t["PICKUPCOUNTY"],
            "TRANSPORTPICKUPZIPCODE"+i:   t["PICKUPPOSTCODE"],
            "TRANSPORTPICKUPCOUNTRY"+i:   t["PICKUPCOUNTRY"],
            "TRANSPORTPICKUPPOSTCODE"+i:  t["PICKUPPOSTCODE"],
            "TRANSPORTPICKUPEMAIL"+i:     t["PICKUPEMAILADDRESS"],
            "TRANSPORTPICKUPHOMEPHONE"+i: t["PICKUPHOMETELEPHONE"],
            "TRANSPORTPICKUPWORKPHONE"+i: t["PICKUPWORKTELEPHONE"],
            "TRANSPORTPICKUPMOBILEPHONE"+i: t["PICKUPMOBILETELEPHONE"],
            "TRANSPORTPICKUPCELLPHONE"+i: t["PICKUPMOBILETELEPHONE"],

            "TRANSPORTDROPOFFNAME"+i:     t["DROPOFFOWNERNAME"], 
            "TRANSPORTDROPOFFDATETIME"+i: python2display(l, t["DROPOFFDATETIME"]),
            "TRANSPORTDROPOFFDATE"+i:     python2display(l, t["DROPOFFDATETIME"]),
            "TRANSPORTDROPOFFTIME"+i:     format_time(t["DROPOFFDATETIME"], "%H:%M"),
            "TRANSPORTDROPOFFADDRESS"+i:  t["DROPOFFADDRESS"],
            "TRANSPORTDROPOFFTOWN"+i:     t["DROPOFFTOWN"],
            "TRANSPORTDROPOFFCITY"+i:     t["DROPOFFTOWN"],
            "TRANSPORTDROPOFFCOUNTY"+i:   t["DROPOFFCOUNTY"],
            "TRANSPORTDROPOFFSTATE"+i:    t["DROPOFFCOUNTY"],
            "TRANSPORTDROPOFFZIPCODE"+i:  t["DROPOFFPOSTCODE"],
            "TRANSPORTDROPOFFPOSTCODE"+i: t["DROPOFFPOSTCODE"],
            "TRANSPORTDROPOFFCOUNTRY"+i:  t["DROPOFFCOUNTRY"],
            "TRANSPORTDROPOFFEMAIL"+i:    t["DROPOFFEMAILADDRESS"],
            "TRANSPORTDROPOFFHOMEPHONE"+i: t["DROPOFFHOMETELEPHONE"],
            "TRANSPORTDROPOFFWORKPHONE"+i: t["DROPOFFWORKTELEPHONE"],
            "TRANSPORTDROPOFFMOBILEPHONE"+i: t["DROPOFFMOBILETELEPHONE"],
            "TRANSPORTDROPOFFCELLPHONE"+i: t["DROPOFFMOBILETELEPHONE"],

            "TRANSPORTMILES"+i:           str(t["MILES"]),
            "TRANSPORTCOST"+i:            format_currency_no_symbol(l, t["COST"]),
            "TRANSPORTCOSTPAIDDATE"+i:    python2display(l, t["COSTPAIDDATE"]),
            "TRANSPORTCOMMENTS"+i:        t["COMMENTS"],

            "TRANSPORTANIMALNAME"+i:      t["ANIMALNAME"],
            "TRANSPORTSHELTERCODE"+i:     t["SHELTERCODE"],
            "TRANSPORTSHORTCODE"+i:       t["SHORTCODE"],
            "TRANSPORTSPECIES"+i:         t["SPECIESNAME"],
            "TRANSPORTBREED"+i:           t["BREEDNAME"],
            "TRANSPORTSEX"+i:             t["SEX"],
        }
        tags.update(x)
    # Add a copy of the transport tags without an index
    if len(transports) > 0:
        add_to_tags("", transports[0]) 
    for i, t in enumerate(transports):
        add_to_tags(str(i+1), t)
    return tags

def voucher_tags(dbo: Database, v: ResultRow) -> Tags:
    """
    Generates a list of tags from a voucher result 
    (from anything using asm3.financial.get_voucher_query)
    """
    l = dbo.locale
    tags = {
        "VOUCHERANIMALNAME":    v["ANIMALNAME"],
        "VOUCHERSHELTERCODE":   v["SHELTERCODE"],
        "VOUCHERTYPENAME":      v["VOUCHERNAME"],
        "VOUCHERCODE":          v["VOUCHERCODE"],
        "VOUCHERVALUE":         format_currency_no_symbol(l, v["VALUE"]),
        "VOUCHERISSUED":        python2display(l, v["DATEISSUED"]),
        "VOUCHEREXPIRES":       python2display(l, v["DATEEXPIRED"]),
        "VOUCHERREDEEMED":      python2display(l, v["DATEPRESENTED"]),
        "VOUCHERCOMMENTS":      v["COMMENTS"]
    }
    return tags

def waitinglist_tags(dbo: Database, a: ResultRow) -> Tags:
    """
    Generates a list of tags from a waiting list result (asm3.waitinglist.get_waitinglist_by_id)
    """
    l = dbo.locale
    tags = {
        "ID":                       asm3.utils.padleft(a["ID"], 6),
        "DATEPUTONLIST":            python2display(l, a["DATEPUTONLIST"]),
        "DATEREMOVEDFROMLIST":      python2display(l, a["DATEREMOVEDFROMLIST"]),
        "DATEOFLASTOWNERCONTACT":   python2display(l, a["DATEOFLASTOWNERCONTACT"]),
        "SIZE":                     a["SIZENAME"],
        "SPECIESNAME":              a["SPECIESNAME"],
        "DESCRIPTION":              a["ANIMALDESCRIPTION"],
        "REASONFORWANTINGTOPART":   a["REASONFORWANTINGTOPART"],
        "REASONFORREMOVAL":         a["REASONFORREMOVAL"],
        "CANAFFORDDONATION":        asm3.utils.iif(a["CANAFFORDDONATION"] == 1, _("Yes", l), _("No", l)),
        "URGENCY":                  a["URGENCYNAME"],
        "COMMENTS":                 a["COMMENTS"],
        "DOCUMENTIMGLINK"       : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK200"    : "<img height=\"200\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK300"    : "<img height=\"300\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK400"    : "<img height=\"400\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >",
        "DOCUMENTIMGLINK500"    : "<img height=\"500\" src=\"" + asm3.html.doc_img_src(dbo, a) + "\" >"
    }

    # Additional fields
    tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, a["ID"], "waitinglist")))

    # Logs
    d = {
        "LOGNAME":            "LOGTYPENAME",
        "LOGDATE":            "d:DATE",
        "LOGTIME":            "t:DATE",
        "LOGCOMMENTS":        "COMMENTS",
        "LOGCREATEDBY":       "CREATEDBY"
    }
    tags.update(table_tags(dbo, d, asm3.log.get_logs(dbo, asm3.log.WAITINGLIST, a["ID"], 0, asm3.log.ASCENDING), "LOGTYPENAME", "DATE", "DATE"))
    return tags

def event_tags(dbo: Database, e: ResultRow) -> Tags:
    """
    Generate a tag dictionary for events
    e - event object that created from asm3.event.get_event
    """
    l = dbo.locale
    tags = {
        "EVENTSTARTDATE":        python2display(l, e["STARTDATETIME"]),
        "EVENTENDDATE":          python2display(l, e["ENDDATETIME"]),
        "EVENTNAME":            e["EVENTNAME"],
        "EVENTDESCRIPTION":     e["EVENTDESCRIPTION"],
        "EVENTRECORDVERSION":   e["RECORDVERSION"],
        "EVENTCREATEDBY":       e["CREATEDBY"],
        "EVENTCREATEDDATE":     python2display(l, e["CREATEDDATE"]),
        "EVENTLASTCHANGEDBY":   e["LASTCHANGEDBY"],
        "EVENTLASTCHANGEDDATE": python2display(l, e["LASTCHANGEDDATE"]),
        "EVENTOWNERNAME":       e["EVENTOWNERNAME"],
        "EVENTADDRESS":         e["EVENTADDRESS"],
        "EVENTTOWN":            e["EVENTTOWN"],
        "EVENTCITY":            e["EVENTTOWN"],
        "EVENTCOUNTY":          e["EVENTCOUNTY"],
        "EVENTSTATE":           e["EVENTCOUNTY"],
        "EVENTPOSTCODE":        e["EVENTPOSTCODE"],
        "EVENTZIPCODE":         e["EVENTPOSTCODE"],
        "EVENTCOUNTRY":         e["EVENTCOUNTRY"]
    }

    tags.update(additional_field_tags(dbo, asm3.additional.get_additional_fields(dbo, e["ID"], "event"), "EVENT"))

    return tags

def append_tags(tags1: Tags, tags2: Tags) -> Tags:
    """
    Adds two dictionaries of tags together and returns
    a new dictionary containing both sets.
    """
    tags = {}
    tags.update(tags1)
    tags.update(tags2)
    return tags

def html_table(l: str, rows: Results, cols: List[Tuple[str, str]]):
    """
    Generates an HTML table for TinyMCE from rows, choosing the cols.
    cols is a list of tuples containing the field name from rows and a localised column name for output.
    Eg: ( ( "ID", "Text for ID field" ) )
    """
    h = []
    h.append("<table border=\"1\">")
    h.append("<thead><tr>")
    for colfield, coltext in cols:
        h.append("<th>%s</th>" % coltext)
    h.append("</tr></thead>")
    h.append("<tbody>")
    for r in rows:
        h.append("<tr>")
        for colfield, coltext in cols:
            v = r[colfield]
            if asm3.utils.is_date(v):
                h.append("<td>%s</td>" % python2displaytime(l, r[colfield]))
            elif asm3.utils.is_currency(colfield):
                h.append("<td>%s</td>" % format_currency(l, r[colfield]))
            elif r[colfield] is None:
                h.append("<td></td>")
            elif asm3.utils.is_str(r[colfield]) or asm3.utils.is_unicode(r[colfield]):
                h.append("<td>%s</td>" % r[colfield].replace("\n", "<br/>"))
            else:
                h.append("<td>%s</td>" % r[colfield])
        h.append("</tr>")
    h.append("</tbody>")
    h.append("</table>")
    return "".join(h)

def table_get_value(l: str, row: ResultRow, k: str) -> str:
    """
    Returns row[k], looking for a type prefix in k -
    c: currency, d: date, t: time, y: yesno, f: float dt: date and time
    """
    if k.startswith("d:"): 
        s = python2display(l, row[k.replace("d:", "")])
    elif k.startswith("t:"): 
        s = format_time(row[k.replace("t:", "")], "%H:%M")
    elif k.startswith("dt:"):
        s = "%s %s" % (python2display(l, row[k.replace("dt:", "")]), format_time(row[k.replace("dt:", "")], "%H:%M"))
    elif k.startswith("c:"):
        s = format_currency_no_symbol(l, row[k.replace("c:", "")])
    elif k.startswith("y:"):
        s = asm3.utils.iif(row[k.replace("y:", "")] == 1, _("Yes", l), _("No", l))
    elif k.startswith("f:"):
        s = "%0.2f" % asm3.utils.cfloat(row[k.replace("f:", "")])
    elif row[k] is None:
        return ""
    else:
        s = str(row[k])
    return s

def table_tags(dbo: Database, d: Tags, rows: Results, typefield: str = "", recentduefield: str = "", recentgivenfield: str = "") -> Tags:
    """
    For a collection of table rows, generates the LAST/DUE/RECENT and indexed tags.

    d: A dictionary of tag names to field expressions. If the field is
       preceded with d:, it is formatted as a date, c: a currency
       eg: { "VACCINATIONNAME" : "VACCINATIONTYPE", "VACCINATIONREQUIRED", "d:DATEREQUIRED" }

    typefield: The name of the field in rows that contains the type for
       creating tags with the type as a suffix

    recentduefield: The name of the field in rows that contains the date
        the last thing was was due for DUE tags.

    recentgivenfield: The name of the field in rows that contains the date
        the last thing was received/given for RECENT tags.

    rows: The table rows
    """
    l = dbo.locale
    tags = {}
    uniquetypes = {}
    recentdue = {}
    recentgiven = {}

    # Go forwards through the rows
    for i, r in enumerate(rows, 1):
        
        # Create the indexed tags
        for k, v in d.items():
            tags[k + str(i)] = table_get_value(l, r, v)

        # Type suffixed tags
        if typefield != "":
            t = r[typefield]

            # If the type is somehow null, we can't do anything
            if t is None: continue

            # Is this the first of this type we've seen?
            # If so, create the tags with type as a suffix
            if t not in uniquetypes:
                uniquetypes[t] = r
                t = t.upper().replace(" ", "").replace("/", "")
                for k, v in d.items():
                    tags[k + t] = table_get_value(l, r, v)

    # Go backwards through rows
    for i, r in enumerate(reversed(rows), 1):

        # Create reversed index tags
        for k, v in d.items():
            tags[k + "LAST" + str(i)] = table_get_value(l, r, v)

        # Due suffixed tags
        if recentduefield != "":
            t = r[typefield]
            # If the type is somehow null, we can't do anything
            if t is None: continue
            # Is this the first type with a due date and blank given date we've seen?
            # If so, create the tags with due as a suffix
            if t not in recentdue and r[recentduefield] is not None and r[recentgivenfield] is None:
                recentdue[t] = r
                t = t.upper().replace(" ", "").replace("/", "")
                for k, v in d.items():
                    tags[k + "DUE" + t] = table_get_value(l, r, v)

        # Recent suffixed tags
        if recentgivenfield != "":
            t = r[typefield]
            # If the type is somehow null, we can't do anything
            if t is None: continue
            # Is this the first type with a date we've seen?
            # If so, create the tags with recent as a suffix
            if t not in recentgiven and r[recentgivenfield] is not None:
                recentgiven[t] = r
                t = t.upper().replace(" ", "").replace("/", "")
                for k, v in d.items():
                    tags[k + "RECENT" + t] = table_get_value(l, r, v)
    return tags

def substitute_tags(searchin: str, tags: Tags, escape_html: bool = True, 
                    opener: str = "&lt;&lt;", closer: str = "&gt;&gt;", crToBr: bool = True) -> str:
    """
    Just to make code more readable as other areas call wordprocessor to build tags and do substitutions
    """
    return asm3.utils.substitute_tags(searchin, tags, escape_html, opener, closer, crToBr)

def substitute_template(dbo: Database, templateid: int, tags: Tags, imdata: bytes = None) -> bytes_or_str:
    """
    Reads the template specified by id "template" and substitutes
    according to the tags in "tags". Returns the built file.
    imdata is the preferred image for the record and since html uses
    URLs, only applies to ODT templates.
    Return value can be bytes (for ODT) or str (for HTML)
    """
    templatedata = asm3.template.get_document_template_content(dbo, templateid) # bytes
    templatename = asm3.template.get_document_template_name(dbo, templateid)
    if templatename.endswith(".html"):
        # Translate any user signature placeholder
        templatedata = asm3.utils.bytes2str(templatedata).replace("signature:user", "&lt;&lt;UserSignatureSrc&gt;&gt;")
        return asm3.utils.substitute_tags(templatedata, tags)
    elif templatename.endswith(".odt"):
        try:
            odt = asm3.utils.bytesio(templatedata)
            zf = zipfile.ZipFile(odt, "r")
            # Load the content.xml file and substitute the tags
            content = asm3.utils.bytes2str(zf.open("content.xml").read())
            content = substitute_tags(content, tags, crToBr=False)
            # Write the replacement file
            zo = asm3.utils.bytesio()
            zfo = zipfile.ZipFile(zo, "w", zipfile.ZIP_DEFLATED)
            for info in zf.infolist():
                if info.filename == "content.xml":
                    zfo.writestr("content.xml", asm3.utils.str2bytes(content))
                elif imdata is not None and (info.file_size == 2897 or info.file_size == 7701):
                    # If the image is the old placeholder.jpg or our default nopic.jpg, substitute for the record image
                    zfo.writestr(info.filename, imdata)
                else:
                    zfo.writestr(info.filename, zf.open(info.filename).read())
            zf.close()
            zfo.close()
            # Return the zip data
            return zo.getvalue()
        except Exception as zderr:
            raise asm3.utils.ASMError("Failed generating odt document: %s" % str(zderr))

def extract_mail_tokens(s: str) -> Dict[str, str]:
    """
    Extracts tokens for mail from document content s.
    Mail tokens are {{FROM x}}, {{SUBJECT x}}
    This process should be run on the output after generating a document so that all
    wordkeys in the mail tokens have been substituted.
    Returns a dictionary containing any found tokens and the body with the tokens removed.
    """
    if s is None: s = ""
    if asm3.utils.is_bytes(s): s = asm3.utils.bytes2str(s)
    results = asm3.utils.regex_multi(r"\{\{(.+?) (.+?)\}\}",  s)
    d = { "FROM": None, "CC": None, "BCC": None, "SUBJECT": None, "BODY": None }
    for k, v in results:
        d[k] = v
    s = asm3.utils.regex_delete(r"\{\{(.+?)\}\}", s)
    d["BODY"] = s
    return d

def generate_animal_doc(dbo: Database, templateid: int, animalid: int, username: str) -> bytes_or_str:
    """
    Generates an animal document from a template using animal keys and
    (if a currentowner is available) person keys
    templateid: The ID of the template
    animalid: The animal to generate for
    """
    a = asm3.animal.get_animal(dbo, animalid)
    if a is None: 
        raise asm3.utils.ASMValidationError("%d is not a valid animal ID" % animalid)
    imdata = None
    try:
        imdata = asm3.media.get_image_file_data(dbo, "animal", animalid)[1]
    except Exception as err:
        asm3.al.warn("could not load preferred image for animal %s: %s" % (animalid, err), "wordprocessor.generate_animal_doc", dbo)
    # We include donations here, so that we have RecentType, DueType, Last1, etc
    # But the call below to get_movement_donations will add the totals and allow
    # receipt/invoice type documents to work if there's an active movement
    tags = animal_tags(dbo, a, includeDonations=True)
    # Use the person info from the latest open movement for the animal
    # This will pick up future dated adoptions instead of fosterers (which are still currentowner)
    # as get_animal_movements returns them in descending order of movement date
    has_person_tags = False
    for m in asm3.movement.get_animal_movements(dbo, animalid):
        if m["MOVEMENTDATE"] is not None and m["RETURNDATE"] is None and m["OWNERID"] is not None and m["OWNERID"] != 0:
            has_person_tags = True
            tags = append_tags(tags, person_tags(dbo, asm3.person.get_person(dbo, m["OWNERID"])))
            tags = append_tags(tags, movement_tags(dbo, m))
            md = asm3.financial.get_movement_donations(dbo, m["ID"])
            if len(md) > 0: 
                tags = append_tags(tags, donation_tags(dbo, md))
            break
    # If we didn't have an open movement and there's a reserve, use that as the person
    if not has_person_tags and a["RESERVEDOWNERID"] is not None and a["RESERVEDOWNERID"] != 0:
        tags = append_tags(tags, person_tags(dbo, asm3.person.get_person(dbo, a["RESERVEDOWNERID"])))
        has_person_tags = True
    # If this is a non-shelter animal, use the owner
    if not has_person_tags and a["NONSHELTERANIMAL"] == 1 and a["ORIGINALOWNERID"] is not None and a["ORIGINALOWNERID"] != 0:
        tags = append_tags(tags, person_tags(dbo, asm3.person.get_person(dbo, a["ORIGINALOWNERID"])))
        has_person_tags = True
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags, imdata)

def generate_animalcontrol_doc(dbo: Database, templateid: int, acid: int, username: str) -> bytes_or_str:
    """
    Generates an animal control incident document from a template
    templateid: The ID of the template
    acid:     The incident id to generate for
    """
    ac = asm3.animalcontrol.get_animalcontrol(dbo, acid)
    if ac is None: raise asm3.utils.ASMValidationError("%d is not a valid incident ID" % acid)
    tags = animalcontrol_tags(dbo, ac)
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags)

def generate_clinic_doc(dbo: Database, templateid: int, appointmentid: int, username: str) -> bytes_or_str:
    """
    Generates a clinic document from a template
    templateid: The ID of the template
    appointmentid: The clinicappointment id to generate for
    """
    c = asm3.clinic.get_appointment(dbo, appointmentid)
    if c is None: raise asm3.utils.ASMValidationError("%d is not a valid clinic appointment ID" % appointmentid)
    tags = clinic_tags(dbo, c)
    tags = append_tags(tags, org_tags(dbo, username))
    a = asm3.animal.get_animal(dbo, c.ANIMALID)
    if a is not None:
        tags = append_tags(tags, animal_tags(dbo, a, includeAdditional=True, includeCosts=False, includeDiet=False, includeDonations=False, \
            includeFutureOwner=False, includeIsVaccinated=True, includeLogs=False, includeMedical=True))
    p = asm3.person.get_person(dbo, c.OWNERID)
    if p is not None:
        tags = append_tags(tags, person_tags(dbo, p))
    return substitute_template(dbo, templateid, tags)

def generate_person_doc(dbo: Database, templateid: int, personid: int, username: str) -> bytes_or_str:
    """
    Generates a person document from a template
    templateid: The ID of the template
    personid: The person to generate for
    """
    p = asm3.person.get_person(dbo, personid)
    im = asm3.media.get_image_file_data(dbo, "person", personid)[1]
    if p is None: raise asm3.utils.ASMValidationError("%d is not a valid person ID" % personid)
    tags = person_tags(dbo, p, includeImg=True, includeDonations=True, includeVouchers=True)
    tags = append_tags(tags, org_tags(dbo, username))
    m = dbo.first_row(asm3.movement.get_person_movements(dbo, personid))
    if m is not None:
        tags = append_tags(tags, movement_tags(dbo, m))
        if m.ANIMALID is not None and m.ANIMALID != 0:
            tags = append_tags(tags, animal_tags(dbo, asm3.animal.get_animal(dbo, m.ANIMALID)))
    return substitute_template(dbo, templateid, tags, im)

def generate_donation_doc(dbo: Database, templateid: int, donationids: List[int], username: str) -> bytes_or_str:
    """
    Generates a donation document from a template
    templateid: The ID of the template
    donationids: A list of ids to generate for
    """
    dons = asm3.financial.get_donations_by_ids(dbo, donationids)
    if len(dons) == 0: 
        raise asm3.utils.ASMValidationError("%s does not contain any valid donation IDs" % donationids)
    d = dons[0]
    tags = person_tags(dbo, asm3.person.get_person(dbo, d.OWNERID))
    if d.ANIMALID is not None and d.ANIMALID != 0:
        tags = append_tags(tags, animal_tags(dbo, asm3.animal.get_animal(dbo, d["ANIMALID"]), includeDonations=False))
    if d.MOVEMENTID is not None and d.MOVEMENTID != 0:
        tags = append_tags(tags, movement_tags(dbo, asm3.movement.get_movement(dbo, d.MOVEMENTID)))
    tags = append_tags(tags, donation_tags(dbo, dons))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags)

def generate_foundanimal_doc(dbo: Database, templateid: int, faid: int, username: str) -> bytes_or_str:
    """
    Generates a found animal document from a template
    templateid: The ID of the template
    faid: The found animal to generate for
    """
    a = asm3.lostfound.get_foundanimal(dbo, faid)
    if a is None:
        raise asm3.utils.ASMValidationError("%d is not a valid found animal ID" % faid)
    tags = person_tags(dbo, asm3.person.get_person(dbo, a.OWNERID))
    tags = append_tags(tags, foundanimal_tags(dbo, a))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags)

def generate_lostanimal_doc(dbo: Database, templateid: int, laid: int, username: str) -> bytes_or_str:
    """
    Generates a found animal document from a template
    templateid: The ID of the template
    laid: The lost animal to generate for
    """
    a = asm3.lostfound.get_lostanimal(dbo, laid)
    if a is None:
        raise asm3.utils.ASMValidationError("%d is not a valid lost animal ID" % laid)
    tags = person_tags(dbo, asm3.person.get_person(dbo, a.OWNERID))
    tags = append_tags(tags, lostanimal_tags(dbo, a))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags)

def generate_licence_doc(dbo: Database, templateid: int, licenceid: int, username: str) -> bytes_or_str:
    """
    Generates a licence document from a template
    templateid: The ID of the template
    licenceid: The licence to generate for
    """
    l = asm3.financial.get_licence(dbo, licenceid)
    if l is None:
        raise asm3.utils.ASMValidationError("%d is not a valid licence ID" % licenceid)
    tags = person_tags(dbo, asm3.person.get_person(dbo, l.OWNERID))
    if l.ANIMALID is not None and l.ANIMALID != 0:
        tags = append_tags(tags, animal_tags(dbo, asm3.animal.get_animal(dbo, l.ANIMALID), includeLicence=False))
    tags = append_tags(tags, licence_tags(dbo, l))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags)

def generate_movement_doc(dbo: Database, templateid: int, movementid: int, username: str) -> bytes_or_str:
    """
    Generates a movement document from a template
    templateid: The ID of the template
    movementid: The movement to generate for
    """
    m = asm3.movement.get_movement(dbo, movementid)
    tags = {}
    if m is None:
        raise asm3.utils.ASMValidationError("%d is not a valid movement ID" % movementid)
    if m.ANIMALID is not None and m.ANIMALID != 0:
        tags = animal_tags(dbo, asm3.animal.get_animal(dbo, m.ANIMALID))
    if m.OWNERID is not None and m.OWNERID != 0:
        tags = append_tags(tags, person_tags(dbo, asm3.person.get_person(dbo, m.OWNERID)))
    tags = append_tags(tags, movement_tags(dbo, m))
    tags = append_tags(tags, donation_tags(dbo, asm3.financial.get_movement_donations(dbo, movementid)))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags)

def generate_transport_doc(dbo: Database, templateid: int, transportids: int, username: str) -> bytes_or_str:
    """
    Generates a transport document from a template
    templateid: The ID of the template
    transportids: A list of ids to generate for
    """
    tt = asm3.movement.get_transports_by_ids(dbo, transportids)
    if len(tt) == 0: 
        raise asm3.utils.ASMValidationError("%s does not contain any valid transport IDs" % transportids)
    tags = transport_tags(dbo, tt)
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags)

def generate_voucher_doc(dbo: Database, templateid: int, voucherid: int, username: str) -> bytes_or_str:
    """
    Generates a voucher document from a template
    templateid: The ID of the template
    voucherid: The ID of the voucher to generate for
    """
    v = asm3.financial.get_voucher(dbo, voucherid)
    if v is None:
        raise asm3.utils.ASMValidationError("%d is not a valid voucher ID" % voucherid)
    tags = person_tags(dbo, asm3.person.get_person(dbo, v.OWNERID))
    if v.ANIMALID is not None and v.ANIMALID != 0:
        tags = append_tags(tags, animal_tags(dbo, asm3.animal.get_animal(dbo, v.ANIMALID)))
    tags = append_tags(tags, voucher_tags(dbo, v))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags)

def generate_waitinglist_doc(dbo: Database, templateid: int, wlid: int, username: str) -> bytes_or_str:
    """
    Generates a waiting list document from a template
    templateid: The ID of the template
    wlid: The waiting list to generate for
    """
    a = asm3.waitinglist.get_waitinglist_by_id(dbo, wlid)
    if a is None:
        raise asm3.utils.ASMValidationError("%d is not a valid waiting list ID" % wlid)
    tags = person_tags(dbo, asm3.person.get_person(dbo, a.OWNERID))
    tags = append_tags(tags, waitinglist_tags(dbo, a))
    tags = append_tags(tags, org_tags(dbo, username))
    return substitute_template(dbo, templateid, tags)

