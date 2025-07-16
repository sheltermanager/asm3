/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const receipt_bulk = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                columns: [
                    { field: "ID", display: _("ID"), formatter: function(row) {
                        return row.ID;
                    }  },
                    { field: "DATE", display: _("Date"), formatter: function(row) {
                        return format.date(row.DATE);
                    }  },
                    { field: "OWNERNAME", display: _("Person"), formatter: function(row) {
                        return row.OWNERNAME;
                    } },
                    { field: "DONATION", display: _("Amount") },
                    { field: "COMMENTS", display: _("Comments") }
                ]
            };

            const buttons = [];

            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
                
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
        },

        destroy: function() {
        },

        name: "receipt_bulk",
        animation: "book",
        title: _("Bulk receipts"),
        routes: {
            "receipt_bulk": function() { common.module_loadandstart("receipt_bulk", "receipt_bulk?" + this.rawqs); }
        }

    };
    
    common.module_register(receipt_bulk);

});
