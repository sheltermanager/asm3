/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const search = {

        /**
         * Gets the description text for an animal result
         */
        description: function(r) {
            let banner = [];
            if (common.trim(r.HIDDENANIMALDETAILS) != "") {
                banner.push(r.HIDDENANIMALDETAILS);
            }
            if (common.trim(r.MARKINGS) != "") {
                banner.push(r.MARKINGS);
            }
            if (common.trim(r.ANIMALCOMMENTS) != "") {
                banner.push(r.ANIMALCOMMENTS);
            }
            return banner.join(". ");
        },

        render: function() {
            let h = [];
            h.push('<div id="asm-content" class="ui-helper-reset ui-widget-content ui-corner-all" style="padding: 10px;">');
            if (controller.explain != "") {
                h.push('<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">' +
                    '<p><span class="ui-icon ui-icon-search"></span>' +
                    controller.explain + "</p></div>");
            }
            if (controller.results.length == 0) {
                h.push('<p class="asm-search-result">' + _("No results found.") + '</p>');
            }
            else {
                h.push('<p class="asm-search-numbertime">' + 
                    common.ntranslate(controller.results.length, [
                        _("{plural0} result found in {1} seconds. Order: {2}"),
                        _("{plural1} results found in {1} seconds. Order: {2}"),
                        _("{plural2} results found in {1} seconds. Order: {2}"),
                        _("{plural3} results found in {1} seconds. Order: {2}")
                    ]).replace("{1}", controller.timetaken).replace("{2}", controller.sortname) +
                    '</p>');
            }
            $.each(controller.results, function(i, r) {
                if (r.RESULTTYPE == "ANIMAL") {
                    if (controller.results.length == 1) {
                        common.route("animal?id=" + r.ID);
                    }
                    h.push('<p class="asm-search-result">' +
                        '<span class="asm-search-name">' + 
                        html.animal_link_thumb_bare(r) +
                        html.icon("animal", _("Animal")));
                    h.push(html.animal_emblems(r));
                    h.push('<a href="animal?id=' + r.ID + '">' + r.ANIMALNAME + ' - ' + r.CODE + '</a> ');
                    h.push('<a href="animal_media?id=' + r.ID + '">' + html.icon("media", _("Jump to media")) + '</a>');
                    h.push('<a href="animal_diary?id=' + r.ID + '">' + html.icon("diary", _("Jump to diary")) + '</a>');
                    h.push('<a href="animal_movements?id=' + r.ID + '">' + html.icon("movement", _("Jump to movements")) + '</a>');
                    h.push('</span>');
                    h.push('<br/>');
                    h.push('<span class="asm-search-detail">' + common.substitute(_("{0} {1} {2} aged {3}"), { "0": r.SEXNAME, "1": r.BREEDNAME, "2": r.SPECIESNAME, "3": r.ANIMALAGE }));
                    h.push('</span>');
                    h.push('<br/>');
                    if (r.DECEASEDDATE != null) {
                        h.push('<span class="asm-search-deceased">' + _("Deceased") + ' ' + html.icon("right") + ' ' + r.DISPLAYLOCATIONNAME + '</span>');
                    }
                    else if (r.NONSHELTERANIMAL == 1) {
                        h.push('<span class="asm-search-nonshelter">' + _("Non-Shelter Animal"));
                        if (r.ORIGINALOWNERID && r.ORIGINALOWNERID > 0) {
                            h.push(" " + html.icon("right") + " ");
                            h.push(html.person_link(r.ORIGINALOWNERID, r.ORIGINALOWNERNAME));
                        }
                        h.push('</span>');
                    }
                    else if (r.OWNERID && r.OWNERID != r.CURRENTOWNERID) {
                        h.push(_("Owner"));
                        h.push(html.icon("right") + ' ' + html.person_link(r.OWNERID, r.OWNERNAME));
                    }
                    else if (r.CURRENTOWNERID) {
                        h.push(r.DISPLAYLOCATIONNAME);
                        h.push(html.icon("right") + ' ' + html.person_link(r.CURRENTOWNERID, r.CURRENTOWNERNAME));
                    }
                    else {
                        h.push(r.DISPLAYLOCATIONNAME);
                        if (r.SHELTERLOCATIONUNIT && !r.ACTIVEMOVEMENTID) {
                            h.push(' <span class="asm-search-locationunit" title="' + html.title(_("Unit")) + '">' + r.SHELTERLOCATIONUNIT + '</span>');
                        }
                    }
                    h.push('<span style="margin-left: 15px;" class="asm-search-personflags">' + edit_header.animal_flags(r) + '</span>');
                    h.push('<br/>');
                    h.push(html.truncate(search.description(r)));
                    h.push('</p>');
                }
                if (r.RESULTTYPE == "LICENCE") {
                    if (controller.results.length == 1) {
                        common.route("person_licence?id=" + r.OWNERID);
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">');
                    h.push(html.icon("licence", _("License")));
                    h.push('<a href="person_licence?id=' + r.OWNERID + '">' + r.OWNERNAME  + ' - ' + r.LICENCENUMBER + '</a></span> ');
                    h.push('<br/>');
                    h.push(r.OWNERADDRESS);
                    h.push('<br />');
                    h.push(r.OWNERTOWN + ", " + r.OWNERCOUNTY + " " + r.OWNERPOSTCODE);
                    h.push('<br />');
                    h.push('<span class="asm-search-personflags">' + r.LICENCETYPENAME + ', ' + format.date(r.ISSUEDATE) + 
                        ' - ' + format.date(r.EXPIRYDATE) + '</span>');
                    h.push('<br/>');
                    h.push(html.truncate(r.COMMENTS));
                    h.push('</p>');
                }
                else if (r.RESULTTYPE == "LOG") {
                    if (controller.results.length == 1) {
                        common.route(r.RECORDTYPE + '_log?id=' + r.LINKID);
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">');
                    h.push(html.icon("log", _("Log")));
                    h.push('<a href="' + r.RECORDTYPE + '_log?id=' + r.LINKID + '">' + r.RECORDDETAIL + '</a></span> ');
                    h.push('<br />');
                    h.push('<span class="asm-search-personflags">' + r.LOGTYPENAME + '</span>');
                    h.push('<br/>');
                    h.push(html.truncate(r.COMMENTS));
                    h.push('</p>');
                }
                else if (r.RESULTTYPE == "PERSON") {
                    if (controller.results.length == 1) {
                        common.route("person?id=" + r.ID);
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">' +
                        '<img align="right" src="' + html.thumbnail_src(r, 'personthumb') + '" class="asm-thumbnail thumbnailshadow" />' +
                        html.icon("person", _("Person")));
                    h.push(html.person_link(r.ID, r.OWNERNAME + ' - ' + r.OWNERCODE) + '</span> ');
                    h.push('<a href="person_diary?id=' + r.ID + '">' + html.icon("diary", _("Jump to diary")) + '</a>');
                    h.push('<a href="person_donations?id=' + r.ID + '">' + html.icon("donation", _("Jump to donations")) + '</a>');
                    h.push('<a href="person_movements?id=' + r.ID + '">' + html.icon("movement", _("Jump to movements")) + '</a>');
                    h.push('<br/>');
                    if (edit_header.person_flags(r)) { 
                        h.push('<span class="asm-search-personflags">' + edit_header.person_flags(r) + '</span>');
                        h.push('<br/>'); 
                    }
                    h.push(r.OWNERADDRESS);
                    h.push('<br />');
                    h.push(r.OWNERTOWN + ", " + r.OWNERCOUNTY + " " + r.OWNERPOSTCODE);
                    h.push('<br />');
                    h.push(html.truncate(r.COMMENTS));
                    h.push('</p>');
                }
                if (r.RESULTTYPE == "VOUCHER") {
                    if (controller.results.length == 1) {
                        common.route("person_vouchers?id=" + r.OWNERID);
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">');
                    h.push(html.icon("donation", _("Voucher")));
                    h.push('<a href="person_vouchers?id=' + r.OWNERID + '">' + r.OWNERNAME  + ' - ' + r.VOUCHERCODE + '</a></span> ');
                    h.push('<br/>');
                    h.push(r.OWNERADDRESS);
                    h.push('<br />');
                    h.push(r.OWNERTOWN + ", " + r.OWNERCOUNTY + " " + r.OWNERPOSTCODE);
                    h.push('<br />');
                    h.push('<span class="asm-search-personflags">' + r.VOUCHERNAME + ', ' + format.date(r.DATEISSUED) + 
                        ' - ' + format.date(r.DATEREDEEMED) + '</span>');
                    h.push('<br/>');
                    h.push(html.truncate(r.COMMENTS));
                    h.push('</p>');
                }
                if (r.RESULTTYPE == "CITATION") {
                    if (controller.results.length == 1) {
                        common.route("person_citations?id=" + r.OWNERID);
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">');
                    h.push(html.icon("citation", _("Citation")));
                    h.push('<a href="person_citations?id=' + r.OWNERID + '">' + r.OWNERNAME  + ' - ' + r.CITATIONNUMBER + '</a></span> ');
                    h.push('<br />');
                    h.push('<span class="asm-search-personflags">' + r.CITATIONNAME + ', ' + format.date(r.CITATIONDATE) + 
                        ' - ' + format.date(r.FINEPAIDDATE) + '</span>');
                    h.push('<br/>');
                    h.push(html.truncate(r.COMMENTS));
                    h.push('</p>');
                }
                else if (r.RESULTTYPE == "WAITINGLIST") {
                    if (controller.results.length == 1) {
                        common.route("waitinglist?id=" + r.ID);
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">');
                    h.push(html.icon("waitinglist", _("Waiting List")));
                    h.push('<a href="waitinglist?id=' + r.ID + '">' + r.OWNERNAME + ' - ' + format.padleft(r.WLID, 6) + '</a></span>');
                    h.push('<br />');
                    h.push(html.truncate(r.ANIMALDESCRIPTION));
                    h.push('</p>');
                }
                else if (r.RESULTTYPE == "ANIMALCONTROL") {
                    if (controller.results.length == 1) {
                        common.route("incident?id=" + r.ID);
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">');
                    h.push(html.icon("call", _("Incident")));
                    h.push('<a href="incident?id=' + r.ID + '">' + r.INCIDENTNAME + ' - ' + common.nulltostr(r.OWNERNAME1) +
                        (r.OWNERNAME2 ? ', ' + common.nulltostr(r.OWNERNAME2) : "") +
                        (r.OWNERNAME3 ? ', ' + common.nulltostr(r.OWNERNAME3) : "") + ' ' +
                        format.padleft(r.ACID, 6) + '</a></span>');
                    h.push('<br />');
                    h.push('<span class="asm-search-personflags">' + format.date(r.INCIDENTDATETIME) + ' - ' + format.date(r.COMPLETEDDATE) + '</span><br />');
                    if (r.DISPATCHADDRESS) {
                        h.push(r.DISPATCHADDRESS + '<br />');
                    }
                    h.push(html.truncate(r.CALLNOTES));
                    h.push('</p>');
                }
                else if (r.RESULTTYPE == "LOSTANIMAL") {
                    if (controller.results.length == 1) {
                        common.route("lostanimal?id=" + r.ID);
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">');
                    h.push(html.icon("animal-lost", _("Lost Animal")));
                    h.push('<a href="lostanimal?id=' + r.ID + '">' + r.OWNERNAME + ' - ' + format.padleft(r.ID, 6) + '</a></span>');
                    h.push('<br />');
                    h.push('<span class="asm-search-detail">' + _("Lost") + ' ' + r.AGEGROUP + ' ' + r.SPECIESNAME + ' / ' + r.AREALOST + ' ' + r.AREAPOSTCODE + '</span><br />');
                    h.push(r.DISTFEAT);
                    h.push('</p>');
                }
                else if (r.RESULTTYPE == "FOUNDANIMAL") {
                    if (controller.results.length == 1) {
                        common.route("foundanimal?id=" + r.ID);
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">');
                    h.push(html.icon("animal-found", _("Found Animal")));
                    h.push('<a href="foundanimal?id=' + r.ID + '">' + r.OWNERNAME + ' - ' + format.padleft(r.ID, 6) + '</a></span>');
                    h.push('<br />');
                    h.push('<span class="asm-search-detail">' + _("Found") + ' ' + r.AGEGROUP + ' ' + r.SPECIESNAME + ' / ' + r.AREAFOUND + ' ' + r.AREAPOSTCODE + '</span><br />');
                    h.push(r.DISTFEAT);
                    h.push('</p>');
                }
            });
            h.push("</div>");
            return h.join("\n");
        },

        bind: function() {
        },

        sync: function() {
        },

        name: "search",
        animation: "results",
        autofocus: "#asm-content a:first",
        title: function() { return _("Search Results for '{0}'").replace("{0}", controller.q); },
        routes: {
            "search": function() { common.module_loadandstart("search", "search?" + this.rawqs); }
        }
    };

    common.module_register(search);

});
