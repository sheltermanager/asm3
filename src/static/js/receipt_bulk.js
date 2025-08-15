/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const receipt_bulk = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                overdue: function(row) {
                    if (!row.EMAILADDRESS) {return true;}
                },
                columns: [
                    { field: "DATE", display: _("Date"), formatter: function(row) {
                            if (row.EMAILADDRESS) {
                                return tableform.table_render_edit_link(row.ID, '&nbsp;', format.date(row.DATE));
                            } else {
                                return '<input type=checkbox style="visibility: hidden;">&nbsp;' + format.date(row.DATE);
                            }
                        }
                    },
                    { field: "TYPE", display: _("Type"), formatter: function(row) {
                            return row.PAYMENTNAME;
                        }
                    },
                    { field: "OWNERNAME", display: _("Person"), formatter: function(row) {
                        return row.OWNERNAME;
                    } },
                    { field: "DONATION", display: _("Amount"), formatter: function(row) {
                        return format.currency(row.DONATION);
                    } },
                    { field: "COMMENTS", display: _("Comments") }
                ]
            };

            const buttons = [
                { id: "refresh", text: _("Refresh"), icon: "refresh", enabled: "always", 
                    click: function() {
                        common.route("receipt_bulk?fromdate=" + $("#fromdate").val() + "&todate=" + $("#todate").val() + "&paymentmethod=" + $("#paymentmethod").val() + "&templateid=" + $("#paymenttemplate").val());
                    }
                },
                { id: "send", text: _("Send"), icon: "email", enabled: "multi", 
                    click: async function() {
                        $("#button-send").button('disable');
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("receipt_bulk", "mode=send&ids=" + ids + "&tid=" + $("#paymenttemplate").val() + "&username=" + asm.user);
                        $("#button-send").button('enable');
                        header.show_info(_('Receipts emailed'));
                    } 
                }
            ];

            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += html.content_header(_("Email bulk receipts"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.fields_render([
                { id: "fromdate", type: "date", label: _("From"), halfsize: true, value: format.date(controller.fromdate) },
                { id: "todate", type: "date", label: _("To"), halfsize: true, value: format.date(controller.todate) },
                { id: "paymentmethod", type: "selectmulti", label: _("Method"), 
                    options: { displayfield: "PAYMENTNAME", valuefield: "ID", rows: controller.paymentmethods } },
                { id: "paymenttemplate", type: "select", label: _("Template"), 
                    options: { displayfield: "NAME", valuefield: "ID", rows: controller.templates } }
            ], { full_width: false });
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        sync: function() {
            $("#paymentmethod").val(controller.paymentmethod);
            $("#paymentmethod").change();
            if (controller.template > 0) {
                $("#paymenttemplate").val(controller.template);
                $("#paymenttemplate").change();
            }

        },

        destroy: function() {
        },

        name: "receipt_bulk",
        animation: "book",
        title: function() { return _("Email bulk receipts"); },
        routes: {
            "receipt_bulk": function() { common.module_loadandstart("receipt_bulk", "receipt_bulk?" + this.rawqs); }
        }
    };
    
    common.module_register(receipt_bulk);

});
