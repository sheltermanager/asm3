
import asm3.al
import asm3.animal
import asm3.animalcontrol
import asm3.cachedisk
import asm3.configuration
import asm3.geo
import asm3.i18n
import asm3.html
import asm3.lookups
import asm3.lostfound
import asm3.media
import asm3.movement
import asm3.person
import asm3.publishers.base
import asm3.template
import asm3.users
import asm3.utils
import asm3.waitinglist
from asm3.sitedefs import BASE_URL, SERVICE_URL
from asm3.sitedefs import ASMSELECT_CSS, ASMSELECT_JS, JQUERY_JS, JQUERY_UI_JS, JQUERY_UI_CSS, SIGNATURE_JS, TIMEPICKER_CSS, TIMEPICKER_JS
from asm3.typehints import Any, datetime, Database, List, PostedData, ResultRow, Results, Tuple

import web062 as web

FIELDTYPE_YESNO = 0
FIELDTYPE_TEXT = 1
FIELDTYPE_NOTES = 2
FIELDTYPE_LOOKUP = 3
FIELDTYPE_SHELTERANIMAL = 4
FIELDTYPE_ADOPTABLEANIMAL = 5
FIELDTYPE_COLOUR = 6
FIELDTYPE_BREED = 7
FIELDTYPE_SPECIES = 8
FIELDTYPE_RAWMARKUP = 9
FIELDTYPE_DATE = 10
FIELDTYPE_CHECKBOX = 11
FIELDTYPE_RADIOGROUP = 12
FIELDTYPE_SIGNATURE = 13
FIELDTYPE_LOOKUP_MULTI = 14
FIELDTYPE_GDPR_CONTACT_OPTIN = 15
FIELDTYPE_TIME = 16
FIELDTYPE_IMAGE = 17
FIELDTYPE_CHECKBOXGROUP = 18
FIELDTYPE_EMAIL = 19
FIELDTYPE_NUMBER = 20

# Types as used in JSON representations
FIELDTYPE_MAP = {
    "YESNO": 0,
    "TEXT": 1,
    "NOTES": 2,
    "LOOKUP": 3,
    "SHELTERANIMAL": 4,
    "ADOPTABLEANIMAL": 5,
    "COLOUR": 6,
    "BREED": 7,
    "SPECIES": 8,
    "RAWMARKUP": 9,
    "DATE": 10,
    "CHECKBOX": 11,
    "RADIOGROUP": 12,
    "SIGNATURE": 13,
    "LOOKUP_MULTI": 14,
    "GDPR_CONTACT_OPTIN": 15,
    "TIME": 16,
    "IMAGE": 17,
    "CHECKBOXGROUP": 18
}

FIELDTYPE_MAP_REVERSE = {v: k for k, v in FIELDTYPE_MAP.items()}

AP_NO = 0
AP_ATTACHANIMAL = 1
AP_CREATEANIMAL = 2
AP_CREATEPERSON = 3
AP_CREATELOSTANIMAL = 4
AP_CREATEFOUNDANIMAL = 5
AP_CREATEINCIDENT = 6
AP_CREATETRANSPORT = 7
AP_CREATEWAITINGLIST = 8
AP_ATTACHANIMAL_CREATEPERSON = 9 
AP_CREATEANIMAL_BROUGHTIN = 10
AP_CREATEANIMAL_NONSHELTER = 11

# The name of an extra text field inserted to trap spambots
SPAMBOT_TXT = 'a_emailaddress'

# Fields that are added to forms by the system and are not user enterable
SYSTEM_FIELDS = [ "useragent", "ipaddress", "retainfor", "formreceived", "mergeperson", "processed" ]

# Online field names that we recognise and will attempt to map to
# known fields when importing from submitted forms
FORM_FIELDS = [
    "emailsubmissionto",
    "title", "initials", "title2", "initials2", 
    "firstname", "forenames", "surname", "lastname", "address",
    "firstname2", "forenames2", "lastname2", "surname2",
    "town", "city", "county", "state", "postcode", "zipcode", "country", "hometelephone", 
    "worktelephone", "worktelephone2", "mobiletelephone", "mobiletelephone2", "celltelephone", "celltelephone2", 
    "emailaddress", "emailaddress2", "idnumber", "idnumber2", "dateofbirth", "dateofbirth2",
    "excludefrombulkemail", "gdprcontactoptin",
    "description", "reason", "size", "species", "breed", "agegroup", "color", "colour", 
    "datelost", "datefound", "arealost", "areafound", "areapostcode", "areazipcode", "microchip",
    "animalname", "animalname2", "animalname3", "reserveanimalname", "reserveanimalname2", "reserveanimalname3",
    "code", "microchip", "age", "dateofbirth", "entryreason", "entrytype", "markings", "comments", "hiddencomments", 
    "type", "breed1", "breed2", "color", "sex", "neutered", "weight", 
    "callnotes", "dispatchaddress", "dispatchcity", "dispatchstate", "dispatchzipcode", "transporttype", 
    "pickupaddress", "pickuptown", "pickupcity", "pickupcounty", "pickupstate", "pickuppostcode", "pickupzipcode", "pickupcountry", "pickupdate", "pickuptime",
    "dropoffaddress", "dropofftown", "dropoffcity", "dropoffcounty", "dropoffstate", "dropoffpostcode", "dropoffzipcode", "dropoffcountry", "dropoffdate", "dropofftime"
]

AUTOCOMPLETE_MAP = {
    "title":            "honorific",
    "firstname":        "given-name",
    "forenames":        "given-name",
    "lastname":         "family-name",
    "surname":          "family-name",
    "address":          "street-address",
    "city":             "address-level2",
    "town":             "address-level2",
    "state":            "address-level3",
    "county":           "address-level3",
    "country":          "country-name",
    "zipcode":          "postal-code",
    "postcode":         "postal-code",
    "mobiletelephone":  "tel",
    "celltelephone":    "tel",
    "emailaddress":     "email"
}

def get_collationid(dbo: Database) -> int:
    """ Returns the next collation ID value for online forms. """
    return dbo.get_id_cache_pk("collationid", "SELECT MAX(CollationID) FROM onlineformincoming")

def get_onlineform(dbo: Database, formid: int) -> ResultRow:
    """ Returns the online form with ID formid """
    return dbo.first_row(dbo.query("SELECT * FROM onlineform WHERE ID = ?", [formid]))

def get_onlineforms(dbo: Database) -> Results:
    """ Return all online forms """
    return dbo.query("SELECT *, (SELECT COUNT(*) FROM onlineformfield WHERE OnlineFormID = onlineform.ID) AS NumberOfFields FROM onlineform ORDER BY Name")

