/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const boarding = {

        model: function() {
            const dialog = {
                add_title: _("Add Boarding"),
                edit_title: _("Edit Boarding"),
                helper_text: "",
                close_on_ok: false,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal", validation: "notzero" },
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
                    { json_field: "INDATETIME", post_field: "indatetime", label: _("In Date"), type: "datetime", validation: "notblank", defaultval: new Date() },
                    { json_field: "OUTDATETIME", post_field: "outdatetime", label: _("Out Date"), type: "datetime", validation: "notblank", defaultval: new Date() },
                    { json_field: "DAILYFEE", post_field: "dailyfee", label: _("Daily Fee"), type: "currency" },
                    { json_field: "SHELTERLOCATION", post_field: "location", label: _("Location"), type: "select", 
                        options: { displayfield: "LOCATIONNAME", valuefield: "ID", rows: controller.internallocations }},
                    { json_field: "SHELTERLOCATIONUNIT", post_field: "unit", label: _("Unit"), type: "select" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    tableform.dialog_show_edit(dialog, row, {
                        onchange: async function() {
                            try {
                                tableform.fields_update_row(dialog.fields, row);
                                await tableform.fields_post(dialog.fields, "mode=update&boardingid=" + row.ID, "boarding");
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }
                            catch(err) {
                                log.error(err, err);
                                tableform.dialog_error(response);
                                tableform.dialog_enable_buttons();
                            }
                        },
                        onload: function(row) {
                            boarding.location_change(); // load units for the selected location
                            $("#unit").val( row.SHELTERLOCATIONUNIT );
                        }
                    });
                },
                complete: function(row) {
                    if (format.date_js(row.OUTDATETIME) < common.today_no_time()) { return true; }
                    return false;
                },
                overdue: function(row) {
                    //return !row.DATECOMPLETED && format.date_js(row.DIARYDATETIME) < common.today_no_time();
                },
                columns: [
                    { field: "ID", display: _("Number") },
                    { field: "INDATETIME", display: _("Check In"), formatter: tableform.format_datetime, initialsort: true, initialsortdirection: "desc" },
                    { field: "OUTDATETIME", display: _("Check Out"), formatter: tableform.format_datetime },
                    { field: "PERSON", display: _("Person"),
                        formatter: function(row) {
                            if (row.OWNERID) {
                                return html.person_link(row.OWNERID, row.OWNERNAME);
                            }
                            return "";
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("person_") != -1;
                        }
                    },
                    { field: "ANIMAL", display: _("Animal"), 
                        formatter: function(row) {
                            if (!row.ANIMALID || row.ANIMALID == 0) { return ""; }
                            let s = html.animal_link(row);
                            return s;
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("animal_") != -1;
                        }
                    },
                    { field: "SHELTERLOCATION", display: _("Location"), 
                        formatter: function(row) {
                            return row.SHELTERLOCATIONNAME + ' <span class="asm-search-locationunit">' + row.SHELTERLOCATIONUNIT + '</span>';
                        }},
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Boarding"), icon: "new", enabled: "always", perm: "abi", click: function() { 
                    boarding.new_boarding();
                }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dbi", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("boarding", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "filter", type: "dropdownfilter", 
                    options: [ "active|" + _("Active boarders"),
                        "m90|" + _("Recent boarders"),
                        "p90|" + _("Future boarders")
                        ],
                    hideif: function() {
                        return controller.name == "animal_boarding" || controller.name == "person_boarding";
                    },
                    click: function(selval) {
                        common.route(controller.name + "?filter=" + selval);
                    }
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        location_change: function() {
            let units = common.get_field(controller.internallocations, $("#location").val(), "UNITS");
            if (units && units.indexOf(",") != -1) {
                $("#unit").html( html.list_to_options(units.split(",")) );
            }
        },

        set_extra_fields: function(row) {
            // TODO: set SHELTERLOCATIONNAME
        },

        render: function() {
            let h = [];
            this.model();
            h.push(tableform.dialog_render(this.dialog));
            if (controller.name == "animal_boarding") {
                h.push(edit_header.animal_edit_header(controller.animal, "boarding", controller.tabcounts));
            }
            else if (controller.name == "person_boarding") {
                h.push(edit_header.person_edit_header(controller.person, "boarding", controller.tabcounts));
            }
            else if (controller.name == "boarding") {
                h.push(html.content_header(_("Boarding Book")));
            }
            h.push(tableform.buttons_render(this.buttons));
            h.push(tableform.table_render(this.table));
            h.push(html.content_footer());
            return h.join("\n");
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            $("#location").change(this.location_change);
        },

        sync: function() {
            // If a filter is given in the querystring, update the select
            if (common.current_url().indexOf("filter=") != -1) {
                let filterurl = common.current_url().substring(common.current_url().indexOf("filter=")+7);
                $("#filter").select("value", filterurl);
            }

            if (controller.newboarding) {
                boarding.new_boarding();
            }
        },

        new_boarding: function() {
            tableform.dialog_show_add(boarding.dialog, {
                onadd: async function() {
                    let response = await tableform.fields_post(boarding.dialog.fields, "mode=create", "boarding");
                    let row = {};
                    row.ID = response;
                    tableform.fields_update_row(boarding.dialog.fields, row);
                    boarding.set_extra_fields(row);
                    controller.rows.push(row);
                    tableform.table_update(boarding.table);
                    tableform.dialog_close();
                },
                onload: function() {
                    tableform.dialog_enable_buttons();
                    boarding.location_change();
                }
            });
        },

        destroy: function() {
            tableform.dialog_destroy();
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "boarding",
        animation: function() { return controller.name.indexOf("boarding") == 0 ? "book" : "formtab"; },
        title:  function() { 
            let t = "";
            if (controller.name == "animal_boarding") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "person_boarding") { t = controller.person.OWNERNAME; }
            else { t = _("Boarding Book"); }
            return t;
        },

        routes: {
            "animal_boarding": function() { common.module_loadandstart("boarding", "animal_boarding?id=" + this.qs.id); },
            "person_boarding": function() { common.module_loadandstart("boarding", "person_boarding?id=" + this.qs.id); },
            "boarding": function() { common.module_loadandstart("boarding", "boarding?" + this.rawqs); }
        }

    };

    common.module_register(boarding);

});
