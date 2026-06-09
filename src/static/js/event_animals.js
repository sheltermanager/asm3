/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function(){

    "use strict";

    const EVENT_ANIMAL_LINKTYPE = 32;

    const event_animals ={

        column_names: function() {
            let cols = [];
            $.each(config.str("EventAnimalViewColumns").split(","), function(i, v) {
                cols.push(common.trim(v));
            });
            return cols;
        },

        column_label: function(name) {
            let labels = {
                "ArrivalDate": _("Arrived"),
                "IMAGE": _("Image"),
                "ANIMAL": _("Animal"),
                "DISPLAYLOCATION": _("Location"),
                "AGEGROUP": _("Age Group"),
                "SPECIESNAME": _("Species"),
                "BASECOLOURNAME": _("Color"),
                "LITTERID": _("Litter"),
                "COMMENTS": _("Comments"),
                "LASTFOSTERER": _("Last Fosterer"),
                "ADOPTED": _("Adopted")
            };
            if (labels.hasOwnProperty(name)) {
                return labels[name];
            }
            if (controller.eventanimaladditional) {
                let addrow = common.get_row(controller.eventanimaladditional, name, "FIELDNAME");
                if (addrow) { return addrow.FIELDLABEL; }
            }
            return name;
        },

        sync_additional_values_from_row: function(row) {
            if (!controller.eventanimaladditionalvalues) {
                controller.eventanimaladditionalvalues = [];
            }
            $.each(controller.eventanimaladditional || [], function(i, f) {
                if (f.LINKTYPE != EVENT_ANIMAL_LINKTYPE) { return; }
                let val = row[f.FIELDNAME.toUpperCase()];
                if (val === undefined) { return; }
                let entry = null;
                $.each(controller.eventanimaladditionalvalues, function(j, v) {
                    if (v.LINKID == row.ID && v.FIELDNAME.toLowerCase() == f.FIELDNAME.toLowerCase()) {
                        entry = v;
                        return false;
                    }
                });
                if (!entry) {
                    entry = { LINKID: row.ID, FIELDNAME: f.FIELDNAME, FIELDTYPE: f.FIELDTYPE, VALUE: val, ANIMALNAME: "", OWNERNAME: "" };
                    controller.eventanimaladditionalvalues.push(entry);
                }
                else {
                    entry.VALUE = val;
                    entry.FIELDTYPE = f.FIELDTYPE;
                }
                let element = $("#add_" + f.ID);
                if (f.FIELDTYPE == additional.ANIMAL_LOOKUP && element.length) {
                    let a = element.animalchooser("get_selected");
                    if (a) { entry.ANIMALNAME = a.ANIMALNAME; }
                }
                else if (additional.is_person_type(f.FIELDTYPE) && element.length) {
                    let p = element.personchooser("get_selected");
                    if (p) { entry.OWNERNAME = p.OWNERNAME; }
                }
            });
        },

        format_additional_column: function(row, name) {
            let rv = "";
            if (!controller.eventanimaladditionalvalues) { return rv; }
            $.each(controller.eventanimaladditionalvalues, function(i, v) {
                if (v.LINKID == row.ID && v.FIELDNAME.toLowerCase() == name.toLowerCase()) {
                    if (v.FIELDTYPE == additional.YESNO) {
                        rv = v.VALUE == "1" ? _("Yes") : _("No");
                    }
                    else if (v.FIELDTYPE == additional.MONEY) {
                        rv = format.currency(v.VALUE);
                    }
                    else if (v.FIELDTYPE == additional.ANIMAL_LOOKUP) {
                        rv = '<a href="animal?id=' + v.VALUE + '">' + v.ANIMALNAME + '</a>';
                    }
                    else if (additional.is_person_type(v.FIELDTYPE)) {
                        rv = html.person_link(v.VALUE, v.OWNERNAME);
                    }
                    else {
                        rv = common.nulltostr(v.VALUE);
                    }
                    return false;
                }
            });
            return rv;
        },

        standard_columns: function() {
            return {
                "ArrivalDate": { field: "ArrivalDate", display: _("Arrived"),
                    formatter: function(row) {
                        let linktext = format.date(row.ARRIVALDATE);
                        if (linktext == "") {
                            linktext = _("(blank)");
                        }
                        else if (format.time(row.ARRIVALDATE) != "00:00:00") {
                            linktext += " " + format.time(row.ARRIVALDATE);
                        }
                        linktext = "<a href=\"#\" class=\"link-edit\" data-id=\"" + row.ID + "\">" + linktext + '</a>';
                        let chkbox = '<input type="checkbox" data-id="' + row.ID + '" title="' + _("Select") + '">';
                        return chkbox + linktext;
                    }
                },
                "IMAGE": { field: "IMAGE", display: "",
                    formatter: function(row) {
                        return html.animal_link_thumb_bare(row);
                    }
                },
                "ANIMAL": { field: "ANIMAL", display: _("Animal"),
                    formatter: function(row) {
                        return html.animal_link(row, { noemblems: controller.name == "event_animals" }) + "<br/>" + row.IDENTICHIPNUMBER;
                    },
                    hideif: function(row) {
                        if (controller.animal) { return true; }
                    }
                },
                "DISPLAYLOCATION": { field: "DISPLAYLOCATION", display: _("Location") },
                "AGEGROUP": { field: "AGEGROUP", display: _("Age Group") },
                "SPECIESNAME": { field: "SPECIESNAME", display: _("Species") },
                "BASECOLOURNAME": { field: "BASECOLOURNAME", display: _("Color") },
                "LITTERID": { field: "LITTERID", display: _("Litter") },
                "COMMENTS": { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments },
                "LASTFOSTERER": { field: "LASTFOSTERER", display: _("Last Fosterer"),
                    formatter: function(row) {
                        return '<span ' +
                                (row.LASTFOSTERERRETURNDATE ? 'class="asm-completerow"' : '') + ">" +
                                html.person_link(row.LASTFOSTERERID, row.LASTFOSTERERNAME) +
                                '<br/>' + common.nulltostr(row.LASTFOSTERERMOBILETELEPHONE) + '<br/>' + common.nulltostr(row.LASTFOSTERERHOMETELEPHONE) + '<br/>' + common.nulltostr(row.LASTFOSTERERWORKTELEPHONE) + '</span>';
                    }
                },
                "ADOPTED": { field: "ADOPTED", display: _("Adopted"),
                    formatter: function(row) {
                        return row.ADOPTED == 1 ? "&#9989;" : "&nbsp;";
                    }
                }
            };
        },

        build_columns: function() {
            let columns = [], standard = event_animals.standard_columns();
            $.each(event_animals.column_names(), function(i, name) {
                if (standard.hasOwnProperty(name)) {
                    columns.push(standard[name]);
                }
                else if (controller.eventanimaladditional && common.get_row(controller.eventanimaladditional, name, "FIELDNAME")) {
                    columns.push({
                        field: name,
                        display: event_animals.column_label(name),
                        formatter: function(row) {
                            return event_animals.format_additional_column(row, name);
                        }
                    });
                }
            });
            return columns;
        },

        model: function() {

            const dialog = {
                add_title: _("Add animal to event"),
                edit_title: _("Edit animal in event"),
                edit_perm: 'cea',
                close_on_ok: false,
                use_default_values: false,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal" },
                    { json_field: "ARRIVALDATE", post_field: "arrival", label: _("Arrived"), type: "datetime" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" },
                    { type: "additional", markup: additional.additional_fields_tableform(additional.merge_definitions_and_values(controller.eventanimaladditional || [], {}), -1, true, "additionaldialog")}
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row, {
                        onload: function() {
                            additional.additional_fields_populate_from_json(additional.merge_definitions_and_values(controller.eventanimaladditional || [], row));
                            tableform.fields_populate_from_json(dialog.fields, row);
                        },
                        onvalidate: function() {
                            return additional.validate_mandatory_dialog("additionaldialog");
                        },
                        onchange: async function() {
                            let afpost = additional.additional_fields_post(controller.eventanimaladditional || [], EVENT_ANIMAL_LINKTYPE);
                            tableform.fields_update_row(dialog.fields, row);
                            try {
                                await tableform.fields_post(dialog.fields, "mode=update&eventanimalid=" + row.ID + afpost, "event_animals");
                                additional.additional_fields_update_row(additional.merge_definitions_and_values(controller.eventanimaladditional || [], row), EVENT_ANIMAL_LINKTYPE, row);
                                event_animals.sync_additional_values_from_row(row);
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }
                            catch(err) {
                                log.error(err, err);
                                tableform.dialog_enable_buttons();
                            }
                        }
                    });
                },
                complete: function(row) {
                    if (row.ARRIVED) { return true; }
                    return false;
                },
                columns: event_animals.build_columns()
            };

            const buttons = [
                    { id: "addanimal", text: _("Add Animal"), icon: "animal-add", tooltip: _("Add animal to this event"), enabled: "always", perm: "cea",
                        click: async function() {
                            $("#addanimal").animalchooser("clear");
                            await tableform.show_okcancel_dialog("#dialog-addanimal", _("Add"), { notzero: [ "addanimal" ] });
                            let a = $("#addanimal").animalchooser("get_selected");
                            await common.ajax_post("event_animals", "mode=create&eventid=" + controller.event.ID + "&animalid=" + a.ID);
                            common.route_reload();
                        }
                    },
                    { id: "addanimals", text: _("Add from List"), icon: "litter", tooltip: _("Add animals to this event from animal list"), enabled: "always", perm: "cea",
                        click: async function() {
                            $("#addanimals").animalchoosermulti("clear");
                            await tableform.show_okcancel_dialog("#dialog-addanimals", _("Add"), { notzero: [ "addanimals" ] });
                            let animals = $("#addanimals").val();
                            await common.ajax_post("event_animals", "mode=createbulk&eventid=" + controller.event.ID + "&animals=" + animals);
                            common.route_reload();
                        }
                    },
                    { id: "removeanimal", text: _("Remove"), icon: "delete", tooltip: _(""), enabled: "multi", perm: "cea",
                        click: async function() {
                            await tableform.delete_dialog();
                            tableform.buttons_default_state(buttons);
                            let ids = tableform.table_ids(table);
                            await common.ajax_post("event_animals", "mode=delete&ids=" + ids);
                            tableform.table_remove_selected_from_json(table, controller.rows);
                            tableform.table_update(table);
                        }
                    },
                    { id: "animalarrived", text: _("Arrived"), icon: "complete", tooltip: _(""), enabled: "multi", perm: "cea",
                        click: async function() {
                            await tableform.show_okcancel_dialog("#dialog-arrived", _("Ok"));
                            tableform.buttons_default_state(buttons);
                            let ids = tableform.table_ids(table);
                            await common.ajax_post("event_animals", "mode=arrived&ids=" + ids);
                            $.each(controller.rows, function(i, v) {
                                if (tableform.table_id_selected(v.ID)) {
                                    if(!v.ARRIVALDATE) {
                                        v.ARRIVALDATE = format.date_now_iso();
                                    }
                                }
                            });
                            tableform.table_update(table);
                        }
                    },
                    { id: "animalendactivefoster", text: _("End active foster"), icon: "movement",
                        tooltip: _("Set current foster movement return date to event start or current time, whichever is later"),
                        enabled: "multi", perm: "cea",
                        click: async function() {
                            await tableform.show_okcancel_dialog("#dialog-endactivefoster", _("Ok"));
                            tableform.buttons_default_state(buttons);
                            let ids = tableform.table_ids(table);
                            await common.ajax_post("event_animals", "mode=endactivefoster&ids=" + ids);
                            $.each(controller.rows, function(i, v) {
                                if (tableform.table_id_selected(v.ID)) {
                                    if(!v.LASTFOSTERERRETURNDATE) {
                                        v.LASTFOSTERERRETURNDATE = format.date_now_iso();
                                    }
                                }
                            });
                            tableform.table_update(table);
                        }
                    },
                    { id: "filter", type: "dropdownfilter",
                        options: [ "all|" + _("All"), "arrived|" + _("Arrived"),
                        "noshow|" + _("No show"), "neednewfoster|" + _("Need new foster"),
                        "dontneednewfoster|" + _("Don't need new foster"),
                        "adopted|" + _("Adopted"),
                        "notadopted|" + _("Not adopted") ],
                        click: function(selval) {
                            common.route(controller.name + "?id=" + controller.event.ID + "&filter=" + selval);
                        }
                    },
                    { id: "refresh", text: _("Refresh"), icon: "refresh", enabled: "always", perm: "vea",
                        click: async function() {
                            event_animals.tablefilters = $("#tableform").table("save_filters");
                            common.route_reload();
                        }
                    }
                ];

            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render_arriveddialog: function() {
            return ['<div id="dialog-arrived" style="display: none" title="' + html.title(_("Arrival")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span>' + _("Update selected animals arrival time?") + '</p>  ',
                '</div>'].join("\n");
        },

        render_endactivefosterdialog: function() {
            return ['<div id="dialog-endactivefoster" style="display: none" title="' + html.title(_("End active foster")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span>' + _("Update selected animals foster return date?") + '</p>  ',
                '</div>'].join("\n");
        },

        render_addanimaldialog: function() {
            return ['<div id="dialog-addanimal" style="display: none" title="' + html.title(_("Add animal")) + '">',
                tableform.fields_render([
                    { post_field: "addanimal", type: "animal", label: _("Animal") }
                ]),
                '</div>'].join("\n");
        },

        render_addanimalsdialog: function() {
            return ['<div id="dialog-addanimals" style="display: none" title="' + html.title(_("Add animals")) + '">',
                tableform.fields_render([
                    { post_field: "addanimals", type: "animalmulti", label: _("Animals") }
                ]),
                '</div>'].join("\n");
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += event_animals.render_arriveddialog();
            s += event_animals.render_endactivefosterdialog();
            s += event_animals.render_addanimaldialog();
            s += event_animals.render_addanimalsdialog();
            s += edit_header.event_edit_header(controller.event, "animals", []);
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function(){
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        enable_widgets: function(){

        // SECURITY =============================================================
            if (!common.has_permission("cea")) { $("#button-addanimal").hide(); }
            if (!common.has_permission("cea")) { $("#button-addanimals").hide(); }
            if (!common.has_permission("cea")) { $("#button-removeanimal").hide(); }
            if (!common.has_permission("cea")) { $("#button-animalarrived").hide(); }
            if (!common.has_permission("cea")) { $("#button-animalendactivefoster").hide(); }

        },

        validation: function(){
            header.hide_error();
            validate.reset();
            if(common.trim($("#startdate").val()) == ""){
                header.show_error(_("Event must have a start date."));
                validate.highlight("startdate");
                validate.dirty(false);
                return false;
            }
            if (common.trim($("#enddate").val()) == ""){
                header.show_error(_("Event must have an end date."));
                validate.highlight("enddate");
                validate.dirty(false);
                return false;
            }
            if (common.trim($("#address").val()) == ""){
                header.show_error(_("Event must have an address."));
                validate.highlight("address");
                validate.dirty(false);
                return false;
            }
            // mandatory additional fields
            if (!additional.validate_mandatory()) { return false; }
            return true;
        },

        sync: function(){

            // Load the data into the controls for the screen
            if (common.querystring_param("filter")) {
                $("#filter").select("value", common.querystring_param("filter"));
            }

            // Update on-screen fields from the data and display the screen
            event_animals.enable_widgets();

            // Dirty handling
            validate.bind_dirty([ "eventanimal_" ]);

            // Reload filters if they were previously set
            $("#tableform").table("load_filters", event_animals.tablefilters);
        },

        destroy: function() {
            common.widget_destroy("#dialog-arrived");
            common.widget_destroy("#dialog-endactivefoster");
            common.widget_destroy("#dialog-addanimal");
            common.widget_destroy("#dialog-addanimals");
            common.widget_destroy("#addanimal", "animalchooser");
            common.widget_destroy("#addanimals", "animalchoosermulti");
            tableform.dialog_destroy();
        },

        name: "event_animals",
        animation: "formtab",
        autofocus: "#eventtype",

        title: function() {
            var e = controller.event;
            var dates_range = "";
            if(format.date(e.STARTDATETIME) == format.date(e.ENDDATETIME))
                    dates_range = format.date(e.STARTDATETIME);
                else
                    dates_range = format.date(e.STARTDATETIME) + " - " + format.date(e.ENDDATETIME);
            return dates_range + " " + e.EVENTNAME + " " + [e.EVENTADDRESS, e.EVENTTOWN, e.EVENTCOUNTY, e.EVENTCOUNTRY].filter(Boolean).join(", ");
        },

        routes: {
            "event_animals": function() { common.module_loadandstart("event_animals", "event_animals?" + this.rawqs); }
        }
    };

    common.module_register(event_animals);

});