def get_onlineform_html(dbo: Database, formid: int, completedocument: bool = True) -> str:
    """ Get the selected online form as HTML """
    h = []
    l = dbo.locale
    form = get_onlineform(dbo, formid)
    if form is None: raise asm3.utils.ASMValidationError("Online form %s does not exist" % formid)
    formfields = get_onlineformfields(dbo, formid)
    if completedocument:
        header = get_onlineform_header(dbo)
        # Calculate the date format and add our extra script
        # references into the header block
        df = asm3.i18n.get_display_date_format(l)
        df = df.replace("%Y", "yy").replace("%m", "mm").replace("%d", "dd")
        extra = "<script>\nDATE_FORMAT = '%s';\n</script>\n" % df
        extra += "<base href=\"%s\" />\n" % BASE_URL
        extra += asm3.html.css_tag(JQUERY_UI_CSS.replace("%(theme)s", "asm")) + \
            asm3.html.css_tag(ASMSELECT_CSS) + \
            asm3.html.css_tag(TIMEPICKER_CSS) + \
            asm3.html.script_tag(JQUERY_JS) + \
            asm3.html.script_tag(JQUERY_UI_JS) + \
            asm3.html.script_tag(SIGNATURE_JS) + \
            asm3.html.script_tag(ASMSELECT_JS) + \
            asm3.html.script_tag(TIMEPICKER_JS) + \
            asm3.html.asm_script_tag("onlineform_extra.js") + \
            "</head>"
        header = header.replace("</head>", extra)
        h.append(header.replace("$$TITLE$$", form.NAME))
        h.append('<h2 class="asm-onlineform-title">%s</h2>' % form.NAME)
        if form.DESCRIPTION is not None and form.DESCRIPTION != "":
            h.append('<p class="asm-onlineform-description">%s</p>' % form.DESCRIPTION)
        h.append(asm3.utils.nulltostr(form.HEADER))
    h.append('<form action="%s/service" method="post" accept-charset="utf-8">' % BASE_URL)
    h.append('<input type="hidden" name="method" value="online_form_post" />')
    h.append('<input type="hidden" name="account" value="%s" />' % dbo.alias)
    h.append('<input type="hidden" name="redirect" value="%s" />' % form.REDIRECTURLAFTERPOST)
    h.append('<input type="hidden" name="retainfor" value="%s" />' % form.RETAINFOR)
    h.append('<input type="hidden" name="flags" value="%s" />' % form.SETOWNERFLAGS)
    h.append('<input type="hidden" name="formname" value="%s" />' % asm3.html.escape(form.NAME))
    h.append('<table class="asm-onlineform-table">')
    for f in formfields:
        fname = "%s_%s" % (f.FIELDNAME, f.ID)
        cname = asm3.html.escape(fname)
        fid = "f%d" % f.ID
        visibleif = ""
        if f.VISIBLEIF:
            visibleif = 'data-visibleif="%s"' % f.VISIBLEIF
        h.append('<tr class="asm-onlineform-tr" %s>' % visibleif)
        required = ""
        requiredtext = ""
        requiredspan = ""
        autocomplete = ""
        if f.FIELDNAME in AUTOCOMPLETE_MAP:
            autocomplete = "autocomplete=\"%s\"" % AUTOCOMPLETE_MAP[f.FIELDNAME]
        if f.MANDATORY == 1: 
            required = "required=\"required\""
            requiredtext = "required=\"required\" pattern=\".*\\S+.*\""
            requiredspan = '<span class="asm-onlineform-required" style="color: #ff0000;">*</span>'
        if f.FIELDTYPE == FIELDTYPE_RAWMARKUP:
            h.append('<td class="asm-onlineform-td asm-onlineform-raw" colspan="2">')
        elif f.FIELDTYPE == FIELDTYPE_CHECKBOX:
            h.append('<td class="asm-onlineform-td">%s</td><td class="asm-onlineform-td">' % requiredspan)
        else:
            # Add label and cell wrapper if it's not raw markup or a checkbox
            h.append('<td class="asm-onlineform-td">')
            h.append('<label for="%s">%s %s</label>' % ( fid, f.LABEL, requiredspan ))
            if f.TOOLTIP: h.append('<span class="asm-onlineform-tooltip">%s</span>' % f.TOOLTIP)
            h.append('</td>')
            h.append('<td class="asm-onlineform-td">')
        if f.FIELDTYPE == FIELDTYPE_YESNO:
            h.append('<select class="asm-onlineform-yesno" id="%s" name="%s" %s>' \
                '<option value=""></option><option>%s</option><option>%s</option></select>' % \
                ( fid, cname, asm3.utils.iif(required != "", required, ""), asm3.i18n._("No", l), asm3.i18n._("Yes", l)))
        elif f.FIELDTYPE == FIELDTYPE_CHECKBOX:
            h.append('<input class="asm-onlineform-check" type="checkbox" id="%s" name="%s" %s /> ' \
                '<label class="asm-onlineform-checkboxlabel" for="%s">%s</label>' % \
                (fid, cname, required, fid, f.LABEL))
        elif f.FIELDTYPE == FIELDTYPE_TEXT:
            h.append('<input class="asm-onlineform-text" type="text" id="%s" name="%s" %s %s />' % ( fid, cname, autocomplete, requiredtext))
        elif f.FIELDTYPE == FIELDTYPE_NUMBER:
            h.append('<input class="asm-onlineform-number" type="text" id="%s" name="%s" %s %s />' % ( fid, cname, autocomplete, requiredtext))
        elif f.FIELDTYPE == FIELDTYPE_EMAIL:
            h.append('<input class="asm-onlineform-email" type="email" id="%s" name="%s" %s %s />' % ( fid, cname, autocomplete, requiredtext))
        elif f.FIELDTYPE == FIELDTYPE_DATE:
            h.append('<input class="asm-onlineform-date" type="text" id="%s" name="%s" %s />' % ( fid, cname, requiredtext))
        elif f.FIELDTYPE == FIELDTYPE_TIME:
            h.append('<input class="asm-onlineform-time" type="text" id="%s" name="%s" %s />' % ( fid, cname, requiredtext))
        elif f.FIELDTYPE == FIELDTYPE_NOTES:
            h.append('<textarea class="asm-onlineform-notes" id="%s" name="%s" %s></textarea>' % ( fid, cname, requiredtext))
        elif f.FIELDTYPE == FIELDTYPE_LOOKUP:
            h.append('<select class="asm-onlineform-lookup" id="%s" name="%s" %s>' % ( fid, cname, required))
            for lv in asm3.utils.nulltostr(f["LOOKUPS"]).split("|"):
                h.append('<option>%s</option>' % lv)
            h.append('</select>')
        elif f.FIELDTYPE == FIELDTYPE_LOOKUP_MULTI:
            h.append('<input type="hidden" name="%s" value="" />' % cname)
            h.append('<select class="asm-onlineform-lookupmulti" multiple="multiple" data-name="%s" data-required="%s" title="" >' % ( cname, asm3.utils.iif(required != "", "required", "")))
            for lv in asm3.utils.nulltostr(f.LOOKUPS).split("|"):
                h.append('<option>%s</option>' % lv)
            h.append('</select>')
        elif f.FIELDTYPE == FIELDTYPE_RADIOGROUP:
            h.append('<div id="%s" class="asm-onlineform-radiogroup" style="display: inline-block">' % (fid))
            for i, lv in enumerate(asm3.utils.nulltostr(f.LOOKUPS).split("|")):
                rid = "%s_%s" % (fid, i)
                h.append('<input type="radio" class="asm-onlineform-radio" id="%s" name="%s" value="%s" %s /> ' \
                    '<label class="asm-onlineform-checkboxlabel" for="%s">%s</label><br />' % (rid, cname, lv, required, rid, lv))
            h.append('</div>')
        elif f.FIELDTYPE == FIELDTYPE_CHECKBOXGROUP:
            h.append('<input type="hidden" name="%s" value="" />' % cname)
            h.append('<div id="%s" class="asm-onlineform-checkgroup" data-name="%s" data-required="%s" style="display: inline-block">' % (fid, cname, asm3.utils.iif(required != "", "required", "")))
            for i, lv in enumerate(asm3.utils.nulltostr(f.LOOKUPS).split("|")):
                rid = "%s_%s" % (fid, i)
                rname = "%s%s_" % (f.FIELDNAME, i)
                h.append('<input type="checkbox" id="%s" data="%s" name="%s"/> ' \
                    '<label class="asm-onlineform-checkboxlabel" for="%s">%s</label><br />' % (rid, lv, rname, rid, lv))
            h.append('</div>')
        elif f.FIELDTYPE == FIELDTYPE_SHELTERANIMAL:
            h.append('<select class="asm-onlineform-shelteranimal" id="%s" name="%s" %s>' % ( fid, cname, required))
            h.append('<option value=""></option>')
            rs = asm3.animal.get_animals_on_shelter_namecode(dbo)
            rs = sorted(rs, key=lambda k: k["ANIMALNAME"])
            for a in rs:
                if f.SPECIESID and f.SPECIESID > 0 and a.SPECIESID != f.SPECIESID: continue
                h.append(f'<option data-id="{a.ID}" value="{asm3.html.escape(a.ANIMALNAME)}::{a.SHELTERCODE}">{a.ANIMALNAME} ({a.SPECIESNAME} - {a.SHELTERCODE})</option>')
            h.append('</select>')
        elif f.FIELDTYPE == FIELDTYPE_ADOPTABLEANIMAL:
            h.append('<select class="asm-onlineform-adoptableanimal" id="%s" name="%s" %s>' % ( fid, cname, required))
            h.append('<option data-id="" value=""></option>')
            pc = asm3.publishers.base.PublishCriteria(asm3.configuration.publisher_presets(dbo))
            rs = asm3.publishers.base.get_animal_data(dbo, pc, include_additional_fields = True)
            rs = sorted(rs, key=lambda k: k["ANIMALNAME"])
            for a in rs:
                if f.SPECIESID and f.SPECIESID > 0 and a.SPECIESID != f.SPECIESID: continue
                h.append(f'<option data-id="{a.ID}" value="{asm3.html.escape(a.ANIMALNAME)}::{a.SHELTERCODE}">{a.ANIMALNAME} ({a.SPECIESNAME} - {a.SHELTERCODE})</option>')
            h.append('</select>')
            h.append('<img class="asm-onlineform-thumbnail" ' \
                ' style="vertical-align: middle; height: 150px; width: 150px; object-fit: contain; display: block; display: none">')
        elif f.FIELDTYPE == FIELDTYPE_GDPR_CONTACT_OPTIN:
            h.append('<input type="hidden" name="%s" value="" />' % cname)
            h.append('<select class="asm-onlineform-gdprcontactoptin asm-onlineform-lookupmulti" multiple="multiple" id="%s" data-name="%s" data-required="%s" title="">' % ( fid, cname, asm3.utils.iif(required != "", "required", "")))
            h.append('<option value="declined">%s</option>' % asm3.i18n._("Declined", l))
            h.append('<option value="email">%s</option>' % asm3.i18n._("Email", l))
            h.append('<option value="post">%s</option>' % asm3.i18n._("Post", l))
            h.append('<option value="sms">%s</option>' % asm3.i18n._("SMS", l))
            h.append('<option value="phone">%s</option>' % asm3.i18n._("Phone", l))
            h.append('</select>')
        elif f.FIELDTYPE == FIELDTYPE_COLOUR:
            h.append('<select class="asm-onlineform-colour" id="%s" name="%s" %s>' % ( fid, cname, required))
            h.append('<option value=""></option>')
            for l in asm3.lookups.get_basecolours(dbo):
                if l.ISRETIRED != 1:
                    h.append('<option>%s</option>' % l.BASECOLOUR)
            h.append('</select>')
        elif f.FIELDTYPE == FIELDTYPE_BREED:
            h.append('<select class="asm-onlineform-breed" id="%s" name="%s" %s>' % ( fid, cname, required))
            h.append('<option value=""></option>')
            for l in asm3.lookups.get_breeds(dbo):
                if l.ISRETIRED != 1:
                    h.append('<option>%s</option>' % l.BREEDNAME)
            h.append('</select>')
        elif f.FIELDTYPE == FIELDTYPE_SPECIES:
            h.append('<select class="asm-onlineform-species" id="%s" name="%s" %s>' % ( fid, cname, required))
            h.append('<option value=""></option>')
            for l in asm3.lookups.get_species(dbo):
                if l.ISRETIRED != 1:
                    h.append('<option>%s</option>' % l.SPECIESNAME)
            h.append('</select>')
        elif f.FIELDTYPE == FIELDTYPE_RAWMARKUP:
            h.append('<input type="hidden" name="%s" value="raw" />' % cname)
            h.append(asm3.utils.nulltostr(f.TOOLTIP))
        elif f.FIELDTYPE == FIELDTYPE_SIGNATURE:
            h.append('<input type="hidden" name="%s" value="" />' % cname)
            h.append('<div class="asm-onlineform-signature" data-name="%s" data-required="%s"></div>' % ( cname, asm3.utils.iif(required != "", "required", "") ))
            h.append('<br/><button type="button" class="asm-onlineform-signature-clear" data-clear="%s">%s</button>' % ( cname, asm3.i18n._("Clear", l) ))
        elif f.FIELDTYPE == FIELDTYPE_IMAGE:
            h.append('<input type="hidden" name="%s" value="" />' % cname)
            h.append('<input class="asm-onlineform-image" type="file" id="%s" data-name="%s" data-required="%s" />' % (fid, cname, asm3.utils.iif(required != "", "required", "")))
        h.append('</td>')
        h.append('</tr>')
    h.append('</table>')
    h.append('<style>')
    h.append('.scb { display: none; }')
    h.append('</style>')
    h.append(f'<p class="scb"><label for="{SPAMBOT_TXT}"></label><input type="text" id="{SPAMBOT_TXT}" name="{SPAMBOT_TXT}" autocomplete="off" /></p>')
    h.append('<p style="text-align: center"><input type="submit" value="%s" /></p>' % asm3.i18n._("Submit", l))
    h.append('</form>')
    if completedocument:
        h.append(asm3.utils.nulltostr(form.FOOTER))
        footer = get_onlineform_footer(dbo)
        h.append(footer.replace("$$TITLE$$", form.NAME))
    return "\n".join(h)

def get_onlineform_json(dbo: Database, formid: int) -> str:
    """
    Get the selected online form as a JSON document
    """
    form = get_onlineform(dbo, formid)
    if form is None: raise asm3.utils.ASMValidationError("Online form %d does not exist")
    formfields = get_onlineformfields(dbo, formid)
    fd = { "name": form.NAME, "description": form.DESCRIPTION, "header": form.HEADER, "footer": form.FOOTER }
    ff = []
    for f in formfields:
        ff.append({ "name": f.FIELDNAME, "label": f.LABEL, "type": FIELDTYPE_MAP_REVERSE[f.FIELDTYPE],
            "mandatory": asm3.utils.iif(f.MANDATORY == 1, True, False), "index": f.DISPLAYINDEX,
            "visibleif": f.VISIBLEIF, "lookups": f.LOOKUPS, "tooltip": f.TOOLTIP})
    fd["fields"] = ff
    return asm3.utils.json(fd, True)

def import_onlineform_json(dbo: Database, j: str) -> int:
    """
    Imports an online form from a JSON document
    """
    fd = asm3.utils.json_parse(j)
    data = {
        "name": fd["name"],
        "description": fd["description"],
        "header": fd["header"],
        "footer": fd["footer"]
    }
    fid = insert_onlineform_from_form(dbo, "import", asm3.utils.PostedData(data, dbo.locale))
    for f in fd["fields"]:
        data = { "formid": str(fid),
            "fieldname": f["name"],
            "fieldtype": str(FIELDTYPE_MAP[f["type"]]),
            "label": f["label"],
            "displayindex": f["index"],
            "mandatory": asm3.utils.iif(f["mandatory"], "1", "0"),
            "visibleif": "visibleif" in f and f["visibleif"] or "",
            "lookups": f["lookups"],
            "tooltip": f["tooltip"]
        }
        insert_onlineformfield_from_form(dbo, "import", asm3.utils.PostedData(data, dbo.locale))
    return fid

def import_onlineform_html(dbo: Database, h: str) -> int:
    """
    Imports an online form from an HTML document
    """
    p = asm3.utils.FormHTMLParser()
    p.feed(h)
    data = {
        "name": p.title,
        "description": "",
        "header": "",
        "footer": ""
    }
    fid = insert_onlineform_from_form(dbo, "import", asm3.utils.PostedData(data, dbo.locale))
    for i, control in enumerate(p.controls):
        name = ""
        label = ""
        tooltip = ""
        fieldtype = "TEXT"
        tag = "input"
        for k, v in control.items():
            if k == "name": 
                name = v
                label = v
            if k == "tag": tag = v
            if k == "title": tooltip = v
        if tag == "select": fieldtype = "LOOKUP"
        if tag == "textarea": fieldtype = "NOTES"
        # without a name, we have nothing
        if name == "": continue
        data = { "formid": str(fid),
            "fieldname": name,
            "fieldtype": str(FIELDTYPE_MAP[fieldtype]),
            "label": label,
            "displayindex": i * 10,
            "mandatory": "0",
            "lookups": "",
            "tooltip": tooltip
        }
        insert_onlineformfield_from_form(dbo, "import", asm3.utils.PostedData(data, dbo.locale))
    return fid

