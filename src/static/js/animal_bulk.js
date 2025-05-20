/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {
    
    "use strict";

    const animal_bulk = {
        render_details: function() {
            return [
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "litterid", label: _("Litter"), type: "autotext",
                        options: { rows: controller.autolitters, displayfield: "label", valuefield: "value" }},
                    { post_field: "animaltype", label: _("Type"), type: "select", 
                        options: animal_bulk.options(controller.animaltypes, "ID", "ANIMALTYPE") },
                    { post_field: "location", label: _("Location"), type: "select", 
                        options: animal_bulk.options(controller.internallocations, "ID", "LOCATIONNAME") },
                    { post_field: "unit", label: _("Unit"), type: "select", options: "" },
                    { post_field: "entryreason", label: _("Entry Category"), type: "select", 
                        options: animal_bulk.options(controller.entryreasons, "ID", "REASONNAME") },
                    { post_field: "holduntil", label: _("Hold until"), type: "date" },
                    { post_field: "fee", label: _("Adoption Fee"), type: "currency" },
                    { post_field: "boardingcost", label: _("Daily Boarding Cost"), type: "currency" },
                    { post_field: "addflag", label: _("Add Flag"), type: "select", 
                        options: animal_bulk.options(controller.flags, "FLAG", "FLAG", 2) },
                    { post_field: "removeflag", label: _("Remove Flag"), type: "select", 
                        options: animal_bulk.options(controller.flags, "FLAG", "FLAG", 2) },
                    { post_field: "notforadoption", label: _("Not For Adoption"), type: "select", 
                        options: '<option value="-1">' + _("(no change)") + '</option>' +
                            '<option value="0">' + _("Adoptable") + '</option>' +
                            '<option value="1">' + _("Not For Adoption") + '</option>' },
                    { post_field: "notforregistration", label: _("Do Not Register Microchip"), type: "select", 
                        options: '<option value="-1">' + _("(no change)") + '</option>' +
                            '<option value="0">' + _("Register Microchip") + '</option>' +
                            '<option value="1">' + _("Do Not Register Microchip") + '</option>' }
                ], { full_width: false }),
                '</div>' // end accordion section
            ].join("\n");
        }, 
        render_notes: function() {
            return [
                '<h3><a href="#">' + _("Notes") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "goodwithcats", label: _("Good with cats"), type: "select", rowclasses: "goodwith",
                        options: animal_bulk.options(controller.ynun, "ID", "NAME") },
                    { post_field: "goodwithdogs", label: _("Good with dogs"), type: "select", rowclasses: "goodwith",
                        options: animal_bulk.options(controller.ynun, "ID", "NAME") },
                    { post_field: "goodwithkids", label: _("Good with kids"), type: "select", rowclasses: "goodwith",
                        options: animal_bulk.options(controller.ynunk, "ID", "NAME") },
                    { post_field: "goodwithelderly", label: _("Good with elderly"), type: "select", rowclasses: "goodwith",
                        options: animal_bulk.options(controller.ynun, "ID", "NAME") },
                    { post_field: "goodtraveller", label: _("Good traveller"), type: "select", rowclasses: "goodwith",
                        options: animal_bulk.options(controller.ynun, "ID", "NAME") },
                    { post_field: "goodonlead", label: _("Good on lead"), type: "select", rowclasses: "goodwith",
                        options: animal_bulk.options(controller.ynun, "ID", "NAME") },
                    { post_field: "housetrained", label: _("Housetrained"), type: "select", rowclasses: "goodwith",
                        options: animal_bulk.options(controller.ynun, "ID", "NAME") },
                    { post_field: "cratetrained", label: _("Crate trained"), type: "select", rowclasses: "goodwith",
                        options: animal_bulk.options(controller.ynun, "ID", "NAME") },
                    { post_field: "energylevel", json_field: "ENERGYLEVEL", label: _("Energy level"), type: "select", 
                        rowclasses: "goodwith dogs", options: html.list_to_options([
                            "-1|" + _("(no change)"),
                            "1|" + _("1 - Very low"),
                            "2|" + _("2 - Low"),
                            "3|" + _("3 - Medium"),
                            "4|" + _("4 - High"),
                            "5|" + _("5 - Very high") ]) }
                ], { full_width: false }),
                '</div>' // end accordion section
            ].join("\n");
        }, 
        render_healthandid: function() {
            return [
                '<h3><a href="#">' + _("Health and Identification") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "neutereddate", label: _("Altered"), type: "date" },
                    { post_field: "neuteringvet", label: _("By"), type: "person", personfilter: "vet", colclasses: "bottomborder" },
                    { post_field: "coordinator", label: _("Adoption Coordinator"), type: "person", personfilter: "coordinator", colclasses: "bottomborder" },
                    { post_field: "currentvet", label: _("Current Vet"), type: "person", personfilter: "vet", colclasses: "bottomborder" },
                    { post_field: "ownersvet", label: _("Owners Vet"), type: "person", personfilter: "vet" }
                ], { full_width: false }),
                '</div>' // end accordion section
            ].join("\n");
        }, 
        render_diary: function() {
            return [
                '<h3><a href="#">' + _("Diary") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "diaryfor", label: _("Add Diary"), type: "select", halfsize: true, 
                        options: animal_bulk.options(controller.forlist, "USERNAME", "USERNAME", 3),
                        xmarkup: [ " ", _("on"), 
                            tableform.render_date({ post_field: "diarydate", halfsize: true, justwidget: true}),
                            tableform.render_time({ post_field: "diarytime", halfsize: true, justwidget: true }) 
                            ].join("\n")
                    },
                    { post_field: "diarysubject", label: _("Subject"), type: "text" },
                    { post_field: "diarynotes", label: _(""), labelpos: "above", type: "textarea", colclasses: "bottomborder" }
                ], { full_width: false }),
                '</div>' // end accordion section
            ].join("\n");
        }, 
        render_log: function() {
            return [
                '<h3><a href="#">' + _("Log") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "logtype", label: _("Add Log"), type: "select", halfsize: true, 
                        options: animal_bulk.options(controller.logtypes, "ID", "LOGTYPENAME", 3),
                        xmarkup: [ " ", _("on"), 
                            tableform.render_date({ post_field: "logdate", halfsize: true, justwidget: true}),
                            ].join("\n")
                    },
                    { post_field: "lognotes", label: _(""), labelpos: "above", type: "textarea", colclasses: "bottomborder" }
                ], { full_width: false }),
                '</div>' // end accordion section
            ].join("\n");
        }, 
        render_movement: function() {
            let choosetypes = [];
            $.each(controller.movementtypes, function(i, v) {
                if (v.ID == 8 && !config.bool("DisableRetailer")) {
                    choosetypes.push(v);
                }
                else if (v.ID == 0) {
                    v.MOVEMENTTYPE = _("Reservation");
                    choosetypes.push(v);
                }
                else if (v.ID !=8 && v.ID != 9 && v.ID != 10 && v.ID != 11 && v.ID != 12) {
                    choosetypes.push(v);
                }
            });
            return [
                '<h3><a href="#">' + _("Movements") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "movementtype", label: _("Add Movement"), type: "select", halfsize: true, 
                        options: animal_bulk.options(choosetypes, "ID", "MOVEMENTTYPE", 3),
                        xmarkup: [ " ", _("on"), 
                            tableform.render_date({ post_field: "movementdate", halfsize: true, justwidget: true}),
                            ].join("\n")
                    },
                    { post_field: "moveto", label: _("to"), type: "person" },
                ], { full_width: false }),
                '</div>' // end accordion section
            ].join("\n");
        }, 
        render_additional: function() {
            return [
                '<h3><a href="#">' + _("Additional") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "updateadditional", type: "check", label: _("Update additional fields") },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 0) },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 2) },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 3) },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 4) },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 5) },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 6) }
                ], { full_width: false }),
                '</div>' // end accordion section
            ].join("\n");
        }, 
        render: function() {
            return [
                html.content_header(_("Bulk change animals")),
                tableform.buttons_render([
                    { id: "update", icon: "save", text: _("Update")  }, 
                    { id: "delete", icon: "delete", text: _("Delete") }, 
                    { type: "raw", markup: '<label for="animals">' + _("Animals") + '</label><div style="display: inline-block; vertical-align: middle; width: 400px;"><input type="hidden" class="asm-field asm-animalchoosermulti" id="animals" data-post="animals"></div>' }, 
                 ], { centered: false }),
                 '<div id="asm-details-accordion">',
                 animal_bulk.render_details(), 
                 animal_bulk.render_notes(), 
                 animal_bulk.render_healthandid(), 
                 animal_bulk.render_diary(), 
                 animal_bulk.render_log(), 
                 animal_bulk.render_movement(), 
                 animal_bulk.render_additional(), 
                 '</div>',
                 html.content_footer()
            ].join("\n");
        }, 

        bind: function() {
            $("#asm-details-accordion").accordion({
                heightStyle: "content"
            });
            validate.indicator([ "animals" ]);
            
            $("#button-update").button().click(async function() {
                if (!validate.notblank([ "animals" ])) { return; }
                $("#button-update").button("disable");
                header.show_loading(_("Updating..."));
                let formdata = "mode=update&" + $("input, select, textarea").toPOST();
                try {
                    let response = await common.ajax_post("animal_bulk", formdata);
                    header.hide_loading();
                    header.show_info(_("{0} animals successfully updated.").replace("{0}", response));
                }
                finally {
                    $("#button-update").button("enable");
                }
            });

            $("#button-delete").button().click(async function() {
                if (!validate.notblank([ "animals" ])) { return; }
                try {
                    await tableform.delete_dialog(null, _("This will permanently remove the selected animals, are you sure?"));
                    $("#button-delete").button("disable");
                    header.show_loading(_("Deleting..."));
                    let formdata = "mode=delete&" + $("input, select, textarea").toPOST();
                    let response = await common.ajax_post("animal_bulk", formdata);
                    header.hide_loading();
                    header.show_info(_("{0} animals successfully deleted.").replace("{0}", response));
                    $("#animals").animalchoosermulti("clear");
                }
                finally {
                    $("#button-delete").button("enable");
                }
            });

            $("#location").change(animal_bulk.update_units);
            animal_bulk.update_units();

            if (!common.has_permission("ca")) { $("#button-update").hide(); }
            if (!common.has_permission("da")) { $("#button-delete").hide(); }

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            // Remove any fields that were disabled in the options
            if (config.bool("DontShowLitterID")) { $("#litteridrow").hide(); }
            if (config.bool("DontShowAdoptionFee")) { $("#feerow").hide(); }
            if (config.bool("DontShowLocationUnit")) { $("#unitrow").hide(); }
            if (config.bool("DontShowNeutered")) { $("#neutereddaterow, #neuteringvetrow").hide(); }
            if (config.bool("DontShowAdoptionCoordinator")) { $("#coordinatorrow").hide(); }
            if (config.bool("DontShowGoodWith")) { $(".goodwith").hide(); }
            if (config.bool("DisableMovements")) { $("#movementtyperow, #movetorow").hide(); }

            // Remove sections that add records if the user doesn't have permissions
            if (!common.has_permission("aamv")) { $("#movementtyperow, #movetorow").hide(); }
            if (!common.has_permission("adn")) { $("#diaryforrow, #diarysubjectrow, #diarynotesrow").hide(); }
            if (!common.has_permission("ale")) { $("#logtyperow, #lognotesrow").hide(); }

            $("#updateadditional").change(animal_bulk.updateadditional_change);
            animal_bulk.updateadditional_change();

        },

        updateadditional_change: function() {
            if ($("#updateadditional").prop("checked")) {
                $(".additional").closest("tr").show();
            }
            else {
                $(".additional").closest("tr").hide();
            }
        },

        /**
         * Wrapper for html.list_to_options
         * if firstval is undefined or 1, include a "no change" option at the top
         * if firstval == 2, show a blank value at the top
         * if firstval == 3, show a blank but with a value of -1
         */
        options: function(rows, idcol, displaycol, firstval) {
            const nochange = '<option value="-1">' + _("(no change)") + '</option>';
            const blankrow = '<option value=""></option>';
            const mrow = '<option value="-1"></option>';
            let s = "";
            if (firstval === undefined || firstval == 1) { s += nochange; }
            if (firstval == 2) { s += blankrow; }
            if (firstval == 3) { s += mrow; }
            s += html.list_to_options(rows, idcol, displaycol);
            return s;
        },

        // Update the units available for the selected location
        update_units: async function() {
            let opts = ['<option value="-1">' + _("(no change)") + '</option>'];
            if ($("#location").val() != -1) {
                $("#unit").empty();
                const response = await common.ajax_post("animal_new", "mode=units&locationid=" + $("#location").val());
                $.each(html.decode(response).split("&&"), function(i, v) {
                    let [unit, desc] = v.split("|");
                    if (!unit) { return false; }
                    if (!desc) { desc = _("(available)"); }
                    opts.push('<option value="' + html.title(unit) + '">' + unit +
                        ' : ' + desc + '</option>');
                });
            }
            $("#unit").html(opts.join("\n")).change();
        },

        destroy: function() {
            common.widget_destroy("#animals");
            common.widget_destroy("#coordinator", "personchooser");
            common.widget_destroy("#currentvet", "personchooser");
            common.widget_destroy("#ownersvet", "personchooser");
            common.widget_destroy("#moveto", "personchooser");
        },

        name: "animal_bulk",
        animation: "newdata",
        autofocus: "#litterid", 
        title: function() { return _("Bulk change animals"); },

        routes: {
            "animal_bulk": function() {
                common.module_loadandstart("animal_bulk", "animal_bulk");
            }
        }


    };

    common.module_register(animal_bulk);

});
