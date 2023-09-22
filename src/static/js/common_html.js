/*global $, console, performance, jQuery, FileReader, Mousetrap, Path */
/*global alert, asm, schema, atob, btoa, header, _, escape, unescape, navigator */
/*global common, config, dlgfx, format */
/*global html: true */

"use strict";

const html = {

    /**
     * Returns a two-item list containing true if animal a is adoptable and the reason.
     * Looks at current publishing options and uses the same logic as the backend publisher
     */
    is_animal_adoptable: function(a) {
        var p = config.str("PublisherPresets"),
            exwks = format.to_int(common.url_param(p.replace(/ /g, "&"), "excludeunder")),
            locs = common.url_param(p.replace(/ /g, "&"), "includelocations");
        if (a.ISCOURTESY == 1) { return [ true, _("Courtesy Listing") ]; }
        if (a.ISNOTAVAILABLEFORADOPTION == 1) { return [ false, _("Not for adoption flag set") ]; }
        if (a.NONSHELTERANIMAL == 1) { return [ false, _("Non-Shelter") ]; }
        if (a.DECEASEDDATE) { return [ false, _("Deceased") ]; }
        if (a.CRUELTYCASE == 1 && p.indexOf("includecase") == -1) { return [ false, _("Cruelty Case") ]; }
        if (a.NEUTERED == 0 && p.indexOf("includenonneutered") == -1 && 
            common.array_in(String(a.SPECIESID), config.str("AlertSpeciesNeuter").split(","))
            ) { return [ false, _("Unaltered") ]; }
        if (a.IDENTICHIPPED == 0 && p.indexOf("includenonmicrochip") == -1 && 
            common.array_in(String(a.SPECIESID), config.str("AlertSpeciesMicrochip").split(","))
            ) { return [ false, _("Not microchipped") ]; }
        if (a.HASACTIVERESERVE == 1 && a.RESERVEDOWNERID && p.indexOf("includereserved") == -1) {
            return [ false, _("Reserved") + " " + html.icon("right") + " " + 
                    html.person_link(a.RESERVEDOWNERID, a.RESERVEDOWNERNAME) ];
        }
        if (a.HASACTIVERESERVE == 1 && p.indexOf("includereserved") == -1) { return [ false, _("Reserved") ]; }
        if (a.ISHOLD == 1 && a.HOLDUNTILDATE && p.indexOf("includehold") == -1) { 
            return [ false, _("Hold until {0}").replace("{0}", format.date(a.HOLDUNTILDATE)) ]; 
        }
        if (a.HASFUTUREADOPTION == 1) { return [ false, _("Adopted") ]; }
        if (a.HASACTIVEBOARDING == 1) { return [ false, _("Boarding") ]; }
        if (a.ISHOLD == 1 && p.indexOf("includehold") == -1) { return [ false, _("Hold") ]; }
        if (a.ISQUARANTINE == 1 && p.indexOf("includequarantine") == -1) { return [ false, _("Quarantine") ]; }
        if (a.DECEASEDDATE) { return [ false, _("Deceased") ]; }
        if (a.HASPERMANENTFOSTER == 1) { return [ false, _("Permanent Foster") ]; }
        if (a.ACTIVEMOVEMENTTYPE == 2 && p.indexOf("includefosters") == -1) { return [ false, _("Foster") ]; }
        if (a.ACTIVEMOVEMENTTYPE == 8 && p.indexOf("includeretailer") == -1) { return [ false, _("Retailer") ]; }
        if (a.ACTIVEMOVEMENTTYPE == 1 && a.HASTRIALADOPTION == 1 && p.indexOf("includetrial") == -1) { return [ false, _("Trial Adoption") ]; }
        if (a.ACTIVEMOVEMENTTYPE == 1 && a.HASTRIALADOPTION == 0) { return [ false, _("Adopted") ]; }
        if (a.ACTIVEMOVEMENTTYPE >= 3 && a.ACTIVEMOVEMENTTYPE <= 7) { return [ false, a.DISPLAYLOCATIONNAME ]; }
        if (!a.WEBSITEMEDIANAME && p.indexOf("includewithoutimage") == -1) { return [ false, _("No picture") ]; }
        if (p.indexOf("includewithoutdescription") == -1 && config.bool("PublisherUseComments") && !a.ANIMALCOMMENTS) { return [ false, _("No description") ]; }
        if (p.indexOf("includewithoutdescription") == -1 && !config.bool("PublisherUseComments") && !a.WEBSITEMEDIANOTES) { return [ false, _("No description") ]; }
        if (exwks) { 
            if (common.add_days(format.date_js(a.DATEOFBIRTH), (exwks * 7)) > new Date()) { 
                return [ false, _("Under {0} weeks old").replace("{0}", exwks) ]; 
            } 
        }
        if (locs && locs != "null" && !a.ACTIVEMOVEMENTTYPE) {
            var inloc = false;
            $.each(locs.split(","), function(i,v) {
                if (format.to_int(v) == a.SHELTERLOCATION) { inloc = true; }
            });
            if (!inloc) { return [ false, _("Not in chosen publisher location") ]; }
        }
        return [ true, _("Available for adoption") ];
    },

    /**
     * Returns true if ADDITIONALFLAGS in s contains flag f
     */
    is_animal_flag: function(s, f) {
        if (!s || !f) { return false; }
        var rv = false;
        $.each(s.split("|"), function(i, v) {
            if (v == f) { rv = true; }
        });
        return rv;
    },

    /**
     * Renders an animal link from the record given.
     * a: An animal or brief animal record
     * o: Options to pass on to animal_emblems
     * o.noemblems: Don't show the emblems
     * o.emblemsright: Show the emblems to the right of the link
     */
    animal_link: function(a, o) {
        var s = "", e = "", animalid = a.ANIMALID || a.ID;
        if (o && o.noemblems) { 
            e = ""; 
        } 
        else { 
            e = html.animal_emblems(a, o) + " "; 
        }
        s = '<a class="asm-embed-name" href="animal?id=' + animalid + '">' + a.ANIMALNAME + ' - ' + 
            (config.bool("UseShortShelterCodes") ? a.SHORTCODE : a.SHELTERCODE) + '</a>';
        if (!o || (o && o.emblemsright)) {
            s += ' ' + e;
        }
        else {
            s = e + ' ' + s;    
        }
        return s;
    },

    /**
     * Renders an animal link thumbnail from the record given
     * a: An animal or brief animal record
     * o: Options to pass on to animal_emblems
     * o.showselector: if true outputs a checkbox to select the animal link
     */
    animal_link_thumb: function(a, o) {
        var s = [];
        var title = common.substitute(_("{0}: Entered shelter {1}, Last changed on {2} by {3}. {4} {5} {6} aged {7}"), { 
            "0": a.CODE,
            "1": format.date(a.MOSTRECENTENTRYDATE),
            "2": format.date(a.LASTCHANGEDDATE),
            "3": a.LASTCHANGEDBY,
            "4": a.SEXNAME,
            "5": a.BREEDNAME,
            "6": a.SPECIESNAME,
            "7": a.ANIMALAGE});
        s.push(common.substitute('<a href="animal?id={id}"><img title="{title}" src="{imgsrc}" class="{thumbnailclasses}" /></a><br />', {
            "id" : a.ID,
            "title" : html.title(title),
            "thumbnailclasses": html.animal_link_thumb_classes(a),
            "imgsrc" : html.thumbnail_src(a, "animalthumb") }));
        let name = a.ANIMALNAME;
        if (config.bool("ShelterViewShowCodes")) { name = name + ' <span class="asm-shelterview-animalcode">' + a.CODE + '</span>';}
        s.push('<a class="asm-shelterview-animalname" href="animal?id=' + a.ID + '">' + name + '</a><br style="margin-bottom: 6px" />');
        s.push(html.animal_emblems(a, o));
        if (o.showselector) {
            s.push('<br style="margin-bottom: 5px" />' +
                '<input type="checkbox" class="animalselect" ' +
                'data="{id}" title="{title}" />'.replace("{id}", a.ID).replace("{title}", _("Select")));
        }
        return s.join("\n");
    },

    /**
     * Renders a bare animal link thumbnail (just the thumbnail surrounded by a link to the record)
     */
    animal_link_thumb_bare: function(a) {
        var animalid = a.ANIMALID || a.ID,
            classes = html.animal_link_thumb_classes(a); 
        return '<a href="animal?id=' + animalid + '"><img src=' + html.thumbnail_src(a, "animalthumb") + ' class="' + classes + '" /></a>';
    },

    /**
     * Returns the classes for animal thumbnails
     */
    animal_link_thumb_classes: function(a) {
        var sxc = (a.SEX == 0 ? "asm-thumbnail-female" : (a.SEX == 1 ? "asm-thumbnail-male" : ""));
        return "asm-thumbnail thumbnailshadow " + (config.bool("ShowSexBorder") ? sxc : "");
    },

    /**
     * Renders a series of animal emblems for the animal record given
     * (animal record can be a brief)
     * a: The animal record to show an emblem for
     * o.showlocation: if true, outputs a single emblem icon to represent the
     *                 animal's current location with a tooltip.
     * o.showunit: if true, will include the location unit number as an emblem
     */
    animal_emblems: function(a, o) {
        var s = [];
        if (!o) { o = {}; }
        if (config.bool("EmblemAlwaysLocation")) { 
            o.showlocation = true; 
        }
        s.push("<span class=\"asm-animal-emblems\">");
        if (o && o.showlocation && !a.DECEASEDDATE) {
            if (a.ARCHIVED == 0 && !a.ACTIVEMOVEMENTTYPE && a.SHELTERLOCATIONNAME) {
                s.push(html.icon("location", _("On Shelter") + " / " + a.SHELTERLOCATIONNAME + " " + common.nulltostr(a.SHELTERLOCATIONUNIT)));
            }
            else if (a.ACTIVEMOVEMENTTYPE == 2 && a.DISPLAYLOCATIONNAME && a.CURRENTOWNERNAME && common.has_permission("vo")) {
                s.push(html.icon("person", a.DISPLAYLOCATIONNAME + " / " + a.CURRENTOWNERNAME));
            }
            else if (a.NONSHELTERANIMAL == 0 && a.DISPLAYLOCATIONNAME && a.CURRENTOWNERNAME && common.has_permission("vo")) {
                s.push(html.icon("movement", a.DISPLAYLOCATIONNAME + " / " + a.CURRENTOWNERNAME));
            }
        }
        if (config.bool("EmblemAdoptable") && a.DATEOFBIRTH && html.is_animal_adoptable(a)[0]) {
            s.push(html.icon("adoptable", _("Adoptable")));
        }
        if (config.bool("EmblemBonded") && (a.BONDEDANIMALID || a.BONDEDANIMAL2ID)) {
            s.push(html.icon("bonded", _("Bonded")));
        }
        if (config.bool("EmblemBoarding") && (a.HASACTIVEBOARDING == 1)) {
            s.push(html.icon("boarding", _("Boarding")));
        }
        if (config.bool("EmblemLongTerm") && a.ARCHIVED == 0 && (a.DAYSONSHELTER > config.integer("LongTermDays"))) {
            s.push(html.icon("calendar", _("Long term")));
        }
        if (config.bool("EmblemCourtesy") && a.ISCOURTESY == 1) {
            s.push(html.icon("share", _("Courtesy Listing")));
        }
        if (config.bool("EmblemDeceased") && a.DECEASEDDATE != null) {
            s.push(html.icon("death", _("Deceased")));
        }
        if (config.bool("EmblemReserved") && a.HASACTIVERESERVE == 1) {
            s.push(html.icon("reservation", _("Reserved")));
        }
        if (config.bool("EmblemTrialAdoption") && a.HASTRIALADOPTION == 1) {
            s.push(html.icon("trial", _("Trial Adoption")));
        }
        if (config.bool("EmblemFutureAdoption") && a.HASFUTUREADOPTION == 1) {
            s.push(html.icon("movement", _("Future Adoption")));
        }
        if (config.bool("EmblemCrueltyCase") && a.CRUELTYCASE == 1) {
            s.push(html.icon("case", _("Cruelty Case")));
        }
        if (config.bool("EmblemNeverVacc") && a.VACCGIVENCOUNT == 0) {
            s.push(html.icon("novaccination", _("Never Vaccinated")));
        }
        if (config.bool("EmblemNonShelter") && a.NONSHELTERANIMAL == 1) {
            s.push(html.icon("nonshelter", _("Non-Shelter")));
        }
        if (config.bool("EmblemPositiveTest") && (
            (a.HEARTWORMTESTED == 1 && a.HEARTWORMTESTRESULT == 2) || 
            (a.COMBITESTED == 1 && a.COMBITESTRESULT == 2) || 
            (a.COMBITESTED == 1 && a.FLVRESULT == 2))) {
            var p = [];
            if (a.HEARTWORMTESTRESULT == 2) { p.push(_("Heartworm+")); }
            if (a.COMBITESTRESULT == 2) { p.push(_("FIV+")); }
            if (a.FLVRESULT == 2) { p.push(_("FLV+")); }
            s.push(html.icon("positivetest", p.join(" ")));
        }
        if (config.bool("EmblemRabies") && !a.RABIESTAG && 
            config.str("AlertSpeciesRabies").split(",").indexOf(String(a.SPECIESID)) != -1) {
            s.push(html.icon("rabies", _("Rabies not given")));
        }
        if (config.bool("EmblemSpecialNeeds") && a.HASSPECIALNEEDS == 1) {
            s.push(html.icon("health", _("Special Needs")));
        }
        if (config.bool("EmblemUnneutered") && a.NEUTERED == 0 && 
            config.str("AlertSpeciesNeuter").split(",").indexOf(String(a.SPECIESID)) != -1) {
            s.push(html.icon("unneutered", _("Unaltered")));
        }
        if (config.bool("EmblemNotMicrochipped") && a.IDENTICHIPPED == 0 && a.NONSHELTERANIMAL == 0 && 
            config.str("AlertSpeciesMicrochip").split(",").indexOf(String(a.SPECIESID)) != -1) {
            s.push(html.icon("microchip", _("Not Microchipped")));
        }
        if (config.bool("EmblemNotForAdoption") && a.ISNOTAVAILABLEFORADOPTION == 1 && (a.ARCHIVED == 0 || a.ACTIVEMOVEMENTTYPE == 2) ) {
            s.push(html.icon("notforadoption", _("Not For Adoption")));
        }
        if (config.bool("EmblemHold") && a.ISHOLD == 1 && (a.ARCHIVED == 0 || a.ACTIVEMOVEMENTTYPE == 2) ) {
            if (a.HOLDUNTILDATE) {
                s.push(html.icon("hold", _("Hold until {0}").replace("{0}", format.date(a.HOLDUNTILDATE))));
            }
            else {
                s.push(html.icon("hold", _("Hold")));
            }
        }
        if (config.bool("EmblemQuarantine") && a.ISQUARANTINE == 1 && (a.ARCHIVED == 0 || a.ACTIVEMOVEMENTTYPE == 2) ) {
            s.push(html.icon("quarantine", _("Quarantine")));
        }
        if (a.POPUPWARNING) {
            s.push(html.icon("warning", String(a.POPUPWARNING)));
        }
        $.each([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], function(i, v) {
            var cflag = config.str("EmblemsCustomFlag" + v), ccond = config.str("EmblemsCustomCond" + v), cemblem = config.str("EmblemsCustomValue" + v);
            if (cflag && cemblem && (ccond == "has" || !ccond) && html.is_animal_flag(a.ADDITIONALFLAGS, cflag)) {
                s.push('<span class="custom" title="' + html.title(cflag) + '">' + cemblem + '</span>');
            }
            if (cflag && cemblem && ccond == "not" && !html.is_animal_flag(a.ADDITIONALFLAGS, cflag)) {
                s.push('<span class="custom" title="' + html.title(_("Not {0}").replace("{0}", cflag)) + '">' + cemblem + '</span>');
            }
        });
        s.push("</span>");
        if (o && o.showunit && a.SHELTERLOCATIONUNIT && a.ARCHIVED == 0 && !a.ACTIVEMOVEMENTTYPE ) {
            s.push(' <span class="asm-search-locationunit" title="' + html.title(_("Unit")) + '">' + a.SHELTERLOCATIONUNIT + '</span>');
        }
        return s.join("");
    },

    /** Returns an array of warnings for moving an animal out of the shelter
     *  a: animal result from the backend
     *  adopt: If true, show warnings specific to adoptions */
    animal_movement_warnings: function(a, adopt) {
        let warn = [];
        // Animal isn't on the shelter
        if (a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2 && a.ACTIVEMOVEMENTTYPE != 8) {
            warn.push(_("This animal is not on the shelter."));
        }
        // If the animal is marked not for adoption
        if (a.ISNOTAVAILABLEFORADOPTION == 1 && adopt) {
            warn.push(_("This animal is marked not for adoption."));
        }
        // If the animal is held, we shouldn't be allowed to adopt it
        if (a.ISHOLD == 1 && adopt) {
            warn.push(_("This animal is currently held and cannot be adopted."));
        }
        // Cruelty case
        if (a.CRUELTYCASE == 1) {
            warn.push(_("This animal is part of a cruelty case and should not leave the shelter."));
        }
        // Outstanding medical
        if (config.bool("WarnOSMedical") && a.HASOUTSTANDINGMEDICAL == 1) {
            warn.push(_("This animal has outstanding medical treatments."));
        }
        // Quarantined
        if (a.ISQUARANTINE == 1) {
            warn.push(_("This animal is currently quarantined and should not leave the shelter."));
        }
        // Unaltered
        if (config.bool("WarnUnaltered") && a.NEUTERED == 0 && adopt) {
            warn.push(_("This animal has not been altered."));
        }
        // Not microchipped
        if (config.bool("WarnNoMicrochip") && a.IDENTICHIPPED == 0) {
            warn.push(_("This animal has not been microchipped."));
        }
       // Check for bonded animals and warn
        if (a.BONDEDANIMALID || a.BONDEDANIMAL2ID) {
            let bw = "";
            if (a.BONDEDANIMAL1NAME) {
                bw += a.BONDEDANIMAL1CODE + " - " + a.BONDEDANIMAL1NAME;
            }
            if (a.BONDEDANIMAL2NAME) {
                if (bw != "") { bw += ", "; }
                bw += a.BONDEDANIMAL2CODE + " - " + a.BONDEDANIMAL2NAME;
            }
            if (bw != "") {
                warn.push(_("This animal is bonded with {0}").replace("{0}", bw));
            }
        }
        // Animal has a warning
        if (a.POPUPWARNING) {
            warn.push(a.POPUPWARNING);
        }
        return warn;
    },

    /** 
     * Renders a shelter timeline event described in e. Events should have
     * the following attributes:
     * LINKTARGET, CATEGORY, EVENTDATE, ID, TEXT1, TEXT2, TEXT3, LASTCHANGEDBY,
     * ICON, DESCRIPTION
     */
    event_text: function(e, o) {
        // If the user does not have permission to see person records, hide events
        // that involve people
        var PEOPLE_EVENTS = { "RESERVED": true, "CANCRESERVE": true, "ADOPTED": true, 
            "FOSTERED": true, "TRANSFER": true, "RECLAIMED": true, "RETAILER": true, 
            "RETURNED": true, "INCIDENTOPEN": true, "INCIDENTCLOSE": true, 
            "LOST": true, "FOUND": true, "WAITINGLIST": true };
        if (PEOPLE_EVENTS[e.CATEGORY] && !common.has_permission("vo")) { return ""; }
        var h = "";
        if (!o) {
            o = { includedate: true, includetime: false, includelink: true, includeicon: true };
        }
        if (o.includedate) {
            h += '<span class="asm-timeline-small-date">' + format.date(e.EVENTDATE) + '</span> ';
        }
        if (o.includetime) {
            h += '<span class="asm-timeline-time">' + format.time(e.EVENTDATE) + '</span>' ;
        }
        if (o.includelink) {
            h += ' <a href="' + e.LINKTARGET + '?id=' + e.ID + '">';
        }
        if (o.includeicon) {
            h += html.icon(e.ICON) + ' ';
        }
        h += e.DESCRIPTION;
        h += '</a> <span class="asm-timeline-by">(' + e.LASTCHANGEDBY + ')</span>';
        return h;
    },

    /**
     * Renders a list of <option> tags for animal flags.
     * It mixes in any additional animal flags to the regular
     * set, sorts them all alphabetically and applies them
     * to the select specified by selector. If an animal record
     * is passed, then it will be checked and selected items
     * will be selected.
     * a: An animal record (or null if not available)
     * flags: A list of extra animal flags from the lookup call
     * node: A jquery dom node of the select box to populate
     * includeall: Have an all/(all) option at the top of the list
     */
    animal_flag_options: function(a, flags, node, includeall) {

        var opt = [];
        var field_option = function(fieldname, post, label) {
            var sel = a && a[fieldname] == 1 ? 'selected="selected"' : "";
            return '<option value="' + post + '" ' + sel + '>' + label + '</option>\n';
        };

        var flag_option = function(flag) {
            var sel = "";
            if (!a || !a.ADDITIONALFLAGS) { sel = ""; }
            else {
                $.each(a.ADDITIONALFLAGS.split("|"), function(i, v) {
                    if (v == flag) {
                        sel = 'selected="selected"';
                    }
                });
            }
            return '<option ' + sel + '>' + flag + '</option>';
        };

        var h = [
            { loc: "any", label: _("Courtesy Listing"), html: field_option("ISCOURTESY", "courtesy", _("Courtesy Listing")) },
            { loc: "on", label: _("Cruelty Case"), html: field_option("CRUELTYCASE", "crueltycase", _("Cruelty Case")) },
            { loc: "any", label: _("Non-Shelter"), html: field_option("NONSHELTERANIMAL", "nonshelter", _("Non-Shelter")) },
            { loc: "on", label: _("Not For Adoption"), html: field_option("ISNOTAVAILABLEFORADOPTION", "notforadoption", _("Not For Adoption")) },
            { loc: "off", label: _("Do Not Publish"), html: field_option("ISNOTAVAILABLEFORADOPTION", "notforadoption", _("Do Not Publish")) },
            { loc: "any", label: _("Do Not Register Microchip"), html: field_option("ISNOTFORREGISTRATION", "notforregistration", _("Do Not Register Microchip")) },
            { loc: "on", label: _("Quarantine"), html: field_option("ISQUARANTINE", "quarantine", _("Quarantine")) }
        ];

        $.each(flags, function(i, v) {
            h.push({ label: v.FLAG, html: flag_option(v.FLAG) });
        });

        h.sort(common.sort_single("label"));

        if (includeall) {
            opt.push('<option value="all">' + _("(all)") + '</option>');
        }

        $.each(h, function(i, v) {
            // Skip if the flag is only for on-shelter and the animal is off-shelter
            if (v.loc == "on" && a && a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2) { return; }
            // Skip if the flag is for off shelter only and the animal is on shelter
            if (v.loc == "off" && a && a.ARCHIVED == 0) { return; }
            opt.push(v.html);    
        });

        node.html(opt.join("\n"));
        node.change();

    },

    /**
     * Renders an accordion panel that contains audit information from
     * the controller
     */
    audit_trail_accordion: function(controller) {
        if (!controller.hasOwnProperty("audit") || !common.has_permission("vatr") || controller.audit.length == 0) {
            return "";
        }
        var h = [
            '<h3><a href="#">' + _("Audit Trail") + '</a></h3>',
            '<div>',
            '<table class="asm-table">',
            '<thead>',
            '<tr>',
            '<th>' + _("Date") + '</th>',
            '<th>' + _("User") + '</th>',
            '<th>' + _("Action") + '</th>',
            '<th>' + _("Table") + '</th>',
            '<th>' + _("Details") + '</th>',
            '</tr>',
            '</thead>',
            '<tbody>'
        ], readableaction = {
            0: _("Add"),
            1: _("Edit"),
            2: _("Delete"),
            3: _("Move"),
            4: _("Login"),
            5: _("Logout"),
            6: _("View"),
            7: _("Report"),
            8: _("Email")
        };
        $.each(controller.audit, function(i, v) {
            if (!config.bool("ShowViewsInAuditTrail") && v.ACTION == 6) { return; }
            h.push('<tr>');
            h.push('<td>' + format.date(v.AUDITDATE) + ' ' + format.time(v.AUDITDATE) + '</td>');
            h.push('<td>' + v.USERNAME + '</td>');
            h.push('<td>' + readableaction[v.ACTION] + '</td>');
            h.push('<td>' + v.TABLENAME + '</td>');
            h.push('<td>' + v.DESCRIPTION + '</td>');
            h.push('</tr>');
        });
        h.push('</tbody>');
        h.push('</table>');
        h.push('</div>');
        return h.join("\n");
    },

    /**
     * Returns a link to an event - but only if the view event permission is set
     * to hide their detail.
     * eventid: The event ID
     * name: The event detail
     */
    event_link: function(eventid, name) {
        var h = "";
        if (!name) { name = ""; }
        if (common.has_permission("ve")) {
            h = '<a href="event?id=' + eventid + '">' + name + '</a>';
        }
        return h;
    },

    /**
     * Renders a list of <option> tags for person flags.
     * It mixes in any additional person flags to the regular
     * set, sorts them all alphabetically and applies them
     * to the select specified by selector. If a person record
     * is passed, then it will be checked and selected items
     * will be selected.
     * p: A person record (or null if not available)
     * flags: A list of extra person flags from the lookup call
     * node: A jquery dom node of the select box to populate
     * includeall: Have an all/(all) option at the top of the list
     */
    person_flag_options: function(p, flags, node, include_all, include_previous_adopter) {

        var opt = [];
        var field_option = function(fieldname, post, label) {
            var sel = p && p[fieldname] == 1 ? 'selected="selected"' : "";
            return '<option value="' + post + '" ' + sel + '>' + label + '</option>\n';
        };

        var flag_option = function(flag) {
            var sel = "";
            if (!p || !p.ADDITIONALFLAGS) { sel = ""; }
            else {
                $.each(p.ADDITIONALFLAGS.split("|"), function(i, v) {
                    if (v == flag) {
                        sel = 'selected="selected"';
                    }
                });
            }
            return '<option ' + sel + '>' + flag + '</option>';
        };

        var h = [
            { label: _("ACO"), html: field_option("ISACO", "aco", _("ACO")) },
            { label: _("Adopter"), html: field_option("ISADOPTER", "adopter", _("Adopter")) },
            { label: _("Adoption Coordinator"), html: field_option("ISADOPTIONCOORDINATOR", "coordinator", _("Adoption Coordinator")) },
            { label: _("Banned"), html: field_option("ISBANNED", "banned", _("Banned")) },
            { label: _("Dangerous"), html: field_option("ISDANGEROUS", "dangerous", _("Dangerous")) },
            { label: _("Deceased"), html: field_option("ISDECEASED", "deceased", _("Deceased")) },
            { label: _("Donor"), html: field_option("ISDONOR", "donor", _("Donor")) },
            { label: _("Driver"), html: field_option("ISDRIVER", "driver", _("Driver")) },
            { label: _("Exclude from bulk email"), html: field_option("EXCLUDEFROMBULKEMAIL", "excludefrombulkemail", _("Exclude from bulk email")) },
            { label: _("Fosterer"), html: field_option("ISFOSTERER", "fosterer", _("Fosterer")) },
            { label: _("Homechecked"), html: field_option("IDCHECK", "homechecked", _("Homechecked")) },
            { label: _("Homechecker"), html: field_option("ISHOMECHECKER", "homechecker", _("Homechecker")) },
            { label: _("Member"), html: field_option("ISMEMBER", "member", _("Member")) },
            { label: _("Other Shelter"), html: field_option("ISSHELTER", "shelter", _("Other Shelter")) },
            { label: _("Sponsor"), html: field_option("ISSPONSOR", "sponsor", _("Sponsor")) },
            { label: _("Staff"), html: field_option("ISSTAFF", "staff", _("Staff")) },
            { label: _("Vet"), html: field_option("ISVET", "vet", _("Vet")) },
            { label: _("Volunteer"), html: field_option("ISVOLUNTEER", "volunteer", _("Volunteer")) }
        ];

        if (!config.bool("DisableRetailer")) {
            h.push({ label: _("Retailer"), html: field_option("ISRETAILER", "retailer", _("Retailer")) });
        }
        if (asm.locale == "en_GB") {
            h.push({ label: _("UK Giftaid"), html: field_option("ISGIFTAID", "giftaid", _("UK Giftaid"))});
        }

        if (include_previous_adopter) {
            h.push({ label: _("Previous Adopter"), html: field_option("", "padopter", _("Previous Adopter"))});
        }

        $.each(flags, function(i, v) {
            h.push({ label: v.FLAG, html: flag_option(v.FLAG) });
        });

        h.sort(common.sort_single("label"));

        if (include_all) {
            opt.push('<option value="all">' + _("(all)") + '</option>');
        }

        $.each(h, function(i, v) {
            opt.push(v.html);    
        });

        node.html(opt.join("\n"));
        node.change();

    },

    /**
     * Returns a link to a person with the address below - 
     * but only if the view person permission is set
     */
    person_link_address: function(row) {
        if (!common.has_permission("vo")) { return _("Forbidden"); }
        return html.person_link(row.OWNERID, row.OWNERNAME) +
            '<br/>' + common.nulltostr(row.OWNERADDRESS) + 
            '<br/>' + common.nulltostr(row.OWNERTOWN) + 
            '<br/>' + common.nulltostr(row.OWNERCOUNTY) + ' ' + common.nulltostr(row.OWNERPOSTCODE) + 
            '<br/>' + common.nulltostr(row.HOMETELEPHONE) + " " + common.nulltostr(row.WORKTELEPHONE) + " " + common.nulltostr(row.MOBILETELEPHONE);
    },

    /**
     * Returns a link to a person - but only if the view person permission is set
     * to hide their name.
     * personid: The person ID
     * name: The person name
     */
    person_link: function(personid, name) {
        var h = "";
        if (!name) { name = ""; }
        if (common.has_permission("vo")) {
            h = '<a href="person?id=' + personid + '">' + name + '</a>';
        }
        return h;
    },

    /** 
     * Returns the list of warnings for a person when moving an animal to them.
     * p: A person result record
     * oopostcode: The original owner postcode of the animal on the movement
     * bipostcode: The brought in postcode of the person on the movement
     */
    person_movement_warnings: function(p, oopostcode, bipostcode) {
        let warn = [];
        // Is this owner banned?
        if (p.ISBANNED == 1 && config.bool("WarnBannedOwner")) {
            warn.push(_("This person has been banned from adopting animals.")); 
        }
        // Owner previously under investigation
        if (p.INVESTIGATION > 0) {
            warn.push(_("This person has been under investigation."));
        }
        // Owner part of animal control incident
        if (p.INCIDENT > 0) {
            warn.push(_("This person has an animal control incident against them."));
        }
        // Owner previously surrendered?
        if (p.SURRENDER > 0 && config.bool("WarnBroughtIn")) {
            warn.push(_("This person has previously surrendered an animal."));
        }
        // Person at this address previously banned?
        if (p.BANNEDADDRESS > 0 && config.bool("WarnBannedAddress")) {
            warn.push(_("This person lives at the same address as someone who was previously banned."));
        }
        // Is this owner not homechecked?
        if (config.bool("WarnNoHomeCheck") && p.IDCHECK == 0) {
            warn.push(_("This person has not passed a homecheck."));
        }
        // Does this owner live in the same postcode area as the animal's
        // original owner?
        if (config.bool("WarnOOPostcode") && (oopostcode || bipostcode)) {
            if ( format.postcode_prefix(oopostcode) == format.postcode_prefix(p.OWNERPOSTCODE) ||
                 format.postcode_prefix(bipostcode) == format.postcode_prefix(p.OWNERPOSTCODE) ) {
                warn.push(_("This person lives in the same area as the person who brought the animal to the shelter.")); 
            }
        }
        // Person has a warning on their record
        if (p.POPUPWARNING) {
            warn.push(p.POPUPWARNING);
        }
        return warn;
    },

    /**
     * Returns the different shelter view modes as a string of HTML options.
     */
    shelter_view_options: function() {
        return [
            '<option value="altered">' + _("Altered") + '</option>',
            '<option value="coordinator">' + _("Adoption Coordinator") + '</option>',
            '<option value="coordinatorfosterer">' + _("Adoption Coordinator and Fosterer") + '</option>',
            '<option value="agegroup">' + _("Age Group") + '</option>',
            '<option value="agegrouplitter">' + _("Age Group and Litter") + '</option>',
            '<option value="color">' + _("Color") + '</option>',
            '<option value="entrycategory">' + _("Entry Category") + '</option>',
            '<option value="flags">' + _("Flags") + '</option>',
            '<option value="fosterer">' + _("Fosterer") + '</option>',
            '<option value="fostereractive">' + _("Fosterer (Active Only)") + '</option>',
            '<option value="fostererspace">' + _("Fosterer (Space Available)") + '</option>',
            '<option value="goodwith">' + _("Good with") + '</option>',
            '<option value="litter">' + _("Litter") + '</option>',
            '<option value="location">' + _("Location") + '</option>',
            '<option value="locationbreed">' + _("Location and Breed") + '</option>',
            '<option value="locationlitter">' + _("Location and Litter") + '</option>',
            '<option value="locationspecies">' + _("Location and Species") + '</option>',
            '<option value="locationspeciesage">' + _("Location and Species (Age)") + '</option>',
            '<option value="locationtype">' + _("Location and Type") + '</option>',
            '<option value="locationunit">' + _("Location and Unit") + '</option>',
            '<option value="locationnv">' + _("Location (No Virtual)") + '</option>',
            '<option value="locationnvs">' + _("Location and Species (No Virtual)") + '</option>',
            '<option value="name">' + _("Name") + '</option>',
            '<option value="pickuplocation">' + _("Pickup Location") + '</option>',
            '<option value="retailer">' + _("Retailer") + '</option>',
            '<option value="sex">' + _("Sex") + '</option>',
            '<option value="sexspecies">' + _("Sex and Species") + '</option>',
            '<option value="site">' + _("Site") + '</option>',
            '<option value="sitefoster">' + _("Site (fosters separate)") + '</option>',
            '<option value="species">' + _("Species") + '</option>',
            '<option value="speciesbreed">' + _("Species and Breed") + '</option>',
            '<option value="speciescode">' + _("Species and Code") + '</option>',
            '<option value="speciescolor">' + _("Species and Color") + '</option>',
            '<option value="status">' + _("Status") + '</option>',
            '<option value="statuslocation">' + _("Status and Location") + '</option>',
            '<option value="statusspecies">' + _("Status and Species") + '</option>',
            '<option value="type">' + _("Type") + '</option>',
            '<option value="unit">' + _("Unit") + '</option>',
            '<option value="unitspecies">' + _("Unit and Species") + '</option>'
        ].join("\n");
    },

    /**
     * Outputs a div box container with jquery ui style
     */
    box: function(margintop, padding) {
        if (!margintop) { 
            margintop = 0;
        }
        if (!padding) {
            padding = 5;
        }
        return '<div class="ui-helper-reset centered ui-widget-content ui-corner-all" style="margin-top: ' + margintop + 'px; padding: ' + padding + 'px;">';
    },

    /**
     * Returns a hidden field that you can use to prevent
     * JQuery UI dialogs auto focusing
     */
    capture_autofocus: function() {
        return '<span class="ui-helper-hidden-accessible"><input type="text"/></span>';
    },

    /**
     * The header that should wrap all content on screens
     * title: The title to show in the box heading
     * notcontent: If undefined, an id of asm-content is set
     */
    content_header: function(title, notcontent) {
        var ids = "";
        if (!notcontent) {
            ids = "id=\"asm-content\" ";
        }
        if (title) {
            return "<div " + ids + " class=\"ui-accordion ui-widget ui-helper-reset ui-accordion-icons\">" +
                "<h3 class=\"ui-accordion-header ui-helper-reset ui-corner-top ui-state-active centered\">" +
                "<a href=\"#\">" + title + "</a></h3>" +
                "<div class=\"ui-helper-reset ui-widget-content ui-corner-bottom\" style=\"padding: 5px;\">";
        }
        return "<div " + ids + " class=\"ui-accordion ui-widget ui-helper-reset ui-accordion-icons\">";
    },

    /**
     * The footer that closes our content header
     */
    content_footer: function() {
        return "</div></div>";
    },

    /** 
     * Decodes any unicode html entities from the following types of objects:
     *      o can be a string
     *      o can be a list of strings
     *      o can be a list of objects with label properties
     */
    decode: function(o) {
        var decode_str = function(s) {
            // Just return the string as is if there are no html entities in there
            // to save unnecessary creating of DOM elements.
            if (String(s).indexOf("&") == -1) { return s; }
            try {
                return $("<div></div>").html(s).text();
            }
            catch(err) {
                return "";
            }
        };
        if (common.is_array(o)) {
            var oa = [];
            $.each(o, function(i, v) {
                if (v.hasOwnProperty("label")) {
                    // It's an object with a label property
                    v.label = decode_str(v.label);
                    oa.push(v);
                }
                else {
                    // It's just a string, decode it
                    oa.push(decode_str(v));
                }
            });
            return oa;
        }
        return decode_str(o);
    },

    /**
     * Returns the html for an icon by its name, including a
     * title attribute.
     */
    icon: function(name, title, style) {
        var extra = "";
        if (title) {
            extra = " title=\"" + this.title(title) + "\"";
        }
        if (style) {
            extra += " style=\"" + style + "\"";
        }
        return "<span class=\"asm-icon asm-icon-" + name + "\"" + extra + "></span>";
    },


    /**
     * Returns a text bar containing s with options o
     * id: The containing div id
     * display: (no default, css display parameter of container)
     * state: highlight (default) | error 
     * icon: info (default, jquery ui icon)
     * padding: (default 5px)
     * margintop: (default not set)
     * maxwidth: (default 900px)
     */
    textbar: function(s, o) {
        let containerid = "", display = "", state = "highlight", icon = "info", padding = "", margintop = "", maxwidth = "max-width: 900px;";
        if (!o) { o = {}; }
        if (!o.padding) { o.padding = "5px"; }
        if (o.id) { containerid = 'id="' + o.id + '"'; }
        if (o.display) { display = "display: " + o.display + ";"; }
        if (o.state) { state = o.state; }
        if (o.icon) { icon = o.icon; }
        if (o.padding) { padding = "padding: " + o.padding + ";"; }
        if (o.margintop) { margintop = "margin-top: " + o.margintop + ";"; }
        if (o.maxwidth) { maxwidth = "max-width: " + o.maxwidth + ";"; }
        return [
            '<div class="ui-widget" ' + containerid + ' style="margin-left: auto; margin-right: auto; ' + margintop + display + maxwidth + '">',
            '<div class="ui-state-' + state + ' ui-corner-all" style="' + padding + '"><p>',
            '<span class="ui-icon ui-icon-' + icon + '"></span>',
            s,
            '</p></div></div>'
        ].join("\n");
       
    },

    /**
     * Returns an error bar, with error icon and the text supplied
     */
    error: function(s, id) {
        return html.textbar(s, { "id": id, "state": "error", "icon": "alert" });
    },

    /**
     * Returns an info bar, with info icon and the text supplied
     */
    info: function(s, id) {
        return html.textbar(s, { "id": id });
    },

    /**
     * Returns an warning bar, with warning icon and the text supplied
     */
    warn: function(s, id) {
        return html.textbar(s, { "id": id, "icon": "alert" });
    },

    /**
     * Reads a list of objects and produces HTML options from it.
     * If valueprop is undefined, we assume a single list of elements.
     *     if the values have a pipe delimiter, we assume value/label pairs
     * l: The list object
     * valueprop: The name of the value property
     * displayprop: The name of the display property. You can also specify multiple columns to concatenate,
     *              separated with ++ eg: SHELTERCODE++ANIMALNAME++SPECIESNAME
     */
    list_to_options: function(l, valueprop, displayprop) {
        var h = "", retired = "", displayval = "";
        $.each(l, function(i, v) {
            if (!valueprop) {
                if (v.indexOf && v.indexOf("|") == -1) {
                    h += "<option value=\"" + html.title(v) + "\">" + v + "</option>";
                }
                else {
                    h += "<option value=\"" + v.split("|")[0] + "\">" + v.split("|")[1] + "</option>";
                }
            }
            else {
                retired = "";
                displayval = "";
                if (displayprop.indexOf("++") != -1) {
                    $.each(displayprop.split("++"), function(idp, vdp) {
                        if (displayval != "") { displayval += " - "; }
                        displayval += v[vdp];
                    });
                }
                else {
                    displayval = v[displayprop];
                }
                if (v.ISRETIRED && v.ISRETIRED == 1) { retired = "data-retired=\"1\""; }
                h += "<option " + retired + " value=\"" + v[valueprop] + "\">" + displayval + "</option>\n";
            }
        });
        return h;
    },

    /**
     * Reads an array of strings and produces HTML options from it.
     * Encode values and labels with a pipe |, eg: value|label - no pipe means no value attribute
     * If the label starts with **, outputs as a group/header instead.
     */
    list_to_options_array: function(a) {
        let d = "", ingroup = false;
        $.each(a, function(ia, va) {
            if (va.indexOf("|") != -1) {
                let [ov, ol] = va.split("|");
                if (ol.indexOf("**--") == 0) { 
                    if (ingroup) { d += "</optgroup>"; }
                    ingroup = true;
                    d += '<optgroup label="' + ol.replace("**--", "") + '">';
                }
                else {
                    d += '<option value="' + ov + '">' + ol + '</option>';
                }
            }
            else {
                if (va.indexOf("**--") == 0) { 
                    if (ingroup) { d += "</optgroup>"; }
                    ingroup = true;
                    d += '<optgroup label="' + va.replace("**--", "") + '">';
                }
                else {
                    d += "<option>" + va + "</option>";
                }
            }
        });
        if (ingroup) {
            d += "</optgroup>";
        }
        return d;
    },

    /**
     * Special list to options for breeds, outputs an 
     * option group for each species
     */
    list_to_options_breeds: function(l) {
        var h = [], spid = 0, retired = "";
        $.each(l, function(i, v) {
            if (v.SPECIESID != spid) {
                if (spid != 0) {
                    h.push("</optgroup>");
                }
                spid = v.SPECIESID;
                h.push("<optgroup id='ngp-" + v.SPECIESID + "' label='" + v.SPECIESNAME + "'>");
            }
            retired = "";
            if (v.ISRETIRED && v.ISRETIRED == 1) { retired = "data-retired=\"1\""; }
            h.push("<option " + retired + " value=\"" + v.ID + "\">" + v.BREEDNAME + "</option>\n");
        });
        return h.join("\n");
    },

    data_url_to_array_buffer: function(url) {
        var bytestring = window.atob(url.split(",")[1]);
        var bytes = new Uint8Array(bytestring.length);
        for (var i = 0; i < bytestring.length; i++) {
            bytes[i] = bytestring.charCodeAt(i);
        }
        return bytes.buffer;
    },

    /** Get the EXIF orientation for file 1-8. 
     *  Also returns -2 (not jpeg) and -1 (no orientation found).
     *  Asynchronous and returns a promise. */
    get_exif_orientation: function(file) {
        var deferred = $.Deferred();
        common.read_file_as_array_buffer(file.slice(0, 64 * 1024))
        .then(function(result) {
            var view = new DataView(result);
            if (view.getUint16(0, false) != 0xFFD8) {
                deferred.resolve(-2);
                return;
            }
            var length = view.byteLength,
                offset = 2;
            while (offset < length) {
                var marker = view.getUint16(offset, false);
                offset += 2;
                if (marker == 0xFFE1) {
                    if (view.getUint32(offset += 2, false) != 0x45786966) {
                        deferred.resolve(-1);
                        return;
                    }
                    var little = view.getUint16(offset += 6, false) == 0x4949;
                    offset += view.getUint32(offset + 4, little);
                    var tags = view.getUint16(offset, little);
                    offset += 2;
                    for (var i = 0; i < tags; i++)
                        if (view.getUint16(offset + (i * 12), little) == 0x0112) {
                            deferred.resolve(view.getUint16(offset + (i * 12) + 8, little));
                            return;
                        }
                }
                else if ((marker & 0xFF00) != 0xFF00) break;
                else offset += view.getUint16(offset, false);
            }
            deferred.resolve(-1);
            return;
        });
        return deferred.promise();
    },

    /**
     * Loads an img element from a file. 
     * Returns a promise, the result is the loaded img.
     */
    load_img: function(file) {
        var reader = new FileReader(),
            img = document.createElement("img"),
            deferred = $.Deferred();
        reader.onload = function(e) {
            img.src = e.target.result;
        };
        reader.onerror = function(e) {
            deferred.reject(reader.error.message);
        };
        img.onload = function() {
            deferred.resolve(img);
        };
        reader.readAsDataURL(file);
        return deferred.promise();
    },

    /** Applies a canvas transformation based on the EXIF orientation passed.
     *  The next drawImage will be rotated correctly. 
     *  It also resizes the canvas if the orientation changes.
     *  If the web browser oriented the image before rendering to the canvas, does nothing.
     **/
    rotate_canvas_to_exif: function(canvas, ctx, orientation) {
        // This function is no longer needed as all browsers do this when loading the image now
        // if (Modernizr.exiforientation) { return; }
        if (true) { return; }
        var width = canvas.width,
            height = canvas.height;
        if (4 < orientation && orientation < 9) {
            canvas.width = height;
            canvas.height = width;
        } 
        else {
            canvas.width = width;
            canvas.height = height;
        }
        switch (orientation) {
            case 2: ctx.transform(-1, 0, 0, 1, width, 0); break;
            case 3: ctx.transform(-1, 0, 0, -1, width, height); break;
            case 4: ctx.transform(1, 0, 0, -1, 0, height); break;
            case 5: ctx.transform(0, 1, 1, 0, 0, 0); break;
            case 6: ctx.transform(0, 1, -1, 0, height, 0); break;
            case 7: ctx.transform(0, -1, -1, 0, height, width); break;
            case 8: ctx.transform(0, -1, 1, 0, 0, width); break;
            default: break;
        }
    },

    /**
     * Scales and rotates Image object img to h and w px, returning a data URL.
     * Depending on the size of the image, chooses an appropriate number
     * of steps to avoid aliasing. Handles rotating the image first
     * via its Exif orientation (1-8).
     */
    scale_image: function(img, w, h, orientation) {
        var scaled;
        if (img.height > h * 2 || img.width > w * 2) { 
            scaled = html.scale_image_2_step(img, w, h, orientation); 
        }
        else {
            scaled = html.scale_image_1_step(img, w, h, orientation);
        }
        return scaled;
    },

    /**
     * Scales DOM element img to h and w, returning a data URL.
     */
    scale_image_1_step: function(img, w, h, orientation) {
        var canvas = document.createElement("canvas"),
            ctx = canvas.getContext("2d");
        canvas.height = h;
        canvas.width = w;
        html.rotate_canvas_to_exif(canvas, ctx, orientation);
        ctx.drawImage(img, 0, 0, w, h);
        return canvas.toDataURL("image/jpeg");
    },

    /**
     * Scales DOM element img to h and w, returning a data URL.
     * Uses a two step process to avoid aliasing.
     */
    scale_image_2_step: function(img, w, h, orientation) {
        var canvas = document.createElement("canvas"),
            ctx = canvas.getContext("2d"),
            oc = document.createElement("canvas"),
            octx = oc.getContext("2d");
        canvas.height = h;
        canvas.width = w;
        // step 1 - render the image at 50% of its size to the first canvas
        oc.width = img.width * 0.5;
        oc.height = img.height * 0.5;
        octx.drawImage(img, 0, 0, oc.width, oc.height);
        // step 2 / final - render the 50% sized canvas to the final canvas at the correct size
        html.rotate_canvas_to_exif(canvas, ctx, orientation);
        ctx.drawImage(oc, 0, 0, oc.width, oc.height, 0, 0, w, h);
        return canvas.toDataURL("image/jpeg");
    },

    /** Returns a list of all US states as a set of option tags */
    states_us_options: function(selected) {
        let US_STATES = [ ["Alabama","AL"], ["Alaska","AK"], ["Arizona","AZ"], ["Arkansas","AR"], ["American Samoa","AS"], 
            ["California","CA"], ["Colorado","CO"], ["Connecticut","CT"], ["District of Columbia","DC"], ["Delaware","DE"], 
            ["Florida","FL"], ["Federated States of Micronesia","FM"], ["Georgia","GA"], ["Guam","GU"], ["Hawaii","HI"], 
            ["Idaho","ID"], ["Illinois","IL"], ["Indiana","IN"], ["Iowa","IA"], ["Kansas","KS"], ["Kentucky","KY"], 
            ["Louisiana","LA"], ["Maine","ME"], ["Marshall Islands","MH"], ["Maryland","MD"], ["Massachusetts","MA"], 
            ["Michigan","MI"], ["Minnesota","MN"], ["Mississippi","MS"], ["Missouri","MO"], ["Montana","MT"], ["Nebraska","NE"], 
            ["Nevada","NV"], ["New Hampshire","NH"], ["New Jersey","NJ"], ["New Mexico","NM"], ["New York","NY"],
            ["North Carolina","NC"], ["North Dakota","ND"], ["Northern Mariana Islands","MP"], ["Ohio","OH"], ["Oklahoma","OK"], 
            ["Oregon","OR"], ["Palau","PW"], ["Pennsylvania","PA"], ["Puerto Rico","PR"], ["Rhode Island","RI"], 
            ["South Carolina","SC"], ["South Dakota","SD"], ["Tennessee","TN"], ["Texas","TX"], ["Utah","UT"],
            ["Vermont","VT"], ["Virgin Islands","VI"], ["Virginia","VA"], ["Washington","WA"], ["West Virginia","WV"], 
            ["Wisconsin","WI"],["Wyoming","WY"]
        ], opts = [ '<option value=""></option>' ];
        $.each(US_STATES, function(i, v) {
            let sel = common.iif(selected == v[1], 'selected="selected"', '');
            opts.push('<option value="' + v[1] + '" ' + sel + '>' + v[1] + " - " + v[0] + '</option>');
        });
        return opts.join("\n");
    },

    /** 
     * Removes HTML tags from a string
     */
    strip_tags: function(s) {
        if (!s) { return ""; }
        /*jslint regexp: true */
        return String(s).replace(/<[^>]+>/g,"");
    },

    /**
     * Santises a string to go in an HTML title
     */
    title: function(s) {
        if (s == null || s === undefined) { return ""; }
        s = String(s);
        s = common.replace_all(s, "\"", "&quot;");
        s = common.replace_all(s, "'", "&apos;");
        return s;
    },

    /**
     * Truncates a string to length. If the string is longer
     * than length, appends ...
     * Throws away html tags too.
     */
    truncate: function(s, length) {
        if (length === undefined) {
            length = 100;
        }
        if (s == null) {
            return "";
        }
        s = this.strip_tags(s);
        if (s.length > length) {
            return s.substring(0, length) + "...";
        }
        return s;
    },

    /**
     * Gets the img src attribute/URI to a picture. If the
     * row doesn't have preferred media, the nopic src is returned instead.
     * Makes life easier for the browser caching things and we can stick
     * a max-age on items being served.
     * row: An animal or person json row containing ID, ANIMALID or PERSONID
     *      and WEBSITEMEDIANAME
     * mode: The mode - animal or person
     */
    img_src: function(row, mode) {
        if (!row.WEBSITEMEDIANAME) {
            return "image?db=" + asm.useraccount + "&mode=nopic";
        }
        var idval = 0, uri = "";
        if (mode == "animal") {
            if (row.hasOwnProperty("ANIMALID")) {
                idval = row.ANIMALID;
            }
            else if (row.hasOwnProperty("ID")) {
                idval = row.ID;
            }
        }
        else if (mode == "person") {
            if (row.hasOwnProperty("PERSONID")) {
                idval = row.PERSONID;
            }
            else if (row.hasOwnProperty("ID")) {
                idval = row.ID;
            }
        }
        else {
            idval = row.ID;
        }
        uri = "image?db=" + asm.useraccount + "&mode=" + mode + "&id=" + idval;
        if (row.WEBSITEMEDIADATE) {
            uri += "&date=" + encodeURIComponent(row.WEBSITEMEDIADATE);
        }
        return uri;
    },

    /**
     * Gets the img src attribute for a thumbnail picture. If the
     * row doesn't have preferred media, the nopic src is returned instead.
     * Makes life easier for the browser caching things and we can stick
     * a max-age on items being served.
     * row: An animal or person json row containing ID, ANIMALID or PERSONID
     *      and WEBSITEMEDIANAME
     * mode: The mode - aanimalthumb or personthumb
     */
    thumbnail_src: function(row, mode) {
        if (!row.WEBSITEMEDIANAME) {
            return "image?db=" + asm.useraccount + "&mode=nopic";
        }
        var idval = 0, uri = "";
        if (mode == "animalthumb") {
            if (row.hasOwnProperty("ANIMALID")) {
                idval = row.ANIMALID;
            }
            else if (row.hasOwnProperty("ID")) {
                idval = row.ID;
            }
        }
        else if (mode == "personthumb") {
            if (row.hasOwnProperty("PERSONID")) {
                idval = row.PERSONID;
            }
            else if (row.hasOwnProperty("ID")) {
                idval = row.ID;
            }
        }
        else {
            idval = row.ID;
        }
        uri = "image?db=" + asm.useraccount + "&mode=" + mode + "&id=" + idval;
        if (row.WEBSITEMEDIADATE) {
            uri += "&date=" + encodeURIComponent(row.WEBSITEMEDIADATE);
        }
        return uri;
    }

};


