/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const stock_movement = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                columns: [
                    { field: "ID", display: _("ID"), formatter: function(row) {
                        return row.ID;
                    }  },
                    { field: "USAGEDATE", display: _("Date"), formatter: function(row) {
                        return format.date(row.USAGEDATE);
                    }  },
                    { field: "PRODUCTNAME", display: _("Product"), formatter: function(row) {
                        if (!row.PRODUCTID) {
                            return row.PRODUCTNAME;
                        } else {
                            return row.PRODUCTNAME + ' <a href="product?id=' + row.PRODUCTID + '">' + html.icon("product", _("View product")) + '</a>';
                        }
                    } },
                    { field: "QUANTITY", display: _("Quantity") },
                    { field: "UNIT", display: _("Unit") },
                    { field: "FROMNAME", display: _("From") },
                    { field: "TONAME", display: _("To") },
                    { field: "COMMENTS", display: _("Comments") }
                ]
            };

            const buttons = [
                { id: "productmovementfilter", type: "dropdownfilter", 
                    options: '<option value="0">' + _("Today") + '</option>' + 
                        '<option value="7">' + _("Last Week") + '</option>' +
                        '<option value="30">' + _("Last Month") + '</option>' +
                        '<option value="91">' + _("Last Quarter") + '</option>' +
                        '<option value="182">' + _("Last 6 Months") + '</option>' +
                        '<option value="365">' + _("Last Year") + '</option>',
                    click: function(selval) {
                        common.route("stock_movement?productid=" + controller.productid + "&offset=" + selval);
                    }
                }
            ];

            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            
            if (controller.productid != 0) {
                s += html.content_header(_("{0} Movements").replace("{0}", controller.productname));
            } else if (controller.stocklevelid != 0) {
                s += html.content_header(_("{0} Movements").replace("{0}", controller.stocklevelname));
            } else {
                s += html.content_header(_("All Stock Movements"));
            }
                
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
            // If an offset is given in the querystring, update the select
            if (common.querystring_param("stocklevelid")) {
                $("#productmovementfilter").fadeOut();
            }
            if (common.querystring_param("offset")) {
                $("#productmovementfilter").select("value", common.querystring_param("offset"));
            }
        },

        destroy: function() {
        },

        name: "stock_movement",
        animation: "book",
        title: function() {
            if (controller.productid != 0) {
                return _("{0} Movements").replace("{0}", controller.productname);
            } else if (controller.stocklevelid != 0) {
                return _("{0} Movements").replace("{0}", controller.stocklevelname);
            } else {
               return _("All Stock Movements");
            }

            /*if (controller.productid != 0) {
                return _("{0} Movements").replace("{0}", controller.productname);
            } else {
                return _("Stock movement");
            }*/
        },
        routes: {
            "stock_movement": function() { common.module_loadandstart("stock_movement", "stock_movement?" + this.rawqs); }
        }

    };
    
    common.module_register(stock_movement);

});
