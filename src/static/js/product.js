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
                    { json_field: "PRODUCTTYPE", post_field: "producttype", label: _("Product type"), type: "select", options: controller.producttypes },
                    { json_field: "BARCODE", post_field: "barcode", label: _("Barcode"), type: "text" },
                    { json_field: "PLU", post_field: "plu", label: _("PLU"), type: "text" },
                    { json_field: "DESCRIPTION", post_field: "productdescription", label: _("Description"), type: "textarea" },
                    { json_field: "TAXRATE", post_field: "taxrate", label: _("Tax Rate"), type: "select", options: controller.taxrates },
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
                            tableform.fields_post(dialog.fields, "mode=update&productid=" + row.ID, "products")
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
                            console.log("Loaded");
                            if ($("#purchaseunittype").val() == 5) {
                                console.log("Showing custom purchase unit");
                                $("#custompurchaseunitrow").fadeIn();
                            } else {
                                console.log("Hiding custom purchase unit");
                                $("#custompurchaseunitrow").fadeOut();
                            }
                
                            if ($("#unittype").val() == 5) {
                                console.log("Showing custom unit");
                                $("#customunitrow").fadeIn();
                            } else {
                                console.log("Hiding custom unit");
                                $("#customunitrow").fadeOut();
                            }
                
                            if ($("#unittype").val() == 0) {
                                console.log("Hiding unit ratio");
                                $("#unitratiorow").fadeOut();
                            } else {
                                console.log("Showing unit ratio");
                                $("#unitratiorow").fadeIn();
                            }
                        }
                    });
                },
                columns: [
                    { field: "PRODUCTNAME", display: _("Name") },
                    { field: "DESCRIPTION", display: _("Type") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Product"), icon: "new", enabled: "always", perm: "asl", 
                    click: function() { product.new_product(); }},
                { id: "move", text: _("Move Stock"), icon: "right", enabled: "one", perm: "asl", 
                    click: function() { product.move_product(); }},
                { id: "clone", text: _("Clone"), icon: "copy", enabled: "one", perm: "asl",
                    click: function() { product.clone_product(); }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dsl", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("products", "mode=delete&ids=" + ids);
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
            let s = [
                '<div id="dialog-move-product" style="display: none;width: 800px;" title="' + html.title(_("Move Product")) + '">',
                '<p><input id=movementdate name=movementdate class="asm-textbox asm-datebox"></p>',
                '<p><input id=movementquantity name=movementquantity class="asm-field asm-textbox asm-intbox"> x <select id=movementunit name=movementunit></select></p>',
                '<p>from <select id=movementfrom name=movementfrom></select></p>',
                '<p>to <select id=movementto name=movementto></select></p>',
                '<p>' + _("Batch") + '<br><input id=batch name=batch></p>',
                '<p>' + _("Expiry") + '<br><input type=text id=expiry name=expiry class="asm-textbox asm-datebox"></p>',
                '</div>',
            ].join("\n");
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
            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", "products")
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

        move_product: async function() {
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
                purchaseunit = "0|" + _("Unit").toLowerCase();
            } else if (activeproduct.PURCHASEUNITTYPE == 1) {
                purchaseunit = "1|kg";
            } else if (activeproduct.PURCHASEUNITTYPE == 2) {
                purchaseunit = "2|g";
            } else if (activeproduct.PURCHASEUNITTYPE == 3) {
                purchaseunit = "3|l";
            } else if (activeproduct.PURCHASEUNITTYPE == 4) {
                purchaseunit = "4|ml";
            } else if (activeproduct.PURCHASEUNITTYPE == 5) {
                purchaseunit = activeproduct.CUSTOMPURCHASEUNIT;
            }
            let units = [purchaseunit,];
            if (activeproduct.UNITTYPE == 1) {
                units.push("1|kg");
            } else if (activeproduct.UNITTYPE == 2) {
                units.push("2|g");
            } else if (activeproduct.UNITTYPE == 3) {
                units.push("3|l");
            } else if (activeproduct.UNITTYPE == 4) {
                units.push("4|ml");
            } else if (activeproduct.UNITTYPE == 5) {
                units.push(activeproduct.CUSTOMUNIT);
            }
            console.log(units);
            $("#movementunit").html(html.list_to_options(units));
            
            $("#movementfrom").val($("#movementfrom option[value^='L']").first().val());
            $("#movementto").val($("#movementto option[value^='U']").first().val());

            $("#movementdate").val(format.date_now());

            $("#movementquantity").val(1);
            $("#movementquantity").focus();

            await tableform.show_okcancel_dialog("#dialog-move-product", _("Move"));
            
            let formdata = "mode=move" +
                "&productid=" + productid +
                "&movementdate=" + $("#movementdate").val() + 
                "&movementquantity=" + $("#movementquantity").val() +
                "&movementunit=" + $("#movementunit").val() +
                "&movementfrom=" + $("#movementfrom").val() +
                "&movementto=" + $("#movementto").val() +
                "&batch=" + $("#batch").val() +
                "&expiry=" + $("#expiry").val()
            console.log(formdata);
            let response = await common.ajax_post("products", formdata);

            console.log("Movement dialog complete.");
        },

        clone_product: function() { 
            let dialog = product.dialog, table = product.table;
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", "products")
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
                console.log("purchaseunittype changed");
                if ($("#purchaseunittype").val() == 5) {
                    $("#custompurchaseunitrow").fadeIn();
                } else {
                    $("#custompurchaseunitrow").fadeOut();
                }
            });
            
            $("#unittype").change(function() {
                console.log("unittype changed");
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
