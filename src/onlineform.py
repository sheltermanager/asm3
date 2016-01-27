#!/usr/bin/python

import al
import animal
import animalcontrol
import audit
import configuration
import db
import dbfs
import i18n
import html
import lookups
import lostfound
import media
import movement
import person
import publish
import utils
import waitinglist
from sitedefs import BASE_URL, ASMSELECT_CSS, ASMSELECT_JS, JQUERY_JS, JQUERY_UI_JS, JQUERY_UI_CSS, SIGNATURE_JS, TOUCHPUNCH_JS

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
    "LOOKUP_MULTI": 14
}

FIELDTYPE_MAP_REVERSE = {v: k for k, v in FIELDTYPE_MAP.items()}

JSKEY_NAME = 'magicASJSkey'
JSKEY_VALUE = '918273645'

# Online field names that we recognise and will attempt to map to
# known fields when importing from submitted forms
FORM_FIELDS = [
    "title", "initials", "firstname", "forenames", "surname", "lastname", "address",
    "town", "city", "county", "state", "postcode", "zipcode", "hometelephone", 
    "worktelephone", "mobiletelephone", "celltelephone", "emailaddress", "excludefrombulkemail",
    "description", "reason", "species", "breed", "agegroup", "color", "colour", 
    "arealost", "areafound", "areapostcode", "areazipcode",
    "animalname", "reserveanimalname",
    "callnotes", "dispatchaddress", "dispatchcity", "dispatchstate", "dispatchzipcode"
]

def get_onlineform(dbo, formid):
    """ Returns the online form with ID formid """
    of = db.query(dbo, "SELECT * FROM onlineform WHERE ID = %d" % utils.cint(formid))
    if len(of) == 0: 
        return None
    return of[0]

def get_onlineforms(dbo):
    """ Return all online forms """
    return db.query(dbo, "SELECT *, (SELECT COUNT(*) FROM onlineformfield WHERE OnlineFormID = onlineform.ID) AS NumberOfFields FROM onlineform ORDER BY Name")

