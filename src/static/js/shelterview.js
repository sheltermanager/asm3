/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    "use strict";

    const shelterview = {

        /**
         * Renders an animal thumbnail
         */
        render_animal: function(a, showunit, allowdrag) {
            let h = [];
            h.push('<div ');
            if (allowdrag) {
                h.push('class="asm-shelterview-animal animaldragtarget" ');
            }
            else {
                h.push('class="asm-shelterview-animal" ');
            }
            h.push('data-animal="' + a.ID + '" ');
            h.push('data-location="' + a.SHELTERLOCATION + '" ');
            h.push('data-unit="' + a.SHELTERLOCATIONUNIT + '" ');
            h.push('data-person="' + a.CURRENTOWNERID + '" ');
            h.push('>');
            h.push(html.animal_link_thumb(a, {showunit: showunit}));
            h.push('</div>');
            return h.join("\n");
        },

        /** 
         * Renders a specialised shelterview that shows each custom
         * flag added by users and all animals that have that flag.
         * It's a special view because the same animal can appear
         * multiple times in this one if it has multiple flags.
         */
        render_flags: function() {
            let h = [], ht = [], c = 0;
            $.each(controller.flags, function(i, f) {
                ht = [];
                c = 0;
                // Build output for every animal who has this flag
                $.each(controller.animals, function(ia, a) {
                    if (!a.ADDITIONALFLAGS) { return; }
                    let aflags = a.ADDITIONALFLAGS.split("|");
                    $.each(aflags, function(x, af) {
                        if (af == f.FLAG) {
                            c += 1;
                            ht.push(shelterview.render_animal(a, false, !a.ACTIVEMOVEMENTTYPE && a.ARCHIVED == 0));
                        }
                    });
                });
                // Output the flag if some animals had it
                if (c > 0) {
                    h.push('<p class="asm-menu-category">' + f.FLAG + ' (' + c + ')</p>');
                    h.push(ht.join("\n"));
                }
            });
            // Output all animals who don't have any flags
            ht = [];
            c = 0; 
            $.each(controller.animals, function(ia, a) {
                if (!a.ADDITIONALFLAGS || a.ADDITIONALFLAGS == '|') {
                    c += 1;
                    ht.push(shelterview.render_animal(a, false, !a.ACTIVEMOVEMENTTYPE && a.ARCHIVED == 0));
                }
            });
            if (c > 0) {
                h.push('<p class="asm-menu-category">' + _("(none)") + ' (' + c + ')</p>');
                h.push(ht.join("\n"));
            }
            // Load the whole thing into the DOM
            $("#viewcontainer").html(h.join("\n"));
        },

        /** 
         * Renders a specialised shelterview that shows good with
         * and housetrained, along with all animals that have a positive value.
         * It's a special view because the same animal can appear
         * multiple times in this one if it has multiple matches.
         */
        render_goodwith: function() {
            let h = [];
            let gw = [
                [ "ISGOODWITHCATS", 0, _("Good with cats") ],
                [ "ISGOODWITHDOGS", 0, _("Good with dogs") ],
                [ "ISGOODWITHCHILDREN", 0, _("Good with children") ],
                [ "ISGOODWITHCHILDREN", 5, _("Good with children over 5") ],
                [ "ISGOODWITHCHILDREN", 12, _("Good with children over 12") ],
                [ "ISGOODWITHELDERLY", 0, _("Good with elderly")],
                [ "ISGOODTRAVELLER", 0, _("Good traveller")],
                [ "ISGOODONLEAD", 0, _("Good on lead")],
                [ "ISCRATETRAINED", 0, _("Crate trained") ],
                [ "ISHOUSETRAINED", 0, _("Housetrained") ],
                [ "ENERGYLEVEL", 1, _("Energy level") + ': ' + _("1 - Very low") ],
                [ "ENERGYLEVEL", 2, _("Energy level") + ': ' + _("2 - Low") ],
                [ "ENERGYLEVEL", 3, _("Energy level") + ': ' + _("3 - Medium") ],
                [ "ENERGYLEVEL", 4, _("Energy level") + ': ' + _("4 - High") ],
                [ "ENERGYLEVEL", 5, _("Energy level") + ': ' + _("5 - Very high") ]
            ];
            $.each(gw, function(i, v) {
                let ht = [], c = 0;
                $.each(controller.animals, function(ia, a) {
                    if (a[v[0]] == v[1]) {
                        c += 1;
                        ht.push(shelterview.render_animal(a, false, !a.ACTIVEMOVEMENTTYPE && a.ARCHIVED == 0));
                    }
                });
                // Output the category and matching animals if there were any
                if (c > 0) {
                    h.push('<p class="asm-menu-category">' + v[2] + ' (' + c + ')</p>');
                    h.push(ht.join("\n"));
                }
            });
            // Load the whole thing into the DOM
            $("#viewcontainer").html(h.join("\n"));
        },

        /**
         * Renders a specialised shelterview that shows all locations, then
         * all units within those locations. Available units are highlighted
         * and occupied units show animal links.
         */
        render_units_available: function() {
            let h = [];
            const is_on_shelter = function(a) {
                return a.HASACTIVEBOARDING == 1 || a.ACTIVEMOVEMENTID == 0;
            };
            $.each(controller.locations, function(il, l) {
                // If the location is empty and this one is retired, stop now
                if (shelterview.location_is_empty(l.ID) && l.ISRETIRED && l.ISRETIRED == 1) { return; }
                // Output the location
                let loclink = "animal_find_results?logicallocation=onshelter&shelterlocation=" + l.ID;
                h.push('<p class="asm-menu-category"><a href="' + loclink + '">' + 
                    l.LOCATIONNAME + ' (' + shelterview.location_animal_count(l.ID) + ')</a></p>');
                // If the location has no units, just output a single unit for the location
                if (!common.trim(common.nulltostr(l.UNITS))) { 
                    let boxinner = [], classes = "unitdroptarget asm-shelterview-unit";
                    $.each(controller.animals, function(ia, a) {
                        if (a.SHELTERLOCATION == l.ID && is_on_shelter(a)) {
                            boxinner.push(shelterview.render_animal(a, false, !a.ACTIVEMOVEMENTTYPE && a.ARCHIVED == 0));
                        }
                    });
                    // Show that unit as available if there are no animals in it
                    if (boxinner.length == 0) { classes += " asm-shelterview-unit-available"; }
                    h.push('<div data-location="' + l.ID + '" data-unit="" class="' + classes + '">');
                    h.push(boxinner.join("\n"));
                    h.push('</div>');
                }
                else {
                    // Output a box for every unit within the location
                    $.each(l.UNITS.split(","), function(iu, u) {
                        u = common.trim(u);
                        // If the unit name is blank, skip it
                        if (!u) { return; }
                        // Find all animals in this unit and construct the inner
                        let boxinner = [], classes = "unitdroptarget asm-shelterview-unit";
                        $.each(controller.animals, function(ia, a) {
                            if (a.SHELTERLOCATION == l.ID && a.SHELTERLOCATIONUNIT == u && is_on_shelter(a)) {
                                boxinner.push(shelterview.render_animal(a, false, !a.ACTIVEMOVEMENTTYPE && a.ARCHIVED == 0));    
                            }
                        });
                        // If there are no animals in this unit, show the background as available or reserved
                        let [ sponsortext, reservetext ] = shelterview.unit_values(l.ID, u);
                        if (boxinner.length == 0) {
                            // Show the unit as reserved if it has a reservation
                            if (reservetext) {
                                classes += " asm-shelterview-unit-reserved";
                            }
                            else {
                                classes += " asm-shelterview-unit-available"; 
                            }
                        }
                        h.push('<div data-location="' + l.ID + '" data-unit="' + u.replace("\"", "") + '" class="' + classes + '">');
                        h.push('<div class="asm-shelterview-unit-name">' + u );
                        // Units include a button to edit whether they are reserved or sponsored. 
                        if (config.bool("ShelterViewReserves") && common.has_permission("rsu")) {
                            h.push('<a href="#" class="asm-shelterview-unit-button floatright"><span class="ui-icon ui-icon-pencil"></span></a>');
                        }
                        h.push('</div>');
                        if (reservetext) {
                            h.push('<div style="margin-top: 10px" class="reservetext">' + _("Reserved for {0}").replace("{0}", reservetext) + '</div>');
                        }
                        if (sponsortext) {
                            h.push('<div style="margin-top: 10px" class="sponsortext">' + _("Sponsored by {0}").replace("{0}", sponsortext) + '</div>');
                        }
                        h.push(boxinner.join("\n"));
                        h.push('</div>');
                    });
                    // Find any animals who were in the location but didn't match one of the
                    // set units. Put them in an "invalid" unit that they can be dragged out of
                    // but not dropped into.
                    let badunit = [];
                    $.each(controller.animals, function(ia, a) {
                        // Skip animals not in this location
                        if (a.SHELTERLOCATION != l.ID) { return; }
                        if (a.ACTIVEMOVEMENTID != 0) { return; }
                        let validunit = false;
                        $.each(l.UNITS.split(","), function(iu, u) {
                            u = common.trim(u);
                            if (a.SHELTERLOCATIONUNIT == u && is_on_shelter(a)) {
                                validunit = true;
                                return false;
                            }
                        });
                        if (!validunit) {
                            badunit.push(shelterview.render_animal(a, true, !a.ACTIVEMOVEMENTTYPE && a.ARCHIVED == 0));
                        }
                    });
                    if (badunit.length > 0) {
                        h.push('<div data-location="' + l.ID + '" data-unit="' + _("invalid") + '" class="asm-shelterview-unit">');
                        h.push('<div class="asm-shelterview-unit-name">' + _("invalid") + '</div>');
                        h.push(badunit.join("\n"));
                        h.push('</div>');
                    }
                }
            });

            // Load the whole thing into the DOM
            $("#viewcontainer").html(h.join("\n"));

            if (config.bool("ShelterViewDragDrop") && !common.browser_is.mobile) {
                $(".animaldragtarget").draggable();
                $(".unitdroptarget").droppable({
                    over: function(event, ui) {
                        $(this).addClass("transparent");
                    },
                    out: function(event, ui) {
                        $(this).removeClass("transparent");
                    },
                    drop: function(event, ui) {
                        let locationid = $(this).attr("data-location");
                        let unit = $(this).attr("data-unit");
                        let animalid = $(ui.draggable).attr("data-animal");
                        let curlocationid = $(ui.draggable).attr("data-location");
                        let curunit = $(ui.draggable).attr("data-unit");
                        if (locationid == curlocationid && unit == curunit) { shelterview.reload(); return; } // Same location and unit, do nothing
                        let droptarget = $(this);
                        header.show_loading(_("Moving..."));
                        common.ajax_post("shelterview", "mode=moveunit&locationid=" + locationid + "&unit=" + encodeURIComponent(unit) + "&animalid=" + animalid)
                            .always(function() {
                                $.each(controller.animals, function(i, a) {
                                    if (a.ID == animalid) {
                                        a.SHELTERLOCATION = locationid;
                                        a.SHELTERLOCATIONUNIT = unit;
                                        return false;
                                    }
                                });
                                shelterview.reload();
                            });
                    }
                });
            }

        },

        /**
         * Renders a specialised shelter view that shows all fosterers with their
         * capacity and allows dragging/dropping between fosterers.
         * mode = 0: all fosterers are shown
         * mode = 1: only fosterers with at least one animal in their care shown
         * mode = 2: only fosterers with space are shown
         */
        render_foster_available: function(mode) {
            let h = [];
            $.each(controller.fosterers, function(ip, p) {
                // Output the fosterers
                let loclink = "person_movements?id=" + p.ID, fh = [], nofosters = 0, capacity = p.FOSTERCAPACITY, extraclasses = "";
                // Find any animals who are with this fosterer
                $.each(controller.animals, function(ia, a) {
                    // Skip animals not in this location
                    if (a.CURRENTOWNERID != p.ID) { return; }
                    nofosters += 1;
                    fh.push(shelterview.render_animal(a, true, a.ACTIVEMOVEMENTTYPE == 2));
                });
                if (!capacity) { capacity = 0; }
                if (nofosters < capacity) { extraclasses = "asm-shelterview-fosterer-available"; }
                if (nofosters == 0 && mode == 1) { return; }
                if (nofosters >= capacity && mode == 2) { return; }
                h.push('<p class="asm-menu-category"><a href="' + loclink + '">' + 
                    p.OWNERNAME + ' (' + nofosters + '/' + capacity + ')</a> ' +
                    '<span class="asm-search-personflags">' + edit_header.person_flags(p) + '</span>' + 
                    '</p>' +
                    '<div style="min-height: 110px" class="persondroptarget ' + extraclasses + '" data-person="' + p.ID + '">' +
                    fh.join("\n") +
                    '</div>');
            });

            // Load the whole thing into the DOM
            $("#viewcontainer").html(h.join("\n"));

            if (config.bool("ShelterViewDragDrop") && !common.browser_is.mobile) {
                $(".animaldragtarget").draggable();
                $(".persondroptarget").droppable({
                    over: function(event, ui) {
                        $(this).addClass("transparent");
                    },
                    out: function(event, ui) {
                        $(this).removeClass("transparent");
                    },
                    drop: function(event, ui) {
                        let personid = $(this).attr("data-person");
                        let animalid = $(ui.draggable).attr("data-animal");
                        let curpersonid = $(ui.draggable).attr("data-person");
                        if (curpersonid == personid) { shelterview.reload(); return; } // Same person, do nothing
                        let droptarget = $(this);
                        header.show_loading(_("Moving..."));
                        common.ajax_post("shelterview", "mode=movefoster&personid=" + personid + "&animalid=" + animalid)
                            .always(function() {
                                $.each(controller.animals, function(i, a) {
                                    if (a.ID == animalid) {
                                        a.CURRENTOWNERID = personid;
                                        return false;
                                    }
                                });
                                shelterview.reload();
                            });
                    }
                });
            }
        },

        /**
         * groupfield: The name of the field to group headings on with totals
         * sorton: Comma separated list of fields to sort on
         * dragdrop: Whether dragging and dropping is on and moves between locations
         * translategroup: Whether the group field needs to be translated
         * filterfunction: A function to call to decide whether or not to include an animal
         */
        render_view: function(groupfield, groupfield2, sorton, dragdrop, translategroup, filterfunction) {
            let h = [], lastgrp = "", lastgrp2 = "", grpdisplay = "", grplink = "", runningtotal = 0, i, 
                locationsused = [], showunit = (groupfield == "DISPLAYLOCATIONNAME");
            // Sort the rows for the view
            controller.animals.sort( common.sort_multi(sorton) );
            $.each(controller.animals, function(i, a) {
                // If a filter function was specified, call it and drop out
                // of this iteration if the return value was false
                if (filterfunction && !filterfunction(a)) { return; }
                // Change of group
                if (lastgrp != a[groupfield]) {
                    if (groupfield2 && lastgrp2 != "") { h.push("</div>"); }
                    if (lastgrp != "") { h.push("</div>"); }
                    // Find the last total token and update it
                    for (i = 0; i < h.length; i += 1) {
                        if (h[i].indexOf("##LASTTOTAL") != -1) {
                            h[i] = h[i].replace("##LASTTOTAL", runningtotal);
                        }
                    }
                    // Reset the counter for the new category and second group
                    runningtotal = 0;
                    lastgrp = a[groupfield];
                    lastgrp2 = "";
                    // Produce an appropriate link based on the group field
                    grplink = "#";
                    if (groupfield == "SHELTERLOCATIONNAME") {
                        grplink = "animal_find_results?logicallocation=onshelter&shelterlocation=" + a.SHELTERLOCATION;
                        locationsused.push(a.SHELTERLOCATION);
                    }
                    if (groupfield == "DISPLAYLOCATIONNAME") {
                        grplink = "animal_find_results?logicallocation=onshelter&shelterlocation=" + a.SHELTERLOCATION;
                        locationsused.push(a.SHELTERLOCATION);
                        if (a.ACTIVEMOVEMENTTYPE == 2) {
                            grplink = "move_book_foster";
                        }
                        if (a.ACTIVEMOVEMENTTYPE == 8) {
                            grplink = "move_book_retailer";
                        }
                        if (a.HASTRIALADOPTION == 1) {
                            grplink = "move_book_trial_adoption";
                        }
                    }
                    if (groupfield == "SPECIESNAME") {
                        grplink = "animal_find_results?logicallocation=onshelter&speciesid=" + a.SPECIESID;
                    }
                    if (groupfield == "ADOPTIONSTATUS") {
                        if (a.ADOPTIONSTATUS == _("Adoptable")) {
                            grplink = "animal_find_results?logicallocation=adoptable";
                        }
                        if (a.ADOPTIONSTATUS == _("Not For Adoption")) {
                            grplink = "animal_find_results?logicallocation=onshelter&flags=notforadoption";
                        }
                        if (a.ADOPTIONSTATUS == _("Reserved")) {
                            grplink = "move_book_reservation";
                        }
                        if (a.ADOPTIONSTATUS == _("Cruelty Case")) {
                            grplink = "animal_find_results?logicallocation=onshelter&flags=crueltycase";
                        }
                        if (a.ADOPTIONSTATUS == _("Hold")) {
                            grplink = "animal_find_results?logicallocation=hold";
                        }
                        if (a.ADOPTIONSTATUS == _("Quarantine")) {
                            grplink = "animal_find_results?logicallocation=onshelter&flags=quarantine";
                        }
                    }
                    if (groupfield == "CURRENTOWNERNAME" && a.CURRENTOWNERID) {
                        grplink = "person?id=" + a.CURRENTOWNERID;
                    }
                    // Does the name need translating?
                    grpdisplay = lastgrp;
                    if (translategroup) {
                        grpdisplay = _(grpdisplay);
                    }
                    h.push('<p class="asm-menu-category"><a href="' + grplink + '">' + 
                        grpdisplay + ' (##LASTTOTAL)</a></p>');
                    // Foster, trial adoptions and retailers can't be drop targets and drag/drop must be on for this view
                    if ((a.ACTIVEMOVEMENTTYPE != 2 && a.ACTIVEMOVEMENTTYPE != 8) && a.HASTRIALADOPTION == 0 && dragdrop) {
                        h.push('<div class="locationdroptarget" data-location="' + a.SHELTERLOCATION + '">');
                    }
                    else {
                        h.push('<div>');
                    }
                }
                // Change of second level group if set
                if (groupfield2 && lastgrp2 != a[groupfield2]) {
                    if (lastgrp2 != "") { h.push("</div>"); }
                    lastgrp2 = a[groupfield2];
                    h.push('<div class="asm-shelterview-unit">');
                    h.push('<div><span class="asm-shelterview-secondgroup">' + lastgrp2 + '</span></div>');
                }
                h.push(shelterview.render_animal(a, true, dragdrop));
                runningtotal += 1;
            });
            if (lastgrp != "") { 
                // Find the last total token and update it
                for (i = 0; i < h.length; i += 1) {
                    if (h[i].indexOf("##LASTTOTAL") != -1) {
                        h[i] = h[i].replace("##LASTTOTAL", runningtotal);
                    }
                }
                h.push("</div>"); 
            }
            // If we're sorting on location, find any locations that were unused
            // and output a section for them - unless they're retired
            if (config.bool("ShelterViewShowEmpty") && (groupfield == "DISPLAYLOCATIONNAME" || groupfield == "SHELTERLOCATIONNAME")) {
                $.each(controller.locations, function(i, v) {
                    if ($.inArray(v.ID, locationsused) == -1 && !v.ISRETIRED) {
                        let loclink = "animal_find_results?logicallocation=onshelter&shelterlocation=" + v.ID;
                        h.push('<p class="asm-menu-category"><a href="' + loclink + '">' + 
                            v.LOCATIONNAME + ' (0)</a></p>');
                        h.push('<div style="min-height: 70px" class="locationdroptarget" data="' + v.ID + '">');
                    }
                });
            }

            // Load the whole thing into the DOM
            $("#viewcontainer").html(h.join("\n"));

            // Handle drag and drop if enabled for this view
            if (dragdrop && config.bool("ShelterViewDragDrop") && !common.browser_is.mobile) {
                $(".animaldragtarget").draggable();
                $(".locationdroptarget").droppable({
                    over: function(event, ui) {
                        $(this).addClass("transparent");
                    },
                    out: function(event, ui) {
                        $(this).removeClass("transparent");
                    },
                    drop: function(event, ui) {
                        let locationid = $(this).attr("data-location");
                        let locationname = common.get_field(controller.locations, locationid, "LOCATIONNAME");
                        let animalid = $(ui.draggable).attr("data-animal");
                        let curlocationid = $(ui.draggable).attr("data-location");
                        if (locationid == curlocationid) { shelterview.reload(); return; } // Same location, do nothing
                        let droptarget = $(this);
                        header.show_loading(_("Moving..."));
                        common.ajax_post("shelterview", "mode=movelocation&locationid=" + locationid + "&animalid=" + animalid)
                            .always(function() {
                                header.hide_loading();
                                droptarget.removeClass("transparent");
                                $.each(controller.animals, function(i, a) {
                                    if (a.ID == animalid) {
                                        a.SHELTERLOCATION = locationid;
                                        a.SHELTERLOCATIONNAME = locationname;
                                        a.DISPLAYLOCATIONNAME = locationname;
                                        return false;
                                    }
                                });
                                shelterview.reload();
                            });
                    }
                });
            }

        },

        /** Returns a location object for the id given */
        location_for_id: function(id) {
            return common.get_row(controller.locations, id, "ID");
        },

        /** Returns a location object for the id given */
        location_name_for_id: function(id) {
            return common.get_row(controller.locations, id, "ID").LOCATIONNAME;
        },

        /** Returns the number of animals in location */
        location_animal_count: function(id) {
            let count = 0;
            $.each(controller.animals, function(ia, a) {
                if (a.ACTIVEMOVEMENTID == 0 && a.SHELTERLOCATION == id) {
                    count++;
                }
            });
            return count;
        },

        /** Returns true if location id has no animals in it */
        location_is_empty: function(id) {
            let empty = true;
            $.each(controller.animals, function(ia, a) {
                if (a.ACTIVEMOVEMENTID == 0 && a.SHELTERLOCATION == id) {
                    empty = false;
                    return false;
                }
            });
            return empty;
        },

        /** Returns the reserved and sponsor text for locationid and unitname */
        unit_values: function(locationid, unitname) {
            let sponsor = "", reserved = "";
            $.each(controller.unitextra.split("&&"), function(i, ux) {
                let v = ux.split("||");
                if (v[0] == locationid && v[1] == unitname) {
                    sponsor = v[2];
                    reserved = v[3];
                }
            });
            return [ sponsor, reserved ];
        },

        reload: function() {
            shelterview.switch_view($("#viewmode").select("value"));
        },

        switch_view: function(viewmode) {
            if (viewmode == "altered") {
                this.render_view("NEUTEREDSTATUS", "", "NEUTEREDSTATUS,ANIMALNAME", false, false);
            }
            else if (viewmode == "agegroup") {
                this.render_view("AGEGROUP", "", "AGEGROUP,ANIMALNAME", false, false);
            }
            else if (viewmode == "agegrouplitter") {
                this.render_view("AGEGROUP", "ACCEPTANCENUMBER", "AGEGROUP,ACCEPTANCENUMBER,ANIMALNAME", false, false);
            }
            else if (viewmode == "color") {
                this.render_view("BASECOLOURNAME", "", "BASECOLOURNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "coordinator") {
                this.render_view("ADOPTIONCOORDINATORNAME", "", "ADOPTIONCOORDINATORNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "coordinatorfosterer") {
                this.render_view("ADOPTIONCOORDINATORNAME", "CURRENTOWNERNAME", "ADOPTIONCOORDINATORNAME,CURRENTOWNERNAME,SPECIESNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "datebroughtin") {
                this.render_view("RECENTENTERED", "", "-RECENTENTERED,ANIMALNAME", false, false);
            }
            else if (viewmode == "entrycategory") {
                this.render_view("ENTRYREASONNAME", "", "ENTRYREASONNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "entrytype") {
                this.render_view("ENTRYTYPENAME", "ENTRYREASONNAME", "ENTRYTYPENAME,ENTRYREASONNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "flags") {
                this.render_flags();
            }
            else if (viewmode == "fosterer") {
                this.render_foster_available(0);
            }
            else if (viewmode == "fostereractive") {
                this.render_foster_available(1);
            }
            else if (viewmode == "fostererspace") {
                this.render_foster_available(2);
            }
            else if (viewmode == "goodwith") {
                this.render_goodwith();
            }
            else if (viewmode == "lastchanged") {
                this.render_view("RECENTCHANGED", "", "-RECENTCHANGED,ANIMALNAME", false, false);
            }
            else if (viewmode == "litter") {
                this.render_view("ACCEPTANCENUMBER", "", "ACCEPTANCENUMBER,SPECIESNAME,ANIMALNAME", false, false, function(a) { return a.ACCEPTANCENUMBER && a.ACCEPTANCENUMBER != ""; });
            }
            else if (viewmode == "location") {
                this.render_view("DISPLAYLOCATIONNAME", "", "DISPLAYLOCATIONNAME,ANIMALNAME", true, false);
            }
            else if (viewmode == "locationnv") {
                this.render_view("SHELTERLOCATIONNAME", "", "SHELTERLOCATIONNAME,ANIMALNAME", true, false);
            }
            else if (viewmode == "locationnvs") {
                this.render_view("SHELTERLOCATIONNAME", "SPECIESNAME", "SHELTERLOCATIONNAME,SPECIESNAME,ANIMALNAME", true, false);
            }
            else if (viewmode == "locationbreed") {
                this.render_view("DISPLAYLOCATIONNAME", "BREEDNAME", "DISPLAYLOCATIONNAME,BREEDNAME,ANIMALNAME", true, false);
            }
            else if (viewmode == "locationlitter") {
                this.render_view("DISPLAYLOCATIONNAME", "ACCEPTANCENUMBER", "DISPLAYLOCATIONNAME,ACCEPTANCENUMBER,ANIMALNAME", true, false);
            }
            else if (viewmode == "locationspecies") {
                this.render_view("DISPLAYLOCATIONNAME", "SPECIESNAME", "DISPLAYLOCATIONNAME,SPECIESNAME,ANIMALNAME", true, false);
            }
            else if (viewmode == "locationspeciesage") {
                this.render_view("DISPLAYLOCATIONNAME", "SPECIESNAME", "DISPLAYLOCATIONNAME,SPECIESNAME,-DATEOFBIRTH,ANIMALNAME", true, false);
            }
            else if (viewmode == "locationtype") {
                this.render_view("DISPLAYLOCATIONNAME", "ANIMALTYPENAME", "DISPLAYLOCATIONNAME,ANIMALTYPENAME,ANIMALNAME", true, false);
            }
            else if (viewmode == "locationunit") {
                this.render_units_available();
            }
            else if (viewmode == "name") {
                this.render_view("FIRSTLETTER", "", "FIRSTLETTER,ANIMALNAME", false, false);
            }
            else if (viewmode == "pickuplocation") {
                this.render_view("PICKUPLOCATIONNAME", "", "PICKUPLOCATIONNAME,ANIMALNAME", false, false, function(a) { return a.ISPICKUP == 1; });
            }
            else if (viewmode == "retailer") {
                this.render_view("CURRENTOWNERNAME", "", "CURRENTOWNERNAME,ANIMALNAME", false, false, function(a) { return a.ACTIVEMOVEMENTTYPE == 8; });
            }
            else if (viewmode == "sex") {
                this.render_view("SEXNAME", "", "SEXNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "sexspecies") {
                this.render_view("SEXNAME", "SPECIESNAME", "SEXNAME,SPECIESNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "site") {
                this.render_view("SITENAME", "DISPLAYLOCATIONNAME", "SITENAME,DISPLAYLOCATIONNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "sitefoster") {
                this.render_view("SITEFOSTER", "DISPLAYLOCATIONNAME", "SITEFOSTER,DISPLAYLOCATIONNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "species") {
                this.render_view("SPECIESNAME", "", "SPECIESNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "speciesbreed") {
                this.render_view("SPECIESNAME", "BREEDNAME", "SPECIESNAME,BREEDNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "speciescode") {
                this.render_view("SPECIESNAME", "", "SPECIESNAME,CODE", false, false);
            }
            else if (viewmode == "speciescolor") {
                this.render_view("SPECIESNAME", "BASECOLOURNAME", "SPECIESNAME,BASECOLOURNAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "status") {
                this.render_view("ADOPTIONSTATUS", "", "ADOPTIONSTATUS,ANIMALNAME", false, true);
            }
            else if (viewmode == "statuslocation") {
                this.render_view("ADOPTIONSTATUS", "DISPLAYLOCATIONNAME", "ADOPTIONSTATUS,DISPLAYLOCATIONNAME,ANIMALNAME", false, true);
            }
            else if (viewmode == "statusspecies") {
                this.render_view("ADOPTIONSTATUS", "SPECIESNAME", "ADOPTIONSTATUS,SPECIESNAME,ANIMALNAME", false, true);
            }
            else if (viewmode == "type") {
                this.render_view("ANIMALTYPENAME", "", "ANIMALTYPENAME,ANIMALNAME", false, false);
            }
            else if (viewmode == "unit") {
                this.render_view("SHELTERLOCATIONUNIT", "", "SHELTERLOCATIONUNIT,ANIMALNAME", false, false, function(a) { return a.SHELTERLOCATIONUNIT != ""; });
            }
            else if (viewmode == "unitspecies") {
                this.render_view("SHELTERLOCATIONUNIT", "SPECIESNAME", "SHELTERLOCATIONUNIT,SPECIESNAME,ANIMALNAME", false, false, function(a) { return a.SHELTERLOCATIONUNIT != ""; });
            }

            // Add target attributes to the rendered animal links if we're opening records in a new tab
            common.inject_target();
        },

        /** Adds the ADOPTIONSTATUS column */
        add_adoption_status: function() {
            $.each(controller.animals, function(i, a) {
                if (a.ARCHIVED == 0 && a.CRUELTYCASE == 1) { a.ADOPTIONSTATUS = _("Cruelty Case"); return; }
                if (a.ARCHIVED == 0 && a.ISQUARANTINE == 1) { a.ADOPTIONSTATUS = _("Quarantine"); return;  }
                if (a.ARCHIVED == 0 && a.ISHOLD == 1) { a.ADOPTIONSTATUS = _("Hold"); return; }
                if (a.ARCHIVED == 0 && a.HASACTIVERESERVE == 1) { a.ADOPTIONSTATUS = _("Reserved"); return; }
                if (a.ARCHIVED == 0 && a.HASPERMANENTFOSTER == 1) { a.ADOPTIONSTATUS = _("Permanent Foster"); return; }
                if (a.ARCHIVED == 0 && a.HASTRIALADOPTION == 1) { a.ADOPTIONSTATUS = _("Trial Adoption"); return; }
                if (html.is_animal_adoptable(a)[0]) { a.ADOPTIONSTATUS = _("Adoptable"); return; } 
                a.ADOPTIONSTATUS = _("Not For Adoption"); 
            });
        },

        /** Adds the FIRSTLETTER column */
        add_first_letter: function() {
            $.each(controller.animals, function(i, a) {
                if (!a.ANIMALNAME) { a.FIRSTLETTER = "0"; return; }
                a.FIRSTLETTER = html.decode(a.ANIMALNAME).substring(0, 1).toUpperCase();
            });
        },

        /** Adds the NEUTEREDSTATUS column */
        add_neutered_status: function() {
            $.each(controller.animals, function(i, a) {
                if (a.NEUTERED == 1) { a.NEUTEREDSTATUS = _("Altered"); return; }
                a.NEUTEREDSTATUS = _("Unaltered");
            });
        },

        /** Adds the SITEFOSTER column */
        add_site_foster: function() {
            $.each(controller.animals, function(i, a) {
                a.SITEFOSTER = a.SITENAME;
                // Copy the displaylocationname to use instead of site, eg Foster/Trial Adoption/Retailer/etc
                if (a.ARCHIVED == 0 && a.ACTIVEMOVEMENTTYPE) { a.SITEFOSTER = a.DISPLAYLOCATIONNAME; }
            });
        },

        /** Adds the RECENTCHANGED column */
        add_recent_changed: function() {
            $.each(controller.animals, function(i, a) {
                a.RECENTCHANGED = a.LASTCHANGEDDATE.substring(0, a.LASTCHANGEDDATE.indexOf("T"));
            });
        },

        /** Adds the RECENTENTERED column */
        add_recent_entered: function() {
            $.each(controller.animals, function(i, a) {
                a.RECENTENTERED = a.MOSTRECENTENTRYDATE.substring(0, a.MOSTRECENTENTRYDATE.indexOf("T"));
            });
        },

        render_unit_dialog: function() {
            return [
                '<div id="dialog-unit" style="display: none" title="">',
                '<input id="ud-location" type="hidden" value="" />',
                '<input id="ud-unit" type="hidden" value="" />',
                tableform.fields_render([
                    { post_field: "reserved", type: "text", label: _("Reserved For"), doublesize: true },
                    { post_field: "sponsor", type: "text", label: _("Sponsored By"), doublesize: true }
                ]),
                '</div>'
            ].join("\n");
        },

        bind_unit_dialog: function() {
            let unitbuttons = { };
            unitbuttons[_("Clear")] = {
                text: _("Clear"),
                "class": 'asm-redbutton',
                click: async function() {
                    $("#dialog-unit").disable_dialog_buttons();
                    try {
                        let formdata = {
                            "mode": "editunit",
                            "location": $("#ud-location").val(),
                            "unit": $("#ud-unit").val(),
                            "sponsor": "",
                            "reserved": ""
                        };
                        let response = await common.ajax_post("shelterview", formdata);
                        controller.unitextra = response;
                        shelterview.switch_view("locationunit");
                    }
                    finally {
                        $("#dialog-unit").dialog("close");
                        $("#dialog-unit").enable_dialog_buttons();
                    }
                }
            };
            unitbuttons[_("Save")] = {
                text: _("Save"),
                "class": 'asm-dialog-actionbutton',
                click: async function() {
                    $("#dialog-unit").disable_dialog_buttons();
                    try {
                        let formdata = {
                            "mode": "editunit",
                            "location": $("#ud-location").val(),
                            "unit": $("#ud-unit").val(),
                            "sponsor": $("#sponsor").val(),
                            "reserved": $("#reserved").val()
                        };
                        let response = await common.ajax_post("shelterview", formdata);
                        controller.unitextra = response;
                        shelterview.switch_view("locationunit");
                    }
                    finally {
                        $("#dialog-unit").dialog("close");
                        $("#dialog-unit").enable_dialog_buttons();
                    }
                }
            };
            unitbuttons[_("Cancel")] = function() {
                $("#dialog-unit").dialog("close");
            };
            $("#dialog-unit").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: unitbuttons
            });
        },

        render: function() {
            let h = [];
            h.push(shelterview.render_unit_dialog());
            h.push('<div id="asm-content" class="ui-helper-reset ui-widget-content ui-corner-all" style="padding: 10px;">');
            h.push('<select id="viewmode" style="float: right;" class="asm-selectbox">');
            h.push(html.shelter_view_options()); 
            h.push('</select>');
            h.push('<p class="asm-menu-category">' + config.str("Organisation") + ' (' + controller.animals.length + ')</p>');
            h.push('<div id="viewcontainer"></div>');
            h.push('</div>');
            return h.join("\n");
        },

        bind: function() {
            $("#viewmode").change(function(e) {
                shelterview.switch_view($("#viewmode").select("value"));
            });
            shelterview.bind_unit_dialog();
            $("#asm-content").on("click", ".asm-shelterview-unit-button", function() {
                let p = $(this).parent().parent();
                $("#ud-location").val( p.attr("data-location") );
                $("#ud-unit").val( p.attr("data-unit") );
                $("#sponsor, #reserved").val("");
                $.each(controller.unitextra.split("&&"), function(i, ux) {
                    let v = ux.split("||");
                    if (v[0] == p.attr("data-location") && v[1] == p.attr("data-unit")) {
                        $("#sponsor").val(v[2]);
                        $("#reserved").val(v[3]);
                    }
                });
                $("#dialog-unit").dialog("open");
                let title = shelterview.location_name_for_id(p.attr("data-location")) + "::" + p.attr("data-unit");
                $("#dialog-unit").parent().find(".ui-dialog-title").html(title);
            });
        },

        sync: function() {
            // Generate extra columns for sort/display
            shelterview.add_adoption_status();
            shelterview.add_first_letter();
            shelterview.add_neutered_status();
            shelterview.add_site_foster();
            shelterview.add_recent_changed();
            shelterview.add_recent_entered();
            // Clean up any null fields that we might want to group on later
            $.each(controller.animals, function(i, v) {
                if (!v.CURRENTOWNERNAME) {
                    v.CURRENTOWNERNAME = _("(none)");
                }
            });
            // Hide site modes if sites are off
            if (!config.bool("MultiSiteEnabled")) { 
                $("option[value='site'], option[value='sitefoster']").hide();
            }
            // Switch to the default view
            let dview = config.str(asm.user + "_ShelterView");
            if (!dview) { dview = config.str("ShelterViewDefault"); }
            $("#viewmode").select("value", dview);
            $("#viewmode").change();
        },

        destroy: function() {
            common.widget_destroy("#dialog-unit");
        },

        name: "shelterview",
        animation: "search",
        autofocus: "#asm-content a:first",
        title: function() { return _("Shelter view"); },

        routes: {
            "shelterview": function() {
                common.module_loadandstart("shelterview", "shelterview");
            }
        }

    };

    common.module_register(shelterview);

});