def get_onlineform_header(dbo: Database) -> str:
    header = asm3.template.get_html_template(dbo, "onlineform")[0]
    if header == "": header = "<!DOCTYPE html>\n" \
        "<html>\n" \
        "<head>\n" \
        "<title>$$TITLE$$</title>\n" \
        "<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />\n" \
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, minimum-scale=1.0\">\n" \
        "<link href='//fonts.googleapis.com/css?family=Roboto' rel='stylesheet' type='text/css'>\n" \
        "<style>\n" \
        "input:focus, textarea:focus, select:focus { box-shadow: 0 0 5px #3a87cd; border: 1px solid #3a87cd; }\n" \
        ".asm-onlineform-title, .asm-onlineform-description { text-align: center; }\n" \
        ".asm-onlineform-tooltip { display: block; font-size: 75%; overflow-wrap: anywhere; hyphens: auto; }\n" \
        "input, textarea, select { border: 1px solid #aaa; }\n" \
        "input[type='submit'] { padding: 10px; cursor: pointer; }\n" \
        "/* phones and smaller devices */\n" \
        "@media screen and (max-device-width:480px) {\n" \
        "    body { font-family: sans-serif; }\n" \
        "    * { font-size: 110%; }\n" \
        "    h2 { font-size: 200%; }\n" \
        "    .asm-onlineform-table td { display: block; width: 100%; margin-bottom: 20px; }\n" \
        "    label, input[type='file'], input[type='text'], input[type='email'], select, textarea { width: 97%; padding: 5px; }\n" \
        "    label { overflow-wrap: anywhere; hypens: auto; }\n" \
        "    input[type='checkbox'] { float: left; width: auto; position: relative; top: 10px }\n" \
        "    input[type='submit'] { background-color: #2CBBBB; border: 1px solid #27A0A0; color: #fff; padding: 20px; }\n" \
        "}\n" \
        "/* full size computers and tablets */\n" \
        "@media screen and (min-device-width:481px) {\n" \
        "	body { background-color: #aaa; font-family: 'Roboto', sans-serif; }\n" \
        "   #page { width: 70%; margin-left: 15%; " \
        "       background-color: #fff; box-shadow: 2px 2px 4px #888; " \
        "       padding-top: 20px; padding-bottom: 20px; }\n" \
        "    .asm-onlineform-td:first-child { max-width: 400px; }\n" \
        "    .asm-onlineform-checkboxlabel { max-width: 400px; display: inline-block; }\n" \
        "    .asm-onlineform-table { margin-left: auto; margin-right: auto }\n" \
        "    textarea { width: 300px; height: 150px; }\n" \
        "    input[type='text'], select { width: 300px; }\n" \
        "    td, input, textarea, select, label { font-size: 110%; }\n" \
        "    td { padding-bottom: 10px; }\n" \
        "}\n" \
       "</style>\n" \
       "<script>\n" \
       "function logohide() { document.getElementById('logo').style.display = 'none'; }\n" \
       "</script>\n" \
       "</head>\n" \
       "<body>\n" \
       "    <div id=\"page\">\n" \
       f"        <p style=\"text-align: center\"><img id=\"logo\" onerror=\"javascript:logohide()\" style=\"height: 150px\" src=\"{SERVICE_URL}?account={dbo.database}&method=dbfs_image&title=splash.jpg\" /></p>" 
    return header

def get_onlineform_footer(dbo: Database) -> str:
    footer = asm3.template.get_html_template(dbo, "onlineform")[2]
    if footer == "": footer = "</div>\n</body>\n</html>"
    return footer

def set_onlineform_headerfooter(dbo: Database, head: str, foot: str) -> None:
    asm3.template.update_html_template(dbo, "", "onlineform", head, "", foot, True)

def get_onlineform_name(dbo: Database, formid: int) -> str:
    """ Returns the name of a form """
    return dbo.query_string("SELECT Name FROM onlineform WHERE ID = ?", [formid])

def get_onlineformfields(dbo: Database, formid: int) -> Results:
    """ Return all fields for a form """
    return dbo.query("SELECT * FROM onlineformfield WHERE OnlineFormID = ? ORDER BY DisplayIndex", [formid])

def get_onlineformincoming_formname(dbo: Database, collationid: int) -> str:
    """ Given a collationid, return the form's name """
    return dbo.query_string("SELECT FormName FROM onlineformincoming WHERE CollationID=?", [collationid])

def get_onlineformincoming_formheader(dbo: Database, collationid: int) -> str:
    """
    Given a collation id for an incoming form, try and find the
    original onlineform header.
    """
    return dbo.query_string("SELECT o.Header FROM onlineform o " \
        "INNER JOIN onlineformincoming oi ON oi.FormName = o.Name " \
        "WHERE oi.CollationID = ?", [collationid])

def get_onlineformincoming_formfooter(dbo: Database, collationid: int) -> str:
    """
    Given a collation id for an incoming form, try and find the
    original onlineform footer.
    """
    return dbo.query_string("SELECT o.Footer FROM onlineform o " \
        "INNER JOIN onlineformincoming oi ON oi.FormName = o.Name " \
        "WHERE oi.CollationID = ?", [collationid])

def get_onlineformincoming_headers(dbo: Database) -> Results:
    """ Returns all incoming form posts """
    return dbo.query("SELECT f.CollationID, f.FormName, f.PostedDate, f.Host, f.Preview, " \
        "(SELECT MAX(Value) FROM onlineformincoming WHERE CollationID=f.CollationID AND FieldName='mergeperson') AS MergePerson, " \
        "CASE WHEN EXISTS(SELECT Value FROM onlineformincoming WHERE CollationID=f.CollationID AND FieldName='processed') THEN 1 ELSE 0 END AS Processed " \
        "FROM onlineformincoming f " \
        "GROUP BY f.CollationID, f.FormName, f.PostedDate, f.Host, f.Preview " \
        "ORDER BY f.PostedDate")

def get_onlineformincoming_detail(dbo: Database, collationid: int) -> Results:
    """ Returns the detail lines for an incoming post """
    return dbo.query("SELECT * FROM onlineformincoming WHERE CollationID = ? ORDER BY DisplayIndex", [collationid])

def get_onlineformincoming_html(dbo: Database, collationid: int, 
                                include_raw: bool = True, include_images: bool = True, include_system: bool = True) -> str:
    """ Returns a partial HTML document of the incoming form data fields """
    h = []
    h.append('<table width="100%">')
    for f in get_onlineformincoming_detail(dbo, collationid):
        label = f.LABEL
        if label is None or label == "": label = f.FIELDNAME
        v = f.VALUE
        if f.FIELDNAME in SYSTEM_FIELDS and not include_system: continue
        if v.startswith("RAW::") and not include_raw: continue
        if v.startswith("data:") and not include_images: continue
        if v.startswith("RAW::"): 
            h.append('<tr>')
            h.append('<td colspan="2">%s</td>' % v[5:])
            h.append('</tr>')
        elif v.startswith("data:"):
            h.append('<tr>')
            h.append('<td>%s</td>' % label )
            h.append('<td><img src="%s" border="0" /></td>' % v)
            h.append('</tr>')
        elif f.FIELDNAME == "useragent":
            # Some user agent strings can be huge and without wrappable characters,
            # so they throw off the formatting of the rest of the form when viewing
            # in the dialog or printing.
            h.append('<tr>')
            h.append('<td>%s</td>' % label )
            h.append('<td><div style="word-wrap: anywhere; max-width: 400px">%s</div></td>' % v)
            h.append('</tr>')
        else:
            h.append('<tr>')
            h.append('<td>%s</td>' % label )
            h.append('<td>%s</td>' % v)
            h.append('</tr>')
    h.append('</table>')
    return "\n".join(h)

def get_onlineformincoming_plain(dbo: Database, collationid: int) -> str:
    """ Returns a plain text fragment of the incoming form data """
    h = []
    for f in get_onlineformincoming_detail(dbo, collationid):
        if f.VALUE.startswith("RAW::") or f.VALUE.startswith("data:"): continue
        label = f.LABEL
        if label is None or label == "": label = f.FIELDNAME
        h.append("%s: %s\n" % (label, f.VALUE))
    return "\n".join(h)

def get_onlineformincoming_csv(dbo: Database, ids: List[int]) -> str:
    """
    Returns all the forms with collationid in ids as CSV data.
    The form fields are laid out as columns with each form as a row.
    """
    rows = []
    cols = []
    buildcols = True # build column list from the first collation id
    for collationid in ids:
        row = {}
        for f in get_onlineformincoming_detail(dbo, collationid):
            if f.VALUE.startswith("RAW::") or f.VALUE.startswith("data:"): continue
            label = f.LABEL or f.FIELDNAME
            if buildcols: cols.append(label)
            row[label] = f.VALUE
        buildcols = False
        rows.append(row)
    return asm3.utils.csv(dbo.locale, rows, cols)

def get_onlineformincoming_html_print(dbo: Database, ids: List[int], 
                                      include_raw: bool = True, include_images: bool = True, include_system: bool = True, 
                                      strip_bgimages: bool = True, strip_script: bool = True, strip_style: bool = True) -> str:
    """
    Returns a complete printable version of the online form
    (header/footer wrapped around the html call above)
    ids: A list of integer ids
    include_raw: Include fields that are raw markup
    include_images: Include base64 encoded images
    include_system: Include system generated fields (ipaddress, retainfor, etc)
    strip_script: Remove any script tags from the form
    strip_style: Remove any style tags from the form
    strip_bgimages: Remove any background-image CSS directives from the form
    """
    title = get_onlineformincoming_formname(dbo, ids[0])
    header = get_onlineform_header(dbo)
    header = header.replace("$$TITLE$$", title)
    headercontent = header[header.find("<body>")+6:]
    header = header[0:header.find("<body>")+6]
    footer = get_onlineform_footer(dbo)
    footer = footer.replace("$$TITLE$$", title)
    footercontent = footer[0:footer.find("</body>")]
    h = []
    h.append(header)
    for i, collationid in enumerate(ids):
        h.append(headercontent)
        formheader = get_onlineformincoming_formheader(dbo, collationid)
        h.append(formheader)
        h.append(get_onlineformincoming_html(dbo, asm3.utils.cint(collationid), include_raw=include_raw, include_images=include_images, include_system=include_system))
        formfooter = get_onlineformincoming_formfooter(dbo, collationid)
        h.append(formfooter)
        h.append(footercontent)
        if i < len(ids)-1:
            h.append('<div style="page-break-before: always;"></div>')
    h.append("</body></html>")
    s = "\n".join(h)
    if strip_bgimages: s= asm3.utils.strip_background_images(s)
    if strip_script: s = asm3.utils.strip_script_tags(s)
    if strip_style: s = asm3.utils.strip_style_tags(s)
    return s

def get_onlineformincoming_date(dbo: Database, collationid: int) -> datetime:
    """ Returns the posted date/time for a collation id """
    return dbo.query_date("SELECT PostedDate FROM onlineformincoming WHERE CollationID = ? %s" % dbo.sql_limit(1), [collationid])

def get_onlineformincoming_name(dbo: Database, collationid: int) -> str:
    """ Returns the form name for a collation id """
    return dbo.query_string("SELECT FormName FROM onlineformincoming WHERE CollationID = ? %s" % dbo.sql_limit(1), [collationid])

def get_onlineformincoming_animalperson(dbo: Database, collationid: int) -> Tuple[str, str, str]:
    """ Returns the animalname, firstname and lastname fields from the form if they are present. Returned as a tuple. """
    animalname = ""
    firstname = ""
    lastname = ""
    for r in dbo.query("SELECT FieldName, Value FROM onlineformincoming WHERE CollationID = ?", [collationid]):
        f = r.FIELDNAME.lower()
        if f.startswith("firstname"): firstname = r.VALUE
        if f.startswith("forenames"): firstname = r.VALUE
        if f.startswith("lastname"): lastname = r.VALUE
        if f.startswith("surname"): lastname = r.VALUE
        if f.startswith("animalname"): animalname = r.VALUE
        if f.startswith("reserveanimalname"): animalname = r.VALUE
    return (animalname, firstname, lastname)

def get_onlineformincoming_retainfor(dbo: Database, collationid: int) -> int:
    """ Returns the retain for period for a collation id """
    return dbo.query_int("SELECT Value FROM onlineformincoming WHERE CollationID = ? AND FieldName = 'retainfor' %s" % dbo.sql_limit(1), [collationid])

