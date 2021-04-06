
import asm3.additional
import asm3.animal
import asm3.animalcontrol
import asm3.configuration
import asm3.diary
import asm3.financial
import asm3.html
import asm3.log
import asm3.lookups
import asm3.media
import asm3.medical
import asm3.person
import asm3.publishers.base
import asm3.reports
import asm3.smcom
import asm3.stock
import asm3.users
import asm3.utils

from asm3.i18n import _, python2display, now, add_days, add_months, add_years, format_currency, format_time
from asm3.sitedefs import MULTIPLE_DATABASES
from asm3.sitedefs import ELECTRONIC_SIGNATURES, JQUERY_JS, JQUERY_MOBILE_CSS, JQUERY_MOBILE_JS, JQUERY_MOBILE_JQUERY_JS, JQUERY_UI_JS, SIGNATURE_JS, MOMENT_JS, TOUCHPUNCH_JS

def header(l):
    return """<!DOCTYPE html>
    <html>
    <head>
    <title>
    %(title)s
    </title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1"> 
    %(css)s
    %(scripts)s
    <style>
    .asm-thumbnail {
        max-width: 70px;
        max-height: 70px;
    }
    </style>
    </head>
    <body>
    """ % {
        "title":    _("Animal Shelter Manager", l),
        "css":      asm3.html.asm_css_tag("asm-icon.css"),
        "scripts":  asm3.html.script_tag(JQUERY_MOBILE_JQUERY_JS) + \
            asm3.html.css_tag(JQUERY_MOBILE_CSS) + \
            asm3.html.script_tag(JQUERY_MOBILE_JS) + \
            asm3.html.asm_script_tag("mobile.js")
    }

def jqm_button(href, text, icon = "", ajax = ""):
    if icon != "": icon = "data-icon=\"%s\"" % icon
    if ajax != "": ajax = "data-ajax=\"%s\"" % ajax
    return "<a data-role=\"button\" %(icon)s %(ajax)s href=\"%(href)s\">%(text)s</a>" % { "icon": icon, "ajax": ajax, "href": href, "text": text }

def jqm_checkbox(name, checked = False):
    c = ""
    if checked: c = "checked=\"checked\""
    return "<input type=\"checkbox\" id=\"%s\" name=\"%s\" %s />" % (name, name, c)

def jqm_collapsible(s, icon = ""):
    return "<div data-role=\"collapsible\" data-collapsed=\"true\" data-collapsed-icon=\"%s\">%s</div>\n" % (icon, s)

def jqm_collapsible_set(s):
    return "<div data-role=\"collapsible-set\">%s</div>\n" % s

def jqm_email(e):
    if e is None or e.strip() == "": return ""
    return '<a href="mailto:%s">%s</a>' % (asm3.html.escape(e), e)

def jqm_fieldcontain(name, label, inner):
    return "<div data-role=\"fieldcontain\"><label for=\"%(name)s\">%(label)s</label>%(inner)s</div>" % { "name": name, "label": label, "inner": inner }

def jqm_form(name, action="mobile_post", method="post", ajax= ""):
    if ajax != "": ajax = "data-ajax=\"%s\"" % ajax
    return "<form %s id=\"%s\" action=\"%s\" method=\"%s\">\n" % (ajax, name, action, method)

def jqm_form_end():
    return "</form>\n"

def jqm_h3(s):
    return "<h3>%s</h3>\n" % s

def jqm_hidden(name, value):
    return "<input type=\"hidden\" id=\"%(name)s\" name=\"%(name)s\" value=\"%(value)s\" />\n" % { "name": name, "value": value }

def jqm_link(href, text, icon = "", linkclass = "", theme = ""):
    if linkclass != "": linkclass = "class=\"" + linkclass + "\""
    if icon != "": icon = "data-icon=\"" + icon + "\""
    if theme != "": theme = "data-theme=\"" + theme + "\""
    return "<a href=\"%(href)s\" %(linkclass)s %(icon)s %(theme)s>%(text)s</a>\n" % {
        "href": href, "text": text, "icon": icon, "linkclass": linkclass, "theme": theme }

def jqm_list(s, showfilter = False):
    return "<ul data-role=\"listview\" data-filter=\"%s\">\n%s</ul>\n" % (showfilter and "true" or "false", s)

def jqm_list_divider(s):
    return "<li data-role=\"list-divider\" role=\"heading\">%s</li>" % s

def jqm_listitem(s):
    return "<li>%s</li>" % s

def jqm_listitem_link(href, text = "", icon = "", counter = -1, rel = "", ajax = ""):
    counterdisplay = ""
    if counter >= 0: counterdisplay = "<span class=\"ui-li-count ui-btn-up-c ui-btn-corner-all\">%d</span>" % counter
    if icon != "": icon = asm3.html.icon(icon)
    if rel != "": rel = "data-rel=\"%s\"" % rel
    if ajax != "": ajax = "data-ajax=\"%s\"" % ajax
    return "<li><a href=\"%(href)s\" %(ajax)s %(rel)s>%(icon)s %(text)s %(counterdisplay)s</a></li>\n" % {
        "href": href, "ajax": ajax, "text": text, "icon": icon, "counterdisplay": counterdisplay, "rel": rel }

def jqm_option(value, label = "", selected = False):
    if selected: selected = "selected=\"selected\""
    if label == "":
        return "<option %s>%s</option>" % (selected, value)
    return "<option value=\"%s\" %s>%s</option>\n" % (value, selected, label)

def jqm_options_next_month(l):
    d = now()
    days = []
    for dummy in range(0, 31):
        days.append(jqm_option(python2display(l,d)))
        d = add_days(d, 1)
    d = add_months(now(), 3)
    days.append(jqm_option(python2display(l,d)))
    d = add_months(now(), 6)
    days.append(jqm_option(python2display(l,d)))
    d = add_years(now(), 1)
    days.append(jqm_option(python2display(l,d)))
    return "\n".join(days)

def jqm_options(rs, valuefield, displayfield, selectedvalue = ""):
    res = []
    for r in rs:
        res.append(jqm_option(str(r[valuefield]), str(r[displayfield]), selectedvalue == str(r[valuefield])))
    return "\n".join(res)

def jqm_p(s):
    return "<p>%s</p>\n" % s

def jqm_page_footer():
    return "</div>\n</div>\n"

def jqm_page_header(pageid, title, link = "", backbutton = True):
    backbuttonattr = ""
    if backbutton: backbuttonattr = "data-add-back-btn=\"true\""
    if pageid != "": pageid = "id=\"%s\"" % pageid
    return "<div data-role=\"page\" %(back)s %(pageid)s>\n" \
        "<div data-role=\"header\">" \
        "<h1>%(title)s</h1>%(link)s" \
        "</div>\n" \
        "<div data-role=\"content\">\n" % { 
            "pageid": pageid, "title": title, "link": link, "back": backbuttonattr }

def jqm_select(name, options, selclass = "", data = ""):
    if selclass != "": selclass = "class=\"" + selclass + "\""
    if data != "": data = "data=\"" + data + "\""
    return "<select id=\"%(name)s\" name=\"%(name)s\" %(data)s %(selclass)s>%(options)s</select>\n" % { \
        "name": name, "options": options, "data": data, "selclass": selclass }

def jqm_slider(name, minv = 0, maxv = 0, val = 0):
    return "<input type=\"range\" id=\"%(name)s\" name=\"%(name)s\" value=\"%(val)s\" min=\"%(minv)s\" max=\"%(maxv)s\" />" % { "name": name, "val": val, "minv": minv, "maxv": maxv }

def jqm_span(s):
    return "<span>%s</span>\n" % s

def jqm_submit(label):
    return "<button data-icon=\"check\" type=\"submit\">%s</button>\n" % label

def jqm_table():
    return "<table>\n"

def jqm_table_end():
    return "</table>\n"

def jqm_tablerow(cell1, cell2 = "", cell3 = "", cell4 = ""):
    s = "<tr>\n<td>" + cell1 + "</td>\n"
    if cell2 != "": s += "<td>%s</td>\n" % cell2
    if cell3 != "": s += "<td>%s</td>\n" % cell3
    if cell4 != "": s += "<td>%s</td>\n" % cell4
    s += "</tr>\n"
    return s

def jqm_tel(l, no):
    if no is None or no.strip() == "": return ""
    dialno = no
    if l in ( "en", "en_CA") and not no.startswith("+"): dialno = "+1%s" % dialno
    if l == "en_GB" and not no.startswith("+"): dialno = "+44%s" % dialno
    if l == "en_IE" and not no.startswith("+"): dialno = "+353%s" % dialno
    return '<a href="tel:%s">%s</a>' % (asm3.html.escape(dialno), no)

def jqm_text(name, value = ""):
    return "<input id=\"%(name)s\" name=\"%(name)s\" value=\"%(value)s\" type=\"text\" />\n" % { "name": name, "value": value }

def person_flags(fl):
    if fl is None: return ""
    s = []
    for f in fl.split("|"):
        if f != "": s.append(f)
    return ", ".join(s)

