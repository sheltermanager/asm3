/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const diarytask = {

        model: function() {
            const dialog = {
                add_title: _("Add diary task"),
                edit_title: _("Edit diary task"),
                edit_perm: 'edt',
                helper_text: _("Diary task items need a pivot, subject and note."),
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "ORDERINDEX", post_field: "orderindex", label: _("Index"), type: "number",
                        callout: _("Task items are executed in order of index, lowest to highest"), validation: "notblank" },
                    { json_field: "DAYPIVOT", post_field: "pivot", label: _("Day Pivot"), type: "number", 
                        callout: _("Create note this many days from today, or 9999 to ask"), validation: "notblank" },
                    { json_field: "WHOFOR", post_field: "for", label: _("For"), type: "select", 
                        options: { rows: controller.forlist, displayfield: "USERNAME", valuefield: "USERNAME", prepend: ('<option value="taskcreator">' + _("(task creator)") + '</option>') }},
                    { json_field: "SUBJECT", label: _("Subject"), post_field: "subject", validation: "notblank", type: "text" },
                    { json_field: "NOTE", label: _("Note"), post_field: "note", validation: "notblank", type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    await tableform.fields_post(dialog.fields, "mode=update&diarytaskdetailid=" + row.ID, "diarytask");
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                columns: [
                    { field: "WHOFOR", display: _("For"), formatter: function(row) {
                        let whofor = row.WHOFOR;
                        if ( whofor == 'taskcreator') {
                            whofor = _("(task creator)");
                        }
                        return tableform.table_render_edit_link(row.ID, whofor);
                    } },
                    { field: "ORDERINDEX", display: _("Index"), initialsort: true },
                    { field: "DAYPIVOT", display: _("Day Pivot") },
                    { field: "SUBJECT", display: _("Subject") },
                    { field: "NOTE", display: _("Note") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New task detail"), icon: "new", enabled: "always", 
                    click: async function() { 
                        await tableform.dialog_show_add(dialog);
                        let response = await tableform.fields_post(dialog.fields, "mode=create&taskid=" + controller.taskid, "diarytask");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("diarytask", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Diary Task: {0}").replace("{0}", controller.taskname));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "diarytask",
        animation: "formtab",
        title: function() { return _("Diary Task: {0}").replace("{0}", controller.taskname); },
        
        routes: {
            "diarytask": function() { 
                common.module_loadandstart("diarytask", "diarytask?taskid=" + this.qs.taskid);
            }
        }

    };

    common.module_register(diarytask);

});