def get_animal_id_from_field(dbo: Database, name: str) -> int:
    """ Used for ADOPTABLE/SHELTER animal fields, gets the ID from the value """
    if name.find("::") != -1:
        animalcode = name.split("::")[1]
        aid = dbo.query_int("SELECT ID FROM animal WHERE ShelterCode = ? ORDER BY ID DESC", [animalcode])
    else:
        aid = dbo.query_int("SELECT ID FROM animal WHERE LOWER(AnimalName) LIKE ? ORDER BY ID DESC", [name.lower()])
    return aid

def insert_onlineform_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Create an onlineform record from posted data
    """
    return dbo.insert("onlineform", {
        "Name":                 post["name"],
        "RedirectUrlAfterPOST": post["redirect"],
        "AutoProcess":          post.integer("autoprocess"),
        "RetainFor":            post.integer("retainfor"),
        "SetOwnerFlags":        post["flags"],
        "EmailAddress":         post["email"],
        "EmailCoordinator":     post.boolean("emailcoordinator"),
        "EmailFosterer":        post.boolean("emailfosterer"),
        "EmailSubmitter":       post.integer("emailsubmitter"),
        "*EmailMessage":        post["emailmessage"],
        "*Header":              post["header"],
        "*Footer":              post["footer"],
        "*Description":         post["description"]
    }, username, setCreated=False)

def update_onlineform_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Update an onlineform record from posted data
    """
    return dbo.update("onlineform", post.integer("formid"), {
        "Name":                 post["name"],
        "RedirectUrlAfterPOST": post["redirect"],
        "AutoProcess":          post.integer("autoprocess"),
        "RetainFor":            post.integer("retainfor"),
        "SetOwnerFlags":        post["flags"],
        "EmailAddress":         post["email"],
        "EmailCoordinator":     post.boolean("emailcoordinator"),
        "EmailFosterer":        post.boolean("emailfosterer"),
        "EmailSubmitter":       post.integer("emailsubmitter"),
        "*EmailMessage":        post["emailmessage"],
        "*Header":              post["header"],
        "*Footer":              post["footer"],
        "*Description":         post["description"]
    }, username, setLastChanged=False)

def delete_onlineform(dbo: Database, username: str, formid: int) -> None:
    """
    Deletes the specified onlineform and fields
    """
    dbo.execute("DELETE FROM onlineformfield WHERE OnlineFormID = ?", [formid])
    dbo.delete("onlineform", formid, username)

def reindex_onlineform(dbo: Database, username: str, formid: int) -> None:
    """
    Resets display indexes to space out by 10 using current order
    """
    fields = get_onlineformfields(dbo, formid)
    
    for i in range(len(fields)):
        newindex = (i + 1) * 10
        dbo.execute("UPDATE onlineformfield SET DISPLAYINDEX = ? WHERE OnlineFormID = ? AND ID = ?", [newindex, formid, fields[i]["ID"]])

def clone_onlineform(dbo: Database, username: str, formid: int) -> int:
    """
    Clones formid
    """
    l = dbo.locale
    f = get_onlineform(dbo, formid)
    if f is None: return

    nfid = dbo.insert("onlineform", {
        "Name":                 asm3.i18n._("Copy of {0}", l).format(f.NAME),
        "RedirectUrlAfterPOST": f.REDIRECTURLAFTERPOST,
        "AutoProcess":          f.AUTOPROCESS,
        "SetOwnerFlags":        f.SETOWNERFLAGS,
        "EmailAddress":         f.EMAILADDRESS,
        "EmailSubmitter":       f.EMAILSUBMITTER,
        "*EmailMessage":        f.EMAILMESSAGE,
        "*Header":              f.HEADER,
        "*Footer":              f.FOOTER,
        "*Description":         f.DESCRIPTION
    }, username, setCreated=False)
    for ff in get_onlineformfields(dbo, formid):
        dbo.insert("onlineformfield", {
            "OnlineFormID":     nfid,
            "FieldName":        ff.FIELDNAME,
            "FieldType":        ff.FIELDTYPE,
            "Label":            ff.LABEL,
            "DisplayIndex":     ff.DISPLAYINDEX,
            "Mandatory":        ff.MANDATORY,
            "VisibleIf":        ff.VISIBLEIF,
            "Lookups":          ff.LOOKUPS,
            "*Tooltip":          ff.TOOLTIP
        })
    return nfid

def insert_onlineformfield_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Create an onlineformfield record from posted data
    """
    l = dbo.locale
    samename = dbo.query_int("SELECT COUNT(ID) FROM onlineformfield " \
        "WHERE OnlineFormID=? AND UPPER(FieldName) LIKE UPPER(?)", \
        [post.integer("formid"), post["fieldname"]])
    if samename > 0:
        raise asm3.utils.ASMValidationError(asm3.i18n._("You have already used field name '{0}' in this form", l).format(post["fieldname"]))

    return dbo.insert("onlineformfield", {
        "OnlineFormID":     post.integer("formid"),
        "FieldName":        post["fieldname"],
        "FieldType":        post.integer("fieldtype"),
        "Label":            post["label"],
        "DisplayIndex":     post.integer("displayindex"),
        "Mandatory":        post.boolean("mandatory"),
        "Lookups":          post["lookups"],
        "SpeciesID":        post.integer("species"),
        "VisibleIf":        post["visibleif"],
        "*Tooltip":         post["tooltip"]
    }, username, setCreated=False)

def update_onlineformfield_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Update an onlineformfield record from posted data
    """
    l = dbo.locale
    samename = dbo.query_int("SELECT COUNT(ID) FROM onlineformfield " \
        "WHERE ID<>? AND OnlineFormID=? AND UPPER(FieldName) LIKE UPPER(?)", \
        [post.integer("formfieldid"), post.integer("formid"), post["fieldname"]])
    if samename > 0:
        raise asm3.utils.ASMValidationError(asm3.i18n._("You have already used field name '{0}' in this form", l).format(post["fieldname"]))

    dbo.update("onlineformfield", post.integer("formfieldid"), {
        "FieldName":        post["fieldname"],
        "FieldType":        post.integer("fieldtype"),
        "Label":            post["label"],
        "DisplayIndex":     post.integer("displayindex"),
        "Mandatory":        post.boolean("mandatory"),
        "Lookups":          post["lookups"],
        "SpeciesID":        post.integer("species"),
        "VisibleIf":        post["visibleif"],
        "*Tooltip":         post["tooltip"]
    }, username, setLastChanged=False)

def delete_onlineformfield(dbo: Database, username: str, fieldid: int) -> None:
    """
    Deletes the specified onlineformfield
    """
    dbo.delete("onlineformfield", fieldid, username)

