/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var person_vouchers = {

        model: function() {
            var dialog = {
                add_title: _("Add voucher"),
                edit_title: _("Edit voucher"),
                edit_perm: 'vcov',
                helper_text: _("Vouchers need an issue and expiry date."),
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "VOUCHERID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "VOUCHERNAME", valuefield: "ID", rows: controller.vouchertypes }},
                    { json_field: "DATEISSUED", post_field: "issued", label: _("Issued"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "DATEEXPIRED", post_field: "expires", label: _("Expires"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "VALUE", post_field: "amount", label: _("Amount"), type: "currency" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row, function() {
                        tableform.fields_update_row(dialog.fields, row);
                        row.VOUCHERNAME = common.get_field(controller.vouchertypes, row.VOUCHERID, "VOUCHERNAME");
                        tableform.fields_post(dialog.fields, "mode=update&voucherid=" + row.ID, "person_vouchers", function(response) {
                            tableform.table_update(table);
                            tableform.dialog_close();
                        });
                    });
                },
                complete: function(row) {
                    if (row.DATEEXPIRED != null && format.date_js(row.DATEEXPIRED) <= new Date()) {
                        return true;
                    }
                },
                columns: [
                    { field: "VOUCHERNAME", display: _("Type") },
                    { field: "ID", display: _("Number"), formatter: function(row) { return format.padleft(row.ID, 6); }},
                    { field: "DATEISSUED", display: _("Issued"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
                    { field: "DATEEXPIRED", display: _("Expires"), formatter: tableform.format_date },
                    { field: "VALUE", display: _("Amount"), formatter: tableform.format_currency },
                    { field: "COMMENTS", display: _("Comments") }
                ]
            };

            var buttons = [
                 { id: "new", text: _("New Voucher"), icon: "new", enabled: "always", perm: "vaov", 
                     click: function() { 
                         tableform.dialog_show_add(dialog, function() {
                             tableform.fields_post(dialog.fields, "mode=create&personid=" + controller.person.ID, "person_vouchers", function(response) {
                                 var row = {};
                                 row.ID = response;
                                 tableform.fields_update_row(dialog.fields, row);
                                 row.VOUCHERNAME = common.get_field(controller.vouchertypes, row.VOUCHERID, "VOUCHERNAME");
                                 controller.rows.push(row);
                                 tableform.table_update(table);
                                 tableform.dialog_close();
                             });
                         }, function() { person_vouchers.vouchertype_change(); });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "vdov", 
                     click: function() { 
                         tableform.delete_dialog(function() {
                             tableform.buttons_default_state(buttons);
                             var ids = tableform.table_ids(table);
                             common.ajax_post("person_vouchers", "mode=delete&ids=" + ids , function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                             });
                         });
                     } 
                 }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render: function() {
            var s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += edit_header.person_edit_header(controller.person, "vouchers", controller.tabcounts);
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            $("#type").change(person_vouchers.vouchertype_change);
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        vouchertype_change: function() {
            var dc = common.get_field(controller.vouchertypes, $("#type").select("value"), "DEFAULTCOST");
            $("#amount").currency("value", dc);
        },

        name: "person_vouchers",
        animation: "formtab",
        title: function() { return controller.person.OWNERNAME; },
        routes: {
            "person_vouchers": function() { common.module_loadandstart("person_vouchers", "person_vouchers?id=" + this.qs.id); }
        }

    };

    common.module_register(person_vouchers);

});
