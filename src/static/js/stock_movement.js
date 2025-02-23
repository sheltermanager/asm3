/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const stock_movement = {

        model: function() {
            const dialog = {
                add_title: _("Add product movement"),
                edit_title: _("Edit product movement"),
                edit_perm: 'vsl',
                close_on_ok: false,
                hide_read_only: true,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "PRODUCTNAME", post_field: "productname", label: _("Name"), type: "text", validation: "notblank" },
                    { json_field: "PRODUCTTYPE", post_field: "producttype", label: _("Product type"), type: "select", options: controller.producttypes, validation: "notnull" },
                    { json_field: "BARCODE", post_field: "barcode", label: _("Barcode"), type: "text" },
                    { json_field: "PLU", post_field: "plu", label: _("PLU"), type: "text" },
                    { json_field: "DESCRIPTION", post_field: "productdescription", label: _("Description"), type: "textarea" },
                    { json_field: "TAXRATE", post_field: "taxrate", label: _("Tax Rate"), type: "select", options: controller.taxrates, validation: "notnull" },
                    { json_field: "RETIRED", post_field: "retired", label: _("Retired"), type: "check" },
                    { json_field: "SUPPLIERID", post_field: "supplierid", label: _("Supplier"), type: "person", personfilter: "supplier", validation:"notzero" },
                    { json_field: "SUPPLIERCODE", post_field: "suppliercode", label: _("Supplier code"), type: "text", colclasses: "bottomborder" },
                    { json_field: "PURCHASEUNITTYPE", post_field: "purchaseunittype", label: _("Purchase Unit"), type: "select",
                        options: ["0|" + _("Unit").toLowerCase(), "1|kg", "2|g", "3|l", "4|ml", "5|" + _("Custom").toLowerCase()]
                    },
                    { json_field: "CUSTOMPURCHASEUNIT", post_field: "custompurchaseunit", label: _("Custom Unit"), type: "text" },
                    { json_field: "COSTPRICE", post_field: "costprice", label: _("Cost price"), type: "currency", colclasses: "bottomborder" },
                    { json_field: "UNITTYPE", post_field: "unittype", label: _("Unit"), type: "select", options: ["0|" + _("Purchase unit").toLowerCase(), "1|kg", "2|g", "3|l", "4|ml", "5|" + _("Custom").toLowerCase()] },
                    { json_field: "CUSTOMUNIT", post_field: "customunit", label: _("Custom Unit"), type: "text" },
                    { json_field: "RETAILPRICE", post_field: "retailprice", label: _("Unit price"), type: "currency" },
                    { json_field: "UNITRATIO", post_field: "unitratio", label: _("Unit Ratio"), type: "number", validation: "notblank", defaultval: 1 }
                ]
            };

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
                            return row.PRODUCTNAME + " <a href=product?id=" + row.PRODUCTID + "><img src='static/images/icons/match.png' title='" + _("Linked to product") + "'></a>"
                        }
                    } },
                    { field: "QUANTITY", display: _("Quantity") },
                    { field: "UNIT", display: _("Unit") },
                    { field: "FROMNAME", display: _("From") },
                    { field: "TONAME", display: _("To") },
                    { field: "COMMENTS", display: _("Comments") }
                ]
            };

            this.dialog = dialog;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            if (controller.productid != 0) {
                s += html.content_header(_("{0} Movements").replace("{0}", controller.productname));
            } else {
                s += html.content_header(_("Stock Movement"));
            }
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

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "stock_movement",
        animation: "book",
        title: function() {
            if (controller.productid != 0) {
                return _("{0} Movements").replace("{0}", controller.productname);
            } else {
                return _("Stock movement");
            }
        },
        routes: {
            "stock_movement": function() { common.module_loadandstart("stock_movement", "stock_movement?" + this.rawqs); }
        }

    };
    
    common.module_register(stock_movement);

});
