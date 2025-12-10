/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const regular_debits = {

        model: function() {
            const dialog = {
                add_title: _("Add regular debit"),
                edit_title: _("Edit regular debit"),
                edit_perm: 'cac',
                close_on_ok: false,
                hide_read_only: true,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "STARTDATE", post_field: "startdate", label: _("Active from"), type: "date", validation: "notblank" },
                    { json_field: "ENDATE", post_field: "enddate", label: _("Active to"), type: "date" },
                    { json_field: "PERIOD", post_field: "period", label: _("Period"), type: "select",
                        options: [
                            "1|Daily",
                            "7|Weekly",
                            "30|Monthly",
                            "365|Yearly"
                        ]
                    },

                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    tableform.dialog_show_edit(dialog, row, {
                        onchange: async function() {
                            
                        },
                        onload: function() {

                        }
                    });
                },
                columns: [
                    { field: "STARTDATE", display: _("Active from"), formatter: tableform.format_date },
                    { field: "ENDDATE", display: _("Active to"), formatter: tableform.format_date },
                ]
            };

            const buttons = [
               { id: "new", text: _("New Regular Debit"), icon: "new", enabled: "always", perm: "aac",
                    click: async function() { 
                        await tableform.dialog_show_add(dialog);
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "regular_debits");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }  
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dac",
                    click: async function() { 
                        await tableform.delete_dialog(null, _("This will permanently remove this regular debit, are you sure you want to do this?"));
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("regular_debits", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            this.model();
            let s = "";
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Regular debits"));
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

        sync: function() {
            
        },

        destroy: function() {
        },

        name: "regular_debits",
        animation: "book",
        title: function() { return _("Regular debits"); },
        routes: {
            "regular_debits": function() { common.module_loadandstart("regular_debits", "filter?" + this.rawqs); }
        }

    };
    
    common.module_register(regular_debits);

});
