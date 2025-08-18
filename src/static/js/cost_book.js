/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const cost_book = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                overdue: function(row) {
                    if (!row.EMAILADDRESS) {return true;}
                },
                columns: [
                    { field: "COSTTYPENAME", display: _("Type") },
                    { field: "COSTDATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
                    { field: "COSTAMOUNT", display: _("Cost"), formatter: tableform.format_currency },
                    { field: "COSTPAIDDATE", display: _("Paid"), formatter: tableform.format_date,
                        hideif: function() { return !config.bool("ShowCostPaid"); }
                    },
                    { field: "INVOICENUMBER", display: _("Invoice Number") },
                    { field: "OWNERNAME", display: _("Payee"),
                        formatter: function(row) {
                            if (row.OWNERID) {
                                return html.person_link(row.OWNERID, row.OWNERNAME);
                            }
                            return "";
                        }
                    },
                    { field: "DESCRIPTION", display: _("Description"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "refresh", text: _("Refresh"), icon: "refresh", enabled: "always", 
                    click: function() {
                        common.route("cost_book");
                    }
                },
                { id: "offset", type: "dropdownfilter", 
                    options: [ 
                        "7|" + _("Paid in last week"),
                        "31|" + _("Paid in last month"),
                        "0|" + _("Unpaid costs") ],
                    click: function(selval) {
                        common.route("cost_book" + "?offset=" + selval);
                    },
                }
            ];

            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += html.content_header(_("Cost book"));
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

        name: "cost_book",
        animation: "book",
        title: function() { return _("Cost book"); },
        routes: {
            "cost_book": function() { common.module_loadandstart("cost_book", "cost_book?" + this.rawqs); }
        }
    };
    
    common.module_register(cost_book);

});
