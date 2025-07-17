/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const receipt_bulk = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                columns: [
                    { field: "DATE", display: _("Date"), formatter: function(row) {
                        //return format.date(row.DATE);
                        return tableform.table_render_edit_link(row.ID, format.date(row.DATE), '')
                    }  },
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
                { type: "raw",  markup: tableform.render_select({
                        'id': 'paymenttemplate',
                        'justwidget': true,
                        'options': { displayfield: "NAME", valuefield: "ID", rows: controller.templates }
                    })
                },
                { type: "raw", markup: '<div style="display: inline-block;vertical-align: top;">' + tableform.render_selectmulti({
                        'id': 'paymentmethod',
                        'justwidget': true,
                        'options': { displayfield: "PAYMENTNAME", valuefield: "ID", rows: controller.paymentmethods }
                    }) + '</div>'
                },
                { id: "complete", text: _("Complete"), icon: "complete", enabled: "multi", 
                    click: async function() { 
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("diary", "mode=complete&ids=" + ids);
                        $.each(controller.rows, function(i, v) {
                        if (tableform.table_id_selected(v.ID)) {
                            v.DATECOMPLETED = format.date_iso(new Date());
                        }
                        });
                        tableform.table_update(table);
                    } 
                },
                { type: "raw", markup: '<span style="float: right;">' + _("from") + ' '},
                { type: "raw", markup: tableform.render_date({'id': "fromdate",'justwidget': true, 'halfsize': true, value: format.date(controller.fromdate)}) },
                { type: "raw", markup: ' ' + _('to') + ' ' },
                { id: "todate", type: "raw", markup: tableform.render_date({'id': "todate",'justwidget': true, 'halfsize': true, value: format.date(controller.todate)}) + '</span>' },
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

            $("#fromdate").change(function() {
                common.route("receipt_bulk?fromdate=" + $("#fromdate").val() + "&todate=" + $("#todate").val());
            });

            $("#todate").change(function() {
                common.route("receipt_bulk?fromdate=" + $("#fromdate").val() + "&todate=" + $("#todate").val());
            });
        },

        sync: function() {
        },

        destroy: function() {
        },

        name: "receipt_bulk",
        animation: "book",
        title: function() {return _("Bulk receipts")},
        routes: {
            "receipt_bulk": function() { common.module_loadandstart("receipt_bulk", "receipt_bulk?" + this.rawqs); }
        }
    };
    
    common.module_register(receipt_bulk);

});
