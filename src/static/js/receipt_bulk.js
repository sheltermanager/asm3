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
                { type: "raw", markup: '<center>'},
                { type: "raw",  markup: tableform.render_select({
                        'id': 'paymenttemplate',
                        'justwidget': true,
                        'options': { displayfield: "NAME", valuefield: "ID", rows: controller.templates },
                        'tooltip': _("Template")
                    })
                },
                { type: "raw", markup: _("from") + ' '},
                { type: "raw", markup: tableform.render_date({'id': "fromdate",'justwidget': true, 'halfsize': true, value: format.date(controller.fromdate), tooltip: _("From date")}) },
                { type: "raw", markup: ' ' + _('to') + ' ' },
                { id: "todate", type: "raw", markup: tableform.render_date({'id': "todate",'justwidget': true, 'halfsize': true, value: format.date(controller.todate), tooltip: _("To date")}) },
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
                        setTimeout(() => { header.show_info(_('Receipts emailed')); }, 850);
                    } 
                },
                { type: "raw", markup: '<br>'},
                { type: "raw", markup: '<div style="display: inline-block;vertical-align: top;">' + tableform.render_selectmulti({
                        'id': 'paymentmethod',
                        'justwidget': true,
                        'options': { displayfield: "PAYMENTNAME", valuefield: "ID", rows: controller.paymentmethods },
                        tooltip: _("Payment methods")
                    }) + '</div>'
                },
                { type: "raw", markup: '</center>'}
            ];

            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += html.content_header(_("Bulk receipts"));
            s += tableform.buttons_render(this.buttons);
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
        title: function() {return _("Bulk receipts");},
        routes: {
            "receipt_bulk": function() { common.module_loadandstart("receipt_bulk", "receipt_bulk?" + this.rawqs); }
        }
    };
    
    common.module_register(receipt_bulk);

});
