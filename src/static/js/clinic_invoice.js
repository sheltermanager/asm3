/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    var clinic_invoice = {

        model: function() {
            var dialog = {
                add_title: _("Add Invoice Item"),
                edit_title: _("Edit Invoice Item"),
                edit_perm: 'ccl',
                helper_text: _("Invoice items need a description and amount."),
                close_on_ok: false,
                fields: [
                    { json_field: "DESCRIPTION", post_field: "description", label: _("Description"), type: "textarea", validation: "notblank" },
                    { json_field: "AMOUNT", post_field: "amount", label: _("Amount"), type: "currency", validation: "notzero" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    tableform.dialog_show_edit(dialog, row)
                            .then(function() {
                                tableform.fields_update_row(dialog.fields, row);
                                return tableform.fields_post(dialog.fields, "mode=update&appointmentid=" + controller.appointmentid + "&itemid=" + row.ID, "clinic_invoice");
                            })
                            .then(function(response) {
                                tableform.table_update(table);
                                tableform.dialog_close();
                            })
                            .always(function() {
                                tableform.dialog_enable_buttons();
                            });
                },
                columns: [
                    { field: "DESCRIPTION", display: _("Description") },
                    { field: "AMOUNT", display: _("Amount"), formatter: tableform.format_currency }
                ]
            };

            var buttons = [
                { id: "new", text: _("New Item"), icon: "new", enabled: "always", perm: "acl", click: function() { 
                    tableform.dialog_show_add(dialog)
                        .then(function() {
                            return tableform.fields_post(dialog.fields, "mode=create&appointmentid=" + controller.appointmentid, "clinic_invoice");
                        })
                        .then(function(response) {
                            var row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
                            controller.rows.push(row);
                            tableform.table_update(table);
                            tableform.dialog_close();
                        })
                        .always(function() {
                            tableform.dialog_enable_buttons();   
                        });
                }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dcl",
                     click: function() { 
                         tableform.delete_dialog()
                             .then(function() {
                                 tableform.buttons_default_state(buttons);
                                 var ids = tableform.table_ids(table);
                                 return common.ajax_post("clinic_invoice", "mode=delete&ids=" + ids);
                             })
                             .then(function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                             });
                     } 
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            var h = [];
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
