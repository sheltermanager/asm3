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
                    { json_field: "PRODUCTTYPEID", post_field: "producttypeid", label: _("Product type"), type: "select", options: controller.producttypes },
                    { json_field: "BARCODE", post_field: "barcode", label: _("Barcode"), type: "text" },
                    { json_field: "PLU", post_field: "plu", label: _("PLU"), type: "text",
                        callout: _("A unique identifier that may be used to link this product with an external POS system")
                     },
                    { json_field: "DESCRIPTION", post_field: "productdescription", label: _("Description"), type: "textarea" },
                    { json_field: "TAXRATE", post_field: "taxrate", label: _("Tax Rate"), type: "select", options: controller.taxrates, validation: "notnull" },
                    { json_field: "ACTIVE", post_field: "active", label: _("Active"), type: "select", options: { rows: controller.yesno, displayfield: "NAME" }, defaultval: "1" },
                    { json_field: "SUPPLIERID", post_field: "supplierid", label: _("Supplier"), type: "person", personfilter: "supplier", validation:"notzero" },
                    { json_field: "SUPPLIERCODE", post_field: "suppliercode", label: _("Supplier code"), type: "text", colclasses: "bottomborder" },

                    { json_field: "PURCHASEUNITTYPEID", post_field: "purchaseunittypeid", label: _("Purchase Unit"), type: "select",
                        callout: _("The units that you acquire in this product in for example, 'tray', 'pallet', 'box', this does not have to be the same as the units that you use to manage your stock internally"), 
                        options: { rows: controller.units, displayfield: "UNITNAME", prepend: '<option value="0">' + _("unit") + '</option><option value="-1">' + _("custom") + '</option>' }
                    },
                    { json_field: "CUSTOMPURCHASEUNIT", post_field: "custompurchaseunit", label: _("Custom Unit"), type: "text" },
                    { json_field: "COSTPRICE", post_field: "costprice", label: _("Cost price"), type: "currency", colclasses: "bottomborder" },

                    { json_field: "UNITTYPEID", post_field: "unittypeid", label: _("Unit"), type: "select", 
                        callout: _("The units that you use to manage this product internally for example, 'tin', 'tablet', 'bag'"), 
                        options: { rows: controller.units, displayfield: "UNITNAME", prepend: '<option value="0">' + _("purchase unit") + '</option><option value="-1">' + _("custom") + '</option>' }
                    },

                    { json_field: "CUSTOMUNIT", post_field: "customunit", label: _("Custom Unit"), type: "text" },
                    { json_field: "RETAILPRICE", post_field: "retailprice", label: _("Unit price"), type: "currency" },
                    { json_field: "UNITRATIO", post_field: "unitratio", label: _("Unit Ratio"), type: "number", validation: "notblank", defaultval: 1,
                        callout: _("The number of 'units' per 'purchase unit' for example, if you get 24 tins per tray and have purchase unit 'tray' and unit 'tin' your unit ratio would be '24'")
                     },
                    { json_field: "GLOBALMINIMUM", post_field: "globalminimum", label: _("Low"), type: "number", defaultval: "0", validation: "notblank",
                        callout: _("Show an alert if the total balance of all stock levels for this product falls below this amount"),
                    }

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
                            if ($("#purchaseunittypeid").val() == -1) {
                                $("#custompurchaseunitrow").fadeIn();
                            } else {
                                $("#custompurchaseunitrow").fadeOut();
                            }
                
                            if ($("#unittypeid").val() == -1) {
                                $("#customunitrow").fadeIn();
                            } else {
                                $("#customunitrow").fadeOut();
                            }
                
                            if ($("#unittypeid").val() == 0) {
                                $("#unitratiorow").fadeOut();
                            } else {
                                $("#unitratiorow").fadeIn();
                            }
                        }
                    });
                },
                overdue: function(row) {
                    return ( row.BALANCE < row.GLOBALMINIMUM );
                },
                columns: [
                    { field: "PRODUCTNAME", display: _("Name") },
                    { field: "UNIT", display: _("Unit"), formatter: function(row) {
                        if (row.UNITTYPEID == 0) {
                            if (row.PURCHASEUNITTYPEID == 0) {
                                return _("unit");
                            } else if (row.PURCHASEUNITTYPEID == -1) {
                                return row.CUSTOMPURCHASEUNIT;
                            } else {
                                let unit = _("undefined");
                                $.each(controller.units, function(unitdictcount, unitdict) {
                                    if (unitdict.ID == row.PURCHASEUNITTYPEID) {
                                        unit = unitdict.UNITNAME;
                                        return false;
                                    }
                                });
                                return unit;
                            }
                        } else if (row.UNITTYPEID == -1) {
                            return row.CUSTOMUNIT;
                        } else {
                            let unit = _("undefined");
                            $.each(controller.units, function(unitdictcount, unitdict) {
                                if (unitdict.ID == row.UNITTYPEID) {
                                    unit = unitdict.UNITNAME;
                                    return false;
                                }
                            });
                            return unit;
                        }
                    } },
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
                { id: "move", text: _("Move Stock"), icon: "stock-movement", enabled: "one", perm: "asl", 
                    click: async function() {
                        product.move_product_init();
                        await tableform.show_okcancel_dialog("#dialog-moveproduct", _("Move"), { width: 500, notblank: [ "movementfrom", "movementto" ] });
                        product.move_product();
                    }
                },
                { id: "showmovements", text: _("Show Movements"), icon: "stock-movement", enabled: "one", perm: "asl", 
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
                },
                { id: "productfilter", type: "dropdownfilter", 
                    options: '<option value="0">' + _("(active)") + '</option>' + 
                        '<option value="-1">' + _("(depleted)") + '</option>' + 
                        '<option value="-2">' + _("(low balance)") + '</option>' +
                        '<option value="-3">' + _("(negative balance)") + '</option>' +
                        '<option value="-4">' + _("(retired)") + '</option>',
                    click: function(selval) {
                        common.route("product?productfilter=" + selval);
                    }
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = '<div id="dialog-moveproduct" style="display: none;width: 800px;" title="' + html.title(_("Move Product")) + '">';
            s += tableform.fields_render([
                { post_field: "movementquantity", json_field: "MOVEMENTQUANTITY", label: _("Quantity"), type: "intnumber", xmarkup: ' &times; ', rowclose: false, halfsize: true, validation: "notzero" },
                { post_field: "movementunit", json_field: "MOVEMENTUNIT", type: "select", justwidget: true, halfsize: true },
                { type: "rowclose" },
                { post_field: "movementdate", json_field: "MOVEMENTDATE", label: _("Date"), type: "date" },
                { post_field: "movementfrom", json_field: "MOVEMENTFROM", label: _("From"), type: "select", validation: "notblank" },
                { post_field: "movementto", json_field: "MOVEMENTTO", label: _("To"), type: "select", validation: "notblank" },
                { post_field: "batch", json_field: "BATCH", label: _("Batch"), type: "text" },
                { post_field: "expiry", json_field: "EXPIRY", label: _("Expiry"), type: "date" },
                { post_field: "comments", json_field: "COMMENTS", label: _("Comments"), type: "textarea" }
            ]);
            s += '</div>';
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Products"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        new_product: function() { 
            let dialog = product.dialog, table = product.table;
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            $("#producttypeid, #taxrateid, #purchaseunittypeid, #unittypeid").val(0);
            $("#unitratio").val(1);
            $("#custompurchaseunitrow").fadeOut();
            $("#customunitrow").fadeOut();
            $("#unitratiorow").fadeOut();
            $("#producttypeid").val(config.integer("StockDefaultProductTypeID"));
            $("#taxrateid").val(config.integer("StockDefaultTaxRateID"));

            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", "product")
                        .then(function(response) {
                            let row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
                            product.set_extra_fields(row);
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
            
            let purchaseunit = _("undefined");
            if (activeproduct.PURCHASEUNITTYPEID == 0) {
                purchaseunit = _("unit");
            } else if (activeproduct.PURCHASEUNITTYPEID == -1) {
                purchaseunit = activeproduct.CUSTOMPURCHASEUNIT;
            } else {
                $.each(controller.units, function(unitcount, unitrow) {
                    if (unitrow.ID == activeproduct.PURCHASEUNITTYPEID) {
                        purchaseunit = unitrow.UNITNAME;
                        return false;
                    }
                });
                
            }
            let unit = _("undefined");
            if (activeproduct.UNITTYPEID == 0) {
                unit = purchaseunit;
            } else if (activeproduct.UNITTYPEID == -1) {
                unit = activeproduct.CUSTOMUNIT;
            } else {
                $.each(controller.units, function(unitcount, unitrow) {
                    if (unitrow.ID == activeproduct.UNITTYPEID) {
                        unit = unitrow.UNITNAME;
                        return false;
                    }
                });
            }
            let units = [activeproduct.UNITRATIO + "|" + purchaseunit,];
            if (activeproduct.UNITTYPEID != 0) {
                units.push("1|" + unit);
            }

            $("#movementunit").html(html.list_to_options(units));
            $("#movementunit").val($("#movementunit option").last().val());
            $("#movementfrom").val("L$" + config.integer(asm.user + "_DefaultStockLocationID"));
            $("#movementto").val("U$" + config.integer(asm.user + "_DefaultStockUsageTypeID"));

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

            let quantity = parseInt($("#movementquantity").val()) * parseInt($("#movementunit").val());
            
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
            };
            let response = await common.ajax_post("product", formdata);
            console.log($("#dialog-moveproduct"));
            let balance = activeproduct.BALANCE;
            if (fromtype == 0 && totype == 1) {
                activeproduct.BALANCE = activeproduct.BALANCE - quantity;
            } else if (fromtype == 1 && totype == 0) {
                activeproduct.BALANCE = activeproduct.BALANCE + quantity;
            }
            //tableform.fields_update_row(this.dialog.fields, activeproduct);
            tableform.buttons_default_state(this.buttons);
            tableform.table_update(this.table);
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

            $("#purchaseunittypeid").change(function() {
                if ($("#purchaseunittypeid").val() == -1) {
                    $("#custompurchaseunitrow").fadeIn();
                } else {
                    $("#custompurchaseunitrow").fadeOut();
                }
            });
            
            $("#unittypeid").change(function() {
                if ($("#unittypeid").val() == -1) {
                    $("#customunitrow").fadeIn();
                } else {
                    $("#customunitrow").fadeOut();
                }
                if ($("#unittypeid").val() == 0) {
                    $("#unitratiorow").fadeOut();
                } else {
                    $("#unitratiorow").fadeIn();
                }
            });

        },

        sync: function() {
            // If a productfilter is given in the querystring, update the select
            if (common.querystring_param("productfilter")) {
                $("#productfilter").select("value", common.querystring_param("productfilter"));
            }
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
                $.each(controller.rows, function(rowcount, row) {
                    if (row.ID == controller.productid) {
                        $("input[data-id='" + controller.productid + "']").prop("checked", true);
                        tableform.table_update_buttons(product.table, product.buttons);
                        product.table.edit(row);
                        return false;
                    }
                });
            }
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        set_extra_fields: function(row) {
            row.PRODUCTTYPENAME = ""
            $.each(controller.producttypes, function(typecount, producttype) {
                if (producttype.split("|")[0] == row.PRODUCTTYPEID) {
                    row.PRODUCTTYPENAME = producttype.split("|")[1];
                    return false;
                }
                
            });
        },

        name: "product",
        animation: "book",
        title: function() { return _("Products"); },
        routes: {
            "product": function() { common.module_loadandstart("product", "product?" + this.rawqs); }
        }

    };
    
    common.module_register(product);

});