def insert_onlineformincoming_from_form(dbo: Database, post: PostedData, remoteip: str, useragent: str) -> int:
    """
    Create onlineformincoming records from posted data. We 
    create a row for every key/value pair in the posted data
    with a unique collation ID.
    """
    # Do some spam/junk tests before accepting the form. If any of these fail, they are logged silently
    # and the submitter still receives the redirect to the thank you page so they don't know that something is up.

    # Check our spambot checkbox/honey trap
    if asm3.configuration.onlineform_spam_honeytrap(dbo):
        if post[SPAMBOT_TXT] != "": 
            asm3.al.error("blocked spambot (honeytrap): %s" % post.data, "insert_onlineformincoming_from_form", dbo)
            return

    # Check that the useragent looks like an actual browser
    # had a few bots that identified as python-requests, etc.
    if asm3.configuration.onlineform_spam_ua_check(dbo):
        if not useragent.strip().startswith("Mozilla"):
            asm3.al.error("blocked spambot (ua=%s): %s" % (useragent, post.data), "insert_onlineformincoming_from_form", dbo)
            return

    # Look for junk in firstname. A lot of bot submitted junk is just random upper and lower case letters. 
    # If we have 2 or more upper and lower case letters in the firstname and no spaces, it's very likely bot junk.
    # We have javascript that title cases name fields, so a mix of cases also indicates the form has been filled out by
    # an automated process instead of a browser.
    # This test does nothing if there's no firstname field in the form.
    if asm3.configuration.onlineform_spam_firstname_mixcase(dbo):
        for k, v in post.data.items():
            if k.startswith("firstname") or k.startswith("forenames"):
                lc = 0
                uc = 0
                sp = 0
                for x in v:
                    if x.isupper():
                        uc += 1
                    elif x == " ":
                        sp += 1
                    else:
                        lc += 1
                if lc >= 2 and uc >= 2 and sp == 0:
                    asm3.al.error("blocked spambot (firstname=%s, uc=%s, lc=%s): %s" % (v, uc, lc, post.data), "insert_onlineformincoming_from_form", dbo)
                    return

    collationid = get_collationid(dbo)

    IGNORE_FIELDS = [ SPAMBOT_TXT, "formname", "flags", "redirect", "account", "filechooser", "method" ]
    l = dbo.locale
    formname = post["formname"]
    posteddate = dbo.now()
    flags = post["flags"]
    address = ""
    emailaddress = ""
    emailsubmissionto = ""
    mobile = ""
    firstname = ""
    lastname = ""
    animalname = ""
    animalname2 = ""
    animalname3 = ""
    images = []
    post.data["formreceived"] = "%s %s" % (asm3.i18n.python2display(dbo.locale, posteddate), asm3.i18n.format_time(posteddate))
    post.data["ipaddress"] = remoteip
    post.data["useragent"] = useragent

    for k, v in post.data.items():

        if k not in IGNORE_FIELDS and not k.startswith("asmSelect"):
            label = ""
            displayindex = 0
            fieldname = k
            fieldtype = FIELDTYPE_TEXT
            tooltip = ""

            # Form fields should have a _ONLINEFORMFIELD.ID suffix we can use to get the
            # original label and display position.
            if k.find("_") != -1:
                fid = asm3.utils.cint(k[k.rfind("_")+1:])
                fieldname = k[0:k.rfind("_")]
                v = v.strip() # no reason for whitespace, can't see it in preview and in address fields it makes a mess
                if fid != 0:
                    fld = dbo.first_row(dbo.query("SELECT FieldType, Label, Tooltip, DisplayIndex FROM onlineformfield WHERE ID = ?", [fid]))
                    if fld is not None:
                        label = fld.LABEL
                        displayindex = fld.DISPLAYINDEX
                        fieldtype = fld.FIELDTYPE
                        tooltip = fld.TOOLTIP
                        # Store a few known fields for access later
                        if fieldname == "address":
                            address = v
                        if fieldname == "emailaddress": 
                            emailaddress = v
                        if fieldname == "emailsubmissionto":
                            emailsubmissionto = v
                        if fieldname == "firstname" or fieldname == "forenames": 
                            firstname = v
                        if fieldname == "lastname" or fieldname == "surname":
                            lastname = v
                        if fieldname == "mobiletelephone" or fieldname == "celltelephone":
                            mobile = v
                        if fieldname == "animalname" or fieldname == "reserveanimalname":
                            animalname = v
                        if fieldname == "animalname2" or fieldname == "reserveanimalname2":
                            animalname2 = v
                        if fieldname == "animalname3" or fieldname == "reserveanimalname3":
                            animalname3 = v
                        # If it's a raw markup field, store the markup as the value
                        if fieldtype == FIELDTYPE_RAWMARKUP:
                            v = "RAW::%s" % tooltip
                        # If we have a checkbox field with a tooltip, it contains additional
                        # person flags, add them to our set
                        if fieldtype == FIELDTYPE_CHECKBOX and asm3.utils.nulltostr(tooltip) != "" and (v == "checked" or v == "on"):
                            if flags != "": flags += ","
                            flags += tooltip
                            dbo.update("onlineformincoming", "CollationID=%s" % collationid, {
                                "Flags":    flags
                            })
                        # We decode images and put them into an images list so that they can
                        # be included as attachments with confirmation emails.
                        if fieldtype == FIELDTYPE_IMAGE and v.startswith("data:image/jpeg"):
                            # Remove prefix of data:image/jpeg;base64, and decode
                            images.append( ("%s.jpg" % fieldname, "image/jpeg", asm3.utils.base64decode(v[v.find(",")+1:])) )

            # Do the insert
            try:
                dbo.insert("onlineformincoming", {
                    "CollationID":      collationid,
                    "FormName":         formname,
                    "PostedDate":       posteddate,
                    "Flags":            flags,
                    "FieldName":        fieldname,
                    "Label":            label,
                    "DisplayIndex":     displayindex,
                    "Host":             remoteip,
                    asm3.utils.iif(fieldtype == FIELDTYPE_RAWMARKUP, "*Value", "Value"): v # don't XSS escape raw markup by prefixing fieldname with *
                }, generateID=False, setCreated=False)
            except Exception as err:
                asm3.al.warn("failed creating incoming field, cid=%s, name=%s, value=%s: %s" % (collationid, fieldname, v, err), 
                    "insert_onlineformincoming_from_form", dbo)
   
    # If there are person fields in this form, find and create a field
    # containing the person that they would merge with after processing with 
    # "Create Person" so that the user will know ahead of time. 
    # This helps with issues such as people signing up with each other's email address.
    if firstname != "" and lastname != "":
        rows = asm3.person.get_person_similar(dbo, email=emailaddress, mobile=mobile, surname=lastname, forenames=firstname, address=address)
        if len(rows) > 0:
            sp = rows[0]
            mergeperson = "%s: %s [%s]" % (sp.ID, sp.OWNERNAME, asm3.person.calc_readable_flags(sp.ADDITIONALFLAGS))
            # Do the insert
            try:
                dbo.insert("onlineformincoming", {
                    "CollationID":      collationid,
                    "FormName":         formname,
                    "PostedDate":       posteddate,
                    "Flags":            flags,
                    "FieldName":        "mergeperson",
                    "Label":            "",
                    "DisplayIndex":     0,
                    "Host":             remoteip,
                    "Value":            mergeperson
                }, generateID=False, setCreated=False)
            except Exception as err:
                asm3.al.warn("failed creating merge person field, cid=%s, value=%s: %s" % (collationid, mergeperson, err), 
                    "insert_onlineformincoming_from_form", dbo)

    # Sort out the preview of the first few fields
    fieldssofar = 0
    preview = []

    # If we have first and last name, include them in the preview
    if firstname != "" and lastname != "":
        preview.append("%s: %s %s" % ( asm3.i18n._("Name"), firstname, lastname ))
        fieldssofar += 2

    # If we have an animal, include that too
    if animalname != "":
        preview.append("%s: %s" % ( asm3.i18n._("Animal"), animalname))
        fieldssofar += 1

    for fld in get_onlineformincoming_detail(dbo, collationid):
        if fieldssofar < 3:
            # Don't include raw markup or signature/image fields in the preview
            if fld.VALUE.startswith("RAW::") or fld.VALUE.startswith("data:"): continue
            # Or the system fields, or fields we would have already added above
            if fld.FIELDNAME in SYSTEM_FIELDS: continue
            if fld.FIELDNAME in ("firstname", "forenames", "lastname", "surname"): continue
            if fld.FIELDNAME in ("animalname", "reserveanimalname"): continue
            fieldssofar += 1
            preview.append( "%s: %s" % (fld.LABEL, fld.VALUE ))

    # Add the preview to the form
    dbo.update("onlineformincoming", "CollationID=%s" % collationid, { 
        "Preview": ", ".join(preview) 
    })
        
    # Get the onlineform if we have one
    formdef = dbo.first_row(dbo.query("SELECT * FROM onlineform o " \
        "INNER JOIN onlineformincoming oi ON oi.FormName = o.Name " \
        "WHERE oi.CollationID = ?", [collationid]))

    # If there's no linked online form, we can't do any of the functionality that follows
    # as it requires data from the online form.
    if not formdef: return collationid

    # A string containing the submitted form for including in emails 
    # (images are included as attachments so not in the form output)
    # (we also suppress system generated fields as most do not find them helpful in the email)
    formdata = get_onlineformincoming_html_print(dbo, [collationid,], include_system=False, include_images=False)

    # Do we have a valid emailaddress field for the form submitter and 
    # one of the options to email the submitter is set?
    if emailaddress != "" and emailaddress.find("@") != -1 and formdef.emailsubmitter != 0:
        # Get the confirmation message
        body = formdef.emailmessage
        attachments = []
        # Submission option 1 = include a copy of the form submission
        if formdef.emailsubmitter == 1: 
            body += "\n" + formdata
            attachments = images
        # Send
        asm3.utils.send_email(dbo, "", emailaddress, "", "", 
            asm3.i18n._("Submission received: {0}", l).format(formname), 
            body, "html", attachments, exceptions=False)

    # Subject line for email notifications to staff and coordinators (max 70 chars)
    subject = "%s - %s" % (asm3.utils.truncate(formname, 32), ", ".join(preview))

    # Did the original form specify some email addresses to send 
    # incoming submissions to?
    if formdef.emailaddress is not None and formdef.emailaddress.strip() != "":
        # If a submitter email has been set AND we sent the submitter a copy, 
        # use the submitter email as reply-to so staff and can reply to their
        # copy of the message and email the applicant/submitter.
        # It's important that this is ONLY done if the option is on to send the submitter
        # confirmation because it avoids situations where people use forms for internal process
        # and want to use an applicant's details but don't want them to see it or accidentally
        # reply to them about it (prime example, forms related to performing homechecks)
        replyto = ""
        if formdef.emailsubmitter != 0: replyto = emailaddress 
        if replyto == "": replyto = asm3.configuration.email(dbo)
        # NOTE: We send emails to shelter contacts as bulk=True to try and prevent
        # backscatter since most shelter emails have some kind of autoresponder
        # NOTE: Since the reply address will be the submitter, we do not allow it
        # to ever override the FROM header
        asm3.utils.send_email(dbo, replyto, formdef.emailaddress, "", "", 
            subject, formdata, "html", images, exceptions=False, bulk=True, fromoverride=False)

    # Was the option set to email the adoption coordinator linked to animalname?
    if formdef.emailcoordinator == 1 and animalname != "":
        for name in (animalname, animalname2, animalname3):
            if name == "": continue
            # If so, find the selected animal from the form
            animalid = get_animal_id_from_field(dbo, name)
            coordinatoremail = dbo.query_string("SELECT EmailAddress FROM animal " \
                "INNER JOIN owner ON owner.ID = animal.AdoptionCoordinatorID " \
                "WHERE animal.ID = ?", [animalid])
            if coordinatoremail != "":
                asm3.utils.send_email(dbo, "", coordinatoremail, "", "", 
                    subject, formdata, "html", images, exceptions=False)

    # Was the option set to email the fosterer linked to animalname?
    if formdef.emailfosterer == 1 and animalname != "":
        for name in (animalname, animalname2, animalname3):
            if name == "": continue
            # If so, find the selected animal from the form
            animalid = get_animal_id_from_field(dbo, name)
            fostereremail = dbo.query_string("SELECT EmailAddress FROM animal " \
                "INNER JOIN adoption ON adoption.ID = animal.ActiveMovementID AND adoption.MovementType = 2 " \
                "INNER JOIN owner ON owner.ID = adoption.OwnerID " \
                "WHERE animal.ID = ?", [animalid])
            if fostereremail != "":
                asm3.utils.send_email(dbo, "", fostereremail, "", "", 
                    subject, formdata, "html", images, exceptions=False)

    # Did the form submission have a value in an "emailsubmissionto" field?
    if emailsubmissionto is not None and emailsubmissionto.strip() != "":
        # If a submitter email is set, use that to reply to instead
        replyto = emailaddress 
        if replyto == "": replyto = asm3.configuration.email(dbo)
        # Remove any line breaks from the list of addresses, this has caused malformed headers before
        emailsubmissionto = emailsubmissionto.replace("\n", "")
        asm3.utils.send_email(dbo, replyto, emailsubmissionto, "", "", 
            subject, formdata, "html", images, exceptions=False, fromoverride=False)

    # Does this form have an option set to autoprocess it? If not, stop now
    if formdef.autoprocess is None or formdef.autoprocess == AP_NO: return collationid

    try:
        if formdef.autoprocess == AP_ATTACHANIMAL:
            attach_animalbyname(dbo, "autoprocess", collationid)
        elif formdef.autoprocess == AP_CREATEANIMAL:
            create_animal(dbo, "autoprocess", collationid)
        elif formdef.autoprocess == AP_CREATEPERSON:
            create_person(dbo, "autoprocess", collationid)
        elif formdef.autoprocess == AP_ATTACHANIMAL_CREATEPERSON:
            try:
                # If we fail to attach the animal (eg: because one wasn't specified)
                # we still need to continue and create the person.
                # Assume if we are attaching to an animal while creating a person that
                # media in the form is for the person.
                attach_animalbyname(dbo, "autoprocess", collationid, attachmedia=False)
            except asm3.utils.ASMValidationError as aterr:
                asm3.al.error("%s" % aterr.getMsg(), "autoprocess", dbo)
            create_person(dbo, "autoprocess", collationid)
        elif formdef.autoprocess == AP_CREATEANIMAL_BROUGHTIN:
            collationid, personid, personname, status = create_person(dbo, "autoprocess", collationid)
            create_animal(dbo, "autoprocess", collationid, broughtinby=personid)
        elif formdef.autoprocess == AP_CREATEANIMAL_NONSHELTER:
            collationid, personid, personname, status = create_person(dbo, "autoprocess", collationid)
            create_animal(dbo, "autoprocess", collationid, nsowner=personid)
        elif formdef.autoprocess == AP_CREATELOSTANIMAL:
            create_lostanimal(dbo, "autoprocess", collationid)
        elif formdef.autoprocess == AP_CREATEFOUNDANIMAL:
            create_foundanimal(dbo, "autoprocess", collationid)
        elif formdef.autoprocess == AP_CREATEINCIDENT:
            create_animalcontrol(dbo, "autoprocess", collationid)
        elif formdef.autoprocess == AP_CREATETRANSPORT:
            create_transport(dbo, "autoprocess", collationid)
        elif formdef.autoprocess == AP_CREATEWAITINGLIST:
            create_waitinglist(dbo, "autoprocess", collationid)
        # We only get here if there were no issues processing the form and it's safe to delete it
        delete_onlineformincoming(dbo, "autoprocess", collationid)
    except asm3.utils.ASMValidationError as verr:
        asm3.al.error("%s" % verr.getMsg(), "autoprocess", dbo)
    except Exception as err:
        asm3.al.error("%s" % err, "autoprocess", dbo)

    return collationid

def delete_onlineformincoming(dbo: Database, username: str, collationid: int) -> None:
    """
    Deletes the specified onlineformincoming set
    """
    # Write an entry to the deletions and audit table for all the incoming form rows as one
    # This is a special case because onlineformincoming does not have an ID field, 
    # so the generic deletions handling in audit.delete_rows and dbms.base.delete cannot do it.
    rows = dbo.query("SELECT * FROM onlineformincoming WHERE CollationID=%s ORDER BY DisplayIndex" % collationid)
    sql = []
    values = {}
    preview = ""
    processed = "-Unprocessed-"
    for r in rows:
        if preview == "" and r.PREVIEW != "": preview = r.PREVIEW
        if r.FIELDNAME == "processed": processed = "=Processed="
        values[r.FIELDNAME] = asm3.utils.strip_html_tags(r.VALUE)
        sql.append(dbo.row_to_insert_sql("onlineformincoming", r))
    asm3.audit.insert_deletion(dbo, username, "onlineformincoming", collationid, "", "".join(sql))
    asm3.audit.delete(dbo, username, "onlineformincoming", collationid, "", "%s %s %s" % (processed, preview, values))
    dbo.delete("onlineformincoming", "CollationID=%s" % collationid, username, writeAudit=False, writeDeletion=False)

def guess_agegroup(dbo: Database, s: str) -> str:
    """ Guesses an agegroup, returns the third band (adult by default) if no match is found """
    s = str(s).lower().strip()
    for g in asm3.configuration.age_groups(dbo):
        if g.lower() == s:
            return g
    return asm3.configuration.age_group_name(dbo, 3)

def guess_animaltype(dbo: Database, s: str) -> int:
    """ Guesses an animal type, returns the default if no match is found """
    s = str(s).lower().strip()
    guess = dbo.query_int("SELECT ID FROM animaltype WHERE LOWER(AnimalType) LIKE ?", ["%%%s%%" % s])
    if guess != 0: return guess
    return asm3.configuration.default_type(dbo)

