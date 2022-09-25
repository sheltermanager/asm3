/*global $, _, asm, common, config, controller, dlgfx, format, edit_header, html, tableform, validate */

$(function() {

    "use strict";

    const person_investigation = {

        model: function() {
            const dialog = {
                add_title: _("Add investigation"),
                edit_title: _("Edit investigation"),
                edit_perm: 'coi',
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "DATE", post_field: "date", label: _("Date"), type: "date", validation: "notblank" },
                    { json_field: "NOTES", post_field: "notes", label: _("Notes"), type: "textarea", validation: "notblank" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    try {
                        await tableform.dialog_show_edit(dialog, row);
                        tableform.fields_update_row(dialog.fields, row);
                        await tableform.fields_post(dialog.fields, "mode=update&investigationid=" + row.ID, "person_investigation");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err);
                        tableform.dialog_enable_buttons();
                    }
                },
                columns: [
                    { field: "CREATEDBY", display: _("By") },
                    { field: "DATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date }, 
                    { field: "NOTES", display: _("Notes"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New"), icon: "new", enabled: "always", perm: "aoi",
                    click: async function() { 
                        await tableform.dialog_show_add(dialog);
                        try {
                            let response = await tableform.fields_post(dialog.fields, "mode=create&personid="  + controller.person.ID, "person_investigation");
                            let row = {};
                            row.ID = response;
                            row.CREATEDBY = asm.user;
                            tableform.fields_update_row(dialog.fields, row);
                            controller.rows.push(row);
                            tableform.table_update(table);
                            tableform.dialog_close();
                        }
                        finally {
                            tableform.dialog_enable_buttons();
                        }
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "doi",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("person_investigation", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;

        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += edit_header.person_edit_header(controller.person, "investigation", controller.tabcounts);
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += '</div> <!-- asmcontent -->';
            s += '</div> <!-- tabs -->';
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "person_investigation",
        animation: "formtab",
        title: function() { return controller.person.OWNERNAME; },
        routes: {
            "person_investigation": function() { common.module_loadandstart("person_investigation", "person_investigation?id=" + this.qs.id); }
        }

    };

    common.module_register(person_investigation);

});