def page(dbo, session, username):
    """
    Generates the main mobile web page
    dbo: Database info
    """
    l = dbo.locale
    nsa = asm3.animal.get_number_animals_on_shelter_now(dbo)
    osa = nsa > 0
    ar = asm3.reports.get_available_reports(dbo)
    vacc = asm3.medical.get_vaccinations_outstanding(dbo)
    test = asm3.medical.get_tests_outstanding(dbo)
    med = asm3.medical.get_treatments_outstanding(dbo)
    dia = asm3.diary.get_uncompleted_upto_today(dbo, username)
    hck = asm3.person.get_reserves_without_homechecks(dbo)
    mess = asm3.lookups.get_messages(dbo, session.user, session.roles, session.superuser)
    testresults = asm3.lookups.get_test_results(dbo)
    stl = asm3.stock.get_stock_locations_totals(dbo)
    inmy = asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "dispatchedaco": session.user, "filter": "incomplete" }, username)
    inun = asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "dispatchedaco": session.user, "filter": "undispatched" }, username)
    inop = asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "filter": "incomplete" }, username)
    infp = asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "filter": "requirefollowup" }, username)
    homelink = jqm_link("mobile", _("Home", l), "home", "ui-btn-right", "b")
    h = []

    def pb(p):
        return asm3.users.check_permission_bool(session, p)

    h.append(header(l))

    logoutlink = ""
    if not session.mobileapp: 
        logoutlink = jqm_link("mobile_logout", _("Logout", l), "delete", "ui-btn-right", "b")

    h.append(jqm_page_header("home", "%s : %s" % (username, _("ASM", l)), logoutlink , False))
    items = []
    if asm3.configuration.smdb_locked(dbo):
        items.append(jqm_listitem(_("This database is locked and in read-only mode. You cannot add, change or delete records.", l)))
    items.append(jqm_listitem_link("#messages", _("Messages", l), "message", len(mess)))
    if len(ar) > 0 and pb(asm3.users.VIEW_REPORT):
        items.append(jqm_listitem_link("#reports", _("Generate Report", l), "report"))
    if pb(asm3.users.CHANGE_MEDIA) and ELECTRONIC_SIGNATURES == "touch":
        items.append(jqm_listitem_link("mobile_sign", _("Signing Pad", l), "signature", -1, "", "false"))
    items.append(jqm_listitem_link("main", _("Desktop/Tablet UI", l), "logo", -1, "", "false"))
    if pb(asm3.users.ADD_ANIMAL) or pb(asm3.users.VIEW_ANIMAL) or pb(asm3.users.CHANGE_VACCINATION) \
       or pb(asm3.users.CHANGE_TEST) or pb(asm3.users.CHANGE_MEDICAL) or pb(asm3.users.ADD_LOG):
        items.append(jqm_list_divider(_("Animal", l)))
    if pb(asm3.users.ADD_ANIMAL):
        items.append(jqm_listitem_link("mobile_post?posttype=aas", _("Add Animal", l), "animal-add"))
    if osa and pb(asm3.users.VIEW_ANIMAL):
        items.append(jqm_listitem_link("mobile_post?posttype=vsa", _("View Shelter Animals", l), "animal", nsa))
    if len(vacc) > 0 and pb(asm3.users.CHANGE_VACCINATION):
        items.append(jqm_listitem_link("#vacc", _("Vaccinate Animal", l), "vaccination", len(vacc)))
    if len(test) > 0 and pb(asm3.users.CHANGE_TEST):
        items.append(jqm_listitem_link("#test", _("Test Animal", l), "test", len(test)))
    if len(med) > 0 and pb(asm3.users.CHANGE_MEDICAL):
        items.append(jqm_listitem_link("#med", _("Medicate Animal", l), "medical", len(med)))
    if osa and pb(asm3.users.ADD_LOG):
        items.append(jqm_listitem_link("#log", _("Add Log to Animal", l), "log", -1, ""))
    if pb(asm3.users.ADD_INCIDENT) or pb(asm3.users.CHANGE_INCIDENT) or pb(asm3.users.VIEW_LICENCE):
        items.append(jqm_list_divider(_("Animal Control", l)))
    if pb(asm3.users.ADD_INCIDENT):
        items.append(jqm_listitem_link("mobile_post?posttype=aincs", _("Add Call", l), "call"))
    if len(inmy) > 0 and pb(asm3.users.CHANGE_INCIDENT):
        items.append(jqm_listitem_link("#inmy", _("My Incidents", l), "call", len(inmy)))
    if len(inun) > 0 and pb(asm3.users.CHANGE_INCIDENT):
        items.append(jqm_listitem_link("#inun", _("My Undispatched Incidents", l), "call", len(inun)))
    if len(inop) > 0 and pb(asm3.users.CHANGE_INCIDENT):
        items.append(jqm_listitem_link("#inop", _("Open Incidents", l), "call", len(inop)))
    if len(infp) > 0 and pb(asm3.users.CHANGE_INCIDENT):
        items.append(jqm_listitem_link("#infp", _("Incidents Requiring Followup", l), "call", len(infp)))
    if pb(asm3.users.VIEW_LICENCE):
        items.append(jqm_listitem_link("#checklicence", _("Check License", l), "licence", -1, ""))
    if pb(asm3.users.ADD_DIARY) or pb(asm3.users.EDIT_MY_DIARY_NOTES):
        items.append(jqm_list_divider(_("Diary", l)))
    if pb(asm3.users.ADD_DIARY):
        items.append(jqm_listitem_link("#diaryadd", _("New Task", l), "diary"))
    if len(dia) > 0 and pb(asm3.users.EDIT_MY_DIARY_NOTES):
        items.append(jqm_listitem_link("#diary", _("Complete Tasks", l), "diary", len(dia)))
    if pb(asm3.users.CHANGE_STOCKLEVEL):
        items.append(jqm_list_divider(_("Financial", l)))
    if len(stl) > 0 and pb(asm3.users.CHANGE_STOCKLEVEL):
        items.append(jqm_listitem_link("#stl", _("Stock Take", l), "stock", len(stl)))
    if pb(asm3.users.CHANGE_PERSON):
        items.append(jqm_list_divider(_("Person", l)))
    if pb(asm3.users.VIEW_PERSON):
        items.append(jqm_listitem_link("#findperson", _("Find Person", l), "person", -1, ""))
    if len(hck) > 0 and pb(asm3.users.CHANGE_PERSON):
        items.append(jqm_listitem_link("#homecheck", _("Perform Homecheck", l), "person", -1, ""))

    h.append(jqm_list("\n".join(items)))
    h.append(jqm_page_footer())

    h += page_messages(l, homelink, mess)
    h += page_message_add(l, homelink, dbo)
    h += page_reports(l, homelink, ar)
    h += page_vaccinations(l, homelink, vacc)
    h += page_tests(l, homelink, test, testresults)
    h += page_medication(l, homelink, med)
    h += page_log_add(l, homelink, dbo)
    h += page_check_licence(l, homelink)
    h += page_diary_add(l, homelink, dbo)
    h += page_diary(l, homelink, dia)
    h += page_homecheck(l, homelink, dbo)
    h += page_stocklevels(l, homelink, stl)
    h += page_incidents(l, homelink, inmy, "inmy", _("My Incidents", l))
    h += page_incidents(l, homelink, inun, "inun", _("My Undispatched Incidents", l))
    h += page_incidents(l, homelink, inop, "inop", _("Open Incidents", l))
    h += page_incidents(l, homelink, infp, "infp", _("Incidents Requiring Followup", l))
    h += page_find_person(l, homelink)

    h.append("</body></html>")
    return "\n".join(h)

def page_sign(dbo, session, username):
    l = session.locale
    ids = asm3.configuration.signpad_ids(dbo, username)
    h = []
    h.append("""<!DOCTYPE html>
    <html>
    <head>
    <title>
    %(title)s
    </title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1"> 
    %(css)s
    <script>
        ids = "%(ids)s";
    </script>
    %(scripts)s
    <style>
    button { 
        padding: 10px; 
        font-size: 100%%; 
    }
    #signature { 
        border: 1px solid #aaa; 
        height: 250px; 
        width: 100%%;
        max-width: 1000px;
    }
    </style>
    </head>
    <body>
    """ % {
        "title":    _("Signing Pad", l),
        "ids":      ids,
        "css":      asm3.html.asm_css_tag("asm-icon.css"),
        "scripts":  asm3.html.script_tag(JQUERY_JS) + \
            asm3.html.script_tag(JQUERY_UI_JS) + \
            asm3.html.script_tag(TOUCHPUNCH_JS) + \
            asm3.html.script_tag(SIGNATURE_JS) + \
            asm3.html.script_tag(MOMENT_JS) + \
            asm3.html.asm_script_tag("mobile_sign.js")
    })
    if ids.strip() == "":
        h.append('<p>%s</p>' % _("Waiting for documents...", l))
        h.append('<p><button id="sig-refresh">' + _("Reload", l) + '</button></p>')
        #h.append('<p><button id="sig-home">' + _("Home", l) + '</button></p>')
        if not session.mobileapp:
            h.append('</p><button id="sig-logout">' + _("Logout", l) + '</button></p>')
    else:
        d = []
        docnotes = []
        for mid in ids.strip().split(","):
            if mid.strip() != "": 
                docnotes.append(asm3.media.get_notes_for_id(dbo, int(mid)))
                dummy, dummy, dummy, contents = asm3.media.get_media_file_data(dbo, int(mid))
                d.append(asm3.utils.bytes2str(contents))
                d.append("<hr />")
        h.append("<p><b>%s: %s</b></p>" % (_("Signing", l), ", ".join(docnotes)))
        h.append('<p><a id="reviewlink" href="#">%s</a></p>' % _("View Document", l))
        h.append('<div id="review" style="display: none">')
        h.append("\n".join(d))
        h.append('</div>')
        h.append('<div id="signature"></div>')
        h.append('<p>')
        h.append('<button id="sig-clear" type="button">' + _("Clear", l) + '</button>')
        h.append('<button id="sig-sign" type="button">' + _("Sign", l) + '</button>')
        h.append('</p>')
        h.append('<p>')
        h.append(_("Please click the Sign button when you are finished.", l))
        h.append('</p>')
        h.append('<p>')
        h.append(_("Once signed, this document cannot be edited or tampered with.", l))
        h.append('</p>')
    h.append("</body></html>")
    return "\n".join(h)

