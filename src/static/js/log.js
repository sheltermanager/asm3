/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const log = {

        model: function() {
            const dialog = {
                add_title: _("Add log"),
                edit_title: _("Edit log"),
                edit_perm: 'cle',
                close_on_ok: false,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "LOGTYPEID", post_field: "type", label: _("Type"), type: "select", 
                        options: { displayfield: "LOGTYPENAME", valuefield: "ID", rows: controller.logtypes }},
                    { json_field: "DATE", post_field: "logdate", label: _("Date"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "DATE", post_field: "logtime", label: _("Time"), type: "time" },
                    { json_field: "COMMENTS", post_field: "entry", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    if (row.COMMENTS.indexOf("ES0") == 0) { return; } // Do not allow editing electronic signature related logs
                    tableform.fields_populate_from_json(dialog.fields, row);
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    log.set_extra_fields(row);
                    try {
                        await tableform.fields_post(dialog.fields, "mode=update&logid=" + row.ID, "log");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    finally {
                        tableform.dialog_enable_buttons();
                    }
                },
                columns: [
                    { field: "LOGTYPENAME", display: _("Type") },
                    { field: "LASTCHANGEDBY", display: _("By") },
                    { field: "DATE", display: _("Date"), formatter: tableform.format_datetime, initialsort: true, initialsortdirection: "desc" },
                    { field: "COMMENTS", display: _("Note"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Log"), icon: "new", enabled: "always", perm: "ale", 
                    click: async function() { 
                        await tableform.dialog_show_add(dialog, {
                            onload: function() {
                                $("#type").select("value", config.integer("AFDefaultLogType"));    
                                $("#logtime").val(format.time(new Date()));
                            },
                            onadd: async function() {
                                try {
                                    let formdata = "mode=create&linktypeid=" + controller.linktypeid + "&linkid=" + controller.linkid;
                                    let response = await tableform.fields_post(dialog.fields, formdata , "log");
                                    let row = {};
                                    row.ID = response;
                                    tableform.fields_update_row(dialog.fields, row);
                                    log.set_extra_fields(row);
                                    controller.rows.push(row);
                                    tableform.table_update(table);
                                    tableform.dialog_close();
                                }
                                finally {
                                    tableform.dialog_enable_buttons();   
                                }
                            }
                        });
                }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dle",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("log", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "filter", type: "dropdownfilter", 
                    options: '<option value="-1">' + _("(all)") + '</option>' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                    click: function(selval) {
                        common.route(controller.name + "?id=" + controller.linkid + "&filter=" + selval);
                    }
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        set_extra_fields: function(row) {
            row.LOGTYPENAME = common.get_field(controller.logtypes, row.LOGTYPEID, "LOGTYPENAME");
            row.LASTCHANGEDBY = asm.user;
        },

        render: function() {
            let h = [];
            this.model();
            h.push(tableform.dialog_render(this.dialog));
            if (controller.name == "animal_log") {
                h.push(edit_header.animal_edit_header(controller.animal, "logs", controller.tabcounts));
            }
            else if (controller.name == "person_log") {
                h.push(edit_header.person_edit_header(controller.person, "logs", controller.tabcounts));
            }
            else if (controller.name == "waitinglist_log") {
                h.push(edit_header.waitinglist_edit_header(controller.animal, "logs", controller.tabcounts));
            }
            else if (controller.name == "lostanimal_log") {
                h.push(edit_header.lostfound_edit_header("lost", controller.animal, "logs", controller.tabcounts));
            }
            else if (controller.name == "foundanimal_log") {
                h.push(edit_header.lostfound_edit_header("found", controller.animal, "logs", controller.tabcounts));
            }
            else if (controller.name == "incident_log") {
                h.push(edit_header.incident_edit_header(controller.incident, "logs", controller.tabcounts));
            }
            h.push(tableform.buttons_render(this.buttons));
            h.push(tableform.table_render(this.table));
            h.push(html.content_footer());
            return h.join("\n");
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            $("#filter").select("removeRetiredOptions", "all");
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        sync: function() {
            // If we have a filter, update the select
            if (controller.filter) {
                $("#filter").select("value", controller.filter);
            }
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "log",
        animation: "formtab",
        title:  function() { 
            let t = "";
            if (controller.name == "animal_log") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "foundanimal_log") { t = common.substitute(_("Found animal - {0} {1} [{2}]"), {
                0: controller.animal.AGEGROUP, 1: controller.animal.SPECIESNAME, 2: controller.animal.OWNERNAME});
            }
            else if (controller.name == "incident_log") { t = common.substitute(_("Incident {0}, {1}: {2}"), {
                0: controller.incident.ACID, 1: controller.incident.INCIDENTNAME, 2: format.date(controller.incident.INCIDENTDATETIME)});
            }
            else if (controller.name == "lostanimal_log") { t = common.substitute(_("Lost animal - {0} {1} [{2}]"), {
                0: controller.animal.AGEGROUP, 1: controller.animal.SPECIESNAME, 2: controller.animal.OWNERNAME});
            }
            else if (controller.name == "person_log") { t = controller.person.OWNERNAME; }
            else if (controller.name == "waitinglist_log") { t = common.substitute(_("Waiting list entry for {0} ({1})"), {
                0: controller.animal.OWNERNAME, 1: controller.animal.SPECIESNAME });
            }
            return t;
        },

        routes: {
            "animal_log": function() { common.module_loadandstart("log", "animal_log?" + this.rawqs); },
            "foundanimal_log": function() { common.module_loadandstart("log", "foundanimal_log?" + this.rawqs); },
            "incident_log": function() { common.module_loadandstart("log", "incident_log?" + this.rawqs); },
            "lostanimal_log": function() { common.module_loadandstart("log", "lostanimal_log?" + this.rawqs); },
            "person_log": function() { common.module_loadandstart("log", "person_log?" + this.rawqs); },
            "waitinglist_log": function() { common.module_loadandstart("log", "waitinglist_log?" + this.rawqs); }
        }


    };
    
    common.module_register(log);

});
