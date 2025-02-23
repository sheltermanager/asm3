/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const product = {

        model: function() {
            const dialog = {
                add_title: _("Add product"),
                edit_title: _("Edit product"),
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
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    tableform.dialog_show_edit(dialog, row, {
                        onchange: function() {
                            tableform.fields_update_row(dialog.fields, row);
                            //stocklevel.set_extra_fields(row);
                            tableform.fields_post(dialog.fields, "mode=update&productid=" + row.ID, "product")
                                .then(function(response) {
                                    tableform.table_update(table);
                                    tableform.dialog_close();
                                })
                                .fail(function(response) {
                                    tableform.dialog_error(response);
                                    tableform.dialog_enable_buttons();
                                });
                        },
                        onload: function() {
                            if ($("#purchaseunittype").val() == 5) {
                                $("#custompurchaseunitrow").fadeIn();
                            } else {
                                $("#custompurchaseunitrow").fadeOut();
                            }
                
                            if ($("#unittype").val() == 5) {
                                $("#customunitrow").fadeIn();
                            } else {
                                $("#customunitrow").fadeOut();
                            }
                
                            if ($("#unittype").val() == 0) {
                                $("#unitratiorow").fadeOut();
                            } else {
                                $("#unitratiorow").fadeIn();
                            }
                        }
                    });
                },
                columns: [
                    { field: "PRODUCTNAME", display: _("Name") },
                    { field: "UNIT", display: _("Unit") },
                    { field: "BALANCE", display: _("Balance"), formatter: function(row) {
                        if (!row.BALANCE) {
                            return 0;
                        } else {
                            return row.BALANCE;
                        }
                    } },
                    { field: "PRODUCTTYPENAME", display: _("Type") },
                    { field: "BARCODE", display: _("Barcode") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Product"), icon: "new", enabled: "always", perm: "asl", 
                    click: function() { product.new_product(); }},
                { id: "move", text: _("Move Stock"), icon: "right", enabled: "one", perm: "asl", 
                    click: async function() {
                        product.move_product_init();
                        await tableform.show_okcancel_dialog("#dialog-moveproduct", _("Move"), { width: 500 });
                        product.move_product();
                    }
                },
                { id: "showmovements", text: _("Show Movements"), icon: "stock", enabled: "one", perm: "asl", 
                    click: function() {
                        document.location.href = "stock_movement?productid=" + tableform.table_selected_id(table);
                    }
                },
                { id: "clone", text: _("Clone"), icon: "copy", enabled: "one", perm: "asl",
                    click: function() { product.clone_product(); }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dsl", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("product", "mode=delete&ids=" + ids);
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
            let s = '<div id="dialog-moveproduct" style="display: none;width: 800px;" title="' + html.title(_("Move Product")) + '">'
            s += tableform.fields_render([
                { post_field: "movementdate", json_field: "MOVEMENTDATE", label: _("Date"), type: "date" },
                { post_field: "movementquantity", json_field: "MOVEMENTQUANTITY", label: _("Quantity"), type: "intnumber", xmarkup: ' &times; ', rowclose: false, halfsize: true },
                { post_field: "movementunit", json_field: "MOVEMENTUNIT", type: "select", justwidget: true, halfsize: true },
                { type: "rowclose" },
                { post_field: "movementfrom", json_field: "MOVEMENTFROM", label: _("From"), type: "select" },
                { post_field: "movementto", json_field: "MOVEMENTTO", label: _("To"), type: "select" },
                { post_field: "batch", json_field: "BATCH", label: _("Batch"), type: "text" },
                { post_field: "expiry", json_field: "EXPIRY", label: _("Expiry"), type: "date" },
                { post_field: "comments", json_field: "COMMENTS", label: _("Comments"), type: "textarea" }
            ]);
            s += '</div>';
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Product"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        new_product: function() { 
            let dialog = product.dialog, table = product.table;
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            $("#producttype, #taxrate, #purchaseunittype, #unittype").val(0);
            $("#unitratio").val(1);
            $("#custompurchaseunitrow").fadeOut();
            $("#customunitrow").fadeOut();
            $("#unitratiorow").fadeOut();
            $("#producttype").val(config.integer("StockDefaultProductTypeID"));
            $("#taxrate").val(config.integer("StockDefaultTaxRateID"));

            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", "product")
                        .then(function(response) {
                            let row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
                            //stocklevel.set_extra_fields(row);
                            controller.rows.push(row);
                            tableform.table_update(table);
                            tableform.dialog_close();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();   
                        });
                },
                onload: function() {
                    
                }
            });
        },

        move_product_init: function() {
            let productid = tableform.table_selected_id();
            let activeproduct = false;
            $.each(controller.rows, function(rowcount, row) {
                if (row.ID == productid) {
                    activeproduct = row;
                    return false;
                }
            });
            let purchaseunit = activeproduct.CUSTOMPURCHASEUNIT;
            if (activeproduct.PURCHASEUNITTYPE == 0) {
                purchaseunit = _("Unit").toLowerCase();
            } else if (activeproduct.PURCHASEUNITTYPE == 1) {
                purchaseunit = "kg";
            } else if (activeproduct.PURCHASEUNITTYPE == 2) {
                purchaseunit = "g";
            } else if (activeproduct.PURCHASEUNITTYPE == 3) {
                purchaseunit = "l";
            } else if (activeproduct.PURCHASEUNITTYPE == 4) {
                purchaseunit = "ml";
            } else if (activeproduct.PURCHASEUNITTYPE == 5) {
                purchaseunit = activeproduct.CUSTOMPURCHASEUNIT;
            }
            let units = [activeproduct.UNITRATIO + "|" + purchaseunit,];
            if (activeproduct.UNITTYPE == 1) {
                units.push("1|kg");
            } else if (activeproduct.UNITTYPE == 2) {
                units.push("1|g");
            } else if (activeproduct.UNITTYPE == 3) {
                units.push("1|l");
            } else if (activeproduct.UNITTYPE == 4) {
                units.push("1|ml");
            } else if (activeproduct.UNITTYPE == 5) {
                units.push("1|" + activeproduct.CUSTOMUNIT);
            }
            $("#movementunit").html(html.list_to_options(units));
            $("#movementunit").val($("#movementunit option").last().val());
            $("#movementfrom").val("L$" + controller.defaultstocklocationid);
            $("#movementto").val("U$" + controller.defaultstockusagetypeid);

            $("#movementdate").val(format.date_now());

            $("#movementquantity").val(1);
        },

        move_product: async function() {
           
            let productid = tableform.table_selected_id();
            let activeproduct = false;
            $.each(controller.rows, function(rowcount, row) {
                if (row.ID == productid) {
                    activeproduct = row;
                    return false;
                }
            });
            let fromid = $("#movementfrom").val().split("$")[1];
            let fromtype = 0;
            if ($("#movementfrom").val().split("$")[0] == "U") {
                fromtype = 1;
            }
            let totype = 0;
            if ($("#movementto").val().split("$")[0] == "U") {
                totype = 1;
            }
            let toid = $("#movementto").val().split("$")[1];

            let quantity = parseInt($("#movementquantity").val()) * parseInt($("#movementunit").val())
            
            let formdata = {
                mode: "move",
                productid: productid,
                productname: activeproduct.PRODUCTNAME,
                productdescription: activeproduct.DESCRIPTION,
                movementdate: $("#movementdate").val() ,
                movementquantity: quantity,
                unitratio: activeproduct.UNITRATIO,
                costprice: activeproduct.COSTPRICE,
                movementunit: $("#movementunit option").last().text(),
                movementfrom: fromid,
                movementfromtype: fromtype,
                movementto: toid,
                movementtotype: totype,
                batch: $("#batch").val(),
                expiry: $("#expiry").val(),
                comments: _("Movement") + ". " + _("{0} to {1}").replace("{0}", $("#movementfrom option:selected").text()).replace("{1}", $("#movementto option:selected").text()) + "\n" + $("#comments").val()
            }
            let response = await common.ajax_post("product", formdata);
        },

        clone_product: function() { 
            let dialog = product.dialog, table = product.table;
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", "product")
                        .then(function(response) {
                            let row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
                            controller.rows.push(row);
                            tableform.table_update(table);
                            tableform.dialog_close();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();
                        });
                },
                onload: function() {
                    let row = tableform.table_selected_row(table);
                    tableform.fields_populate_from_json(dialog.fields, row);
                    $("#productname").val(_("Copy of {0}").replace("{0}", $("#productname").val()));
                }
            });
        },
        
        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            if (controller.newproduct == 1) {
                this.new_product();
            }

            $("#purchaseunittype").change(function() {
                if ($("#purchaseunittype").val() == 5) {
                    $("#custompurchaseunitrow").fadeIn();
                } else {
                    $("#custompurchaseunitrow").fadeOut();
                }
            });
            
            $("#unittype").change(function() {
                if ($("#unittype").val() == 5) {
                    $("#customunitrow").fadeIn();
                } else {
                    $("#customunitrow").fadeOut();
                }
                if ($("#unittype").val() == 0) {
                    $("#unitratiorow").fadeOut();
                } else {
                    $("#unitratiorow").fadeIn();
                }
            });

        },

        sync: function() {
            //let stocklocations = html.list_to_options(controller.stocklocations, "ID", "LOCATIONNAME");
            //let usagetypes = html.list_to_options(controller.stockusagetypes, "ID", "USAGETYPENAME");
            let stocklocations = [];
            $.each(controller.stocklocations, function(locationcount, location) {
                stocklocations.push("L$" + location.ID + "|" + location.LOCATIONNAME);
            });
            $.each(controller.stockusagetypes, function(usagecount, usage) {
                stocklocations.push("U$" + usage.ID + "|" + usage.USAGETYPENAME);
            });
            $("#movementfrom").html(html.list_to_options(stocklocations));
            $("#movementto").html(html.list_to_options(stocklocations));

            if (controller.productid != 0) {
                this.table.edit(controller.row);
            }
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        /*set_extra_fields: function(row) {
            row.STOCKLOCATIONNAME = common.get_field(controller.stocklocations, row.STOCKLOCATIONID, "LOCATIONNAME");
        },*/

        name: "product",
        animation: "book",
        title: function() { return _("Product"); },
        routes: {
            "product": function() { common.module_loadandstart("product", "product?" + this.rawqs); }
        }

    };
    
    common.module_register(product);

});
