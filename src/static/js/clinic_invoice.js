/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const clinic_invoice = {

        model: function() {
            const dialog = {
                add_title: _("Add Invoice Item"),
                edit_title: _("Edit Invoice Item"),
                width: '550px',
                edit_perm: 'ccl',
                close_on_ok: false,
                fields: [
                    { json_field: "DESCRIPTION", post_field: "description", label: _("Description"), 
                        type: "autotext", validation: "notblank", doublesize: true, 
                        change: function() { 
                            if ($("#description").val() in clinic_invoice.invoiceitemsdict) {
                                $("#amount").val(format.currency(clinic_invoice.invoiceitemsdict[$("#description").val()]));
                            }
                        } },
                    { json_field: "AMOUNT", post_field: "amount", label: _("Amount"), type: "currency", validation: "notzero" }
                ]
            };
            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    try {
                        tableform.fields_populate_from_json(dialog.fields, row);
                        await tableform.dialog_show_edit(dialog, row);
                        tableform.fields_update_row(dialog.fields, row);
                        await tableform.fields_post(dialog.fields, "mode=update&appointmentid=" + controller.appointmentid + "&itemid=" + row.ID, "clinic_invoice");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    finally {
                        tableform.dialog_enable_buttons();
                    }
                },
                change: function(rows) {
                    $("#button-move").button("option", "disabled", true);
                    if (rows.length == 1 && !rows[0].STOCKUSAGEIDS) {
                        $("#button-move").button("option", "disabled", false);
                    }
                },
                columns: [
                    { field: "DESCRIPTION", display: _("Description") },
                    { field: "AMOUNT", display: _("Amount"), formatter: tableform.format_currency },
                    { field: "STOCKUSAGEIDS", display: _("Stock Deducted"), 
                        formatter: function(row) {
                            if (row.STOCKUSAGEIDS) {
                                return _("Yes");
                            } else {
                                return _("No");
                            }
                        }
                    }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Item"), icon: "new", enabled: "always", perm: "acl", 
                    click: async function() { 
                        try {
                            await tableform.dialog_show_add(dialog);
                            $.each($(".recentinvoiceitem"), function(i, v) {
                                let response = tableform.fields_post(dialog.fields, "mode=create&appointmentid=" + controller.appointmentid, "clinic_invoice");
                                let row = {};
                                row.ID = response;
                                tableform.fields_update_row(dialog.fields, row);
                                controller.rows.push(row);
                            });
                            let response = await tableform.fields_post(dialog.fields, "mode=create&appointmentid=" + controller.appointmentid, "clinic_invoice");
                            let row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
                            controller.rows.push(row);
                            tableform.table_update(table);
                            tableform.dialog_close();
                        }
                        finally {
                            tableform.dialog_enable_buttons();   
                        }
                    }
                },
                { id: "move", text: _("Move Stock"), icon: "stock-usage", enabled: "one", perm: "csl",
                    click: async function() {
                        clinic_invoice.move_product_init();
                        tableform.show_okcancel_dialog("#dialog-moveproduct", _("Move"), { 
                            width: 500, okclick: clinic_invoice.move_product, notblank: [ "movementfrom", "movementto" ] });
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dcl",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        var ids = tableform.table_ids(table);
                        await common.ajax_post("clinic_invoice", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        get_active_product: function() {
            let activeproductid = $("#movementproduct").val();
            let activeproduct = {};
            if (activeproductid != "0") {
                $.each(controller.products, function(i, v) {
                    if (v.ID == activeproductid) {
                        activeproduct = v;
                        return false;
                    }
                });
            }
            return activeproduct;
        },

        move_product_init: function() {
            $("#movementproduct").val("0");
            $("#movementunit").html('');
            $("#movementquantity").val("1");
            $("#movementfrom").val("L$" + config.integer(asm.user + "_DefaultStockLocationID"));
            $("#movementto").val("U$" + config.integer(asm.user + "_DefaultStockUsageTypeID"));
            $("#movementdate").val(format.date_now());
            $("#movementquantity").val(1);
        },

        move_product: async function() {
            let productid = $("#movementproduct").val();
            let activeproduct = clinic_invoice.get_active_product();
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
                invoiceid: tableform.table_selected_id(clinic_invoice.table),
                invoiceprice: tableform.table_selected_row(clinic_invoice.table).AMOUNT,
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
                comments: _("Move: {0} to {1}").replace("{0}", $("#movementfrom option:selected").text()).replace("{1}", $("#movementto option:selected").text()) + "\n" + $("#comments").val()
            };
            await common.ajax_post("product", formdata).then(function(result) {
                console.log("Moved.");
                console.log(result);
            });
            // common.route_reload();
        },

        render_moveproduct: function() {
            return [
                '<div id="dialog-moveproduct" style="display: none;width: 800px;" title="' + html.title(_("Move Product")) + '">',
                html.info(_("Move Stock.")),
                tableform.fields_render([
                { post_field: "movementproduct", json_field: "PRODUCTID", label: _("Product"), type: "select", validation: "notblank",
                    options: { rows: controller.products, displayfield: "PRODUCTNAME", prepend: '<option value="0"></option>' }
                 },
                { post_field: "movementquantity", json_field: "MOVEMENTQUANTITY", label: _("Quantity"), type: "intnumber", xmarkup: ' &times; ', rowclose: false, halfsize: true, validation: "notzero" },
                { post_field: "movementunit", json_field: "MOVEMENTUNIT", type: "select", justwidget: true, halfsize: true },
                { type: "rowclose" },
                { post_field: "movementdate", json_field: "MOVEMENTDATE", label: _("Date"), type: "date" },
                { post_field: "movementfrom", json_field: "MOVEMENTFROM", label: _("From"), type: "select", validation: "notblank" },
                { post_field: "movementto", json_field: "MOVEMENTTO", label: _("To"), type: "select", validation: "notblank" },
                { post_field: "batch", json_field: "BATCH", label: _("Batch"), type: "text" },
                { post_field: "expiry", json_field: "EXPIRY", label: _("Expiry"), type: "date" },
                { post_field: "comments", json_field: "COMMENTS", label: _("Comments"), type: "textarea" }
                ]),
                '</div>'
            ].join("\n");
        },

        render: function() {
            let h = [this.render_moveproduct(),];
            this.model();
            h.push(tableform.dialog_render(this.dialog));
            h.push(html.content_header(this.title()));
            h.push(html.info(_("Appointment {0}. {1} on {2} for {3}")
                .replace("{0}", format.padleft(controller.appointment.ID, 6))
                .replace("{1}", controller.appointment.OWNERNAME != null ? controller.appointment.OWNERNAME : _("Shelter"))
                .replace("{2}", format.date(controller.appointment.DATETIME) + " " + format.time(controller.appointment.DATETIME))
                .replace("{3}", controller.appointment.ANIMALNAME)
                ));
            h.push(tableform.buttons_render(this.buttons));
            h.push(tableform.table_render(this.table));
            h.push(html.content_footer());
            return h.join("\n");
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            $("#movementproduct").change(function() {
                let activeproductid = $("#movementproduct").val();
                if (activeproductid != "0") {
                    let activeproduct = clinic_invoice.get_active_product();
                    // $.each(controller.products, function(i, v) {
                    //     if (v.ID == activeproductid) {
                    //         activeproduct = v;
                    //     }
                    // });
                    console.log(activeproduct);
                    let purchaseunit = _("undefined");
                    if (activeproduct.PURCHASEUNITTYPEID == 0) {
                        purchaseunit = _("unit");
                    } 
                    else if (activeproduct.PURCHASEUNITTYPEID == -1) {
                        purchaseunit = activeproduct.CUSTOMPURCHASEUNIT;
                    } 
                    else {
                        purchaseunit = common.get_field(controller.units, activeproduct.PURCHASEUNITTYPEID, "UNITNAME");
                    }
                    let unit = _("undefined");
                    if (activeproduct.UNITTYPEID == 0) {
                        unit = purchaseunit;
                    } else if (activeproduct.UNITTYPEID == -1) {
                        unit = activeproduct.CUSTOMUNIT;
                    } else {
                        unit = common.get_field(controller.units, activeproduct.UNITTYPEID, "UNITNAME");
                    }
                    let units = [activeproduct.UNITRATIO + "|" + purchaseunit,];
                    if (activeproduct.UNITTYPEID != 0) {
                        units.push("1|" + unit);
                    }
                    $("#moveproductname").html(activeproduct.PRODUCTNAME);
                    $("#movementunit").html(html.list_to_options(units));
                    $("#movementunit").val($("#movementunit option").last().val());
                    $("#movementfrom").val("L$" + config.integer(asm.user + "_DefaultStockLocationID"));
                    $("#movementto").val("U$" + config.integer(asm.user + "_DefaultStockUsageTypeID"));
                } else {
                    clinic_invoice.move_product_init();
                }
            });
        },

        sync: function() {
            let sourcelist = [];
            clinic_invoice.invoiceitemsdict = {};
            $.each(controller.invoiceitems, function(i, v) {
                sourcelist.push(v.CLINICINVOICEITEMNAME);
                clinic_invoice.invoiceitemsdict[v.CLINICINVOICEITEMNAME] = v.DEFAULTCOST;
            });
            $("#description").autocomplete({source: sourcelist});
            let stocklocations = [];
            $.each(controller.stocklocations, function(i, v) {
                stocklocations.push("L$" + v.ID + "|" + v.LOCATIONNAME);
            });
            $.each(controller.stockusagetypes, function(i, v) {
                stocklocations.push("U$" + v.ID + "|" + v.USAGETYPENAME);
            });
            $("#movementfrom").html(html.list_to_options(stocklocations));
            $("#movementto").html(html.list_to_options(stocklocations));
        },

        validation: function() {
            if (!validate.notzero(["amount"])) { return false; }
            if (!validate.notblank([ "description" ])) { return false; }
            return true;
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "clinic_invoice",
        animation: "book",
        title:  function() { 
            return _("Clinic Invoice - {0}").replace("{0}", controller.appointment.OWNERNAME);
        },

        routes: {
            "clinic_invoice": function() { common.module_loadandstart("clinic_invoice", "clinic_invoice?" + this.rawqs); }
        }

    };
    
    common.module_register(clinic_invoice);

});
