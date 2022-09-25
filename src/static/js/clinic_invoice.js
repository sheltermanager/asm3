/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const clinic_invoice = {

        model: function() {
            const dialog = {
                add_title: _("Add Invoice Item"),
                edit_title: _("Edit Invoice Item"),
                edit_perm: 'ccl',
                close_on_ok: false,
                fields: [
                    { json_field: "DESCRIPTION", post_field: "description", label: _("Description"), type: "textarea", validation: "notblank" },
                    { json_field: "AMOUNT", post_field: "amount", label: _("Amount"), type: "currency", validation: "notzero" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    try {
                        tableform.fields_populate_from_json(dialog.fields, row);
                        await tableform.dialog_show_edit(dialog, row);
                        tableform.fields_update_row(dialog.fields, row);
                        await tableform.fields_post(dialog.fields, "mode=update&appointmentid=" + controller.appointmentid + "&itemid=" + row.ID, "clinic_invoice");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    finally {
                        tableform.dialog_enable_buttons();
                    }
                },
                columns: [
                    { field: "DESCRIPTION", display: _("Description") },
                    { field: "AMOUNT", display: _("Amount"), formatter: tableform.format_currency }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Item"), icon: "new", enabled: "always", perm: "acl", 
                    click: async function() { 
                        try {
                            await tableform.dialog_show_add(dialog);
                            let response = await tableform.fields_post(dialog.fields, "mode=create&appointmentid=" + controller.appointmentid, "clinic_invoice");
                            var row = {};
                            row.ID = response;
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
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dcl",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        var ids = tableform.table_ids(table);
                        await common.ajax_post("clinic_invoice", "mode=delete&ids=" + ids);
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
            let h = [];
            this.model();
            h.push(tableform.dialog_render(this.dialog));
            h.push(html.content_header(this.title()));
            h.push(html.info(_("Appointment {0}. {1} on {2} for {3}")
                .replace("{0}", format.padleft(controller.appointment.ID, 6))
                .replace("{1}", controller.appointment.OWNERNAME != null ? controller.appointment.OWNERNAME : _("Shelter"))
                .replace("{2}", format.date(controller.appointment.DATETIME) + " " + format.time(controller.appointment.DATETIME))
                .replace("{3}", controller.appointment.ANIMALNAME)
                ));
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
        },

        sync: function() {
        },

        validation: function() {
            if (!validate.notzero(["amount"])) { return false; }
            if (!validate.notblank([ "description" ])) { return false; }
            return true;
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "clinic_invoice",
        animation: "book",
        title:  function() { 
            return _("Clinic Invoice - {0}").replace("{0}", controller.appointment.OWNERNAME);
        },

        routes: {
            "clinic_invoice": function() { common.module_loadandstart("clinic_invoice", "clinic_invoice?" + this.rawqs); }
        }

    };
    
    common.module_register(clinic_invoice);

});