def page_messages(l, homelink, mess):
    h = []
    h.append(jqm_page_header("messages", _("Messages", l), homelink))
    h.append(jqm_button("#addmessage", _("Add Message", l), "plus"))
    hm = []
    for m in mess:
        icon = "info"
        if m["PRIORITY"] == 1:
            icon = "alert"
        inner = jqm_h3(python2display(l, m["ADDED"]) + " " + m["CREATEDBY"])
        inner += jqm_p(m["MESSAGE"])
        hm.append(jqm_collapsible(inner, icon))
    h.append(jqm_collapsible_set("\n".join(hm)))
    h.append(jqm_page_footer())
    return h

def page_message_add(l, homelink, dbo):
    h = []
    h.append(jqm_page_header("addmessage", _("Add Message", l), homelink))
    h.append(jqm_form("messageform"))
    h.append(jqm_hidden("posttype", "message"))
    h.append(jqm_fieldcontain("forname", _("For", l), jqm_select("forname", asm3.html.options_users_and_roles(dbo, False, True))))
    h.append(jqm_fieldcontain("expires", _("Expires", l), jqm_select("expires", jqm_options_next_month(l))))
    h.append(jqm_fieldcontain("priority", _("Priority", l), jqm_select("priority", 
        jqm_option("0", _("Information", l), True) + jqm_option("1", _("Important", l), False))))
    h.append(jqm_fieldcontain("email", _("Send via email", l), jqm_checkbox("email", asm3.configuration.email_messages(dbo))))
    h.append(jqm_fieldcontain("message", _("Note", l), jqm_text("message")))
    h.append(jqm_submit(_("Add Message", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    return h

def page_reports(l, homelink, ar):
    h = []
    h.append(jqm_page_header("reports", _("Reports", l), homelink))
    rs = []
    group = ""
    for r in ar:
        if group != r["CATEGORY"]:
            group = r["CATEGORY"]
            rs.append(jqm_list_divider(group))
        rs.append(jqm_listitem_link("mobile_report?id=%d" % r["ID"], r["TITLE"], "report", ajax="false"))
    h.append(jqm_list("\n".join(rs), True))
    h.append(jqm_page_footer())
    return h

def page_vaccinations(l, homelink, vacc):
    h = []
    h.append(jqm_page_header("vacc", _("Vaccinate", l), homelink))
    group = ""
    vlist = []
    vforms = []
    for v in vacc:
        required = python2display(l, v["DATEREQUIRED"])
        if group != required:
            group = required
            vlist.append(jqm_list_divider(group))
        pageid = "v" + str(v["ID"])
        vlist.append(jqm_listitem_link("#" + pageid, 
            "%s - %s (%s)" % (v["ANIMALNAME"], v["SHELTERCODE"], v["VACCINATIONTYPE"]),
            "vaccination", -1, ""))
        vforms.append(jqm_page_header(pageid, v["VACCINATIONTYPE"], homelink))
        vforms.append(jqm_table())
        vforms.append(jqm_tablerow( _("Animal", l), 
            jqm_link("mobile_post?posttype=va&id=%d" % v["ANIMALID"], v["SHELTERCODE"] + " " + v["ANIMALNAME"])))
        vforms.append(jqm_tablerow( _("Vaccination", l), "%s %s" % (required, v["VACCINATIONTYPE"])))
        vforms.append(jqm_tablerow( _("Comments", l), v["COMMENTS"]))
        vforms.append(jqm_table_end())
        vforms.append(jqm_button("mobile_post?posttype=vacc&id=%s&animalid=%s" % (str(v["ID"]), str(v["ANIMALID"])), _("Vaccinate", l), "check"))
        vforms.append(jqm_page_footer())
    h.append(jqm_list("\n".join(vlist), True))
    h.append(jqm_page_footer())
    h.append("\n".join(vforms))
    return h

def page_tests(l, homelink, test, testresults):
    h = []
    h.append(jqm_page_header("test", _("Test", l), homelink))
    group = ""
    tlist = []
    tforms = []
    for t in test:
        required = python2display(l, t["DATEREQUIRED"])
        if group != required:
            group = required
            tlist.append(jqm_list_divider(group))
        pageid = "t" + str(t["ID"])
        tlist.append(jqm_listitem_link("#" + pageid, 
            "%s - %s (%s)" % (t["ANIMALNAME"], t["SHELTERCODE"], t["TESTNAME"]),
            "vaccination", -1, ""))
        tforms.append(jqm_page_header(pageid, t["TESTNAME"], homelink))
        tforms.append(jqm_table())
        tforms.append(jqm_tablerow( _("Animal", l), 
            jqm_link("mobile_post?posttype=va&id=%d" % t["ANIMALID"], t["SHELTERCODE"] + " " + t["ANIMALNAME"])))
        tforms.append(jqm_tablerow( _("Test", l), required + " " + t["TESTNAME"]))
        tforms.append(jqm_tablerow( _("Comments", l), t["COMMENTS"]))
        tforms.append(jqm_table_end())
        tforms.append(jqm_p(_("Result", l) + ": " + 
            "<select class=\"testresult\" data=\"%s\" data-animal=\"%s\">" % (str(t["ID"]), t["ANIMALID"]) +
            "<option value=""></option>" + 
            jqm_options(testresults, "ID", "RESULTNAME") + "</select>"))
        tforms.append(jqm_page_footer())
    h.append(jqm_list("\n".join(tlist), True))
    h.append(jqm_page_footer())
    h.append("\n".join(tforms))
    return h

def page_medication(l, homelink, med):
    h = []
    h.append(jqm_page_header("med", _("Medicate", l), homelink))
    group = ""
    mlist = []
    mforms = []
    for m in med:
        required = python2display(l, m["DATEREQUIRED"])
        if group != required:
            group = required
            mlist.append(jqm_list_divider(group))
        pageid = "m" + str(m["TREATMENTID"])
        mlist.append(jqm_listitem_link("#" + pageid,
            "%s - %s (%s)" % (m["ANIMALNAME"], m["SHELTERCODE"], m["TREATMENTNAME"]),
            "medical", -1, ""))
        mforms.append(jqm_page_header(pageid, m["TREATMENTNAME"], homelink))
        mforms.append(jqm_table())
        mforms.append(jqm_tablerow(_("Animal", l),
            jqm_link("mobile_post?posttype=va&id=%d" % m["ANIMALID"], m["SHELTERCODE"] + " " + m["ANIMALNAME"])))
        mforms.append(jqm_tablerow(_("Treatment", l), "%s %s<br />%s" % (required, m["TREATMENTNAME"], m["DOSAGE"])))
        mforms.append(jqm_tablerow(_("Comments", l), m["COMMENTS"]))
        mforms.append(jqm_table_end())
        mforms.append(jqm_button("mobile_post?posttype=med&id=%s&animalid=%s&medicalid=%s" % 
            (str(m["TREATMENTID"]), str(m["ANIMALID"]), str(m["REGIMENID"])), _("Medicate", l), "check"))
        mforms.append(jqm_page_footer())
    h.append(jqm_list("\n".join(mlist), True))
    h.append(jqm_page_footer())
    h.append("\n".join(mforms))
    return h

def page_check_licence(l, homelink):
    h = []
    h.append(jqm_page_header("checklicence", _("Check License", l), homelink))
    h.append(jqm_form("licenceform"))
    h.append(jqm_hidden("posttype", "lc"))
    h.append(jqm_fieldcontain("licence", _("License Number", l), jqm_text("licence")))
    h.append(jqm_submit(_("Check", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    return h

def page_diary(l, homelink, dia):
    h = []
    h.append(jqm_page_header("diary", _("Diary", l), homelink))
    group = ""
    dlist = []
    dforms = []
    for d in dia:
        fordate = python2display(l, d["DIARYDATETIME"])
        if group != fordate:
            group = fordate
            dlist.append(jqm_list_divider(group))
        pageid = "d" + str(d["ID"])
        dlist.append(jqm_listitem_link("#" + pageid,
            "%s (%s)" % (d["SUBJECT"], d["LINKINFO"]),
            "diary", -1, ""))
        dforms.append(jqm_page_header(pageid, d["SUBJECT"], homelink))
        dforms.append(jqm_table())
        dforms.append(jqm_tablerow(_("Subject", l), d["SUBJECT"]))
        lt = d["LINKINFO"]
        if d["LINKTYPE"] == asm3.diary.ANIMAL:
            lt = jqm_link("mobile_post?posttype=va&id=%d" % d["LINKID"], d["LINKINFO"])
        dforms.append(jqm_tablerow(_("Link", l), lt))
        dforms.append(jqm_tablerow(_("Note", l), d["NOTE"]))
        dforms.append(jqm_table_end())
        dforms.append(jqm_button("mobile_post?posttype=dia&on=0&id=%s" % str(d["ID"]), _("Complete", l), "check"))
        dforms.append(jqm_p(_("Or move this diary on to", l) + ": " + 
            "<select class=\"diaryon\" data=\"%s\">" % str(d["ID"]) +
            jqm_options_next_month(l) + "</select>"))
        dforms.append(jqm_page_footer())
    h.append(jqm_list("\n".join(dlist), True))
    h.append(jqm_page_footer())
    h.append("\n".join(dforms))
    return h

def page_diary_add(l, homelink, dbo):
    h = []
    h.append(jqm_page_header("diaryadd", _("Add Diary", l), homelink))
    h.append(jqm_form("diaryform"))
    h.append(jqm_hidden("posttype", "dianew"))
    h.append(jqm_fieldcontain("diaryfor", _("For", l), jqm_select("diaryfor", asm3.html.options_users_and_roles(dbo))))
    h.append(jqm_fieldcontain("diarydate", _("Date", l), jqm_select("diarydate", jqm_options_next_month(l))))
    h.append(jqm_fieldcontain("subject", _("Subject", l), jqm_text("subject")))
    h.append(jqm_fieldcontain("note", _("Note", l), jqm_text("note")))
    h.append(jqm_submit(_("Add Diary", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    return h

def page_find_person(l, homelink):
    h = []
    h.append(jqm_page_header("findperson", _("Find Person", l), homelink))
    h.append(jqm_form("findpersonform"))
    h.append(jqm_hidden("posttype", "fp"))
    h.append(jqm_fieldcontain("q", _("Search", l), jqm_text("q")))
    h.append(jqm_submit(_("Search", l)))
    h.append(jqm_page_footer())
    return h

def page_log_add(l, homelink, dbo):
    h = []
    h.append(jqm_page_header("log", _("Add Log", l), homelink))
    h.append(jqm_form("logform"))
    h.append(jqm_hidden("posttype", "log"))
    h.append(jqm_fieldcontain("animalid", _("Animal", l), jqm_select("animalid", asm3.html.options_animals_on_shelter(dbo))))
    h.append(jqm_fieldcontain("logtypeid", _("Log Type", l), jqm_select("logtypeid", asm3.html.options_log_types(dbo))))
    h.append(jqm_fieldcontain("logtext", _("Log Text", l), jqm_text("logtext")))
    h.append(jqm_submit(_("Add Log", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    return h

def page_homecheck(l, homelink, dbo):
    h = []
    h.append(jqm_page_header("homecheck", _("Perform Homecheck", l), homelink))
    h.append(jqm_form("hcform"))
    h.append(jqm_hidden("posttype", "hc"))
    h.append(jqm_fieldcontain("personid", _("Person", l), jqm_select("personid", asm3.html.options_people_not_homechecked(dbo))))
    h.append(jqm_fieldcontain("comments", _("Comments", l), jqm_text("comments")))
    h.append(jqm_submit(_("Pass Homecheck", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    return h

def page_stocklevels(l, homelink, stl):
    h = []
    h.append(jqm_page_header("stl", _("Stock Take", l), homelink))
    vlist = []
    for s in stl:
        vlist.append(jqm_listitem_link("mobile_post?posttype=st&id=%s" % s["ID"], s["LOCATIONNAME"], "stock", s["TOTAL"]))
    h.append(jqm_list("\n".join(vlist), True))
    h.append(jqm_page_footer())
    return h

def page_incidents(l, homelink, inc, pageid = "inmy", pagetitle = ""):
    h = []
    h.append(jqm_page_header(pageid, pagetitle, homelink))
    vlist = []
    for i in inc:
        vlist.append(jqm_listitem_link("mobile_post?posttype=vinc&id=%s" % i["ID"], 
            "%s: %s - %s" % (python2display(l, i["INCIDENTDATETIME"]), i["INCIDENTNAME"], i["DISPATCHADDRESS"]), "call"))
    h.append(jqm_list("\n".join(vlist), True))
    h.append(jqm_page_footer())
    return h

def page_login(l, post):
    accountline = ""
    accounttext = _("Database", l)
    if asm3.smcom.active(): accounttext = _("SM Account", l)
    if MULTIPLE_DATABASES:
        accountline = "<div data-role='fieldcontain'><label for='database'>%s</label><input type='text' id='database' name='database' value='%s'/></div>" % (accounttext, asm3.html.escape(post["smaccount"]))
    return header(l) + """
        <div data-role='page' id='login'>
        <div data-role='header'>
        <h1>%s</h1>
        </div>
        <div data-role='content'>
        <form id="loginform" action="mobile_login" target="_self" method="post">
        <h2>%s</h2>
        %s
        <div data-role="fieldcontain">
            <label for="username">%s</label>
            <input type="text" id="username" name="username" value='%s' autocomplete="username" />
        </div>
        <div data-role="fieldcontain">
            <label for="password">%s</label>
            <input type="password" id="password" name="password" value='%s' autocomplete="current-password" />
        </div>
        <button type="submit">%s</button>
        </form>
        </div>
        </div>
        </body>
        </html>
    """ % ( _("Login", l), _("Login", l), accountline, 
        _("Username", l), asm3.html.escape(post["username"]), 
        _("Password", l), asm3.html.escape(post["password"]),
        _("Login", l) )

def handler(session, post):
    """
    Handles posts from the frontend. Depending on the type we either
    return more HTML for the javascript to inject, or GO URL to have
    the controller redirect to URL
    """
    l = session.locale
    user = session.user
    locationfilter = session.locationfilter
    siteid = session.siteid
    dbo = session.dbo
    homelink = "<a href='mobile' data-ajax='false' class='ui-btn-right' data-icon='home' data-theme='b'>%s</a>" % _("Home", l)
    mode = post["posttype"]
    pid = post.integer("id")
    animalid = post.integer("animalid")

    def pc(p):
        asm3.users.check_permission(session, p)

    if mode == "vacc":
        # We're vaccinating an animal
        pc(asm3.users.CHANGE_VACCINATION)
        a = asm3.animal.get_animal(dbo, animalid)
        asm3.medical.update_vaccination_today(dbo, user, pid)
        return jqm_page_header("", _("Vaccination Given", l), homelink) + \
            jqm_p(_("Vaccination marked as given for {0} - {1}", l).format(a["ANIMALNAME"], a["SHELTERCODE"])) + \
            jqm_button("mobile#vacc", _("More Vaccinations", l), "", "false") + \
            jqm_page_footer()

    if mode == "test":
        # We're performing a test on an animal
        pc(asm3.users.CHANGE_TEST)
        a = asm3.animal.get_animal(dbo, animalid)
        asm3.medical.update_test_today(dbo, user, pid, post.integer("resultid"))
        return jqm_page_header("", _("Test Performed", l), homelink) + \
            jqm_p(_("Test marked as performed for {0} - {1}", l).format(a["ANIMALNAME"], a["SHELTERCODE"])) + \
            jqm_button("mobile#test", _("More Tests", l), "", "false") + \
            jqm_page_footer()

    elif mode == "med":
        # We're treating an animal
        pc(asm3.users.CHANGE_MEDICAL)
        a = asm3.animal.get_animal(dbo, animalid)
        asm3.medical.update_treatment_today(dbo, user, pid)
        return jqm_page_header("", _("Treatment Given", l), homelink) + \
            jqm_p(_("Treatment marked as given for {0} - {1}", l).format(a["ANIMALNAME"], a["SHELTERCODE"])) + \
            jqm_button("mobile#med", _("More Medications", l), "", "false") + \
            jqm_page_footer()

    elif mode == "dia":
        # We're completing a diary task
        pc(asm3.users.EDIT_MY_DIARY_NOTES)
        d = asm3.diary.get_diary(dbo, pid)
        if post["on"] == "0":
            asm3.diary.complete_diary_note(dbo, user, pid)
            return jqm_page_header("", _("Completed", l), homelink) + \
                jqm_p(_("Diary note {0} marked completed", l).format(d["SUBJECT"])) + \
                jqm_button("mobile#diary", _("More diary notes", l), "", "false") + \
                jqm_page_footer()
        else:
            asm3.diary.rediarise_diary_note(dbo, user, pid, post.date("on"))
            return jqm_page_header("", _("Rediarised", l), homelink) + \
                jqm_p(_("Diary note {0} rediarised for {1}", l).format(d["SUBJECT"], post["on"])) + \
                jqm_button("mobile#diary", _("More diary notes", l), "", "false") + \
                jqm_page_footer()

    elif mode == "dianew":
        # We're adding a diary note
        pc(asm3.users.ADD_DIARY)
        asm3.diary.insert_diary(dbo, user, 0, 0, post.date("diarydate"), 
            post["diaryfor"], post["subject"], post["note"])
        return "GO mobile"

    elif mode == "message":
        # We're adding a message
        asm3.lookups.add_message(dbo, user, post.boolean("email"), post["message"], post["forname"], post.integer("priority"), post.date("expires"))
        return "GO mobile"

    elif mode == "log":
        pc(asm3.users.ADD_LOG)
        # We're adding a log to an animal
        a = asm3.animal.get_animal(dbo, animalid)
        asm3.log.add_log(dbo, user, asm3.log.ANIMAL, animalid, post.integer("logtypeid"), post["logtext"])
        return "GO mobile"

    elif mode == "hc":
        pc(asm3.users.CHANGE_PERSON)
        # We're marking an owner homechecked
        asm3.person.update_pass_homecheck(dbo, user, post.integer("personid"), post["comments"])
        return "GO mobile"

    elif mode == "vsa":
        # Return a list of the shelter animals
        pc(asm3.users.VIEW_ANIMAL)
        h = []
        alin = []
        h.append(header(l))
        h.append(jqm_page_header("", _("Shelter Animals", l), homelink))
        an = asm3.animal.get_animal_find_simple(dbo, "", locationfilter=locationfilter, siteid=siteid)
        for a in an:
            alin.append(jqm_listitem_link("mobile_post?posttype=va&id=%d" % a["ID"],
                "%s - %s (%s %s %s) %s" % (a["CODE"], a["ANIMALNAME"], a["SEXNAME"], a["BREEDNAME"], a["SPECIESNAME"], a["IDENTICHIPNUMBER"]),
                asm3.utils.iif(asm3.publishers.base.is_animal_adoptable(dbo, a), "animal", "notforadoption")))
        h.append(jqm_list("\n".join(alin), True))
        h.append(jqm_page_footer())
        h.append("</body></html>")
        return "\n".join(h)

    elif mode == "uai":
        pc(asm3.users.ADD_MEDIA)
        # Upload an animal image
        asm3.media.attach_file_from_form(dbo, user, asm3.media.ANIMAL, animalid, post)
        return "GO mobile_post?posttype=va&id=%d&success=true" % animalid

    elif mode == "aas":
        pc(asm3.users.ADD_ANIMAL)
        return handler_addanimal(l, homelink, dbo)

    elif mode == "aa":
        pc(asm3.users.ADD_ANIMAL)
        nid, dummy = asm3.animal.insert_animal_from_form(dbo, post, user)
        return "GO mobile_post?posttype=va&id=%d" % nid

    elif mode == "aincs":
        pc(asm3.users.ADD_INCIDENT)
        return handler_addincident(l, homelink, dbo)

    elif mode == "ainc":
        pc(asm3.users.ADD_INCIDENT)
        post.data["incidentdate"] = python2display(l, now(dbo.timezone))
        post.data["incidenttime"] = format_time(now(dbo.timezone))
        post.data["calldate"] = post.data["incidentdate"]
        post.data["calltime"] = post.data["incidenttime"]
        post.data["calltaker"] = user
        nid = asm3.animalcontrol.insert_animalcontrol_from_form(dbo, post, user)
        return "GO mobile_post?posttype=vinc&id=%d" % nid

    elif mode == "fp":
        pc(asm3.users.VIEW_PERSON)
        q = post["q"]
        matches = []
        if q.strip() != "": 
            matches = asm3.person.get_person_find_simple(dbo, q, user, classfilter="all", \
                includeStaff=asm3.users.check_permission_bool(session, asm3.users.VIEW_STAFF), \
                includeVolunteers=asm3.users.check_permission_bool(session, asm3.users.VIEW_VOLUNTEER), limit=100, siteid=siteid)
        h = []
        alin = []
        h.append(header(l))
        h.append(jqm_page_header("", _("Results", l), homelink))
        for p in matches:
            alin.append(jqm_listitem_link("mobile_post?posttype=vp&id=%d" % p["ID"],
                "%s - %s" % (p["OWNERNAME"], p["OWNERADDRESS"]),
                "person"))
        h.append(jqm_list("\n".join(alin), True))
        h.append(jqm_page_footer())
        h.append("</body></html>")
        return "\n".join(h)

    elif mode == "lc":
        pc(asm3.users.VIEW_LICENCE)
        q = post["q"]
        q = post["licence"]
        matches = []
        if q.strip() != "": matches = asm3.financial.get_licence_find_simple(dbo, q)
        return handler_check_licence(l, homelink, q, matches)

    elif mode == "va":
        # Display a page containing the selected animal by id
        pc(asm3.users.VIEW_ANIMAL)
        a = asm3.animal.get_animal(dbo, pid)
        af = asm3.additional.get_additional_fields(dbo, pid, "animal")
        diet = asm3.animal.get_diets(dbo, pid)
        vacc = asm3.medical.get_vaccinations(dbo, pid)
        test = asm3.medical.get_tests(dbo, pid)
        med = asm3.medical.get_regimens(dbo, pid)
        logs = asm3.log.get_logs(dbo, asm3.log.ANIMAL, pid)
        return handler_viewanimal(session, l, dbo, a, af, diet, vacc, test, med, logs, homelink, post)

    elif mode == "vinc":
        # Display a page containing the selected incident by id
        pc(asm3.users.VIEW_INCIDENT)
        a = asm3.animalcontrol.get_animalcontrol(dbo, pid)
        amls = asm3.animalcontrol.get_animalcontrol_animals(dbo, pid)
        cit = asm3.financial.get_incident_citations(dbo, pid)
        dia = asm3.diary.get_diaries(dbo, asm3.diary.ANIMALCONTROL, pid)
        logs = asm3.log.get_logs(dbo, asm3.log.ANIMALCONTROL, pid)
        return handler_viewincident(session, l, dbo, a, amls, cit, dia, logs, homelink, post)

    elif mode == "vinccomp":
        # Mark the incident with pid completed with type=ct
        pc(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_animalcontrol_completenow(dbo, pid, user, post.integer("ct"))
        return "GO mobile_post?posttype=vinc&id=%d" % pid

    elif mode == "vincdisp":
        # Mark the incident with id dispatched now with the current user as aco
        pc(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_animalcontrol_dispatchnow(dbo, pid, user)
        return "GO mobile_post?posttype=vinc&id=%d" % pid

    elif mode == "vincresp":
        pc(asm3.users.CHANGE_INCIDENT)
        # Mark the incident with id responded to now
        asm3.animalcontrol.update_animalcontrol_respondnow(dbo, pid, user)
        return "GO mobile_post?posttype=vinc&id=%d" % pid

    elif mode == "vinclog":
        # Add a log to the incident of id with logtype and logtext
        pc(asm3.users.ADD_LOG)
        asm3.log.add_log(dbo, user, asm3.log.ANIMALCONTROL, pid, post.integer("logtype"), post["logtext"])
        return "GO mobile_post?posttype=vinc&id=%d" % pid

    elif mode == "vp":
        # Display a page containing the selected person by id
        pc(asm3.users.VIEW_PERSON)
        p = asm3.person.get_person(dbo, pid)
        af = asm3.additional.get_additional_fields(dbo, pid, "person")
        cit = asm3.financial.get_person_citations(dbo, pid)
        dia = asm3.diary.get_diaries(dbo, asm3.diary.PERSON, pid)
        lic = asm3.financial.get_person_licences(dbo, pid)
        links = asm3.person.get_links(dbo, pid)
        logs = asm3.log.get_logs(dbo, asm3.log.PERSON, pid)
        return handler_viewperson(session, l, dbo, p, af, cit, dia, lic, links, logs, homelink, post)

    elif mode == "st":
        # Display a page to adjust stock levels for id
        pc(asm3.users.VIEW_STOCKLEVEL)
        sl = asm3.stock.get_stocklevels(dbo, pid)
        su = asm3.lookups.get_stock_usage_types(dbo)
        return handler_stocklocation(l, homelink, asm3.lookups.get_stock_location_name(dbo, pid), sl, su)

    elif mode == "stu":
        pc(asm3.users.CHANGE_STOCKLEVEL)
        sl = asm3.stock.get_stocklevels(dbo, pid)
        # Update the stock levels from the posted values
        asm3.stock.stock_take_from_mobile_form(dbo, user, post)
        return "GO mobile"

    elif mode == "sign":
        # We're electronically signing a document
        for mid in post.integer_list("ids"):
            try:
                asm3.media.sign_document(dbo, user, mid, post["sig"], post["signdate"], "signmobile")
            finally:
                asm3.configuration.signpad_ids(dbo, user, "")
        return "ok"

def handler_addanimal(l, homelink, dbo):
    h = []
    h.append(header(l))
    h.append(jqm_page_header("animaladd", _("Add Animal", l), homelink))
    h.append(jqm_form("animalform"))
    h.append(jqm_hidden("posttype", "aa"))
    h.append(jqm_fieldcontain("animalname", _("Name", l), jqm_text("animalname")))
    if asm3.configuration.manual_codes(dbo):
        h.append(jqm_fieldcontain("sheltercode", _("Code", l), jqm_text("sheltercode")))
    h.append(jqm_fieldcontain("estimatedage", _("Age", l), jqm_text("estimatedage", "1.0")))
    h.append(jqm_fieldcontain("sex", _("Sex", l), jqm_select("sex", asm3.html.options_sexes(dbo))))
    h.append(jqm_fieldcontain("animaltype", _("Type", l), jqm_select("animaltype", asm3.html.options_animal_types(dbo, False, asm3.configuration.default_type(dbo)))))
    h.append(jqm_fieldcontain("species", _("Species", l), jqm_select("species", asm3.html.options_species(dbo, False, asm3.configuration.default_species(dbo)))))
    h.append(jqm_fieldcontain("breed1", _("Breed", l), jqm_select("breed1", asm3.html.options_breeds(dbo, False, asm3.configuration.default_breed(dbo)))))
    h.append(jqm_fieldcontain("basecolour", _("Color", l), jqm_select("basecolour", asm3.html.options_colours(dbo, False, asm3.configuration.default_colour(dbo)))))
    h.append(jqm_fieldcontain("internallocation", _("Location", l), jqm_select("internallocation", asm3.html.options_internal_locations(dbo, False, asm3.configuration.default_location(dbo)))))
    h.append(jqm_fieldcontain("unit", _("Unit", l), jqm_text("unit")))
    h.append(jqm_fieldcontain("size", _("Size", l), jqm_select("size", asm3.html.options_sizes(dbo, False, asm3.configuration.default_size(dbo)))))
    h.append(jqm_submit(_("Add Animal", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_addincident(l, homelink, dbo):
    h = []
    h.append(header(l))
    h.append(jqm_page_header("incidentadd", _("Add Call", l), homelink))
    h.append(jqm_form("incform"))
    h.append(jqm_hidden("posttype", "ainc"))
    h.append(jqm_fieldcontain("incidenttype", _("Type", l), jqm_select("incidenttype", asm3.html.options_incident_types(dbo, False, asm3.configuration.default_incident(dbo)))))
    h.append(jqm_fieldcontain("callnotes", _("Notes", l), jqm_text("callnotes")))
    h.append(jqm_fieldcontain("dispatchaddress", _("Address", l), jqm_text("dispatchaddress")))
    h.append(jqm_fieldcontain("dispatchtown", _("City", l), jqm_text("dispatchtown")))
    h.append(jqm_fieldcontain("dispatchcounty", _("State", l), jqm_text("dispatchcounty")))
    h.append(jqm_fieldcontain("dispatchpostcode", _("Zipcode", l), jqm_text("dispatchpostcode")))
    h.append(jqm_submit(_("Add", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_check_licence(l, homelink, q, matches):
    """
    Generates the page of results of matching licences.
    l: The locale
    matches: A list of licence records from get_licence_find_simple
    """
    h = []
    h.append(header(l))
    h.append(jqm_page_header("", _("Results for '{0}'.", l).format(q), homelink))
    for m in matches:
        h.append("<p><b>%s (%s) - %s</b>" % (m["LICENCENUMBER"], m["LICENCETYPENAME"], m["OWNERNAME"]))
        if m["OWNERADDRESS"] is not None and m["OWNERADDRESS"].strip() != "":
            h.append("<br/>%s, %s, %s %s" % (m["OWNERADDRESS"], m["OWNERTOWN"], m["OWNERCOUNTY"], m["OWNERPOSTCODE"]))
        h.append("<br/>%s %s %s" % (python2display(l, m["ISSUEDATE"]), asm3.html.icon("right"), python2display(l, m["EXPIRYDATE"])))
        if m["SHELTERCODE"] is not None: 
            h.append("<br/>%s %s" % (m["SHELTERCODE"], m["ANIMALNAME"]))
        if len(m["COMMENTS"]) != 0: 
            h.append("<br/>%s" % m["COMMENTS"])
        h.append("</p>")
    if q.strip() == "":
        h.append("<p>%s</p>" % _("No data.", l))
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_viewanimal(session, l, dbo, a, af, diet, vacc, test, med, logs, homelink, post):
    """
    Generate the view animal mobile page.
    session: The session
    l:  The locale
    a:  An animal record
    af: Additional fields for the animal record
    diet: Diets for the animal
    vacc: Vaccinations for the animal
    test: Tests for the animal
    med: Medicals for the animal
    logs: Logs for the animal
    homelink: Link to the home menu
    post: The posted values
    """
    def table():
        return "<table style='width: 100%; border-bottom: 1px solid black;'>"
    def table_end():
        return "</table>"
    def hd(label):
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td></tr>" % label
    def tr(label, value, value2 = "", value3 = ""):
        if value is None or str(value).startswith("None "): value = ""
        if value2 is None or str(value2).startswith("None"): value2 = ""
        if value2 is not None and value2 != "": value2 = "<td>%s</td>" % value2
        if value3 is not None and value3 != "": value3 = "<td>%s</td>" % value3
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td><td>%s</td>%s%s</tr>" % (label, value, value2, value3)
    h = []
    h.append(header(l))
    h.append(jqm_page_header("", "%s - %s" % (a["CODE"], a["ANIMALNAME"]), homelink))
    h.append(table())
    h.append("<tr><td><img src='%s' class='asm-thumbnail' /></td>" % asm3.html.thumbnail_img_src(dbo, a, "animalthumb"))
    h.append("<td><h2 style='margin: 2px;'>%s - %s</h2>" % (a["CODE"], a["ANIMALNAME"]))
    h.append("%s %s %s</td>" % (a["SEXNAME"], a["BREEDNAME"], a["SPECIESNAME"]))
    h.append("</tr></table>")
    h.append(table())
    uploadstatus = ""
    if post["success"] == "true":
        uploadstatus = _("Photo successfully uploaded.", l)
    h.append("""
        <tr><td style='font-weight: bold; width: 150px;'>%s</td>
        <td>
        <form data-ajax="false" action="mobile_post" method="post" enctype="multipart/form-data">
        <input type="hidden" name="animalid" value="%d" />
        <input type="hidden" name="posttype" value="uai" />
        <input type="hidden" name="comments" value="" />
        <input type="hidden" name="base64image" value="" />
        <input type="file" data-role='none' accept="image/*" capture="camera" name="filechooser" id="fc%d" />
        <input id='sfc%d' type='submit' data-icon='arrow-u' data-inline='true' data-mini='true' value='%s' />
        </form>
        <span class="tip">%s</span>
        </td></tr>""" % (_("Upload Photo", l), a["ID"], a["ID"], 
                         a["ID"], _("Send", l), uploadstatus))
    h.append(table_end())
    h.append(table())
    h.append(tr( _("Status", l), asm3.publishers.base.get_adoption_status(dbo, a)))
    h.append(tr( _("Type", l), a["ANIMALTYPENAME"]))
    h.append(tr( _("Location", l), a["DISPLAYLOCATION"]))
    h.append(tr( _("Color", l), a["BASECOLOURNAME"]))
    h.append(tr( _("Coat Type", l), a["COATTYPENAME"]))
    h.append(tr( _("Size", l), a["SIZENAME"]))
    h.append(tr( _("DOB", l), python2display(l, a["DATEOFBIRTH"]), a["ANIMALAGE"]))
    h.append(table_end())
    h.append(table())
    h.append(tr( _("Markings", l), a["MARKINGS"]))
    h.append(tr( _("Hidden Comments", l), a["HIDDENANIMALDETAILS"]))
    h.append(tr( _("Comments", l), a["ANIMALCOMMENTS"]))
    h.append(table_end())
    h.append(table())
    h.append(tr( _("Cats", l), a["ISGOODWITHCATSNAME"]))
    h.append(tr( _("Dogs", l), a["ISGOODWITHDOGSNAME"]))
    h.append(tr( _("Children", l), a["ISGOODWITHCHILDRENNAME"]))
    h.append(tr( _("Housetrained", l), a["ISHOUSETRAINEDNAME"]))
    h.append(table_end())
    h.append(table())
    if asm3.users.check_permission_bool(session, asm3.users.VIEW_PERSON):
        h.append(tr( _("Original Owner", l), a["ORIGINALOWNERNAME"]))
        h.append(tr( _("Brought In By", l), a["BROUGHTINBYOWNERNAME"]))
    h.append(tr( _("Date Brought In", l), python2display(l, a["DATEBROUGHTIN"])))
    h.append(tr( _("Bonded With", l), "%s %s %s %s" % (a["BONDEDANIMAL1CODE"], a["BONDEDANIMAL1NAME"], a["BONDEDANIMAL2CODE"], a["BONDEDANIMAL2NAME"])))
    h.append(tr( _("Transfer?", l), a["ISTRANSFERNAME"] == 1))
    h.append(tr( _("Entry Category", l), a["ENTRYREASONNAME"]))
    h.append(tr( _("Entry Reason", l), a["REASONFORENTRY"]))
    h.append(table_end())
    h.append(table())
    h.append(tr( _("Microchipped", l), python2display(l, a["IDENTICHIPDATE"]), asm3.utils.iif(a["IDENTICHIPPED"] == 1, a["IDENTICHIPNUMBER"], "")))
    h.append(tr( _("Tattoo", l), python2display(l, a["TATTOODATE"]), asm3.utils.iif(a["TATTOO"] == 1, a["TATTOONUMBER"], "")))
    h.append(tr( _("Neutered", l), asm3.utils.iif(a["NEUTERED"] == 1, python2display(l, a["NEUTEREDDATE"]), "")))
    h.append(tr( _("Declawed", l), asm3.utils.iif(a["DECLAWED"] == 1, a["DECLAWEDNAME"], "")))
    h.append(tr( _("Heartworm Tested", l), python2display(l, a["HEARTWORMTESTDATE"]), asm3.utils.iif(a["HEARTWORMTESTED"] == 1, a["HEARTWORMTESTRESULTNAME"], "")))
    h.append(tr( _("FIV/L Tested", l), python2display(l, a["COMBITESTDATE"]), asm3.utils.iif(a["COMBITESTED"] == 1, "%s %s" % (a["COMBITESTRESULTNAME"], a["FLVRESULTNAME"]), "")))
    h.append(tr( _("Health Problems", l), a["HEALTHPROBLEMS"]))
    h.append(tr( _("Rabies Tag", l), a["RABIESTAG"]))
    h.append(tr( _("Special Needs", l), a["HASSPECIALNEEDSNAME"]))
    h.append(tr( _("Current Vet", l), a["CURRENTVETNAME"], jqm_tel(l, a["CURRENTVETWORKTELEPHONE"])))
    h.append(table_end())
    
    if len(af) > 0:
        h.append(table())
        for d in af:
            if d["FIELDTYPE"] == asm3.additional.ANIMAL_LOOKUP:
                h.append(tr(d["FIELDLABEL"], asm3.animal.get_animal_namecode(dbo, asm3.utils.cint(d["VALUE"]))))
            elif d["FIELDTYPE"] == asm3.additional.PERSON_LOOKUP:
                h.append(tr(d["FIELDLABEL"], asm3.person.get_person_name_code(dbo, asm3.utils.cint(d["VALUE"]))))
            elif d["FIELDTYPE"] == asm3.additional.MONEY:
                h.append(tr(d["FIELDLABEL"], format_currency(l, d["VALUE"])))
            elif d["FIELDTYPE"] == asm3.additional.YESNO:
                h.append(tr(d["FIELDLABEL"], d["VALUE"] == "1" and _("Yes", l) or _("No", l)))
            else:
                h.append(tr(d["FIELDLABEL"], d["VALUE"]))
        h.append(table_end())
    
    if asm3.users.check_permission_bool(session, asm3.users.VIEW_DIET):
        h.append(table())
        h.append(hd(_("Diet", l)))
        for d in diet:
            h.append(tr(python2display(l, d["DATESTARTED"]), d["DIETNAME"], d["COMMENTS"]))
        h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_VACCINATION):
        h.append(table())
        h.append(hd(_("Vaccination", l)))
        for v in vacc:
            h.append(tr(python2display(l, v["DATEREQUIRED"]), python2display(l, v["DATEOFVACCINATION"]), v["VACCINATIONTYPE"]))
        h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_TEST):
        h.append(table())
        h.append(hd(_("Test", l)))
        for t in test:
            h.append(tr(python2display(l, t["DATEREQUIRED"]), python2display(l, t["DATEOFTEST"]), t["TESTNAME"], asm3.utils.iif(t["DATEOFTEST"] is not None, t["RESULTNAME"], "")))
        h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_MEDICAL):
        h.append(table())
        h.append(hd(_("Medical", l)))
        for m in med:
            h.append(tr(python2display(l, m["STARTDATE"]), m["TREATMENTNAME"], m["DOSAGE"]))
        h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_LOG):
        h.append(table())
        h.append(hd(_("Log", l)))
        for lo in logs:
            h.append(tr(python2display(l, lo["DATE"]), lo["LOGTYPENAME"], lo["COMMENTS"]))
        h.append(table_end())

    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_viewincident(session, l, dbo, a, amls, cit, dia, logs, homelink, post):
    """
    Generate the view incident mobile page.
    session: The session
    l:  The locale
    a:   An incident record
    amls: Any linked animals for the incident
    cit: Citations for the incident
    dia: Diary notes for the incident
    logs: Logs for the incident
    homelink: Link to the home menu
    post: The posted values
    """
    def table():
        return "<table style='width: 100%; border-bottom: 1px solid black;'>"
    def table_end():
        return "</table>"
    def hd(label):
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td></tr>" % label
    def tr(label, value, value2 = "", value3 = ""):
        if value is None or str(value).startswith("None "): value = ""
        if value2 is None or str(value2).startswith("None"): value2 = ""
        if value2 is not None and value2 != "": value2 = "<td>%s</td>" % value2
        if value3 is not None and value3 != "": value3 = "<td>%s</td>" % value3
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td><td>%s</td>%s%s</tr>" % (label, value, value2, value3)
    def dt(field):
        if field is None: return ""
        return "%s %s" % (python2display(l, field), format_time(field))
    h = []
    h.append(header(l))
    h.append(jqm_page_header("", "%s - %s" % (a["INCIDENTNAME"], a["OWNERNAME"]), homelink))
    h.append(table())
    h.append("<tr>")
    h.append("<td><h2 style='margin: 2px;'>%s - %s</h2>" % (a["INCIDENTNAME"], a["OWNERNAME"]))
    h.append("%s</td>" % (a["CALLNOTES"]))
    h.append("</tr></table>")
    h.append(table())
    h.append(tr( _("Number", l), asm3.utils.padleft(a["ID"], 6)))
    h.append(tr( _("Type", l), a["INCIDENTNAME"]))
    h.append(tr( _("Incident Date/Time", l), dt(a["INCIDENTDATETIME"])))
    h.append(tr( _("Notes", l), a["CALLNOTES"]))
    h.append(tr( _("Completion Date/Time", l), dt(a["COMPLETEDDATE"])))
    comptp = a["COMPLETEDNAME"]
    if a["COMPLETEDDATE"] is None:
        comptp = jqm_select("comptype", 
            '<option value="-1"></option>' + jqm_options(asm3.lookups.get_incident_completed_types(dbo), "ID", "COMPLETEDNAME"), 
            "completedtype", str(a["ID"]))
    h.append(tr( _("Completion Type", l), comptp))
    h.append(tr( _("Call Date/Time", l), dt(a["CALLDATETIME"])))
    h.append(tr( _("Taken By", l), a["CALLTAKER"]))
    if asm3.users.check_permission_bool(session, asm3.users.VIEW_PERSON):
        h.append(tr( _("Caller", l), a["CALLERNAME"]))
        h.append(tr( _("Phone", l), "%s %s %s" % (jqm_tel(l, a["CALLERHOMETELEPHONE"]), jqm_tel(l, a["CALLERWORKTELEPHONE"]), jqm_tel(l, a["CALLERMOBILETELEPHONE"]))))
        h.append(tr( _("Victim", l), a["VICTIMNAME"]))
    h.append(table_end())
   
    h.append(table())
    h.append(hd(_("Dispatch", l)))
    h.append(tr( _("Address", l), a["DISPATCHADDRESS"]))
    h.append(tr( _("City", l), a["DISPATCHTOWN"]))
    h.append(tr( _("State", l), a["DISPATCHCOUNTY"]))
    h.append(tr( _("Zipcode", l), a["DISPATCHPOSTCODE"]))
    h.append(tr( _("Dispatched ACO", l), a["DISPATCHEDACO"]))
    dispdt = dt(a["DISPATCHDATETIME"])
    if dispdt == "":
        dispdt = jqm_button("mobile_post?posttype=vincdisp&id=%d" % a["ID"], _("Dispatch", l), "calendar", "false")
    h.append(tr( _("Dispatch Date/Time", l), dispdt))
    respdt = dt(a["RESPONDEDDATETIME"])
    if respdt == "":
        respdt = jqm_button("mobile_post?posttype=vincresp&id=%d" % a["ID"], _("Respond", l), "calendar", "false")
    # If it's not dispatched yet, don't allow respond
    if a["DISPATCHDATETIME"] is None: respdt = ""
    h.append(tr( _("Responded Date/Time", l), respdt))
    h.append(tr( _("Followup Date/Time", l), dt(a["FOLLOWUPDATETIME"])))
    h.append(tr( _("Followup Date/Time", l), dt(a["FOLLOWUPDATETIME2"])))
    h.append(tr( _("Followup Date/Time", l), dt(a["FOLLOWUPDATETIME3"])))
    h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_PERSON):
        h.append(table())
        h.append(hd(_("Suspect/Animal", l)))
        h.append(tr( _("Suspect 1", l), a["OWNERNAME1"]))
        h.append(tr( _("Suspect 2", l), a["OWNERNAME2"]))
        h.append(tr( _("Suspect 3", l), a["OWNERNAME3"]))
    for m in amls:
        h.append(tr( _("Animal", l), '<a href="mobile_post?posttype=va&id=%d">%s - %s</a>' % (m["ANIMALID"], m["SHELTERCODE"], m["ANIMALNAME"])))
    h.append(tr( _("Species", l), a["SPECIESNAME"]))
    h.append(tr( _("Sex", l), a["SEXNAME"]))
    h.append(tr( _("Age Group", l), a["AGEGROUP"]))
    h.append(tr( _("Description", l), a["ANIMALDESCRIPTION"]))
    h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_CITATION):
        h.append(table())
        h.append(hd(_("Citations", l)))
        for c in cit:
            h.append(tr(python2display(l, c["CITATIONDATE"]), c["CITATIONNAME"], c["COMMENTS"]))
        h.append(table_end())

    h.append(table())
    h.append(hd(_("Diary", l)))
    for d in dia:
        h.append(tr(python2display(l, d["DIARYDATETIME"]), d["SUBJECT"], d["NOTE"]))
    h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_LOG):
        h.append(table())
        h.append(hd(_("Log", l)))
        for lo in logs:
            h.append(tr(python2display(l, lo["DATE"]), lo["LOGTYPENAME"], lo["COMMENTS"]))
        h.append(table_end())

    h.append(jqm_form("aclog", ajax="false"))
    h.append(jqm_hidden("id", str(a["ID"])))
    h.append(jqm_hidden("posttype", "vinclog"))
    h.append(jqm_fieldcontain("logtype", _("Log Type", l), jqm_select("logtype", jqm_options(asm3.lookups.get_log_types(dbo), "ID", "LOGTYPENAME"))))
    h.append(jqm_fieldcontain("logtext", _("Log Text", l), jqm_text("logtext")))
    h.append(jqm_submit(_("Add Log", l)))
    h.append(jqm_form_end())

    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_viewperson(session, l, dbo, p, af, cit, dia, lic, links, logs, homelink, post):
    """
    Generate the view person mobile page.
    session: The session
    l:  The locale
    o:  A person record
    af: Additional fields for the person record
    cit: Citations for the person
    dia: Diary notes for the person
    lic: Licenses for the person
    logs: Logs for the animal
    homelink: Link to the home menu
    post: The posted values
    """
    def table():
        return "<table style='width: 100%; border-bottom: 1px solid black;'>"
    def table_end():
        return "</table>"
    def hd(label):
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td></tr>" % label
    def tr(label, value, value2 = "", value3 = ""):
        if value is None or str(value).startswith("None "): value = ""
        if value2 is None or str(value2).startswith("None"): value2 = ""
        if value2 is not None and value2 != "": value2 = "<td>%s</td>" % value2
        if value3 is not None and value3 != "": value3 = "<td>%s</td>" % value3
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td><td>%s</td>%s%s</tr>" % (label, value, value2, value3)
    h = []
    h.append(header(l))
    h.append(jqm_page_header("", "%s" % p["OWNERNAME"], homelink))
    h.append(table())
    h.append("<tr><td><img src='%s' class='asm-thumbnail' /></td>" % asm3.html.thumbnail_img_src(dbo, p, "personthumb"))
    h.append("<td><h2 style='margin: 2px;'>%s - %s</h2>" % (p["OWNERNAME"], p["OWNERADDRESS"]))
    h.append("%s</td>" % person_flags(p["ADDITIONALFLAGS"]))
    h.append("</tr></table>")

    h.append(table())
    h.append(tr( _("Name", l), p["OWNERNAME"]))
    h.append(tr( _("Address", l), p["OWNERADDRESS"]))
    h.append(tr( _("City", l), p["OWNERTOWN"]))
    h.append(tr( _("State", l), p["OWNERCOUNTY"]))
    h.append(tr( _("Zipcode", l), p["OWNERPOSTCODE"]))
    h.append(tr( _("Home Phone", l), jqm_tel(l, p["HOMETELEPHONE"])))
    h.append(tr( _("Work Phone", l), jqm_tel(l, p["WORKTELEPHONE"])))
    h.append(tr( _("Cell Phone", l), jqm_tel(l, p["MOBILETELEPHONE"])))
    h.append(tr( _("Email", l), jqm_email(p["EMAILADDRESS"])))
    h.append(tr( _("Exclude from bulk email", l), asm3.utils.iif(p["EXCLUDEFROMBULKEMAIL"] == 1, _("Yes", l), _("No", l))))
    h.append(table_end())
    h.append(table())
    h.append(tr( _("Comments", l), p["COMMENTS"]))
    h.append(tr( _("Membership Number", l), p["MEMBERSHIPNUMBER"]))
    h.append(tr( _("Membership Expiry", l), python2display(l, p["MEMBERSHIPEXPIRYDATE"])))
    h.append(tr( _("Foster Capacity", l), str(p["FOSTERCAPACITY"])))
    h.append(table_end())
    
    if len(af) > 0:
        h.append(table())
        for d in af:
            if d["FIELDTYPE"] == asm3.additional.ANIMAL_LOOKUP:
                h.append(tr(d["FIELDLABEL"], asm3.animal.get_animal_namecode(dbo, asm3.utils.cint(d["VALUE"]))))
            elif d["FIELDTYPE"] == asm3.additional.PERSON_LOOKUP:
                h.append(tr(d["FIELDLABEL"], asm3.person.get_person_name_code(dbo, asm3.utils.cint(d["VALUE"]))))
            elif d["FIELDTYPE"] == asm3.additional.MONEY:
                h.append(tr(d["FIELDLABEL"], format_currency(l, d["VALUE"])))
            elif d["FIELDTYPE"] == asm3.additional.YESNO:
                h.append(tr(d["FIELDLABEL"], d["VALUE"] == "1" and _("Yes", l) or _("No", l)))
            else:
                h.append(tr(d["FIELDLABEL"], d["VALUE"]))
        h.append(table_end())

    h.append(table())
    h.append(hd(_("Links", l)))
    for k in links:
        h.append(tr(python2display(l, k["DDATE"]), k["TYPEDISPLAY"], k["LINKDISPLAY"]))
    h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_CITATION):
        h.append(table())
        h.append(hd(_("Citations", l)))
        for c in cit:
            h.append(tr(python2display(l, c["CITATIONDATE"]), c["CITATIONNAME"], c["COMMENTS"]))
        h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_DIARY):
        h.append(table())
        h.append(hd(_("Diary", l)))
        for d in dia:
            h.append(tr(python2display(l, d["DIARYDATETIME"]), d["SUBJECT"], d["NOTE"]))
        h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_LICENCE):
        h.append(table())
        h.append(hd(_("License", l)))
        for i in lic:
            h.append(tr(python2display(l, i["ISSUEDATE"]), python2display(l, i["EXPIRYDATE"]), i["LICENCENUMBER"]))
        h.append(table_end())

    if asm3.users.check_permission_bool(session, asm3.users.VIEW_LOG):
        h.append(table())
        h.append(hd(_("Log", l)))
        for lo in logs:
            h.append(tr(python2display(l, lo["DATE"]), lo["LOGTYPENAME"], lo["COMMENTS"]))
        h.append(table_end())

    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_stocklocation(l, homelink, locationname, sl, su):
    """
    Generate a page that allows adjusting stock levels in the 
    records sl. su is a list of stock usages for the dropdown
    """
    h = []
    h.append(header(l))
    h.append(jqm_page_header("", locationname, homelink))
    h.append(jqm_form("st", ajax="false"))
    h.append(jqm_hidden("posttype", "stu"))
    h.append(jqm_fieldcontain("usagetype", _("Usage Type", l) , jqm_select("usagetype", jqm_options(su, "ID", "USAGETYPENAME", "6"))))
    for s in sl:
        h.append(jqm_fieldcontain("sl%d" % s["SLID"], s["NAME"], jqm_slider("sl%d" % s["SLID"], 0, s["TOTAL"], s["BALANCE"])))
    h.append(jqm_submit(_("Save", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def login(post, session, remoteip, useragent, path):
    """
    Handles the login post
    """
    url = asm3.users.web_login(post, session, remoteip, useragent, path)
    if url == "FAIL" or url == "DISABLED":
        return "mobile_login"
    else:
        return "mobile"

def report_criteria(dbo, crid, title, crit):
    """
    Generates the mobile report criteria page
    """
    h = []
    l = dbo.locale
    homelink = "<a href='mobile' data-ajax='false' class='ui-btn-right' data-icon='home' data-theme='b'>%s</a>" % _("Home", l)
    h.append(header(l))
    h.append(jqm_page_header("", title, homelink))
    h.append("<div id=\"criteriaform\">")
    h.append("<input data-post=\"id\" type=\"hidden\" value=\"%d\" />" % crid)
    h.append("<input data-post=\"mode\" type=\"hidden\" value=\"exec\" />")
    h.append(crit)
    h.append("</div>")
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

