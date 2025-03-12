/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const stock_level = {

        model: function() {
            const dialog = {
                add_title: _("Add stock"),
                edit_title: _("Edit stock"),
                edit_perm: 'csl',
                close_on_ok: false,
                hide_read_only: true,
                columns: 1,
                width: 800,
                fields: [
                    { json_field: "PRODUCTLIST", post_field: "productlist", label: _("Product templates"), type: "select", readonly: true, 
                        options: { rows: controller.products, displayfield: "PRODUCTNAME", prepend: '<option value=""></option>' }},
                    { json_field: "NAME", post_field: "name", label: _("Name"), type: "autotext", validation: "notblank",
                        options: controller.stocknames.split("|") },
                    { json_field: "DESCRIPTION", post_field: "description", label: _("Description"), type: "textarea" },
                    { json_field: "BARCODE", post_field: "barcode", label: _("Barcode"), type: "text" },
                    { json_field: "STOCKLOCATIONID", post_field: "location", label: _("Location"), type: "select", 
                        options: { displayfield: "LOCATIONNAME", valuefield: "ID", rows: controller.stocklocations }},
                    { json_field: "UNITNAME", post_field: "unitname", label: _("Units"), type: "autotext", validation: "notblank",
                        callout: _("The type of unit in the container, eg: tablet, vial, etc."),
                        options: controller.stockunits.split("|") },
                    { json_field: "COST", post_field: "cost", label: _("Cost"), type: "currency",
                        callout: _("The wholesale/trade price the container was bought for") },
                    { json_field: "UNITPRICE", post_field: "unitprice", label: _("Unit Price"), type: "currency",
                        callout: _("The retail/resale price per unit") },
                    { json_field: "TOTAL", post_field: "total", label: _("Total"), type: "number", 
                        callout: _("Total number of units in the container") },
                    { type: "nextcol" },
                    { json_field: "", post_field: "quantity", label: _("Quantity"), type: "intnumber", validation: "notblank", 
                        defaultval: "1", min: 1, max: 100, readonly: true, 
                        callout: _("The number of stock records to create (containers)") },
                    { json_field: "STOCKLOCATIONID", post_field: "location", label: _("Location"), type: "select", 
                        options: { displayfield: "LOCATIONNAME", valuefield: "ID", rows: controller.stocklocations }},
                    { json_field: "BALANCE", post_field: "balance", label: _("Balance"), type: "number", validation: "notblank",
                        callout: _("The remaining units in the container") },
                    { json_field: "LOW", post_field: "low", label: _("Low"), type: "number",
                        callout: _("Show an alert if the balance falls below this amount")
                    },
                    { json_field: "BATCHNUMBER", post_field: "batchnumber", label: _("Batch"), type: "text", 
                        callout: _("If this stock record is for a drug, the batch number from the container") },
                    { json_field: "EXPIRY", post_field: "expiry", label: _("Expiry"), type: "date",
                        callout: _("If this stock record is for a perishable good, the expiry date on the container") },
                    { rowid: "usageinfo", type: "raw", label: "", 
                        markup: html.info(_("Usage explains why this stock record was created or adjusted. Usage records will only be created if the balance changes.")) },
                    { json_field: "", post_field: "usagetype", label: _("Usage Type"), type: "select",
                        options: { displayfield: "USAGETYPENAME", valuefield: "ID", rows: controller.stockusagetypes }},
                    { json_field: "", post_field: "usagedate", label: _("Usage Date"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    stock_level.active_row_id = row.ID;
                    tableform.dialog_show_edit(dialog, row, {
                        onchange: function() {
                            tableform.fields_update_row(dialog.fields, row);
                            stock_level.set_extra_fields(row);
                            tableform.fields_post(dialog.fields, "mode=update&stocklevelid=" + row.ID, "stock_level")
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
                            $("#usagedate").date("today");
                            $("#usagetype").select("firstvalue");
                            $("#quantity").val("1"); // Ignored during edit but validated
                            stock_level.hide_usage_fields();
                        }
                    });
                },
                complete: function(row) {
                    if (!row.BALANCE) { return true; }
                    return false;
                },
                overdue: function(row) {
                    return ( (row.EXPIRY && format.date_js(row.EXPIRY) <= common.today_no_time()) ||
                             (row.LOW && row.BALANCE < row.LOW) );
                },
                columns: [
                    { field: "NAME", display: _("Name"), initialsort: controller.sortexp != 1 },
                    { field: "STOCKLOCATIONNAME", display: _("Location") },
                    { field: "UNITNAME", display: _("Unit") },
                    { field: "BALANCE", display: _("Balance"), formatter: function(row) {
                        let s = row.BALANCE + " / " + row.TOTAL;
                        if (row.LOW) { s += " " + _("(low at {0})").replace("{0}", row.LOW); }
                        return s;
                    }},
                    { field: "BARCODE", display: _("Barcode") },
                    { field: "COST", display: _("Cost"), formatter: tableform.format_currency },
                    { field: "UNITPRICE", display: _("Unit Price"), formatter: tableform.format_currency },
                    { field: "BATCHNUMBER", display: _("Batch") },
                    { field: "EXPIRY", display: _("Expiry"), formatter: tableform.format_date, initialsort: controller.sortexp == 1 },
                    { field: "DESCRIPTION", display: _("Description") }
                ]
            };

            const buttons = [
                { id: "new", text: _("Add Stock"), icon: "new", enabled: "always", perm: "asl", 
                    click: function() { stock_level.new_level(); }},
                { id: "showmovements", text: _("Show Movements"), icon: "stock-movement", enabled: "one", perm: "asl", 
                    click: function() {
                        document.location.href = "stock_movement?stocklevelid=" + tableform.table_selected_id(table);
                    }
                },
                { id: "clone", text: _("Clone"), icon: "copy", enabled: "one", perm: "asl",
                    click: function() { stock_level.clone_level(); }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dsl", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("stock_level", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "scan", text: _("Scan"), icon: "find", enabled: "always", perm: "asl", 
                    hideif: function() { return !common.browser_is.mobile; },
                    click: async function() {
                        let code = await barcode.scan();
                        let barcodefilter = $(".tablesorter-filter-row input[data-column='4']");
                        barcodefilter.val(code);
                        barcodefilter.change();
                        //$("#tableform-toggle-filter").click();
                        table.filter_toggle = true;
                        //$(".tablesorter-filter-row").toggle(table.filter_toggle);
                        console.log(table.filter_toggle);
                        $(".tablesorter-filter-row").show();
                    } 
                },
                { id: "viewlocation", type: "dropdownfilter", 
                    options: '<option value="0">' + _("(active)") + '</option>' + 
                        '<option value="-1">' + _("(depleted)") + '</option>' + 
                        '<option value="-2">' + _("(low balance)") + '</option>' + 
                        html.list_to_options(controller.stocklocations, "ID", "LOCATIONNAME"),
                    click: function(selval) {
                        common.route("stock_level?viewlocation=" + selval);
                    }
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Stock levels"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        new_level: function() { 
            let dialog = stock_level.dialog, table = stock_level.table;
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            $("#productlist").val(-1);
            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", "stock_level")
                        .then(function(response) {
                                tableform.dialog_close();
                                common.route_reload();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();   
                        });
                },
                onload: function() {
                    stock_level.show_usage_fields();
                    $("#usagetype").select("firstvalue");
                }
            });
        },

        clone_level: function() { 
            let dialog = stock_level.dialog, table = stock_level.table;
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", "stock_level")
                        .then(function(response) {
                            tableform.dialog_close();
                            common.route_reload();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();
                        });
                },
                onload: function() {
                    let row = tableform.table_selected_row(table);
                    tableform.fields_populate_from_json(dialog.fields, row);
                    $("#name").val(_("Copy of {0}").replace("{0}", $("#name").val()));
                    stock_level.show_usage_fields();
                    $("#usagetype").select("firstvalue");
                    $("#usagedate").date("today");
                    $("#quantity").val("1"); 
                }
            });
        },

        hide_usage_fields: function() {
            $("#usageinfo").hide();
            $("#usagetyperow").hide();
            $("#usagedaterow").hide();
            $("#commentsrow").hide();
        },

        show_usage_fields: function() {
            $("#usageinfo").fadeIn();
            $("#usagetyperow").fadeIn();
            $("#usagedaterow").fadeIn();
            $("#commentsrow").fadeIn();
        },
        
        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            // If the user edits the balance, prompt for usage info
            $("#balance").change(stock_level.show_usage_fields);

            // If the user edits the total and balance is blank, default it to total
            $("#total").change(function() {
                if (!$("#balance").val()) {
                    $("#balance").val($("#total").val());
                }
            });

            // If the user changes the name and we don't have a description or unit,
            // look up the last stock we saw with that name to auto fill the fields
            $("#name").change(function() {
                if (!$("#description").val() && !$("#unitname").val()) {
                    common.ajax_post("stock_level", "mode=lastname&name=" + $("#name").val())
                        .then(function(data) {
                            if (data != "||") {
                                let d = data.split("|");
                                $("#description").val(d[0]);
                                $("#unitname").val(d[1]);
                                $("#total").val(d[2]);
                                $("#balance").val(d[2]);
                            }
                        });
                }
            });

            // Generate code button
            if (common.browser_is.mobile) {
                $("#barcode").after('<button id="definebarcode">' + _("Scan a barcode to assign to the stock") + '</button>');
                $("#definebarcode")
                    .button({ icons: { primary: "ui-icon-transferthick-e-w" }, text: false })
                    .click(async function() {
                        let code = await barcode.scan();
                        $("#barcode").val(code);
                    });
            }

            $("#productlist").change(function() {
                let productid = $("#productlist").val();
                let activeproduct = common.get_row(controller.products, productid);
                $("#name").val(activeproduct.PRODUCTNAME);
                $("#description").val(activeproduct.DESCRIPTION);
                let unittype = activeproduct.CUSTOMUNIT;
                if (activeproduct.UNITTYPEID == 0) {
                    if (activeproduct.PURCHASEUNITTYPEID == 0) {
                        unittype = _("unit");
                    } else if (activeproduct.PURCHASEUNITTYPEID == 1) {
                        unittype = "kg";
                    } else if (activeproduct.PURCHASEUNITTYPEID == 2) {
                        unittype = "g";
                    } else if (activeproduct.PURCHASEUNITTYPEID == 3) {
                        unittype = "l";
                    } else if (activeproduct.PURCHASEUNITTYPEID == 4) {
                        unittype = "ml";
                    } else if (activeproducttype.PURCHASEUNITTYPE == 5) {
                        unittype = activeproducttype.CUSTOMPURCHASEUNIT;
                    }
                } else if (activeproduct.UNITTYPEID == 1) {
                    unittype = "kg";
                } else if (activeproduct.UNITTYPEID == 2) {
                    unittype = "g";
                } else if (activeproduct.UNITTYPEID == 3) {
                    unittype = "l";
                } else if (activeproduct.UNITTYPEID == 4) {
                    unittype = "ml";
                }
                $("#unitname").val(unittype);
                $("#cost").currency("value", activeproduct.COSTPRICE);
                $("#unitprice").currency("value", activeproduct.RETAILPRICE);
                $("#total").val(activeproduct.UNITRATIO);
                $("#balance").val(activeproduct.UNITRATIO);
                $("#low").val(0);
                $("#namerow").fadeIn();
            });

            if (controller.newlevel == 1) {
                this.new_level();
            }

        },

        sync: function() {
            // If a viewlocation is given in the querystring, update the select
            if (common.querystring_param("viewlocation")) {
                $("#viewlocation").select("value", common.querystring_param("viewlocation"));
            }

            if (common.querystring_param("barcode")) {
                let barcode = common.querystring_param("barcode");
                let barcodefilter = $(".tablesorter-filter-row input[data-column='4']");
                barcodefilter.val(barcode);
                $("#tableform-toggle-filter").click();
            }
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        set_extra_fields: function(row) {
            row.STOCKLOCATIONNAME = common.get_field(controller.stocklocations, row.STOCKLOCATIONID, "LOCATIONNAME");
        },

        name: "stock_level",
        animation: "book",
        title: function() { return _("Stock levels"); },
        routes: {
            "stock_level": function() { common.module_loadandstart("stock_level", "stock_level?" + this.rawqs); }
        }

    };
    
    common.module_register(stock_level);

});