def get_onlineform_html(dbo, formid, completedocument = True):
    """ Get the selected online form as HTML """
    h = []
    l = dbo.locale
    form = db.query(dbo, "SELECT * FROM onlineform WHERE ID = %d" % formid)
    if len(form) == 0:
        raise utils.ASMValidationError("Online form %d does not exist")
    form = form[0]
    formfields = get_onlineformfields(dbo, formid)
    # If a date field has been used, we need to pull jquery ui into the header
    # and have it applied to all date fields.
    needjqui = False
    for f in formfields:
        if f["FIELDTYPE"] == FIELDTYPE_DATE or f["FIELDTYPE"] == FIELDTYPE_SIGNATURE or f["FIELDTYPE"] == FIELDTYPE_LOOKUP_MULTI:
            needjqui = True
    if completedocument:
        header = get_onlineform_header(dbo)
        if needjqui:
            df = i18n.get_display_date_format(l)
            df = df.replace("%Y", "yy").replace("%m", "mm").replace("%d", "dd")
            header = header.replace("</head>", """
                %s
                <script>
                $(document).ready(function() {
                    $(".asm-onlineform-date").datepicker({ dateFormat: '%s' });
                    try {
                        $(".asm-onlineform-signature").signature({ guideline: true });
                        $(".asm-onlineform-signature-clear").click(function() {
                            var signame = $(this).attr("data-clear");
                            $("div[data-name='" + signame + "']").signature("clear");
                        });
                    } catch (ex) {}
                    $(".asm-onlineform-lookupmulti").asmSelect({
                        animate: true,
                        sortable: true,
                        removeLabel: '<strong>&times;</strong>',
                        listClass: 'bsmList-custom',  
                        listItemClass: 'bsmListItem-custom',
                        listItemLabelClass: 'bsmListItemLabel-custom',
                        removeClass: 'bsmListItemRemove-custom'
                    });
                    $("input[type='submit']").click(function() {
                        var rv;
                        $(".asm-onlineform-signature").each(function() {
                            try {
                                var img = $(this).find("canvas").get(0).toDataURL("image/png");
                                var fieldname = $(this).attr("data-name");
                                $("input[name='" + fieldname + "']").val(img);
                                if ($(this).signature("isEmpty") && $(this).parent().find(".asm-onlineform-required").length > 0) {
                                    alert("Signature is required.");
                                    rv = false;
                                }
                            }
                            catch (exo) {
                                if (window.console) { console.log(exo); }
                            }
                        });
                        $(".asm-onlineform-lookupmulti").each(function() {
                            var fieldname = $(this).attr("data-name"),
                                v = $(this).val();
                            $("input[name='" + fieldname + "']").val(v);
                            if (!v) {
                                alert("You must choose at least one option");
                                rv = false;
                            }

                        });
                        return rv;
                    });
                });
                </script>
                </head>""" % (html.css_tag(JQUERY_UI_CSS.replace("%(theme)s", "smoothness")) + \
                    html.css_tag(ASMSELECT_CSS) + \
                    html.script_tag(JQUERY_JS) + \
                    html.script_tag(JQUERY_UI_JS) + \
                    html.script_tag(TOUCHPUNCH_JS) + \
                    html.script_tag(SIGNATURE_JS) + \
                    html.script_tag(ASMSELECT_JS),
                    df))
        h.append(header.replace("$$TITLE$$", form["NAME"]))
        h.append('<h2 class="asm-onlineform-title">%s</h2>' % form["NAME"])
        if form["DESCRIPTION"] is not None and form["DESCRIPTION"] != "":
            h.append('<p class="asm-onlineform-description">%s</p>' % form["DESCRIPTION"])
        h.append(utils.nulltostr(form["HEADER"]))
    h.append('<form action="%s/service" method="post" accept-charset="utf-8">' % BASE_URL)
    h.append('<input type="hidden" name="method" value="online_form_post" />')
    h.append('<input type="hidden" name="account" value="%s" />' % dbo.alias)
    h.append('<input type="hidden" name="redirect" value="%s" />' % form["REDIRECTURLAFTERPOST"])
    h.append('<input type="hidden" name="flags" value="%s" />' % form["SETOWNERFLAGS"])
    h.append('<input type="hidden" name="formname" value="%s" />' % html.escape(form["NAME"]))
    h.append('<table class="asm-onlineform-table">')
    for f in formfields:
        fname = f["FIELDNAME"] + "_" + str(f["ID"])
        h.append('<tr class="asm-onlineform-tr">')
        if f["FIELDTYPE"] == FIELDTYPE_RAWMARKUP:
            h.append('<td class="asm-onlineform-td" colspan="2">')
        elif f["FIELDTYPE"] == FIELDTYPE_CHECKBOX:
            h.append('<td class="asm-onlineform-td"></td><td class="asm-onlineform-td">')
        else:
            # Add label and cell wrapper if it's not raw markup or a checkbox
            h.append('<td class="asm-onlineform-td">')
            h.append('<label for="f%d">%s</label>' % ( f["ID"], f["LABEL"] ))
            h.append('</td>')
            h.append('<td class="asm-onlineform-td">')
        required = ""
        if f["MANDATORY"] == 1: 
            required = "required=\"required\""
            h.append('<span class="asm-onlineform-required" style="color: #ff0000;">*</span>')
        else:
            h.append('<span class="asm-onlineform-notrequired" style="visibility: hidden">*</span>')
        if f["FIELDTYPE"] == FIELDTYPE_YESNO:
            h.append('<select class="asm-onlineform-yesno" name="%s" title="%s"><option>%s</option><option>%s</option></select>' % \
                ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), i18n._("No", l), i18n._("Yes", l)))
        elif f["FIELDTYPE"] == FIELDTYPE_CHECKBOX:
            h.append('<input class="asm-onlineform-check" type="checkbox" name="%s" %s /> <label for="f%d">%s</label>' % \
                ( html.escape(fname), required, f["ID"], f["LABEL"]))
        elif f["FIELDTYPE"] == FIELDTYPE_TEXT:
            h.append('<input class="asm-onlineform-text" type="text" name="%s" title="%s" %s />' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), required))
        elif f["FIELDTYPE"] == FIELDTYPE_DATE:
            h.append('<input class="asm-onlineform-date" type="text" name="%s" title="%s" %s />' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), required))
        elif f["FIELDTYPE"] == FIELDTYPE_NOTES:
            h.append('<textarea class="asm-onlineform-notes" name="%s" title="%s" %s></textarea>' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), required))
        elif f["FIELDTYPE"] == FIELDTYPE_LOOKUP:
            h.append('<select class="asm-onlineform-lookup" name="%s" title="%s" %s>' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), required))
            for lv in utils.nulltostr(f["LOOKUPS"]).split("|"):
                h.append('<option>%s</option>' % lv)
            h.append('</select>')
        elif f["FIELDTYPE"] == FIELDTYPE_LOOKUP_MULTI:
            h.append('<input type="hidden" name="%s" value="" />' % html.escape(fname))
            h.append('<select class="asm-onlineform-lookupmulti" multiple="multiple" data-name="%s" title="%s">' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"])))
            for lv in utils.nulltostr(f["LOOKUPS"]).split("|"):
                h.append('<option>%s</option>' % lv)
            h.append('</select>')
        elif f["FIELDTYPE"] == FIELDTYPE_RADIOGROUP:
            h.append('<div class="asm-online-radiogroup" style="display: inline-block">')
            for lv in utils.nulltostr(f["LOOKUPS"]).split("|"):
                h.append('<input type="radio" class="asm-onlineform-radio" name="%s" value="%s" %s /> %s<br />' % (html.escape(fname), lv, required, lv))
            h.append('</div>')
        elif f["FIELDTYPE"] == FIELDTYPE_SHELTERANIMAL:
            h.append('<select class="asm-onlineform-shelteranimal" name="%s" title="%s" %s>' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), required))
            h.append('<option></option>')
            for a in animal.get_animals_on_shelter_namecode(dbo):
                h.append('<option value="%(name)s::%(code)s">%(name)s (%(code)s)</option>' % { "name": a["ANIMALNAME"], "code": a["SHELTERCODE"]})
            h.append('</select>')
        elif f["FIELDTYPE"] == FIELDTYPE_ADOPTABLEANIMAL:
            h.append('<select class="asm-onlineform-adoptableanimal" name="%s" title="%s" %s>' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), required))
            h.append('<option></option>')
            pc = publish.PublishCriteria(configuration.publisher_presets(dbo))
            rs = publish.get_animal_data(dbo, pc, True)
            for a in rs:
                h.append('<option value="%(name)s::%(code)s">%(name)s (%(code)s)</option>' % { "name": a["ANIMALNAME"], "code": a["SHELTERCODE"]})
            h.append('</select>')
        elif f["FIELDTYPE"] == FIELDTYPE_COLOUR:
            h.append('<select class="asm-onlineform-colour" name="%s" title="%s" %s>' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), required))
            for l in lookups.get_basecolours(dbo):
                h.append('<option>%s</option>' % l["BASECOLOUR"])
            h.append('</select>')
        elif f["FIELDTYPE"] == FIELDTYPE_BREED:
            h.append('<select class="asm-onlineform-breed" name="%s" title="%s" %s>' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), required))
            for l in lookups.get_breeds(dbo):
                h.append('<option>%s</option>' % l["BREEDNAME"])
            h.append('</select>')
        elif f["FIELDTYPE"] == FIELDTYPE_SPECIES:
            h.append('<select class="asm-onlineform-species" name="%s" title="%s" %s>' % ( html.escape(fname), utils.nulltostr(f["TOOLTIP"]), required))
            for l in lookups.get_species(dbo):
                h.append('<option>%s</option>' % l["SPECIESNAME"])
            h.append('</select>')
        elif f["FIELDTYPE"] == FIELDTYPE_RAWMARKUP:
            h.append('<input type="hidden" name="%s" value="raw" />' % html.escape(fname))
            h.append(utils.nulltostr(f["TOOLTIP"]))
        elif f["FIELDTYPE"] == FIELDTYPE_SIGNATURE:
            h.append('<input type="hidden" name="%s" value="" />' % html.escape(fname))
            h.append('<div class="asm-onlineform-signature" style="width: 500px; height: 200px" data-name="%s"></div>' % ( html.escape(fname) ))
            h.append('<br/><button type="button" class="asm-onlineform-signature-clear" data-clear="%s">%s</button>' % ( html.escape(fname), i18n._("Clear", l) ))
        h.append('</td>')
        h.append('</tr>')
    h.append('</table>')
    if configuration.online_form_verify_jskey(dbo):
        h.append('<script>')
        h.append('document.write("<input " + \n"type=" + "\'hidden\'" + \n" name=" + "\'%s\'" + \n" value=" + "\'%s\'" + " />");' % (JSKEY_NAME, JSKEY_VALUE))
        h.append('</script>')
    h.append('<p style="text-align: center"><input type="submit" value="Submit" /></p>')
    h.append('</form>')
    if completedocument:
        h.append(utils.nulltostr(form["FOOTER"]))
        footer = get_onlineform_footer(dbo)
        h.append(footer.replace("$$TITLE$$", form["NAME"]))
    return "\n".join(h)

