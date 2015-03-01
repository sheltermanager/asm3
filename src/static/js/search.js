/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    var search = {

        /**
         * Gets the description text for an animal result
         */
        description: function(r) {
            var banner = [];
            if ($.trim(r.HIDDENANIMALDETAILS) != "") {
                banner.push(r.HIDDENANIMALDETAILS);
            }
            if ($.trim(r.MARKINGS) != "") {
                banner.push(r.MARKINGS);
            }
            if ($.trim(r.ANIMALCOMMENTS) != "") {
                banner.push(r.ANIMALCOMMENTS);
            }
            return banner.join(". ");
        },

        render: function() {
            var h = [];
            h.push('<div id="asm-content" class="ui-helper-reset ui-widget-content ui-corner-all" style="padding: 10px;">');
            if (controller.explain != "") {
                h.push('<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">' +
                    '<p><span class="ui-icon ui-icon-search" style="float: left; margin-right: .3em;"></span>' +
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
                        window.location = "animal?id=" + r.ID;
                    }
                    h.push('<p class="asm-search-result">' +
                        '<span class="asm-search-name">' + 
                        '<img align="right" src="' + html.thumbnail_src(r, "animalthumb") + '" class="asm-thumbnail thumbnailshadow" />' +
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
                            h.push("<a href=\"person?id=" + r.ORIGINALOWNERID + "\">" + r.ORIGINALOWNERNAME + "</a>");
                        }
                        h.push('</span>');
                    }
                    else if (r.CURRENTOWNERID != null) {
                        h.push(r.DISPLAYLOCATIONNAME);
                        h.push(html.icon("right") + ' <a href="person?id=' + r.CURRENTOWNERID + '">' + r.CURRENTOWNERNAME + '</a>');
                    }
                    else {
                        h.push(r.DISPLAYLOCATIONNAME);
                        if (r.SHELTERLOCATIONUNIT && !r.ACTIVEMOVEMENTID) {
                            h.push(' <span class="asm-search-locationunit" title="' + html.title(_("Unit")) + '">' + r.SHELTERLOCATIONUNIT + '</span>');
                        }
                    }
                    h.push('<br/>');
                    h.push(html.truncate(search.description(r)));
                    h.push('</p>');
                }
                if (r.RESULTTYPE == "LICENCE") {
                    if (controller.results.length == 1) {
                        window.location = "person_licence?id=" + r.OWNERID;
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">');
                    h.push(html.icon("licence", _("License")));
                    h.push('<a href="person_licence?id=' + r.OWNERID + '">' + r.OWNERNAME  + ' - ' + r.LICENCENUMBER + '</a></span> ');
                    h.push('<br/>');
                    h.push(r.OWNERADDRESS);
                    h.push('<br />');
                    h.push('<span class="asm-search-personflags">' + r.LICENCETYPENAME + ', ' + format.date(r.ISSUEDATE) + 
                        ' - ' + format.date(r.EXPIRYDATE) + '</span>');
                    h.push('<br/>');
                    h.push(html.truncate(r.COMMENTS));
                    h.push('</p>');
                }
                else if (r.RESULTTYPE == "PERSON") {
                    if (controller.results.length == 1) {
                        window.location = "person?id=" + r.ID;
                    }
                    h.push('<p class="asm-search-result"><span class="asm-search-name">' +
                        '<img align="right" src="' + html.thumbnail_src(r, 'personthumb') + '" class="asm-thumbnail thumbnailshadow" />' +
                        html.icon("person", _("Person")));
                    h.push('<a href="person?id=' + r.ID + '">' + r.OWNERNAME + ' - ' + r.OWNERCODE + '</a></span> ');
                    h.push('<a href="person_diary?id=' + r.ID + '">' + html.icon("diary", _("Jump to diary")) + '</a>');
                    h.push('<a href="person_donations?id=' + r.ID + '">' + html.icon("donation", _("Jump to donations")) + '</a>');
                    h.push('<a href="person_movements?id=' + r.ID + '">' + html.icon("movement", _("Jump to movements")) + '</a>');
                    h.push('<br/>');
                    h.push(r.OWNERADDRESS);
                    h.push('<br />');
                    h.push('<span class="asm-search-personflags">' + edit_header.person_flags(r) + '</span>');
                    h.push('<br/>');
                    h.push(html.truncate(r.COMMENTS));
                    h.push('</p>');
                }
                else if (r.RESULTTYPE == "WAITINGLIST") {
                    if (controller.results.length == 1) {
                        window.location = "waitinglist?id=" + r.ID;
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
                        window.location = "incident?id=" + r.ID;
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
                        window.location = "lostanimal?id=" + r.ID;
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
                        window.location = "foundanimal?id=" + r.ID;
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
        }
    };

    // Show the results into the page
    $("body").append(search.render());
    
    // If only one result was returned, stop now as we're going to be redirected.
    if (controller.results.length == 1) { return; }

    common.bind_widgets();
    search.bind();
    common.apply_label_overrides("search");
    $("#asm-content").asmcontent("results");

});
