/*global $, _, asm, common, config, format, header, html */
/*global edit_header: true */

var edit_header;

$(function() {

"use strict";

// If this is the login or database create page, don't do anything - they don't have headers, 
// but for the sake of making life easy, they still include this file.
if (common.current_url().indexOf("/login") != -1 ||
    common.current_url().indexOf("/database") != -1) {
    return;
}

// The edit header object deals with the banners at the top of the animal,
// person, waiting list and lost/found edit pages..
// it also has functions for person and animal flags
edit_header = {

    /**
     * Renders the header for any of the animal edit pages, with thumbnail image,
     * info and tabs. The caller will need to add a div to close out this header.
     * a: The animal row from the json
     * selected: The name of the selected tab (animal, vaccination, medical, diet, costs,
     *           donations, media, diary, movements, log)
     * counts:   A count of the number of records for each tab (in uppercase). If it's
     *           non-zero, an icon is shown on some tabs.
     */
    animal_edit_header: function(a, selected, counts) {
        let check_display_icon = function(key, iconname) {
            if (key == "animal") { return html.icon("blank"); }
            if (counts[key.toUpperCase()] > 0) {
                return html.icon(iconname);
            }
            return html.icon("blank");
        };
        let mediaprompt = "";
        if (a.WEBSITEMEDIANAME == null) {
            mediaprompt = '<br /><span style="white-space: nowrap"><a href="animal_media?id=' + a.ID + '&newmedia=1">[ ' + _("Add a photo") + ' ]</a></span>';
        }
        let currentowner = "";
        if (a.CURRENTOWNERID) {
            currentowner = " " + html.person_link(a.CURRENTOWNERID, a.CURRENTOWNERNAME);
        }
        let owner = "";
        if (a.OWNERID) {
            owner = " " + html.person_link(a.OWNERID, a.OWNERNAME);
        }
        let available = "";
        if (a.ARCHIVED == 0 && a.HASACTIVEBOARDING == 1) {
            // currently boarding at the shelter
            available = _("Boarding Animal");
            if (a.OWNERID && a.OWNERID > 0) {
                available += " " + html.icon("right") + " ";
                available += html.person_link(a.OWNERID, a.OWNERNAME);
            }
            available = html.info(available);
        }
        else if (a.NONSHELTERANIMAL == 1) {
            // show non-shelter info link
            available = _("Non-Shelter Animal");
            if (a.ORIGINALOWNERID && a.ORIGINALOWNERID > 0) {
                available += " " + html.icon("right") + " ";
                available += html.person_link(a.ORIGINALOWNERID, a.ORIGINALOWNERNAME);
            }
            available = html.info(available);
        }
        else if ((a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2) || (a.HASPERMANENTFOSTER == 1))  {
            // left the shelter, don't show anything
            available = "";
        }
        else if (html.is_animal_adoptable(a)[0]) {
            // available
            available = html.info(_("Available for adoption"));
        }
        else {
            // not available, include reason
            available = html.error(_("Not available for adoption") + 
                "<br/>(" + html.is_animal_adoptable(a)[1] + ")");
        }
        let banner = [];
        if (common.nulltostr(a.HIDDENANIMALDETAILS) != "") {
            banner.push(a.HIDDENANIMALDETAILS);
        }
        if (common.nulltostr(a.MARKINGS) != "") {
            banner.push(a.MARKINGS);
        }
        if (common.nulltostr(a.ANIMALCOMMENTS) != "") {
            banner.push(a.ANIMALCOMMENTS);
        }
        let displaylocation = "";
        if (a.DECEASEDDATE != null) {
            var deathreason = a.DISPLAYLOCATIONNAME;
            if (a.DIEDOFFSHELTER == 1) { deathreason = _("Died off shelter"); }
            displaylocation = "<span style=\"color: red\">" + _("Deceased") + " " + html.icon("right") + " " + deathreason + "</span> " + format.date(a.DECEASEDDATE);
        }
        else {
            if (owner != "" && a.CURRENTOWNERID != a.OWNERID) {
                displaylocation = _("Owner") + " " + html.icon("right") + " " + owner;
            }
            else if (currentowner != "" && !a.HASACTIVEBOARDING) {
                displaylocation = a.DISPLAYLOCATIONNAME + " " + html.icon("right") + " " + currentowner;
            }
            else if (a.SHELTERLOCATIONUNIT && !a.ACTIVEMOVEMENTDATE) {
                displaylocation = a.DISPLAYLOCATIONNAME + ' <span class="asm-search-locationunit" title="' + html.title(_("Unit")) + '">' + a.SHELTERLOCATIONUNIT + '</span>';
            }
            else {
                displaylocation = a.DISPLAYLOCATIONNAME;
            }
        }
        let animalcontrol = "";
        if (a.ANIMALCONTROLINCIDENTID) {
            animalcontrol = '<tr><td>' + _("Incident") + ':</td><td><b>' +
                '<a href="incident?id=' + a.ANIMALCONTROLINCIDENTID + '">' +
                format.date(a.ANIMALCONTROLINCIDENTDATE) + ' ' + 
                a.ANIMALCONTROLINCIDENTNAME + '</b></td></tr>';
        }
        let hold = "";
        if (a.ISHOLD == 1 && a.HOLDUNTILDATE) {
            hold = '<tr><td>' + _("Hold until") + ':</td><td><b>' + format.date(a.HOLDUNTILDATE) + '</b></td></tr>';
        }
        let coordinator = "";
        if (a.ADOPTIONCOORDINATORID) {
            coordinator = '<tr><td>' + _("Adoption Coordinator") + ':</td><td><b>' + html.person_link(a.ADOPTIONCOORDINATORID, a.ADOPTIONCOORDINATORNAME) + '</b></td></tr>';
        }
        let chipinfo = "";
        if (a.IDENTICHIPPED == 1) {
            chipinfo = '<tr><td>' + _("Microchip") + ':</td><td><b>' + a.IDENTICHIPNUMBER + " " + common.nulltostr(a.IDENTICHIP2NUMBER) + '</b></td></tr>';
        }
        let timeonshelter = a.TIMEONSHELTER + ' (' + a.DAYSONSHELTER + ' ' + _("days") + ')';
        let entershelterdate = "";
        if (a.ARCHIVED == 0 && a.HASACTIVEBOARDING == 1) {
            entershelterdate = format.date(a.ACTIVEBOARDINGINDATE) + " " + format.time(a.ACTIVEBOARDINGINDATE);
        }
        else {
            entershelterdate = format.date(a.MOSTRECENTENTRYDATE) + " ";
            if (format.time(a.MOSTRECENTENTRYDATE) != "00:00:00") { 
                entershelterdate += format.time(a.MOSTRECENTENTRYDATE); 
            }
        }
        let leftshelterdate = "";
        if (a.ARCHIVED == 0 && a.HASACTIVEBOARDING == 1) {
            leftshelterdate = format.date(a.ACTIVEBOARDINGOUTDATE) + " " + format.time(a.ACTIVEBOARDINGOUTDATE);
            timeonshelter = "";
        }
        else if (a.ARCHIVED == 1 && a.DECEASEDDATE && a.DIEDOFFSHELTER == 0) { 
            leftshelterdate = format.date(a.DECEASEDDATE); 
        }
        else if (a.ARCHIVED == 1) { 
            leftshelterdate = format.date(a.ACTIVEMOVEMENTDATE); 
        }
        let sizeweight = "";
        if (a.WEIGHT && !config.bool("DontShowSizeWeightHeader")) {
            sizeweight = a.SIZENAME + " / " + a.WEIGHT + (config.bool("ShowWeightInLbs") || config.bool("ShowWeightInLbsFraction") ? "lb" : "kg");
        }
        var first_column = [
            '<input type="hidden" id="animalid" value="' + a.ID + '" />',
            '<div class="asm-grid">',
            '<div class="asm-grid-col-3">',
                '<table><tr>',
                '<td align="center">',
                    '<a target="_blank" href="' + html.img_src(a, "animal") + '">',
                    '<img class="' + html.animal_link_thumb_classes(a) + '" src="' + html.thumbnail_src(a, "animalthumb") + '" />',
                    '</a>',
                    mediaprompt,
                '</td>',
                '<td>',
                '<h2>' + html.icon("animal", _("Animal")) + a.ANIMALNAME + ' - ' + a.CODE + ' ' + html.animal_emblems(a) + '</h2>',
                '<p>' + common.substitute(_("{0} {1} aged {2}"), { "0": "<b>" + a.SEXNAME, "1": a.SPECIESNAME + "</b>", "2": "<b>" + a.ANIMALAGE + "</b>" }),
                sizeweight,
                '<br />',
                html.truncate(banner.join(". "), 100),
                '</p>',
                '</td></tr></table>',
            '</div>'
        ].join("\n");
        var second_column = [
            '<div class="asm-grid-col-3">',
            '<table>',
            '<tr>',
            '<td id="hloc">' + _("Location") + ':</td><td><b>' + displaylocation + '</b></td>',
            '</tr>',
            coordinator,
            animalcontrol,
            chipinfo,
            '<tr>',
            '<td id="hentshel">' + _("Entered shelter") + ':</td><td><b>' + entershelterdate + '</b></td>',
            '</tr>',
            hold,
            '<tr>',
            '<td id="hleftshel">' + _("Left shelter") + ':</td><td><b>' + leftshelterdate + '</b></td>',
            '</tr>',
            timeonshelter != "" ? '<tr><td id="htimeonshel">' + _("Time on shelter") + ':</td><td><b>' + timeonshelter + '</b></td></tr>' : '',
            '</table>',
            '</div>'
        ].join("\n");
        if (a.NONSHELTERANIMAL == 1) {
            second_column = [ 
                '<div class="asm-grid-col-3">',
                '<table>',
                '<tr>',
                animalcontrol,
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        }
        var third_column = [
            '<div class="asm-grid-col-3">',
            _("Added by {0} on {1}").replace("{0}", "<b>" + a.CREATEDBY + "</b>").replace("{1}", "<b>" + format.date(a.CREATEDDATE) + "</b>") + '<br />',
            _("Last changed by {0} on {1}").replace("{0}", "<b>" + a.LASTCHANGEDBY + "</b>").replace("{1}", "<b>" + format.date(a.LASTCHANGEDDATE) + "</b>") + '<br />',
            available,
            '</div>',
            '</div>'
        ].join("\n");
        var s = [
            '<div class="asm-banner ui-helper-reset ui-widget-content ui-corner-all">',
            first_column,
            second_column,
            third_column,
            '</div>',
            '<div class="asm-tabbar">',
            '<ul class="asm-tablist">'
        ].join("\n");
        var tabs = [[ "animal", "animal", _("Animal"), "", "va" ],
            [ "vaccination", "animal_vaccination", _("Vaccination"), "vaccination", "vav" ],
            [ "test", "animal_test", _("Test"), "test", "vat" ],
            [ "medical", "animal_medical", _("Medical"), "medical", "mvam" ],
            [ "boarding", "animal_boarding", _("Boarding"), "boarding", "vbi" ],
            [ "clinic", "animal_clinic", _("Clinic"), "health", "vcl" ],
            [ "licence", "animal_licence", _("License"), "licence", "vapl" ],
            [ "diet", "animal_diet", _("Diet"), "diet", "dvad" ],
            [ "costs", "animal_costs", _("Costs"), "cost", "cvad" ],
            [ "donations", "animal_donations", _("Payments"), "donation", "ovod" ],
            [ "media", "animal_media", _("Media"), "media", "vam" ],
            [ "diary", "animal_diary", _("Diary"), "diary", "vdn" ],
            [ "transport", "animal_transport", _("Transport"), "transport", "vtr" ],
            [ "movements", "animal_movements", _("Movements"), "movement", "vamv" ],
            [ "logs", "animal_log", _("Log"), "log", "vle" ]];
        $.each(tabs, function(it, vt) {
            var key = vt[0], url = vt[1], display = vt[2], iconname = vt[3], perms = vt[4];
            if (perms && !common.has_permission(perms)) { return; } // don't show if no permission
            if ((key == "boarding") && config.bool("DisableBoarding")) { return; }
            if ((key == "boarding") && a.HASACTIVEBOARDING == 0 && a.ARCHIVED == 0) { return; } // don't show boarding tab for non-owned shelter animals
            if ((key == "clinic") && config.bool("DisableClinic")) { return; }
            if ((key == "licence") && config.bool("DisableAnimalControl")) { return; }
            if ((key == "movements") && config.bool("DisableMovements")) { return; }
            if ((key == "movements") && a.NONSHELTERANIMAL == 1) { return; }
            if ((key == "transport") && config.bool("DisableTransport")) { return; }
            if (key == selected) {
                s += "<li class=\"ui-tabs-selected ui-state-active\"><a href=\"#\">" + display + " " + check_display_icon(key, iconname) + "</a></li>";
            }
            else {
                s += "<li><a href=\"" + url + "?id=" + a.ID + "\">" + display + " " + check_display_icon(key, iconname) + "</a></li>";
            }
        });
        s += "</ul>";
        s += '<div id="asm-content">';
        return s;
    },

    /**
     * Returns a bunch of <li> tags with links to run diary tasks.
     * tasks: A set of diary task records
     * mode: ANIMAL or PERSON
     */
    diary_task_list: function(tasks, mode) {
        var s = [];
        $.each(tasks, function(i, t) {
            s.push('<li class="asm-menu-item"><a href="#" class="diarytask" data="' + mode + ' ' + t.ID + ' ' + t.NEEDSDATE + '">' + t.NAME + '</a></li>');
        });
        return s.join("\n");
    },

    gdpr_contact_options: function() {
        return [
            '<option value="didnotask">' + _("Did not ask") + '</option>',
            '<option value="declined">' + _("Declined") + '</option>',
            '<option value="email">' + _("Email") + '</option>',
            '<option value="post">' + _("Post") + '</option>',
            '<option value="sms">' + _("SMS") + '</option>',
            '<option value="phone">' + _("Phone") + '</option>'
        ];
    },

    /**
     * Renders the header for any of the event edit pages, with thumbnail image,
     * info and tabs. The caller will need to add a div to close out this header.
     * e: The event row from the json
     * selected: The name of the selected tab (Details)
     * counts:   A count of the number of records for each tab (in uppercase). If it's
     *           non-zero, an icon is shown on some tabs.
     */
    event_edit_header: function(e, selected, counts){
        var check_display_icon = function(key, iconname) {
            if (key == "event") { return html.icon("blank"); }
            if (counts[key.toUpperCase()] > 0) {
                return html.icon(iconname);
            }
            return html.icon("blank");
        };
        var eventName = "";
        if (e.EVENTNAME) {eventName = e.EVENTNAME;}
        else {eventName = "Unnamed event";}
        var location = [e.EVENTTOWN, e.EVENTCOUNTY, e.EVENTPOSTCODE, e.EVENTCOUNTRY].filter(Boolean).join(", ");
        var h = [
            '<div class="asm-banner ui-helper-reset ui-widget-content ui-corner-all">',
            '<input type="hidden" id="eventid" value="' + e.ID + '" />',
            '<div class="asm-grid">',
            '<div class="asm-grid-col-3">',
            '<h2>' + html.icon("event", _("Event")) + ' ' + eventName + '</h2>',
            '<p>' + html.truncate(e.EVENTDESCRIPTION, 100) + '</p>', 
            '</div>',
            '<div class="asm-grid-col-3">',
            '<table>',
            '<td></td>',
            '<td><b>',
            format.date(e.STARTDATETIME) + "-" + format.date(e.ENDDATETIME),
            '</b></td></tr>',
            '<tr>',
            '<td></td>',
            '<td><b>',
            e.EVENTADDRESS,
            '</b></td></tr>',
            '<tr>',
            '<td>' + _("Address") + ": " + '</td>',
            '<td><b>',
            location,
            '</b></td></tr>',
            '<td>' + _("Adoptions") + ": " + '</td>',
            '<td><b>',
            e.ADOPTIONS,
            '</b></td></tr>',
            '</table>',
            '</div>',
            '<div class="asm-grid-col-3">',
            _("Added by {0} on {1}").replace("{0}", "<b>" + e.CREATEDBY + "</b>").replace("{1}", "<b>" + format.date(e.CREATEDDATE) + "</b>") + ' <br/>',
            _("Last changed by {0} on {1}").replace("{0}", "<b>" + e.LASTCHANGEDBY + "</b>").replace("{1}", "<b>" + format.date(e.LASTCHANGEDDATE) + "</b>"),
            '</div>',
            '</div></div>',
            '<div class="asm-tabbar">',
            '<ul class="asm-tablist">'
        ];
        var tabs = [[ "event", "event", _("Event"), "", "ve" ],
            [ "animals", "event_animals", _("Animals"), "", "vea" ]
            ];
        $.each(tabs, function(it, vt) {
            var key = vt[0], url = vt[1], display = vt[2], iconname = vt[3], perms = vt[4];
            if (perms && !common.has_permission(perms)) { return; } // don't show if no permission
            if (key == selected) {
                h.push("<li class=\"ui-tabs-selected ui-state-active\"><a href=\"#\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
            else {
                h.push("<li><a href=\"" + url + "?id=" + e.ID + "\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
        });
        h.push('</ul>');
        h.push('<div id="asm-content">');
        return h.join("\n");
    },

    /** 
     * Returns the header for the incident pages, with the banner info and
     * tabs.
     * a: An animalcontrol row from animalcontrol.get_animalcontrol_query
     * selected: The name of the selected tab (details, media, diary, log)
     */
    incident_edit_header: function(a, selected, counts) {
        var check_display_icon = function(key, iconname) {
            if (key == "details") { return html.icon("blank"); }
            if (counts[key.toUpperCase()] > 0) {
                return html.icon(iconname);
            }
            return html.icon("blank");
        };
        var fine = "";
        if (a.FINEAMOUNT && a.FINEAMOUNT > 0 && a.FINEPAIDDATE) {
            fine = '<span class="asm-search-finepaid">' + _("{0} fine, paid").replace("{0}", format.currency(a.FINEAMOUNT)) + '</span>';
        }
        else if (a.FINEAMOUNT && a.FINEAMOUNT > 0) {
            fine = '<span class="asm-search-fineunpaid">' + _("{0} fine, unpaid").replace("{0}", format.currency(a.FINEAMOUNT)) + '</span>';
        }
        var h = [
            '<div class="asm-banner ui-helper-reset ui-widget-content ui-corner-all">',
            '<input type="hidden" id="incidentid" value="' + a.ACID + '" />',
            '<div class="asm-grid">',
            '<div class="asm-grid-col-3">',
            '<h2>' + html.icon("call", _("Incident")) + ' ' +
                format.padleft(controller.incident.ACID, 6) + ' ' + a.INCIDENTNAME +
                (a.OWNERNAME1 ? ' - ' + a.OWNERNAME1 : "") + 
                (a.OWNERNAME2 ? ', ' + a.OWNERNAME2 : "") + 
                (a.OWNERNAME3 ? ', ' + a.OWNERNAME3 : "") + 
                '</h2>',
            '<p>' + html.truncate(a.CALLNOTES) + '</p>',
            '</div>',
            '<div class="asm-grid-col-3">',
            '<table>',
            '<tr>',
            '<td>' + _("Call") + ':</td><td><b>' + format.date(a.CALLDATETIME) + ' ' + format.time(a.CALLDATETIME) + ' ' + 
                common.nulltostr(a.CALLERNAME) + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Address") + ':</td><td><b>' + a.DISPATCHADDRESS + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Dispatch") + ':</td><td><b>' + format.date(a.DISPATCHDATETIME) + ' ' + format.time(a.DISPATCHDATETIME) + 
                ' ' + common.nulltostr(a.DISPATCHEDACO) + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Responded") + ':</td><td><b>' + format.date(a.RESPONDEDDATETIME) + ' ' + format.time(a.RESPONDEDDATETIME) + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Followup") + ':</td><td><b>' + format.date(a.FOLLOWUPDATETIME) + ' ' + format.time(a.FOLLOWUPDATETIME) + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Completed") + ':</td><td><b>' + format.date(a.COMPLETEDDATE) + ' ' + format.time(a.COMPLETEDDATE) + ' ' + common.nulltostr(a.COMPLETEDNAME) + '</b></td>',
            '</tr>',
            '</table>',
            '</div>',
            '<div class="asm-grid-col-3">',
            _("Added by {0} on {1}").replace("{0}", "<b>" + a.CREATEDBY + "</b>").replace("{1}", "<b>" + format.date(a.CREATEDDATE) + "</b>") + ' <br/>',
            _("Last changed by {0} on {1}").replace("{0}", "<b>" + a.LASTCHANGEDBY + "</b>").replace("{1}", "<b>" + format.date(a.LASTCHANGEDDATE) + "</b>"),
            '<br />',
            fine,
            '</div>',
            '</div>',
            '</div>',
            '<div class="asm-tabbar">',
            '<ul class="asm-tablist">'
        ];
        var tabs = [[ "details", "incident", _("Details"), "", "vaci" ],
            [ "citation", "incident_citations", _("Citations"), "citation", "vacc" ],
            [ "media", "incident_media", _("Media"), "media", "vam" ],
            [ "diary", "incident_diary", _("Diary"), "diary", "vdn" ],
            [ "logs", "incident_log", _("Log"), "log", "vle" ]];
        $.each(tabs, function(it, vt) {
            var key = vt[0], url = vt[1], display = vt[2], iconname = vt[3], perms = vt[4];
            if (perms && !common.has_permission(perms)) { return; } // don't show if no permission
            if (key == selected) {
                h.push("<li class=\"ui-tabs-selected ui-state-active\"><a href=\"#\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
            else {
                h.push("<li><a href=\"" + url + "?id=" + a.ID + "\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
        });
        h.push('</ul>');
        h.push('<div id="asm-content">');
        return h.join("\n");
    },

    /**
     * Returns the header for the lost and found pages, with the banner info and
     * tabs. Since the content will be contained in a tba, the caller needs to add a
     * div when they are done.
     * mode: "lost" or "found"
     * a: A lost/found animal row from lostfound.get_lostanimal/get_foundanimal
     * selected: The name of the selected tab (details, media, diary, log)
     * counts: A dictionary of tabnames with record counts
     */
    lostfound_edit_header: function(mode, a, selected, counts) {
        var check_display_icon = function(key, iconname) {
            if (key == "animal") { return html.icon("blank"); }
            if (counts[key.toUpperCase()] > 0) {
                return html.icon(iconname);
            }
            return html.icon("blank");
        };
        var lf = "", area = "", dl = "", dlv = "", prefix = "", icon = "";
        if (mode == "lost") {
            lf = _("Lost");
            area = a.AREALOST;
            dl = _("Date Lost");
            dlv = format.date(a.DATELOST);
            prefix = "lostanimal";
            icon = "animal-lost";
        }
        if (mode == "found") {
            lf = _("Found");
            area = a.AREAFOUND;
            dl = _("Date Found");
            dlv = format.date(a.DATEFOUND);
            prefix = "foundanimal";
            icon = "animal-found";
        }
        var h = [
            '<div class="asm-banner ui-helper-reset ui-widget-content ui-corner-all">',
            '<input type="hidden" id="lfid" value="' + a.LFID + '" />',
            '<div class="asm-grid">',
            '<div class="asm-grid-col-3">',
            '<h2>' + html.icon(icon, lf) + a.OWNERNAME + '</h2>',
            '<p>' + lf + ': ' + a.AGEGROUP + ' ' + a.SPECIESNAME + ' / ' + html.truncate(area) + '<br>',
            html.truncate(a.DISTFEAT) + '</p>',
            '</div>',
            '<div class="asm-grid-col-3">',
            '<table>',
            '<tr>',
            '<td>' + dl + ':</td><td><b>' + dlv + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Date Reported") + ':</td><td><b>' + format.date(a.DATEREPORTED) + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Comments") + ':</td><td><b>' + html.truncate(a.COMMENTS) + '</b></td>',
            '</tr>',
            '</table>',
            '</div>',
            '<div class="asm-grid-col-3">',
            _("Added by {0} on {1}").replace("{0}", "<b>" + a.CREATEDBY + "</b>").replace("{1}", "<b>" + format.date(a.CREATEDDATE) + "</b>") + ' <br/>',
            _("Last changed by {0} on {1}").replace("{0}", "<b>" + a.LASTCHANGEDBY + "</b>").replace("{1}", "<b>" + format.date(a.LASTCHANGEDDATE) + "</b>"),
            '</div>',
            '</div>',
            '</div>',
            '<div class="asm-tabbar">',
            '<ul class="asm-tablist">'
        ];
        var tabs = [[ "details", prefix, _("Details"), "", "" ],
            [ "media", prefix + "_media", _("Media"), "media", "vam" ],
            [ "diary", prefix + "_diary", _("Diary"), "diary", "vdn" ],
            [ "logs", prefix + "_log", _("Log"), "log", "vle" ]];
        $.each(tabs, function(it, vt) {
            var key = vt[0], url = vt[1], display = vt[2], iconname = vt[3], perms = vt[4];
            if (perms && !common.has_permission(perms)) { return; } // don't show if no permission
            if (key == selected) {
                h.push("<li class=\"ui-tabs-selected ui-state-active\"><a href=\"#\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
            else {
                h.push("<li><a href=\"" + url + "?id=" + a.ID + "\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
        });
        h.push('</ul>');
        h.push('<div id="asm-content">');
        return h.join("\n");
    },

    /**
     * Returns the header for any of the person pages, with the thumbnail image, info and tabs
     * Since the content will be contained in a tab, the caller needs to add a div
     * p: A person row from get_person
     * selected: The name of the selected tab (person, donations, vouchers, media, diary, movements, links, log)
     */
    person_edit_header: function(p, selected, counts) {
        const check_display_icon = function(key, iconname) {
            if (key == "person") { return html.icon("blank"); }
            if (counts[key.toUpperCase()] > 0) {
                return html.icon(iconname);
            }
            return html.icon("blank");
        };
        let flags = this.person_flags(p);
        let latestmove = "", latestmovedeceased = "";
        if (p.LATESTMOVEANIMALID) { 
            if (p.LATESTMOVEDECEASEDDATE) { latestmovedeceased = html.icon("death"); }
            latestmove = "<tr><td>" + _("Last Movement") + ":</td>";
            latestmove += "<td><b>" + p.LATESTMOVETYPENAME + " " + html.icon("right") + " ";
            latestmove += '<a href="animal?id=' + p.LATESTMOVEANIMALID + '">' + p.LATESTMOVEANIMALNAME + '</a></b> ' + latestmovedeceased + '</td></tr>';
        }
        let s = [
            '<div class="asm-banner ui-helper-reset ui-widget-content ui-corner-all">',
            '<input type="hidden" id="personid" value="' + p.ID + '" />',
            '<div class="asm-grid">',
            '<div class="asm-grid-col-3">',
            '<table><tr>',
            '<td>',
            '<a href="' + html.img_src(p, "person") + '">',
            '<img class="asm-thumbnail thumbnailshadow" src="' + html.thumbnail_src(p, "personthumb") + '" />',
            '</a>',
            '</td>',
            '<td>',
            '<h2>' + html.icon("person", _("Person")) + p.OWNERNAME + ' - ' + p.OWNERCODE + '</h2>',
            '<p><span class="asm-search-personflags">' + flags + '</span><br/>',
            html.truncate(p.COMMENTS) + '</p>',
            '</td>',
            '</tr></table>',
            '</div>',
            '<div class="asm-grid-col-3">',
            '<table>',
            latestmove,
            '<tr>',
            '<td></td><td>' + p.OWNERADDRESS + '<br />',
            p.OWNERTOWN + ' ' + p.OWNERCOUNTY + ' ' + p.OWNERPOSTCODE + '<br />',
            p.HOMETELEPHONE + ' <br />',
            p.WORKTELEPHONE + ' <br />',
            p.MOBILETELEPHONE,
            '</td>',
            '</tr>',
            '</table>',
            '</div>',
            '<div class="asm-grid-col-3">',
            _("Added by {0} on {1}").replace("{0}", "<b>" + p.CREATEDBY + "</b>").replace("{1}", "<b>" + format.date(p.CREATEDDATE) + "</b>"),
            '<br />',
            _("Last changed by {0} on {1}").replace("{0}", "<b>" + p.LASTCHANGEDBY + "</b>").replace("{1}", "<b>" + format.date(p.LASTCHANGEDDATE) + "</b>"),
            '</div>',
            '</div>',
            '</div>',
            '<div class="asm-tabbar">',
            '<ul class="asm-tablist">'
        ];
        var tabs =[[ "person", "person", _("Person"), "", "vo" ],
            [ "licence", "person_licence", _("License"), "licence", "vapl" ],
            [ "investigation", "person_investigation", _("Investigation"), "investigation", "voi" ],
            [ "citation", "person_citations", _("Citations"), "citation", "vacc" ],
            [ "rota", "person_rota", _("Rota"), "rota", "voro" ],
            [ "traploan", "person_traploan", _("Equipment Loans"), "traploan", "vatl" ],
            [ "boarding", "person_boarding", _("Boarding"), "boarding", "vbi" ],
            [ "clinic", "person_clinic", _("Clinic"), "health", "vcl" ],
            [ "donations", "person_donations", _("Payments"), "donation", "ovod" ],
            [ "vouchers", "person_vouchers", _("Vouchers"), "donation", "vvov" ],
            [ "media", "person_media", _("Media"), "media", "vam" ],
            [ "diary", "person_diary", _("Diary"), "diary", "vdn" ],
            [ "movements", "person_movements", _("Movements"), "movement", "vamv" ],
            [ "links", "person_links", _("Links"), "link", "volk" ],
            [ "logs", "person_log", _("Log"), "log", "vle" ]];
        $.each(tabs, function(it, vt) {
            var key = vt[0], url = vt[1], display = vt[2], iconname = vt[3], perms = vt[4];
            if (perms && !common.has_permission(perms)) { return; } // don't show if no permission
            if ((key == "boarding") && config.bool("DisableBoarding")) { return; }
            if ((key == "citation" || key == "licence" || key == "investigation") && config.bool("DisableAnimalControl")) { return; }
            if ((key == "clinic") && config.bool("DisableClinic")) { return; }
            if ((key == "traploan") && config.bool("DisableTrapLoan")) { return; }
            if ((key == "movements") && config.bool("DisableMovements")) { return; }
            if ((key == "rota") && ((!p.ISVOLUNTEER && !p.ISSTAFF) || config.bool("DisableRota"))) { return; }
            if (key == selected) {
                s.push("<li class=\"ui-tabs-selected ui-state-active\"><a href=\"#\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
            else {
                s.push("<li><a href=\"" + url + "?id=" + p.ID + "\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
        });
        s.push("</ul>");
        s.push('<div id="asm-content">');
        return s.join("\n");
    },

    /**
     * Looks up how many investigations, incidents and brought in by instances a person has. 
     * This used to be part of get_person_query and in the record, but it slows things right down on
     * larger datasets and was only needed during adoption/reserve.
     * Accepts a person id and returns a promise for the data, which will be a person record
     * with extra warning values for SURRENDER, INCIDENT and INVESTIGATION
     * Eg: header_edit_header.person_with_adoption_warnings(20).then(function(rec) { alert("Person has " + rec.SURRENDER); })
     */
    person_with_adoption_warnings: function(personid) {
        var formdata = "mode=personwarn&id=" + personid;
        return common.ajax_post("person_embed", formdata); 
    },

    /**
     * Returns a string list of enabled flags for an animal record,
     * Eg: Quarantine, Cruelty Case, etc.
     */
    animal_flags: function(a) {
        var flags = [];
        if (a.ISCOURTESY == 1) {
            flags.push(_("Courtesy Listing"));
        }
        if (a.CRUELTYCASE == 1) {
            flags.push(_("Cruelty Case"));
        }
        if (a.NONSHELTERANIMAL == 1) {
            flags.push(_("Non-Shelter"));
        }
        if (a.ISNOTAVAILABLEFORADOPTION == 1) {
            flags.push("<span style=\"color: red\">" + _("Not For Adoption") + "</span>");
        }
        if (a.ISQUARANTINE == 1) {
            flags.push(_("Quarantine"));
        }
        if (a.ADDITIONALFLAGS != null) {
            var stock = [ "courtesy", "crueltycase", "nonshelter", "notforadoption", "notforregistration", "quarantine" ];
            $.each(a.ADDITIONALFLAGS.split("|"), function(i, v) {
                if (v != "" && $.inArray(v, stock) == -1) {
                    flags.push(v);
                }
            });
        }
        flags.sort();
        return flags.join(", ");
    },

    /**
     * Returns a string list of enabled flags for a person record,
     * Eg: Volunteer, member, donor, etc.
     */
    person_flags: function(p) {
        var flags = [];
        if (p.ISACO == 1) {
            flags.push(_("ACO"));
        }
        if (p.ISBANNED == 1) {
            flags.push("<span class=\"asm-flag-banned\">" + _("Banned") + "</span>");
        }
        if (p.ISDANGEROUS == 1) {
            flags.push("<span class=\"asm-flag-dangerous\">" + _("Dangerous") + "</span>");
        }
        if (p.INVESTIGATION > 0) {
            flags.push("<span class=\"asm-flag-investigation\">" + _("Investigation") + "</span>");
        }
        if (p.INCIDENT > 0) {
            flags.push("<span class=\"asm-flag-incident\">" + _("Incident") + "</span>");
        }
        if (p.ISDECEASED == 1) {
            flags.push("<span class=\"asm-flag-deceased\">" + _("Deceased") + "</span>");
        }
        if (p.ISADOPTER == 1) {
            flags.push(_("Adopter"));
        }
        if (p.ISADOPTIONCOORDINATOR == 1) {
            flags.push(_("Adoption Coordinator"));
        }
        if (p.ISDONOR == 1) {
            flags.push(_("Donor"));
        }
        if (p.ISDRIVER == 1) {
            flags.push(_("Driver"));
        }
        if (p.ISFOSTERER == 1) {
            flags.push(_("Fosterer"));
        }
        if (p.IDCHECK == 1) {
            flags.push(_("Homechecked"));
        }
        if (p.ISHOMECHECKER == 1) {
            flags.push(_("Homechecker"));
        }
        if (p.ISMEMBER == 1) {
            flags.push(_("Member"));
        }
        if (p.ISRETAILER == 1) {
            flags.push(_("Retailer"));
        }
        if (p.ISSHELTER == 1) {
            flags.push(_("Shelter"));
        }
        if (p.ISSTAFF == 1) {
            flags.push(_("Staff"));
        }
        if (p.ISVET == 1) {
            flags.push(_("Vet"));
        }
        if (p.ISVOLUNTEER == 1) {
            flags.push(_("Volunteer"));
        }
        if (p.EXCLUDEFROMBULKEMAIL == 1) {
            flags.push(_("Exclude from bulk email"));
        }
        if (p.ISSPONSOR == 1){
            flags.push(_("Sponsor"));
        }
        if (p.ADDITIONALFLAGS != null) {
            var stock = [ "aco", "adopter", "banned", "dangerous", "coordinator", "deceased", "donor", "driver", "excludefrombulkemail",
                "fosterer", "homechecked", "homechecker", "member", "shelter", "retailer", "sponsor", "staff", "giftaid",
                "vet", "volunteer"];
            $.each(p.ADDITIONALFLAGS.split("|"), function(i, v) {
                if (v != "" && $.inArray(v, stock) == -1) {
                    flags.push(v);
                }
            });
        }
        flags.sort();
        return flags.join(", ");
    },

    /**
     * Returns a bunch of <li> tags with links to create document templates.
     * templates: A set of template rows from the dbfs
     * linktype: A valid generation mode for document_gen
     * id: The record ID
     */
    template_list: function(templates, linktype, id) {
        var s = [];
        var lastpath = "";
        $.each(templates, function(i, t) {
            if (t.PATH != lastpath) {
                s.push('<li class="asm-menu-category">' + t.PATH + '</li>');
                lastpath = t.PATH;
            }
            s.push('<li class="asm-menu-item"><a target="_blank" class="templatelink" data="' + t.ID + '" href="document_gen?linktype=' + linktype + '&id=' + id + '&dtid=' + t.ID + '">' + t.NAME + '</a></li>');
        });
        return s.join("\n");
    },

    /**
     * Returns option tags from a list of HTML document templates.
     * The values are the template IDs
     */
    template_list_options: function(templates) {
        var s = [];
        var lastpath = "";
        s.push('<option value=""></option>');
        $.each(templates, function(i, t) {
            if (t.NAME.indexOf(".html") == -1) { return; }
            if (t.PATH != lastpath) {
                if (lastpath != "") { s.push('</optgroup>'); }
                s.push('<optgroup label="' + t.PATH + '">');
                lastpath = t.PATH;
            }
            s.push('<option value="' + t.ID + '">' + t.NAME + '</option>');
        });
        if (lastpath != "") { s.push('</optgroup>'); }
        return s.join("\n");
    },

    /** 
     * Returns the header for the waiting list pages, with the banner info and
     * tabs.
     * a: A waiting list row from animal.get_waitinglist_query
     * selected: The name of the selected tab (details, media, diary, log)
     */
    waitinglist_edit_header: function(a, selected, counts) {
        var check_display_icon = function(key, iconname) {
            if (key == "details") { return html.icon("blank"); }
            if (counts[key.toUpperCase()] > 0) {
                return html.icon(iconname);
            }
            return html.icon("blank");
        };
        var hclass = "", removal = "";
        if (!a.DATEREMOVEDFROMLIST) {
            if (a.URGENCY == 5) { hclass = "asm-wl-lowest"; }
            else if (a.URGENCY == 4) { hclass = "asm-wl-low"; }
            else if (a.URGENCY == 3) { hclass = "asm-wl-medium"; }
            else if (a.URGENCY == 2) { hclass = "asm-wl-high"; }
            else if (a.URGENCY == 1) { hclass = "asm-wl-urgent"; }
        }
        else {
            removal = "<tr><td>" + _("Removed") + ":</td><td><b>" + format.date(a.DATEREMOVEDFROMLIST) + "</b></td></tr>";
        }
        var h = [
            '<div class="asm-banner ui-helper-reset ui-widget-content ui-corner-all">',
            '<input type="hidden" id="waitinglistid" value="' + a.WLID + '" />',
            '<div class="asm-grid ' + hclass + '">',
            '<div class="asm-grid-col-3">',
            '<h2>' + html.icon("waitinglist", _("Waiting List")) + a.OWNERNAME + '</h2>',
            '<p>' + a.SPECIESNAME + ': ' + html.truncate(a.ANIMALDESCRIPTION) + '</p>',
            '</div>',
            '<div class="asm-grid-col-3">',
            '<table>',
            '<tr>',
            '<td>' + _("Rank") + ':</td><td><b>' + a.RANK + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Date put on list") + ':</td><td><b>' + format.date(a.DATEPUTONLIST) + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Time on list") + ':</td><td><b>' + a.TIMEONLIST + '</b></td>',
            '</tr><tr>',
            '<td>' + _("Reason") + ':</td><td><b>' + html.truncate(a.REASONFORWANTINGTOPART) + '</b></td>',
            '</tr>',
            removal,
            '</table>',
            '</div>',
            '<div class="asm-grid-col-3">',
            _("Added by {0} on {1}").replace("{0}", "<b>" + a.CREATEDBY + "</b>").replace("{1}", "<b>" + format.date(a.CREATEDDATE) + "</b>") + ' <br/>',
            _("Last changed by {0} on {1}").replace("{0}", "<b>" + a.LASTCHANGEDBY + "</b>").replace("{1}", "<b>" + format.date(a.LASTCHANGEDDATE) + "</b>"),
            '</div>',
            '</div>',
            '</div>',
            '<div class="asm-tabbar">',
            '<ul class="asm-tablist">'
        ];
        var tabs = [[ "details", "waitinglist", _("Details"), "", "vwl" ],
            [ "media", "waitinglist_media", _("Media"), "media", "vam" ],
            [ "diary", "waitinglist_diary", _("Diary"), "diary", "vdn" ],
            [ "logs", "waitinglist_log", _("Log"), "log", "vle" ]];
        $.each(tabs, function(it, vt) {
            var key = vt[0], url = vt[1], display = vt[2], iconname = vt[3], perms = vt[4];
            if (perms && !common.has_permission(perms)) { return; } // don't show if no permission
            if (key == selected) {
                h.push("<li class=\"ui-tabs-selected ui-state-active\"><a href=\"#\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
            else {
                h.push("<li><a href=\"" + url + "?id=" + a.ID + "\">" + display + " " + check_display_icon(key, iconname) + "</a></li>");
            }
        });
        h.push('</ul>');
        h.push('<div id="asm-content">');
        return h.join("\n");
    }

};

});