def get_onlineform_json(dbo, formid):
    """
    Get the selected online form as a JSON document
    """
    form = db.query(dbo, "SELECT * FROM onlineform WHERE ID = %d" % formid)
    if len(form) == 0:
        raise utils.ASMValidationError("Online form %d does not exist")
    form = form[0]
    formfields = get_onlineformfields(dbo, formid)
    fd = { "name": form["NAME"], "description": form["DESCRIPTION"] }
    ff = []
    for f in formfields:
        ff.append({ "name": f["FIELDNAME"], "label": f["LABEL"], "type": FIELDTYPE_MAP_REVERSE[f["FIELDTYPE"]],
            "mandatory": utils.iif(f["MANDATORY"] == 1, True, False), "index": f["DISPLAYINDEX"],
            "lookups": f["LOOKUPS"], "tooltip": f["TOOLTIP"]})
    fd["fields"] = ff
    return html.json(fd, True)

def import_onlineform_json(dbo, j):
    """
    Imports an online form from a JSON document
    """
    fd = html.json_parse(j)
    data = {
        "name": fd["name"],
        "description": fd["description"]
    }
    fid = insert_onlineform_from_form(dbo, "import", utils.PostedData(data, dbo.locale))
    for f in fd["fields"]:
        data = { "formid": str(fid),
            "fieldname": f["name"],
            "fieldtype": str(FIELDTYPE_MAP[f["type"]]),
            "label": f["label"],
            "displayindex": f["index"],
            "mandatory": utils.iif(f["mandatory"], "1", "0"),
            "lookups": f["lookups"],
            "tooltip": f["tooltip"]
        }
        insert_onlineformfield_from_form(dbo, "import", utils.PostedData(data, dbo.locale))

def get_onlineform_header(dbo):
    header = dbfs.get_string_filepath(dbo, "/onlineform/head.html")
    if header == "": header = "<!DOCTYPE html>\n" \
        "<html>\n" \
       "<head>\n" \
       "<title>$$TITLE$$</title>\n" \
       "<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />\n" \
       "<link type=\"text/css\" href=\"https://fonts.googleapis.com/css?family=Lato:400,700|Roboto+Slab:400,700|Inconsolata:400,700\" rel=\"stylesheet\">\n" \
       "<style>\n" \
       "body { font-family: \"Lato\",\"proxima-nova\",\"Helvetica Neue\",Arial,sans-serif; }\n" \
       "input:focus, textarea:focus, select:focus { box-shadow: 0 0 5px #3a87cd; border: 1px solid #3a87cd; }\n" \
       "input, textarea, select { border: 1px solid #aaa; }\n" \
       ".asm-onlineform-title, .asm-onlineform-description { text-align: center; }\n" \
       ".asm-onlineform-table { margin-left: auto; margin-right: auto }\n" \
       ".asm-onlineform-td:first-child { max-width: 200px; }\n" \
       ".asm-onlineform-td:nth-child(2) { white-space: nowrap; }\n" \
       "textarea { width: 300px; height: 150px; }\n" \
       "</style>\n" \
       "</head>\n" \
       "<body>"
    return header

def get_onlineform_footer(dbo):
    footer = dbfs.get_string_filepath(dbo, "/onlineform/foot.html")
    if footer == "": footer = "</body>\n</html>"
    return footer

def get_onlineform_name(dbo, formid):
    """ Returns the name of a form """
    return db.query_string(dbo, "SELECT Name FROM onlineform WHERE ID = %d" % int(formid))

def get_onlineformfields(dbo, formid):
    """ Return all fields for a form """
    return db.query(dbo, "SELECT * FROM onlineformfield WHERE OnlineFormID=%d ORDER BY DisplayIndex" % formid)

def get_onlineformincoming_formheader(dbo, collationid):
    """
    Given a collation id for an incoming form, try and find the
    original onlineform header.
    """
    return db.query_string(dbo, "SELECT o.Header FROM onlineform o " \
        "INNER JOIN onlineformincoming oi ON oi.FormName = o.Name " \
        "WHERE oi.CollationID = %d" % int(collationid))

def get_onlineformincoming_formfooter(dbo, collationid):
    """
    Given a collation id for an incoming form, try and find the
    original onlineform footer.
    """
    return db.query_string(dbo, "SELECT o.Footer FROM onlineform o " \
        "INNER JOIN onlineformincoming oi ON oi.FormName = o.Name " \
        "WHERE oi.CollationID = %d" % int(collationid))

def get_onlineformincoming_headers(dbo):
    """ Returns all incoming form posts """
    return db.query(dbo, "SELECT DISTINCT f.CollationID, f.FormName, f.PostedDate, f.Host, f.Preview " \
        "FROM onlineformincoming f ORDER BY f.PostedDate")