def guess_breed(dbo: Database, s: str) -> int:
    """ Guesses a breed, returns the default if no match is found """
    s = str(s).lower().strip()
    guess = dbo.query_int("SELECT ID FROM breed WHERE LOWER(BreedName) LIKE ?", ["%%%s%%" % s])
    if guess != 0: return guess
    return asm3.configuration.default_breed(dbo)

def guess_colour(dbo: Database, s: str) -> int:
    """ Guesses a colour, returns the default if no match is found """
    s = str(s).lower().strip()
    guess = dbo.query_int("SELECT ID FROM basecolour WHERE LOWER(BaseColour) LIKE ?", ["%s" % s])
    if guess != 0: return guess
    guess = dbo.query_int("SELECT ID FROM basecolour WHERE LOWER(BaseColour) LIKE ?", ["%%%s%%" % s])
    if guess != 0: return guess
    return asm3.configuration.default_colour(dbo)

def guess_entryreason(dbo: Database, s: str) -> int:
    """ Guesses an entry reason, returns the default if no match is found """
    s = str(s).lower().strip()
    guess = dbo.query_int("SELECT ID FROM entryreason WHERE LOWER(ReasonName) LIKE ?", ["%%%s%%" % s])
    if guess != 0: return guess
    return asm3.configuration.default_entry_reason(dbo)

def guess_entrytype(dbo: Database, s: str) -> int:
    """ Guesses an entry type, returns the default if no match is found """
    s = str(s).lower().strip()
    guess = dbo.query_int("SELECT ID FROM lksentrytype WHERE LOWER(EntryTypeName) LIKE ?", ["%%%s%%" % s])
    if guess != 0: return guess
    return asm3.configuration.default_entry_type(dbo)

def guess_sex(dummy: Any, s: str) -> int:
    """ Guesses a sex """
    if s.lower().startswith("m"):
        return 1
    return 0

def guess_size(dbo: Database, s: str) -> int:
    """ Guesses a size """
    s = str(s).lower().strip()
    guess = dbo.query_int("SELECT ID FROM lksize WHERE LOWER(Size) LIKE ?", ["%%%s%%" % s])
    if guess != 0: return guess
    return asm3.configuration.default_size(dbo)

def guess_species(dbo: Database, s: str) -> int:
    """ Guesses a species, returns the default if no match is found """
    s = str(s).lower().strip()
    guess = dbo.query_int("SELECT ID FROM species WHERE LOWER(SpeciesName) LIKE ?", [s])
    if guess != 0: return guess
    return asm3.configuration.default_species(dbo)

def guess_transporttype(dbo: Database, s: str) -> int:
    """ Guesses a transporttype """
    s = str(s).lower().strip()
    guess = dbo.query_int("SELECT ID FROM transporttype WHERE LOWER(TransportTypeName) LIKE ?", [s])
    if guess != 0: return guess
    return dbo.query_int("SELECT ID FROM transporttype ORDER BY ID")

def truncs(s: str) -> str:
    """ Truncates a string for inserting to short text columns """
    return asm3.utils.truncate(s, 1024)

def attach_form(dbo: Database, username: str, linktype: int, linkid: int, collationid: int, attachmedia: bool = True) -> None:
    """
    Attaches the incoming form to the media tab. 
    attachmedia: if True, finds any images in the form and attaches 
                 those as images in the media tab of linktype/linkid.
    """
    l = dbo.locale
    fo = dbo.first_row(dbo.query("SELECT * FROM onlineformincoming WHERE CollationID=? %s" % dbo.sql_limit(1), [collationid]))
    formname = asm3.i18n._("Online Form", l)
    if fo is not None: formname = fo.FORMNAME
    animalname, firstname, lastname = get_onlineformincoming_animalperson(dbo, collationid)
    if linktype == asm3.media.ANIMAL and firstname != "":
        formname = "%s - %s %s" % (formname, firstname, lastname)
    elif linktype == asm3.media.PERSON and animalname != "":
        formname = "%s - %s" % (formname, animalname)
    try:
        # Add a processed field to the form. This allows the UI to find and indicate previously processed forms
        # as well as keeping an additive record of what records a form has been attached to.
        pval = "%s,%s" % (linktype, linkid)
        dbo.insert("onlineformincoming", {
            "CollationID":      collationid,
            "FormName":         fo.FORMNAME,
            "PostedDate":       fo.POSTEDDATE,
            "Flags":            fo.FLAGS,
            "FieldName":        "processed",
            "Label":            "",
            "DisplayIndex":     0,
            "Host":             fo.HOST,
            "Preview":          fo.PREVIEW,
            "Value":            pval
        }, generateID=False, setCreated=False)
    except Exception as err:
        asm3.al.warn("failed creating processed field, cid=%s, value=%s: %s" % (collationid, pval, err), 
            "onlineform.attach_form", dbo)
    formhtml = get_onlineformincoming_html_print(dbo, [collationid,])
    retainfor = get_onlineformincoming_retainfor(dbo, collationid)
    mid = asm3.media.create_document_media(dbo, username, linktype, linkid, formname, formhtml, retainfor)
    if asm3.configuration.auto_hash_processed_forms(dbo):
        dtstr = "%s %s" % (asm3.i18n.python2display(l, dbo.now()), asm3.i18n.format_time(dbo.now()))
        asm3.media.sign_document(dbo, username, mid, "", \
            asm3.i18n._("Processed by {0} on {1}", l).format(username, dtstr), "onlineform")
    if attachmedia:
        fields = get_onlineformincoming_detail(dbo, collationid)
        for f in fields:
            if f.VALUE.startswith("data:image/jpeg"):
                d = {
                    "retainfor":    str(retainfor),
                    "filename":     "image.jpg",
                    "filetype":     "image/jpeg",
                    "filedata":     f.VALUE
                }
                if linktype == 0:
                    d["excludefrompublish"] = "1" # auto exclude images for animals to prevent them going to adoption websites
                asm3.media.attach_file_from_form(dbo, username, linktype, linkid, asm3.utils.PostedData(d, dbo.locale))

