/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function(){

    "use strict";

    const event_animals ={

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
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    try {
                        await tableform.fields_post(dialog.fields, "mode=update&eventanimalid=" + row.ID, "event_animals");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err);
                        tableform.dialog_enable_buttons();
                    }
                },
                complete: function(row) {
                    if (row.ARRIVED) { return true; }
                    return false;
                },
                columns: [
                    { field: "ArrivalDate", display: _("Arrived") ,
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
                    { field: "IMAGE", display: "", 
                        formatter: function(row) {
                            return html.animal_link_thumb_bare(row);
                        }
                    },
                    { field: "ANIMAL", display: _("Animal"), 
                        formatter: function(row) {
                            return html.animal_link(row, { noemblems: controller.name == "event_animals" });
                        },
                        hideif: function(row) {
                            // Don't show for animal records
                            if (controller.animal) { return true; }
                        }
                    },
                    { field: "DISPLAYLOCATION", display: _("Location")
                    },
                    { field: "AGEGROUP", display: _("Age Group")
                    },
                    { field: "SPECIESNAME", display: _("Species")
                    },
                    { field: "BASECOLOURNAME", display: _("Color")
                    },

                    { field: "LITTERID", display: _("Litter"),
                    },
                    { field: "COMMENTS", display: _("Comments")
                    },
                    { field: "LASTFOSTERER", display: _("Last Fosterer"),
                        formatter: function(row) {
                            return '<span ' +
                                    (row.LASTFOSTERERRETURNDATE ? 'class="asm-completerow"' : '') + ">" + 
                                    html.person_link(row.LASTFOSTERERID, row.LASTFOSTERERNAME) + 
                                    '<br/>' + common.nulltostr(row.LASTFOSTERERMOBILETELEPHONE) + '<br/>' + common.nulltostr(row.LASTFOSTERERHOMETELEPHONE) + '<br/>' + common.nulltostr(row.LASTFOSTERERWORKTELEPHONE) + '</span>';
                        }
                    },
                    { field: "ADOPTED", display: _("Adopted"),
                        formatter: function(row) {  
                            return row.ADOPTED == 1 ? "&#9989;" : "&nbsp;";
                        }
                    }
                ]
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
                    { id: "animalendactivefoster", text: _("End active foster"), tooltip: _("Set current foster movement return date to event start or current time, whichever is later"), enabled: "multi", perm: "cea",
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
                        //TODO: refresh list - get request doesn't get all arguments (filter specifically, until reload)
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
                '<table width="100%">',
                '<tr>',
                '<td><label for="addanimal">' + _("Animal") + '</label></td>',
                '<td><input id="addanimal" data="addanimal" type="hidden" class="asm-animalchooser" /></td>',
                '</tr>',
                '</table>',
                '</div>'].join("\n");
        },

        render_addanimalsdialog: function() {
            return ['<div id="dialog-addanimals" style="display: none" title="' + html.title(_("Add animals")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="addanimals">' + _("Animals") + '</label></td>',
                '<td><input id="addanimals" data="addanimals" type="hidden" class="asm-animalchoosermulti" /></td>',
                '</tr>',
                '</table>',
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

             $(".asm-tabbar").asmtabs();
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