def get_onlineformincoming_detail(dbo, collationid):
    """ Returns the detail lines for an incoming post """
    return db.query(dbo, "SELECT * FROM onlineformincoming WHERE CollationID = %d ORDER BY DisplayIndex" % int(collationid))

def get_onlineformincoming_html(dbo, collationid, includeRaw = False):
    """ Returns an HTML fragment of the incoming form data """
    h = []
    h.append('<table width="100%">')
    for f in get_onlineformincoming_detail(dbo, collationid):
        label = f["LABEL"]
        if label is None or label == "": label = f["FIELDNAME"]
        v = f["VALUE"]
        if v.startswith("RAW::") and not includeRaw: 
            continue
        if v.startswith("RAW::"): 
            h.append('<tr>')
            h.append('<td colspan="2">%s</td>' % v[5:])
            h.append('</tr>')
        elif v.startswith("data:"):
            h.append('<tr>')
            h.append('<td>%s</td>' % label )
            h.append('<td><img src="%s" border="0" /></td>' % v)
            h.append('</tr>')
        else:
            h.append('<tr>')
            h.append('<td>%s</td>' % label )
            h.append('<td>%s</td>' % v)
            h.append('</tr>')
    h.append('</table>')
    return "\n".join(h)

def get_onlineformincoming_plain(dbo, collationid):
    """ Returns a plain text fragment of the incoming form data """
    h = []
    for f in get_onlineformincoming_detail(dbo, collationid):
        if f["VALUE"].startswith("RAW::") or f["VALUE"].startswith("data:"): continue
        label = f["LABEL"]
        if label is None or label == "": label = f["FIELDNAME"]
        h.append("%s: %s\n" % (label, f["VALUE"]))
    return "\n".join(h)

def get_onlineformincoming_html_print(dbo, ids):
    """
    Returns a complete printable version of the online form
    (header/footer wrapped around the html call above)
    ids: A list of integer ids
    """
    header = get_onlineform_header(dbo)
    headercontent = header[header.find("<body>")+6:]
    header = header[0:header.find("<body>")+6]
    footer = get_onlineform_footer(dbo)
    footercontent = footer[0:footer.find("</body>")]
    h = []
    h.append(header)
    for i, collationid in enumerate(ids):
        h.append(headercontent)
        formheader = get_onlineformincoming_formheader(dbo, collationid)
        h.append(formheader)
        h.append(get_onlineformincoming_html(dbo, utils.cint(collationid), True))
        formfooter = get_onlineformincoming_formfooter(dbo, collationid)
        h.append(formfooter)
        h.append(footercontent)
        if i < len(ids)-1:
            h.append('<div style="page-break-before: always;"></div>')
    h.append("</body></html>")
    return "\n".join(h)

def get_onlineformincoming_name(dbo, collationid):
    """ Returns the form name for a collation id """
    return db.query_string(dbo, "SELECT FormName FROM onlineformincoming WHERE CollationID = %d LIMIT 1" % int(collationid))