def attach_animalbyname(dbo: Database, username: str, collationid: int, attachmedia: bool = True) -> Tuple[int, int, str]:
    """
    Finds the existing shelter animal with "animalname" and
    attaches the form to it as animal asm3.media.
    Return value is a tuple of collationid, animalid, animal code/name
    If the animal is bonded, attaches the form to the bonded animals too. 
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    animalname = ""
    has_name = False
    animalid = 0
    for f in fields:
        if f.FIELDNAME == "animalname" or f.FIELDNAME == "reserveanimalname": 
            animalname = f.VALUE
            animalid = get_animal_id_from_field(dbo, animalname)
            has_name = True
            break
    if not has_name:
        raise asm3.utils.ASMValidationError(asm3.i18n._("There is not enough information in the form to attach to a shelter animal record (need an animal name).", l))
    if animalid == 0:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Could not find animal with name '{0}'", l).format(animalname))
    for aid in asm3.animal.get_animal_id_and_bonds(dbo, animalid):
        attach_form(dbo, username, asm3.media.ANIMAL, aid, collationid, attachmedia=attachmedia)
    return (collationid, animalid, asm3.animal.get_animal_namecode(dbo, animalid))

def attach_animal(dbo: Database, username: str, animalid: int, collationid: int) -> None:
    """
    Attaches the form to a specific animal. If the animal is bonded, attaches to those as well.
    """
    for aid in asm3.animal.get_animal_id_and_bonds(dbo, animalid):
        asm3.onlineform.attach_form(dbo, username, asm3.media.ANIMAL, aid, collationid)

def attach_person(dbo: Database, username: str, personid: int, collationid: int) -> None:
    """
    Attaches the form to a specific person
    """
    asm3.onlineform.attach_form(dbo, username, asm3.media.PERSON, personid, collationid)

def create_animal(dbo: Database, username: str, collationid: int, broughtinby: int = 0, nsowner: int = 0) -> Tuple[int, int, str, int]:
    """
    Creates an animal record from the incoming form data with collationid.
    If broughtinby is specified, sets this as the broughtinbyownerid on the animal record.
    If nsowner is specified, sets this as the ownerid and originalownerid on the record and makes it nonshelter.
    Also, attaches the form to the animal as media.
    The return value is a tuple of collationid, animalid, sheltercode - animalname, status
    status is 0 for created, 1 for updated existing
    "animalname", "code", "microchip", "age", "dateofbirth", "entryreason", "markings", 
    "comments", "hiddencomments", "type", "species", "breed1", "breed2", "color", "sex", 
    "neutered", "weight"
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    # formreceived = asm3.i18n.python2display(l, dbo.now())
    d = { "estimatedage": "", "dateofbirth": "", "broughtinby": str(broughtinby) }
    if nsowner != 0:
        d["nonshelter"] = "on"
        d["nsowner"] = str(nsowner)
    breed1 = ""
    breed2 = ""
    for f in fields:
        if f.FIELDNAME == "animalname": d["animalname"] = truncs(f.VALUE)
        if f.FIELDNAME == "code": 
            d["code"] = truncs(f.VALUE)
            d["sheltercode"] = truncs(f.VALUE)
            d["shortcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "dateofbirth": d["dateofbirth"] = f.VALUE
        if f.FIELDNAME == "age": d["estimatedage"] = f.VALUE
        if f.FIELDNAME == "markings": d["markings"] = f.VALUE
        if f.FIELDNAME == "comments": d["comments"] = f.VALUE
        if f.FIELDNAME == "microchip": 
            d["microchipped"] = "on"
            d["microchipnumber"] = truncs(f.VALUE)
        if f.FIELDNAME == "hiddencomments": d["hiddenanimaldetails"] = f.VALUE
        if f.FIELDNAME == "reason": d["reasonforentry"] = f.VALUE
        if f.FIELDNAME == "entryreason": d["entryreason"] = str(guess_entryreason(dbo, f.VALUE))
        if f.FIELDNAME == "entrytype": d["entrytype"] = str(guess_entrytype(dbo, f.VALUE))
        if f.FIELDNAME == "type": d["animaltype"] = str(guess_animaltype(dbo, f.VALUE))
        if f.FIELDNAME == "species": d["species"] = str(guess_species(dbo, f.VALUE))
        if f.FIELDNAME == "breed" or f.FIELDNAME == "breed1": 
            breed1 = f.VALUE
            d["breed1"] = str(guess_breed(dbo, f.VALUE))
        if f.FIELDNAME == "breed2": 
            breed2 = f.VALUE
            d["breed2"] = str(guess_breed(dbo, f.VALUE))
        if f.FIELDNAME == "color": d["basecolour"] = str(guess_colour(dbo, f.VALUE))
        if f.FIELDNAME == "colour": d["basecolour"] = str(guess_colour(dbo, f.VALUE))
        if f.FIELDNAME == "sex": d["sex"] = str(guess_sex(dbo, f.VALUE))
        if f.FIELDNAME == "size": d["size"] = str(guess_size(dbo, f.VALUE))
        if f.FIELDNAME == "neutered" and (f.VALUE == "Yes" or f.VALUE == "on"): d["neutered"] = "on"
        if f.FIELDNAME == "weight" and asm3.utils.is_numeric(f.VALUE): d["weight"] = f.VALUE
        if f.FIELDNAME.startswith("additional"): d[f.FIELDNAME] = f.VALUE
    # If the form has a breed, but no species, use the species from that breed
    # For wildlife rescues, breed might be the thing people recognise over species (eg: corvid vs crow, magpie)
    if "species" not in d and "breed1" in d:
        d["species"] = str(asm3.lookups.get_species_for_breed(dbo, asm3.utils.cint(d["breed1"])))
    if "size" not in d: d["size"] = guess_size(dbo, "nomatchesusedefault")
    # Set the crossbreed based on the incoming breed values
    d["crossbreed"] = "0"
    if breed1 != breed2 and breed2.strip() != "": d["crossbreed"] = "1"
    if d["crossbreed"] == "0" and "breed1" in d and "breed2" in d: d["breed2"] = d["breed1"]
    # Have we got enough info to create the animal record? We need a name at a minimum
    if "animalname" not in d:
        raise asm3.utils.ASMValidationError(asm3.i18n._("There is not enough information in the form to create an animal record (need animalname).", l))
    # If a code has not been supplied and manual codes are turned on, 
    # generate one from the date and time to prevent record creation failing.
    if "code" not in d and asm3.configuration.manual_codes(dbo):
        gencode = "OF%s" % asm3.i18n.format_date(dbo.now(), "%y%m%d%H%M%S")
        d["sheltercode"] = gencode
        d["shortcode"] = gencode
    # Are date of birth and age blank? Assume an age of 1.0 if they are
    if d["dateofbirth"] == "" and d["estimatedage"] == "": d["estimatedage"] = "1.0"
    status = 0 # default: created new record
    # Does this animal code already exist?
    animalid = 0
    if "code" in d and d["code"] != "":
        similar = asm3.animal.get_animal_sheltercode(dbo, d["code"])
        if similar is not None:
            status = 1 # updated existing record
            animalid = similar.ID
            # Merge additional fields
            asm3.additional.merge_values_for_link(dbo, asm3.utils.PostedData(d, dbo.locale), username, animalid, "animal")
            # Overwrite fields that are present and have a value
            asm3.animal.merge_animal_details(dbo, username, animalid, d, force=True)
    # Create the animal record if we didn't find one
    if animalid == 0:
        # Set some default values that the form couldn't set
        d["internallocation"] = asm3.configuration.default_location(dbo)
        animalid, sheltercode = asm3.animal.insert_animal_from_form(dbo, asm3.utils.PostedData(d, dbo.locale), username)
    attach_form(dbo, username, asm3.media.ANIMAL, animalid, collationid)
    return (collationid, animalid, "%s - %s" % (sheltercode, d["animalname"]), status)

def create_person(dbo: Database, username: str, collationid: int, merge: bool = True) -> Tuple[int, int, str, int]:
    """
    Creates a person record from the incoming form data with collationid.
    if merge is True, will update, find and attach to an existing person instead of creating if one exists.
    Also, attaches the form to the person as media.
    The return value is tuple of collationid, personid, personname, status
    status is 0 for created, 1 for updated existing, 2 for existing and banned
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    d["ownertype"] = "1" # Individual
    flags = None
    formreceived = asm3.i18n.python2display(l, dbo.now())
    for f in fields:
        if flags is None: flags = f.FLAGS
        if flags is None: flags = ""
        if f.FIELDNAME == "title": d["title"] = truncs(f.VALUE)
        if f.FIELDNAME == "title2": d["title2"] = truncs(f.VALUE)
        if f.FIELDNAME == "initials": d["initials"] = truncs(f.VALUE)
        if f.FIELDNAME == "initials2": d["initials2"] = truncs(f.VALUE)
        if f.FIELDNAME == "forenames" or f.FIELDNAME == "firstname": d["forenames"] = truncs(f.VALUE)
        if f.FIELDNAME == "forenames2" or f.FIELDNAME == "firstname2": d["forenames2"] = truncs(f.VALUE)
        if f.FIELDNAME == "surname" or f.FIELDNAME == "lastname": d["surname"] = truncs(f.VALUE)
        if f.FIELDNAME == "lastname2" or f.FIELDNAME == "surname2":
            d["surname2"] = truncs(f.VALUE)
            if d["surname2"] != "": d["ownertype"] = "3" # Couple
        if f.FIELDNAME == "address": d["address"] = truncs(f.VALUE)
        if f.FIELDNAME == "town": d["town"] = truncs(f.VALUE)
        if f.FIELDNAME == "city": d["town"] = truncs(f.VALUE)
        if f.FIELDNAME == "county": d["county"] = truncs(f.VALUE)
        if f.FIELDNAME == "state": d["county"] = truncs(f.VALUE)
        if f.FIELDNAME == "postcode": d["postcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "zipcode": d["postcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "country": d["country"] = truncs(f.VALUE)
        if f.FIELDNAME == "hometelephone": d["hometelephone"] = truncs(f.VALUE)
        if f.FIELDNAME == "worktelephone": d["worktelephone"] = truncs(f.VALUE)
        if f.FIELDNAME == "worktelephone2": d["worktelephone2"] = truncs(f.VALUE)
        if f.FIELDNAME == "mobiletelephone" or f.FIELDNAME == "celltelephone": d["mobiletelephone"] = truncs(f.VALUE)
        if f.FIELDNAME == "mobiletelephone2" or f.FIELDNAME == "celltelephone2": d["mobiletelephone2"] = truncs(f.VALUE)
        if f.FIELDNAME == "emailaddress": d["emailaddress"] = truncs(f.VALUE)
        if f.FIELDNAME == "emailaddress2": d["emailaddress2"] = truncs(f.VALUE)
        if f.FIELDNAME == "idnumber": d["idnumber"] = truncs(f.VALUE)
        if f.FIELDNAME == "idnumber2": d["idnumber2"] = truncs(f.VALUE)
        if f.FIELDNAME == "dateofbirth": d["dateofbirth"] = f.VALUE
        if f.FIELDNAME == "dateofbirth2": d["dateofbirth2"] = f.VALUE
        if f.FIELDNAME == "excludefrombulkemail" and f.VALUE != "" and f.VALUE != asm3.i18n._("No", l): 
            flags += ",excludefrombulkemail"
        if f.FIELDNAME == "gdprcontactoptin": d["gdprcontactoptin"] = truncs(f.VALUE)
        if f.FIELDNAME == "comments": d["comments"] = f.VALUE
        if f.FIELDNAME.startswith("reserveanimalname"): d[f.FIELDNAME] = truncs(f.VALUE)
        if f.FIELDNAME.startswith("additional"): d[f.FIELDNAME] = f.VALUE
        if f.FIELDNAME == "formreceived" and f.VALUE.find(" ") != -1: 
            recdate, rectime = f.VALUE.split(" ")
            formreceived = asm3.i18n.parse_time( asm3.i18n.display2python(l, recdate), rectime )
    d["flags"] = flags
    # Have we got enough info to create the person record? We just need a surname
    if "surname" not in d:
        raise asm3.utils.ASMValidationError(asm3.i18n._("There is not enough information in the form to create a person record (need a surname).", l))
    status = 0 # created
    # Use the current user's site for our new person record if they have one assigned
    siteid = asm3.users.get_site(dbo, username)
    if siteid != 0: d["site"] = str(siteid)
    # Does this person already exist?
    personid = 0
    if "surname" in d and "forenames" in d:
        demail = ""
        dmobile = ""
        daddress = ""
        if "emailaddress" in d: demail = d["emailaddress"]
        if "mobiletelephone" in d: dmobile = d["mobiletelephone"]
        if "address" in d: daddress = d["address"]
        similar = asm3.person.get_person_similar(dbo, demail, dmobile, d["surname"], d["forenames"], daddress, siteid)
        if merge and len(similar) > 0:
            personid = similar[0].ID
            status = 1 # updated existing record
            if similar[0].ISBANNED == 1: status = 2 # existing record and person banned
            # Merge flags and any extra details
            asm3.person.merge_flags(dbo, username, personid, flags)
            # Merge additional fields
            asm3.additional.merge_values_for_link(dbo, asm3.utils.PostedData(d, dbo.locale), username, personid, "person")
            if "gdprcontactoptin" in d: asm3.person.merge_gdpr_flags(dbo, "import", personid, d["gdprcontactoptin"])
            # Merge person details and force form ones to override existing ones if present
            asm3.person.merge_person_details(dbo, username, personid, d, force=True)
    # Create the person record if we didn't find one
    if personid == 0:
        personid = asm3.person.insert_person_from_form(dbo, asm3.utils.PostedData(d, dbo.locale), username)
        # Since we created a brand new person, try and get a geocode for the address if present
        if "address" in d and "town" in d and "county" in d and "postcode" in d:
            latlon = asm3.geo.get_lat_long(dbo, d["address"], d["town"], d["county"], d["postcode"])
            if latlon is not None: asm3.person.update_latlong(dbo, personid, latlon)
    personname = asm3.person.get_person_name_code(dbo, personid)
    attach_form(dbo, username, asm3.media.PERSON, personid, collationid)
    # Was there a reserveanimalname field? If so, create reservation(s) to the person if possible
    for k, v in d.items():
        # This condition means that we only potentially create a blank reservation
        # for the first reserveanimalname field. Subsequent reserveanimalnameX fields will not create
        # a reservation if there's no value.
        if k == "reserveanimalname" or (k.startswith("reserveanimalname") and v != ""):
            try:
                asm3.movement.insert_reserve(dbo, username, personid, get_animal_id_from_field(dbo, v), formreceived)
            except Exception as err:
                asm3.al.warn("could not create reservation for %d on %s (%s)" % (personid, v, err), "create_person", dbo)
                web.ctx.status = "200 OK" # ASMValidationError sets status to 500
    return (collationid, personid, personname, status)

def create_animalcontrol(dbo: Database, username: str, collationid: int) -> Tuple[int, int, str, int]:
    """
    Creates a animal control/incident record from the incoming form data with 
    collationid.
    Also, attaches the form to the incident as asm3.media.
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    has_person = False
    status = 0 # Will always be a new record for the incident, but person status can override if given
    d["incidentdate"] = asm3.i18n.python2display(l, dbo.now())
    d["incidenttime"] = asm3.i18n.format_time(dbo.now())
    d["calldate"] = d["incidentdate"]
    d["calltime"] = d["incidenttime"]
    d["incidenttype"] = asm3.configuration.default_incident(dbo)
    for f in fields:
        if f.FIELDNAME == "lastname" and f.VALUE != "": has_person = True
        if f.FIELDNAME == "surname" and f.VALUE != "": has_person = True
        if f.FIELDNAME == "callnotes": d["callnotes"] = f.VALUE
        if f.FIELDNAME == "dispatchaddress": d["dispatchaddress"] = truncs(f.VALUE)
        if f.FIELDNAME == "dispatchcity": d["dispatchtown"] = truncs(f.VALUE)
        if f.FIELDNAME == "dispatchstate": d["dispatchcounty"] = truncs(f.VALUE)
        if f.FIELDNAME == "dispatchzipcode": d["dispatchpostcode"] = truncs(f.VALUE)
        if f.FIELDNAME.startswith("additional"): d[f.FIELDNAME] = f.VALUE
    # Have we got enough info to create the animal control record? We need notes and dispatchaddress
    if "callnotes" not in d or "dispatchaddress" not in d:
        raise asm3.utils.ASMValidationError(asm3.i18n._("There is not enough information in the form to create an incident record (need call notes and dispatch address).", l))
    # If we have person info, create that person as the caller
    if has_person:
        collationid, personid, personname, status = create_person(dbo, username, collationid)
        d["caller"] = personid
    # Create the incident
    incidentid = asm3.animalcontrol.insert_animalcontrol_from_form(dbo, asm3.utils.PostedData(d, dbo.locale), username)
    asm3.additional.merge_values_for_link(dbo, asm3.utils.PostedData(d, dbo.locale), username, incidentid, "incident")
    attach_form(dbo, username, asm3.media.ANIMALCONTROL, incidentid, collationid)
    display = "%s - %s" % (asm3.utils.padleft(incidentid, 6), asm3.utils.truncate(d["dispatchaddress"], 20))
    return (collationid, incidentid, display, status)

def create_lostanimal(dbo: Database, username: str, collationid: int) -> Tuple[int, int, str, int]:
    """
    Creates a lost animal record from the incoming form data with collationid.
    Also, attaches the form to the lost animal as asm3.media.
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    d["datereported"] = asm3.i18n.python2display(l, dbo.now())
    for f in fields:
        if f.FIELDNAME == "species": d["species"] = guess_species(dbo, f.VALUE)
        if f.FIELDNAME == "sex": d["sex"] = guess_sex(dbo, f.VALUE)
        if f.FIELDNAME == "breed": d["breed"] = guess_breed(dbo, f.VALUE)
        if f.FIELDNAME == "breed1": d["breed"] = guess_breed(dbo, f.VALUE)
        if f.FIELDNAME == "agegroup": d["agegroup"] = guess_agegroup(dbo, f.VALUE)
        if f.FIELDNAME == "color": d["colour"] = guess_colour(dbo, f.VALUE)
        if f.FIELDNAME == "colour": d["colour"] = guess_colour(dbo, f.VALUE)
        if f.FIELDNAME == "description": d["markings"] = f.VALUE
        if f.FIELDNAME == "datelost": d["datelost"] = f.VALUE
        if f.FIELDNAME == "arealost": d["arealost"] = f.VALUE
        if f.FIELDNAME == "areapostcode": d["areapostcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "areazipcode": d["areapostcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "microchip": d["microchip"] = truncs(f.VALUE)
        if f.FIELDNAME == "comments": d["comments"] = f.VALUE
        if f.FIELDNAME.startswith("additional"): d[f.FIELDNAME] = f.VALUE
    if "datelost" not in d or asm3.i18n.display2python(l, d["datelost"]) is None:
        d["datelost"] = asm3.i18n.python2display(l, dbo.now())
    if "species" not in d: d["species"] = guess_species(dbo, "")
    if "sex" not in d: d["sex"] = guess_sex(dbo, "")
    if "breed" not in d: d["breed"] = guess_breed(dbo, "")
    if "agegroup" not in d: d["agegroup"] = guess_agegroup(dbo, "")
    if "colour" not in d: d["colour"] = guess_colour(dbo, "")
    # Have we got enough info to create the lost animal record? We need a description and arealost
    if "markings" not in d or "arealost" not in d:
        raise asm3.utils.ASMValidationError(asm3.i18n._("There is not enough information in the form to create a lost animal record (need a description and area lost).", l))
    # We need the person record before we create the lost animal
    collationid, personid, personname, status = create_person(dbo, username, collationid)
    d["owner"] = personid
    # Create the lost animal
    lostanimalid = asm3.lostfound.insert_lostanimal_from_form(dbo, asm3.utils.PostedData(d, dbo.locale), username)
    asm3.additional.merge_values_for_link(dbo, asm3.utils.PostedData(d, dbo.locale), username, lostanimalid, "lostanimal")
    attach_form(dbo, username, asm3.media.LOSTANIMAL, lostanimalid, collationid)
    return (collationid, lostanimalid, "%s - %s" % (asm3.utils.padleft(lostanimalid, 6), personname), status)
  
def create_foundanimal(dbo: Database, username: str, collationid: int) -> Tuple[int, int, str, int]:
    """
    Creates a found animal record from the incoming form data with collationid.
    Also, attaches the form to the found animal as asm3.media.
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    d["datereported"] = asm3.i18n.python2display(l, dbo.now())
    for f in fields:
        if f.FIELDNAME == "species": d["species"] = guess_species(dbo, f.VALUE)
        if f.FIELDNAME == "sex": d["sex"] = guess_sex(dbo, f.VALUE)
        if f.FIELDNAME == "breed": d["breed"] = guess_breed(dbo, f.VALUE)
        if f.FIELDNAME == "breed1": d["breed"] = guess_breed(dbo, f.VALUE)
        if f.FIELDNAME == "agegroup": d["agegroup"] = guess_agegroup(dbo, f.VALUE)
        if f.FIELDNAME == "color": d["colour"] = guess_colour(dbo, f.VALUE)
        if f.FIELDNAME == "colour": d["colour"] = guess_colour(dbo, f.VALUE)
        if f.FIELDNAME == "description": d["markings"] = f.VALUE
        if f.FIELDNAME == "datefound": d["datefound"] = f.VALUE
        if f.FIELDNAME == "areafound": d["areafound"] = f.VALUE
        if f.FIELDNAME == "areapostcode": d["areapostcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "areazipcode": d["areapostcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "microchip": d["microchip"] = truncs(f.VALUE)
        if f.FIELDNAME == "comments": d["comments"] = f.VALUE
        if f.FIELDNAME.startswith("additional"): d[f.FIELDNAME] = f.VALUE
    if "datefound" not in d or asm3.i18n.display2python(l, d["datefound"]) is None:
        d["datefound"] = asm3.i18n.python2display(l, dbo.now())
    if "species" not in d: d["species"] = guess_species(dbo, "")
    if "sex" not in d: d["sex"] = guess_sex(dbo, "")
    if "breed" not in d: d["breed"] = guess_breed(dbo, "")
    if "agegroup" not in d: d["agegroup"] = guess_agegroup(dbo, "")
    if "colour" not in d: d["colour"] = guess_colour(dbo, "")
    # Have we got enough info to create the found animal record? We need a description and areafound
    if "markings" not in d or "areafound" not in d:
        raise asm3.utils.ASMValidationError(asm3.i18n._("There is not enough information in the form to create a found animal record (need a description and area found).", l))
    # We need the person record before we create the found animal
    collationid, personid, personname, status = create_person(dbo, username, collationid)
    d["owner"] = personid
    # Create the found animal
    foundanimalid = asm3.lostfound.insert_foundanimal_from_form(dbo, asm3.utils.PostedData(d, dbo.locale), username)
    asm3.additional.merge_values_for_link(dbo, asm3.utils.PostedData(d, dbo.locale), username, foundanimalid, "foundanimal")
    attach_form(dbo, username, asm3.media.FOUNDANIMAL, foundanimalid, collationid)
    return (collationid, foundanimalid, "%s - %s" % (asm3.utils.padleft(foundanimalid, 6), personname), status)

def create_transport(dbo: Database, username: str, collationid: int) -> Tuple[int, int, str, int]:
    """
    Creates a transport record from the incoming form data with collationid.
    Also, attaches the form to the animal as asm3.media.
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    animalid = 0
    animalname = ""
    for f in fields:
        if f.FIELDNAME == "animalname": 
            animalname = f.VALUE
            animalid = get_animal_id_from_field(dbo, animalname)
            d["animal"] = str(animalid)
        if f.FIELDNAME == "description": d["comments"] = f.VALUE
        if f.FIELDNAME == "pickupaddress": d["pickupaddress"] = truncs(f.VALUE)
        if f.FIELDNAME == "pickupcity": d["pickuptown"] = truncs(f.VALUE)
        if f.FIELDNAME == "pickuptown": d["pickuptown"] = truncs(f.VALUE)
        if f.FIELDNAME == "pickupcounty": d["pickupcounty"] = truncs(f.VALUE)
        if f.FIELDNAME == "pickupstate": d["pickupcounty"] = truncs(f.VALUE)
        if f.FIELDNAME == "pickuppostcode": d["pickuppostcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "pickupzipcode": d["pickuppostcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "pickupcountry": d["pickupcountry"] = truncs(f.VALUE)
        if f.FIELDNAME == "pickupdate": d["pickupdate"] = f.VALUE
        if f.FIELDNAME == "pickuptime": d["pickuptime"] = f.VALUE
        if f.FIELDNAME == "dropoffaddress": d["dropoffaddress"] = truncs(f.VALUE)
        if f.FIELDNAME == "dropoffcity": d["dropofftown"] = truncs(f.VALUE)
        if f.FIELDNAME == "dropofftown": d["dropofftown"] = truncs(f.VALUE)
        if f.FIELDNAME == "dropoffcounty": d["dropoffcounty"] = truncs(f.VALUE)
        if f.FIELDNAME == "dropoffstate": d["dropoffcounty"] = truncs(f.VALUE)
        if f.FIELDNAME == "dropoffpostcode": d["dropoffpostcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "dropoffzipcode": d["dropoffpostcode"] = truncs(f.VALUE)
        if f.FIELDNAME == "dropoffcountry": d["dropoffcountry"] = truncs(f.VALUE)
        if f.FIELDNAME == "dropoffdate": d["dropoffdate"] = f.VALUE
        if f.FIELDNAME == "dropofftime": d["dropofftime"] = f.VALUE
        if f.FIELDNAME == "transporttype": d["type"] = guess_transporttype(dbo, f.VALUE)
    if "type" not in d:
        d["type"] = guess_transporttype(dbo, "nomatchesusedefault")
    # Have we got enough info to create the transport record? We need an animal to attach to
    if "animal" not in d:
        raise asm3.utils.ASMValidationError(asm3.i18n._("There is not enough information in the form to create a transport record (need animalname).", l))
    if "pickupdate" not in d or "dropoffdate" not in d or d["pickupdate"] == "" or d["dropoffdate"] == "":
        raise asm3.utils.ASMValidationError(asm3.i18n._("There is not enough information in the form to create a transport record (need pickupdate and dropoffdate).", l))
    if animalid == 0:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Could not find animal with name '{0}'", l).format(animalname))
    # Create the transport
    asm3.movement.insert_transport_from_form(dbo, username, asm3.utils.PostedData(d, dbo.locale))
    attach_form(dbo, username, asm3.media.ANIMAL, animalid, collationid)
    return (collationid, animalid, asm3.animal.get_animal_namecode(dbo, animalid))

def create_waitinglist(dbo: Database, username: str, collationid: int) -> Tuple[int, int, str, int]:
    """
    Creates a waitinglist record from the incoming form data with collationid.
    Also, attaches the form to the waiting list as asm3.media.
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    d["dateputon"] = asm3.i18n.python2display(l, dbo.now())
    d["urgency"] = str(asm3.configuration.waiting_list_default_urgency(dbo))
    for f in fields:
        if f.FIELDNAME == "animalname": d["animalname"] = f.VALUE
        if f.FIELDNAME == "dateofbirth": d["dateofbirth"] = f.VALUE
        if f.FIELDNAME == "microchip": d["microchip"] = truncs(f.VALUE)
        if f.FIELDNAME == "breed": d["breed"] = guess_breed(dbo, f.VALUE)
        if f.FIELDNAME == "breed1": d["breed"] = guess_breed(dbo, f.VALUE)
        if f.FIELDNAME == "neutered" and (f.VALUE == "Yes" or f.VALUE == "on"): d["neutered"] = "on"
        if f.FIELDNAME == "sex": d["sex"] = guess_sex(dbo, f.VALUE)
        if f.FIELDNAME == "size": d["size"] = guess_size(dbo, f.VALUE)
        if f.FIELDNAME == "species": d["species"] = guess_species(dbo, f.VALUE)
        if f.FIELDNAME == "description": d["description"] = f.VALUE
        if f.FIELDNAME == "reason": d["reasonforwantingtopart"] = f.VALUE
        if f.FIELDNAME == "comments": d["comments"] = f.VALUE
        if f.FIELDNAME.startswith("additional"): d[f.FIELDNAME] = f.VALUE
    if "breed" not in d and "breed1" not in d: d["breed"] = guess_breed(dbo, "nomatchesusedefault")
    if "size" not in d: d["size"] = guess_size(dbo, "nomatchesusedefault")
    if "species" not in d: d["species"] = guess_species(dbo, "nomatchesusedefault")
    # Have we got enough info to create the waiting list record? We need a description
    if "description" not in d:
        raise asm3.utils.ASMValidationError(asm3.i18n._("There is not enough information in the form to create a waiting list record (need a description).", l))
    # We need the person record before we create the waiting list
    collationid, personid, personname, status = create_person(dbo, username, collationid)
    d["owner"] = personid
    # Create the waiting list
    wlid = asm3.waitinglist.insert_waitinglist_from_form(dbo, asm3.utils.PostedData(d, dbo.locale), username)
    asm3.additional.merge_values_for_link(dbo, asm3.utils.PostedData(d, dbo.locale), username, wlid, "waitinglist")
    attach_form(dbo, username, asm3.media.WAITINGLIST, wlid, collationid)
    return (collationid, wlid, "%s - %s" % (asm3.utils.padleft(wlid, 6), personname), status)

def auto_remove_old_incoming_forms(dbo: Database) -> None:
    """
    Automatically removes incoming forms older than the daily amount set
    """
    removeafter = asm3.configuration.auto_remove_incoming_forms_days(dbo)
    if removeafter <= 0:
        asm3.al.debug("auto remove incoming forms is off.", "onlineform.auto_remove_old_incoming_forms", dbo)
        return
    removecutoff = dbo.today(offset=removeafter*-1)
    rows = dbo.query("SELECT DISTINCT(CollationID) FROM onlineformincoming WHERE PostedDate < %s" % dbo.sql_date(removecutoff))
    for r in rows:
        delete_onlineformincoming(dbo, "system", r.COLLATIONID)
    asm3.al.debug("removed %s incoming forms older than %s days" % (len(rows), removeafter), "onlineform.auto_remove_old_incoming_forms", dbo)

