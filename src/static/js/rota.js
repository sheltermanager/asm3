/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const rota = {

        model: function() {
            const dialog = {
                add_title: _("Add rota item"),
                edit_title: _("Edit rota item"),
                edit_perm: 'coro',
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "OWNERID", post_field: "person", personmode: "brief", personfilter: "volunteerandstaff", 
                        label: _("Person"), type: "person", validation: "notzero" },
                    { json_field: "ROTATYPEID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "ROTATYPE", valuefield: "ID", rows: controller.rotatypes }},
                    { json_field: "WORKTYPEID", post_field: "worktype", label: _("Work"), type: "select", options: { displayfield: "WORKTYPE", valuefield: "ID", rows: controller.worktypes }},
                    { json_field: "STARTDATETIME", post_field: "startdate", label: _("Starts"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "STARTDATETIME", post_field: "starttime", label: _("at"), type: "time", validation: "notblank", defaultval: config.str("DefaultShiftStart") },
                    { json_field: "ENDDATETIME", post_field: "enddate", label: _("Ends"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "ENDDATETIME", post_field: "endtime", label: _("at"), type: "time", validation: "notblank", defaultval: config.str("DefaultShiftEnd") },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row, { onload: function() { rota.type_change(); }} );
                    tableform.fields_update_row(dialog.fields, row);
                    row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                    row.ROTATYPENAME = common.get_field(controller.rotatypes, row.ROTATYPEID, "ROTATYPE");
                    row.WORKTYPENAME = common.get_field(controller.worktypes, row.WORKTYPEID, "WORKTYPE");
                    await tableform.fields_post(dialog.fields, "mode=update&rotaid=" + row.ID, controller.name);
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                columns: [
                    { field: "ROTATYPENAME", display: _("Type") },
                    { field: "WORKTYPENAME", display: _("Work"), 
                        formatter: function(row) { 
                            if (row.ROTATYPEID <= 10) { return row.WORKTYPENAME; }
                            return "";
                        }
                    },
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
                    { field: "STARTDATETIME", display: _("Start Time"), formatter: tableform.format_datetime, initialsort: true, initialsortdirection: "desc" },
                    { field: "ENDDATETIME", display: _("End Time"), formatter: tableform.format_datetime },
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New"), icon: "new", enabled: "always", perm: "aoro",
                    click: async function() { 
                        $("#person").personchooser("clear");
                        if (controller.person) {
                            $("#person").personchooser("loadbyid", controller.person.ID);
                        }
                        await tableform.dialog_show_add(dialog, { onload: function() { rota.type_change(); }} );
                        let response = await tableform.fields_post(dialog.fields, "mode=create", controller.name);
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                        row.ROTATYPENAME = common.get_field(controller.rotatypes, row.ROTATYPEID, "ROTATYPE");
                        row.WORKTYPENAME = common.get_field(controller.worktypes, row.WORKTYPEID, "WORKTYPE");
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "doro",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post(controller.name, "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                     } 
                 }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;

        },

        type_change: function() {
            $("#worktyperow").toggle(format.to_int($("#type").val()) <= 10);
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            if (controller.name.indexOf("person_rota") == 0) {
                s += edit_header.person_edit_header(controller.person, "rota", controller.tabcounts);
            }
            else {
                s += html.content_header(controller.title);
            }
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            $("#startdate").change(function() {
                $("#enddate").val($("#startdate").val());
            });

            $("#type").change(rota.type_change);

        },

        destroy: function() {
            common.widget_destroy("#person");
            tableform.dialog_destroy();
        },

        name: "rota",
        animation: "formtab",
        title: function() {
            if (controller.name == "person_rota") {
                return controller.person.OWNERNAME;
            }
        },
        routes: {
            "person_rota": function() { common.module_loadandstart("rota", "person_rota?id=" + this.qs.id); }
        }

    };

    common.module_register(rota);

});