def insert_onlineform_from_form(dbo, username, post):
    """
    Create an onlineform record from posted data
    """
    formid = db.get_id(dbo, "onlineform")
    sql = db.make_insert_sql("onlineform", ( 
        ( "ID", db.di(formid)),
        ( "Name", post.db_string("name")),
        ( "RedirectUrlAfterPOST", post.db_string("redirect")),
        ( "SetOwnerFlags", post.db_string("flags")),
        ( "EmailAddress", post.db_string("email")),
        ( "Header", db.ds(post["header"], False) ),
        ( "Footer", db.ds(post["footer"], False) ),
        ( "Description", db.ds(post["description"], False) )
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "onlineform", str(formid))
    return formid

def update_onlineform_from_form(dbo, username, post):
    """
    Update an onlineform record from posted data
    """
    formid = post.integer("formid")
    sql = db.make_update_sql("onlineform", "ID=%d" % formid, ( 
        ( "Name", post.db_string("name")),
        ( "RedirectUrlAfterPOST", post.db_string("redirect")),
        ( "SetOwnerFlags", post.db_string("flags")),
        ( "EmailAddress", post.db_string("email")),
        ( "Header", db.ds(post["header"], False) ),
        ( "Footer", db.ds(post["footer"], False) ),
        ( "Description", db.ds(post["description"], False) )
        ))
    preaudit = db.query(dbo, "SELECT * FROM onlineform WHERE ID = %d" % formid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM onlineform WHERE ID = %d" % formid)
    audit.edit(dbo, username, "onlineform", audit.map_diff(preaudit, postaudit))

def delete_onlineform(dbo, username, formid):
    """
    Deletes the specified onlineform and fields
    """
    audit.delete(dbo, username, "onlineform", str(db.query(dbo, "SELECT * FROM onlineform WHERE ID=%d" % int(formid))))
    db.execute(dbo, "DELETE FROM onlineformfield WHERE OnlineFormID = %d" % int(formid))
    db.execute(dbo, "DELETE FROM onlineform WHERE ID = %d" % int(formid))

def clone_onlineform(dbo, username, formid):
    l = dbo.locale
    f = get_onlineform(dbo, formid)
    nfid = db.get_id(dbo, "onlineform")
    if f is None: return
    sql = db.make_insert_sql("onlineform", ( 
        ( "ID", db.di(nfid)),
        ( "Name", db.ds( i18n._("Copy of {0}", l).format(f["NAME"]))),
        ( "RedirectUrlAfterPOST", db.ds(f["REDIRECTURLAFTERPOST"])),
        ( "SetOwnerFlags", db.ds(f["SETOWNERFLAGS"])),
        ( "EmailAddress", db.ds(f["EMAILADDRESS"])),
        ( "Header", db.ds(f["HEADER"], False)),
        ( "Footer", db.ds(f["FOOTER"], False)),
        ( "Description", db.ds(f["DESCRIPTION"], False))
        ))
    db.execute(dbo, sql)
    for ff in get_onlineformfields(dbo, formid):
        formfieldid = db.get_id(dbo, "onlineformfield")
        sql = db.make_insert_sql("onlineformfield", ( 
            ( "ID", db.di(formfieldid)),
            ( "OnlineFormID", db.di(nfid)),
            ( "FieldName", db.ds(ff["FIELDNAME"])),
            ( "FieldType", db.di(ff["FIELDTYPE"])),
            ( "Label", db.ds(ff["LABEL"])),
            ( "DisplayIndex", db.di(ff["DISPLAYINDEX"])),
            ( "Mandatory", db.di(ff["MANDATORY"])),
            ( "Lookups", db.ds(ff["LOOKUPS"])),
            ( "Tooltip", db.ds(ff["TOOLTIP"]))
            ))
        db.execute(dbo, sql)
    audit.create(dbo, username, "onlineform", str(nfid) + " cloned from " + str(formid))

def insert_onlineformfield_from_form(dbo, username, post):
    """
    Create an onlineformfield record from posted data
    """
    formfieldid = db.get_id(dbo, "onlineformfield")
    sql = db.make_insert_sql("onlineformfield", ( 
        ( "ID", db.di(formfieldid)),
        ( "OnlineFormID", post.db_integer("formid")),
        ( "FieldName", post.db_string("fieldname")),
        ( "FieldType", post.db_integer("fieldtype")),
        ( "Label", post.db_string("label")),
        ( "DisplayIndex", post.db_integer("displayindex")),
        ( "Mandatory", post.db_boolean("mandatory")),
        ( "Lookups", post.db_string("lookups")),
        ( "Tooltip", db.ds(post["tooltip"], False))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "onlineformfield", str(formfieldid))
    return formfieldid

def update_onlineformfield_from_form(dbo, username, post):
    """
    Update an onlineformfield record from posted data
    """
    formfieldid = post.integer("formfieldid")
    sql = db.make_update_sql("onlineformfield", "ID=%d" % formfieldid, ( 
        ( "FieldName", post.db_string("fieldname")),
        ( "FieldType", post.db_integer("fieldtype")),
        ( "Label", post.db_string("label")),
        ( "DisplayIndex", post.db_integer("displayindex")),
        ( "Mandatory", post.db_boolean("mandatory")),
        ( "Lookups", post.db_string("lookups")),
        ( "Tooltip", db.ds(post["tooltip"], False))
        ))
    preaudit = db.query(dbo, "SELECT * FROM onlineformfield WHERE ID = %d" % formfieldid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM onlineformfield WHERE ID = %d" % formfieldid)
    audit.edit(dbo, username, "onlineformfield", audit.map_diff(preaudit, postaudit))

def delete_onlineformfield(dbo, username, fieldid):
    """
    Deletes the specified onlineformfield
    """
    audit.delete(dbo, username, "onlineformfield", str(db.query(dbo, "SELECT * FROM onlineformfield WHERE ID=%d" % int(fieldid))))
    db.execute(dbo, "DELETE FROM onlineformfield WHERE ID = %d" % int(fieldid))

def insert_onlineformincoming_from_form(dbo, post, remoteip):
    """
    Create onlineformincoming records from posted data. We 
    create a row for every key/value pair in the posted data
    with a unique collation ID.
    """
    # If we are using a js generated field to protect against
    # spambots, verify it is there
    if configuration.online_form_verify_jskey(dbo):
        if post[JSKEY_NAME] != JSKEY_VALUE:
            raise utils.ASMValidationError("Invalid verification key")
    IGNORE_FIELDS = [ JSKEY_NAME, "formname", "flags", "redirect", "account", "filechooser", "method", "asmSelect0", "asmSelect1", "asmSelect2" ]
    l = dbo.locale
    collationid = db.query_int(dbo, "SELECT MAX(CollationID) FROM onlineformincoming") + 1
    formname = post["formname"]
    posteddate = i18n.now(dbo.timezone)
    flags = post["flags"]
    submitteremail = ""
    for k, v in post.data.iteritems():
        if k not in IGNORE_FIELDS:
            label = ""
            displayindex = 0
            fieldname = k
            # Form fields should have a _ONLINEFORMFIELD.ID suffix we can use to get the
            # original label and display position.
            if k.find("_") != -1:
                fid = utils.cint(k[k.rfind("_")+1:])
                fieldname = k[0:k.rfind("_")]
                if fieldname == "emailaddress": submitteremail = v.strip()
                if fid != 0:
                    fld = db.query(dbo, "SELECT FieldType, Label, Tooltip, DisplayIndex FROM onlineformfield WHERE ID = %d" % fid)
                    if len(fld) > 0:
                        label = fld[0]["LABEL"]
                        displayindex = fld[0]["DISPLAYINDEX"]
                        # If it's a raw markup field, store the markup as the value
                        if fld[0]["FIELDTYPE"] == FIELDTYPE_RAWMARKUP:
                            v = "RAW::%s" % fld[0]["TOOLTIP"]
                        # If we have a checkbox field with a tooltip, it contains additional
                        # person flags, add them to our set
                        if fld[0]["FIELDTYPE"] == FIELDTYPE_CHECKBOX:
                            if utils.nulltostr(fld[0]["TOOLTIP"]) != "":
                                flags += fld[0]["TOOLTIP"]
                                db.execute(dbo, "UPDATE onlineformincoming SET Flags = %s WHERE CollationID = %d" % (db.ds(flags), collationid))
            # Do the insert
            sql = db.make_insert_sql("onlineformincoming", ( 
                ( "CollationID", db.di(collationid)),
                ( "FormName", db.ds(formname)),
                ( "PostedDate", db.ddt(posteddate)),
                ( "Flags", db.ds(flags)),
                ( "FieldName", db.ds(fieldname)),
                ( "Label", db.ds(label)),
                ( "DisplayIndex", db.di(displayindex)),
                ( "Host", db.ds(remoteip)),
                ( "Value", utils.iif(fld[0]["FIELDTYPE"] == FIELDTYPE_RAWMARKUP, db.ds(v, False), db.ds(v)) )
                ))
            db.execute(dbo, sql)
    # Sort out the preview of the first few fields
    fieldssofar = 0
    preview = []
    for fld in get_onlineformincoming_detail(dbo, collationid):
        if fieldssofar < 3:
            # Don't include raw markup or signature fields in the preview
            if fld["VALUE"].startswith("RAW::") or fld["VALUE"].startswith("data:"): continue
            fieldssofar += 1
            preview.append( fld["LABEL"] + ": " + fld["VALUE"] )
    db.execute(dbo, "UPDATE onlineformincoming SET Preview = %s WHERE CollationID = %s" % ( db.ds(", ".join(preview)), db.di(collationid) ))
    # Do we have a valid emailaddress for the submitter? If so, send them a copy
    # of their submission
    if submitteremail != "" and submitteremail.find("@") != -1:
        utils.send_email(dbo, configuration.email(dbo), submitteremail, "", i18n._("Submission received: {0}", l).format(formname), 
            get_onlineformincoming_html_print(dbo, [collationid,]), "html")
    # Did the original form specify some email addresses to send 
    # incoming submissions to?
    email = db.query_string(dbo, "SELECT o.EmailAddress FROM onlineform o " \
        "INNER JOIN onlineformincoming oi ON oi.FormName = o.Name " \
        "WHERE oi.CollationID = %d" % int(collationid))
    if email is not None and email.strip() != "":
        utils.send_email(dbo, configuration.email(dbo), email, "", "%s - %s" % (formname, ", ".join(preview)), 
            get_onlineformincoming_html_print(dbo, [collationid,]), "html")
    return collationid

def delete_onlineformincoming(dbo, username, collationid):
    """
    Deletes the specified onlineformincoming set
    """
    audit.delete(dbo, username, "onlineformincoming", str(db.query(dbo, "SELECT * FROM onlineformincoming WHERE CollationID=%d" % int(collationid))))
    db.execute(dbo, "DELETE FROM onlineformincoming WHERE CollationID = %d" % int(collationid))

def guess_agegroup(dbo, s):
    """ Guesses an agegroup, returns the default if no match is found """
    s = str(s).lower()
    guess = db.query_string(dbo, "SELECT ItemValue FROM configuration WHERE ItemName LIKE 'AgeGroup%Name' AND LOWER(ItemValue) LIKE '%" + db.escape(s) + "%'")
    if guess != "": return guess
    return db.query_string(dbo, "SELECT ItemValue FROM configuration WHERE ItemName LIKE 'AgeGroup2Name'")

def guess_breed(dbo, s):
    """ Guesses a breed, returns the default if no match is found """
    s = str(s).lower()
    guess = db.query_int(dbo, "SELECT ID FROM breed WHERE LOWER(BreedName) LIKE '%" + db.escape(s) + "%'")
    if guess != 0: return guess
    return configuration.default_breed(dbo)

def guess_colour(dbo, s):
    """ Guesses a colour, returns the default if no match is found """
    s = str(s).lower()
    guess = db.query_int(dbo, "SELECT ID FROM basecolour WHERE LOWER(BaseColour) LIKE '%" + db.escape(s) + "%'")
    if guess != 0: return guess
    return configuration.default_colour(dbo)

def guess_sex(dummy, s):
    """ Guesses a sex """
    if s.lower().startswith("M"):
        return 1
    return 0

def guess_species(dbo, s):
    """ Guesses a species, returns the default if no match is found """
    s = str(s).lower()
    guess = db.query_int(dbo, "SELECT ID FROM species WHERE LOWER(SpeciesName) LIKE '%" + db.escape(s) + "%'")
    if guess != 0: return guess
    return configuration.default_species(dbo)

def attach_animal(dbo, username, collationid):
    """
    Finds the existing shelter animal with "animalname" and
    attaches the form to it as person media.
    Return value is a tuple of collationid, animalid, animal code/name
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    animalname = ""
    sheltercode = ""
    for f in fields:
        if f["FIELDNAME"] == "animalname": 
            bits = f["VALUE"].split("::")
            if len(bits) == 2:
                animalname = bits[0]
                sheltercode = bits[1]
    if sheltercode == "" or animalname == "":
        raise utils.ASMValidationError(i18n._("There is not enough information in the form to attach to a shelter animal record (need an animal name).", l))
    # Find the animal
    aid = db.query_int(dbo, "SELECT ID FROM animal WHERE ShelterCode = '%s' ORDER BY ID DESC" % sheltercode)
    if aid == 0:
        raise utils.ASMValidationError(i18n._("Could not find animal with name '{0}'", l).format(animalname))
    formname = get_onlineformincoming_name(dbo, collationid)
    formhtml = get_onlineformincoming_html_print(dbo, [collationid,])
    media.create_document_media(dbo, username, media.ANIMAL, aid, formname, formhtml )
    return (collationid, aid, animal.get_animal_namecode(dbo, aid))

def create_person(dbo, username, collationid):
    """
    Creates a person record from the incoming form data with collationid.
    Also, attaches the form to the person as media.
    The return value is tuple of collationid, personid, personname
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    flags = None
    for f in fields:
        if flags is None: flags = f["FLAGS"]
        if f["FIELDNAME"] == "title": d["title"] = f["VALUE"]
        if f["FIELDNAME"] == "forenames": d["forenames"] = f["VALUE"]
        if f["FIELDNAME"] == "firstname": d["forenames"] = f["VALUE"]
        if f["FIELDNAME"] == "surname": d["surname"] = f["VALUE"]
        if f["FIELDNAME"] == "lastname": d["surname"] = f["VALUE"]
        if f["FIELDNAME"] == "address": d["address"] = f["VALUE"]
        if f["FIELDNAME"] == "town": d["town"] = f["VALUE"]
        if f["FIELDNAME"] == "city": d["town"] = f["VALUE"]
        if f["FIELDNAME"] == "county": d["county"] = f["VALUE"]
        if f["FIELDNAME"] == "state": d["county"] = f["VALUE"]
        if f["FIELDNAME"] == "postcode": d["postcode"] = f["VALUE"]
        if f["FIELDNAME"] == "zipcode": d["postcode"] = f["VALUE"]
        if f["FIELDNAME"] == "hometelephone": d["hometelephone"] = f["VALUE"]
        if f["FIELDNAME"] == "worktelephone": d["worktelephone"] = f["VALUE"]
        if f["FIELDNAME"] == "mobiletelephone": d["mobiletelephone"] = f["VALUE"]
        if f["FIELDNAME"] == "celltelephone": d["mobiletelephone"] = f["VALUE"]
        if f["FIELDNAME"] == "emailaddress": d["emailaddress"] = f["VALUE"]
        if f["FIELDNAME"] == "excludefrombulkemail" and f["VALUE"] != "" and f["VALUE"] != i18n._("No", l): d["excludefrombulkemail"] = "on"
        if f["FIELDNAME"].startswith("reserveanimalname"): d[f["FIELDNAME"]] = f["VALUE"]
    d["flags"] = flags
    # Have we got enough info to create the person record? We just need a surname
    if not d.has_key("surname"):
        raise utils.ASMValidationError(i18n._("There is not enough information in the form to create a person record (need a surname).", l))
    # Does this person already exist?
    personid = 0
    if d.has_key("surname") and d.has_key("forenames") and d.has_key("address"):
        similar = person.get_person_similar(dbo, d["surname"], d["forenames"], d["address"])
        if len(similar) > 0:
            personid = similar[0]["ID"]
            # Merge flags and any extra details
            person.merge_flags(dbo, username, personid, flags)
            person.merge_person_details(dbo, username, personid, d)
    # Create the person record if we didn't find one
    if personid == 0:
        personid = person.insert_person_from_form(dbo, utils.PostedData(d, dbo.locale), username)
    personname = person.get_person_name_code(dbo, personid)
    # Attach the form to the person
    formname = get_onlineformincoming_name(dbo, collationid)
    formhtml = get_onlineformincoming_html_print(dbo, [collationid,])
    media.create_document_media(dbo, username, media.PERSON, personid, formname, formhtml )
    # Was there a reserveanimalname field? If so, create reservation(s) to the person if possible
    for k, v in d.iteritems():
        if k.startswith("reserveanimalname"):
            movement.insert_reserve_for_animal_name(dbo, username, personid, v)
    return (collationid, personid, personname)

def create_animalcontrol(dbo, username, collationid):
    """
    Creates a animal control/incident record from the incoming form data with 
    collationid.
    Also, attaches the form to the incident as media.
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    d["incidentdate"] = i18n.python2display(l, i18n.now(dbo.timezone))
    d["incidenttime"] = i18n.format_time_now(dbo.timezone)
    d["calldate"] = d["incidentdate"]
    d["calltime"] = d["incidenttime"]
    d["incidenttype"] = 1
    for f in fields:
        if f["FIELDNAME"] == "callnotes": d["callnotes"] = f["VALUE"]
        if f["FIELDNAME"] == "dispatchaddress": d["dispatchaddress"] = f["VALUE"]
        if f["FIELDNAME"] == "dispatchcity": d["dispatchtown"] = f["VALUE"]
        if f["FIELDNAME"] == "dispatchstate": d["dispatchcounty"] = f["VALUE"]
        if f["FIELDNAME"] == "dispatchzipcode": d["dispatchpostcode"] = f["VALUE"]
    # Have we got enough info to create the animal control record? We need notes and dispatchaddress
    if not d.has_key("callnotes") or not d.has_key("dispatchaddress"):
        raise utils.ASMValidationError(i18n._("There is not enough information in the form to create an incident record (need call notes and dispatch address).", l))
    # We need the person/caller record before we create the incident
    collationid, personid, personname = create_person(dbo, username, collationid)
    d["caller"] = personid
    # Create the incident 
    incidentid = animalcontrol.insert_animalcontrol_from_form(dbo, utils.PostedData(d, dbo.locale), username)
    # Attach the form to the incident
    formname = get_onlineformincoming_name(dbo, collationid)
    formhtml = get_onlineformincoming_html(dbo, collationid)
    media.create_document_media(dbo, username, media.ANIMALCONTROL, incidentid, formname, formhtml )
    return (collationid, incidentid, utils.padleft(incidentid, 6) + " - " + personname)

def create_lostanimal(dbo, username, collationid):
    """
    Creates a lost animal record from the incoming form data with collationid.
    Also, attaches the form to the lost animal as media.
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    d["datelost"] = i18n.python2display(l, i18n.now(dbo.timezone))
    d["datereported"] = i18n.python2display(l, i18n.now(dbo.timezone))
    for f in fields:
        if f["FIELDNAME"] == "species": d["species"] = guess_species(dbo, f["VALUE"])
        if f["FIELDNAME"] == "sex": d["sex"] = guess_sex(dbo, f["VALUE"])
        if f["FIELDNAME"] == "breed": d["breed"] = guess_breed(dbo, f["VALUE"])
        if f["FIELDNAME"] == "agegroup": d["agegroup"] = guess_agegroup(dbo, f["VALUE"])
        if f["FIELDNAME"] == "color": d["colour"] = guess_colour(dbo, f["VALUE"])
        if f["FIELDNAME"] == "colour": d["colour"] = guess_colour(dbo, f["VALUE"])
        if f["FIELDNAME"] == "description": d["markings"] = f["VALUE"]
        if f["FIELDNAME"] == "arealost": d["arealost"] = f["VALUE"]
        if f["FIELDNAME"] == "areapostcode": d["areapostcode"] = f["VALUE"]
        if f["FIELDNAME"] == "areazipcode": d["areazipcode"] = f["VALUE"]
    if not d.has_key("species"): d["species"] = guess_species(dbo, "")
    if not d.has_key("sex"): d["sex"] = guess_sex(dbo, "")
    if not d.has_key("breed"): d["breed"] = guess_breed(dbo, "")
    if not d.has_key("agegroup"): d["agegroup"] = guess_agegroup(dbo, "")
    if not d.has_key("colour"): d["colour"] = guess_colour(dbo, "")
    # Have we got enough info to create the lost animal record? We need a description and arealost
    if not d.has_key("markings") or not d.has_key("arealost"):
        raise utils.ASMValidationError(i18n._("There is not enough information in the form to create a lost animal record (need a description and area lost).", l))
    # We need the person record before we create the lost animal
    collationid, personid, personname = create_person(dbo, username, collationid)
    d["owner"] = personid
    # Create the lost animal
    lostanimalid = lostfound.insert_lostanimal_from_form(dbo, utils.PostedData(d, dbo.locale), username)
    # Attach the form to the lost animal
    formname = get_onlineformincoming_name(dbo, collationid)
    formhtml = get_onlineformincoming_html(dbo, collationid)
    media.create_document_media(dbo, username, media.LOSTANIMAL, lostanimalid, formname, formhtml )
    return (collationid, lostanimalid, utils.padleft(lostanimalid, 6) + " - " + personname)
  
def create_foundanimal(dbo, username, collationid):
    """
    Creates a found animal record from the incoming form data with collationid.
    Also, attaches the form to the found animal as media.
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    d["datefound"] = i18n.python2display(l, i18n.now(dbo.timezone))
    d["datereported"] = i18n.python2display(l, i18n.now(dbo.timezone))
    for f in fields:
        if f["FIELDNAME"] == "species": d["species"] = guess_species(dbo, f["VALUE"])
        if f["FIELDNAME"] == "sex": d["sex"] = guess_sex(dbo, f["VALUE"])
        if f["FIELDNAME"] == "breed": d["breed"] = guess_breed(dbo, f["VALUE"])
        if f["FIELDNAME"] == "agegroup": d["agegroup"] = guess_agegroup(dbo, f["VALUE"])
        if f["FIELDNAME"] == "color": d["colour"] = guess_colour(dbo, f["VALUE"])
        if f["FIELDNAME"] == "colour": d["colour"] = guess_colour(dbo, f["VALUE"])
        if f["FIELDNAME"] == "description": d["markings"] = f["VALUE"]
        if f["FIELDNAME"] == "areafound": d["areafound"] = f["VALUE"]
        if f["FIELDNAME"] == "areapostcode": d["areapostcode"] = f["VALUE"]
        if f["FIELDNAME"] == "areazipcode": d["areazipcode"] = f["VALUE"]
    if not d.has_key("species"): d["species"] = guess_species(dbo, "")
    if not d.has_key("sex"): d["sex"] = guess_sex(dbo, "")
    if not d.has_key("breed"): d["breed"] = guess_breed(dbo, "")
    if not d.has_key("agegroup"): d["agegroup"] = guess_agegroup(dbo, "")
    if not d.has_key("colour"): d["colour"] = guess_colour(dbo, "")
    # Have we got enough info to create the found animal record? We need a description and areafound
    if not d.has_key("markings") or not d.has_key("areafound"):
        raise utils.ASMValidationError(i18n._("There is not enough information in the form to create a found animal record (need a description and area found).", l))
    # We need the person record before we create the found animal
    collationid, personid, personname = create_person(dbo, username, collationid)
    d["owner"] = personid
    # Create the found animal
    foundanimalid = lostfound.insert_foundanimal_from_form(dbo, utils.PostedData(d, dbo.locale), username)
    # Attach the form to the found animal
    formname = get_onlineformincoming_name(dbo, collationid)
    formhtml = get_onlineformincoming_html(dbo, collationid)
    media.create_document_media(dbo, username, media.FOUNDANIMAL, foundanimalid, formname, formhtml )
    return (collationid, foundanimalid, utils.padleft(foundanimalid, 6) + " - " + personname)
  
def create_waitinglist(dbo, username, collationid):
    """
    Creates a waitinglist record from the incoming form data with collationid.
    Also, attaches the form to the waiting list as media.
    """
    l = dbo.locale
    fields = get_onlineformincoming_detail(dbo, collationid)
    d = {}
    d["dateputon"] = i18n.python2display(l, i18n.now(dbo.timezone))
    d["urgency"] = "5"
    for f in fields:
        if f["FIELDNAME"] == "species": d["species"] = guess_species(dbo, f["VALUE"])
        if f["FIELDNAME"] == "description": d["description"] = f["VALUE"]
        if f["FIELDNAME"] == "reason": d["reasonforwantingtopart"] = f["VALUE"]
    if not d.has_key("species"): d["species"] = guess_species(dbo, "")
    # Have we got enough info to create the waiting list record? We need a description
    if not d.has_key("description"):
        raise utils.ASMValidationError(i18n._("There is not enough information in the form to create a waiting list record (need a description).", l))
    # We need the person record before we create the waiting list
    collationid, personid, personname = create_person(dbo, username, collationid)
    d["owner"] = personid
    # Create the waiting list
    wlid = waitinglist.insert_waitinglist_from_form(dbo, utils.PostedData(d, dbo.locale), username)
    # Attach the form to the waiting list
    formname = get_onlineformincoming_name(dbo, collationid)
    formhtml = get_onlineformincoming_html(dbo, collationid)
    media.create_document_media(dbo, username, media.WAITINGLIST, wlid, formname, formhtml )
    return (collationid, wlid, utils.padleft(wlid, 6) + " - " + personname)

def auto_remove_old_incoming_forms(dbo):
    """
    Automatically removes incoming forms older than the daily amount set
    """
    removeafter = configuration.auto_remove_incoming_forms_days(dbo)
    if removeafter <= 0:
        al.debug("auto remove incoming forms is off.", "onlineform.auto_remove_old_incoming_forms")
        return
    removecutoff = i18n.subtract_days(i18n.now(dbo.timezone), removeafter)
    al.debug("remove date: incoming forms < %s" % db.dd(removecutoff), "onlineform.auto_remove_old_incoming_forms")
    sql = "DELETE FROM onlineformincoming WHERE PostedDate < %s" % db.dd(removecutoff)
    count = db.execute(dbo, sql)
    al.debug("removed %d incoming forms older than %d days" % (count, int(removeafter)), "onlineform.auto_remove_old_incoming_forms", dbo)

