/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const stocklevel = {

        model: function() {
            const dialog = {
                add_title: _("Add stock"),
                edit_title: _("Edit stock"),
                edit_perm: 'csl',
                close_on_ok: false,
                hide_read_only: true,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "NAME", post_field: "name", label: _("Name"), type: "text", validation: "notblank" },
                    { json_field: "DESCRIPTION", post_field: "description", label: _("Description"), type: "textarea" },
                    { json_field: "", post_field: "quantity", label: _("Quantity"), type: "intnumber", validation: "notblank", defaultval: "1", readonly: true, 
                        callout: _("The number of stock records to create") },
                    { json_field: "STOCKLOCATIONID", post_field: "location", label: _("Location"), type: "select", 
                        options: { displayfield: "LOCATIONNAME", valuefield: "ID", rows: controller.stocklocations }},
                    { json_field: "UNITNAME", post_field: "unitname", label: _("Units"), type: "text", validation: "notblank",
                        callout: _("The type of unit in the container, eg: tablet, vial, etc.") },
                    { json_field: "TOTAL", post_field: "total", label: _("Total"), type: "number", 
                        callout: _("Total number of units in the container") },
                    { json_field: "BALANCE", post_field: "balance", label: _("Balance"), type: "number", validation: "notblank",
                        callout: _("The remaining units in the container") },
                    { json_field: "BATCHNUMBER", post_field: "batchnumber", label: _("Batch"), type: "text", 
                        callout: _("If this stock record is for a drug, the batch number from the container") },
                    { json_field: "EXPIRY", post_field: "expiry", label: _("Expiry"), type: "date",
                        callout: _("If this stock record is for a perishable good, the expiry date on the container") },
                    { json_field: "COST", post_field: "cost", label: _("Cost"), type: "currency",
                        callout: _("The wholesale/trade price the container was bought for") },
                    { json_field: "UNITPRICE", post_field: "unitprice", label: _("Unit Price"), type: "currency",
                        callout: _("The retail/resale price per unit") },
                    { type: "raw", label: "", markup: html.info(_("Usage explains why this stock record was created or adjusted. Usage records will only be created if the balance changes.")) },
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
                    tableform.dialog_show_edit(dialog, row, {
                        onchange: function() {
                            tableform.fields_update_row(dialog.fields, row);
                            stocklevel.set_extra_fields(row);
                            tableform.fields_post(dialog.fields, "mode=update&stocklevelid=" + row.ID, "stocklevel")
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
                            $("#usagedate").datepicker("setDate", new Date());
                            $("#usagetype").select("firstvalue");
                            $("#quantity").val("1"); // Ignored during edit but validated
                            stocklevel.hide_usage_fields();
                        }
                    });
                },
                complete: function(row) {
                    if (!row.BALANCE) { return true; }
                    return false;
                },
                overdue: function(row) {
                    return row.EXPIRY && format.date_js(row.EXPIRY) <= common.today_no_time();
                },
                columns: [
                    { field: "NAME", display: _("Name"), initialsort: controller.sortexp != 1 },
                    { field: "STOCKLOCATIONNAME", display: _("Location") },
                    { field: "UNITNAME", display: _("Unit") },
                    { field: "BALANCE", display: _("Balance"), formatter: function(row) {
                        return row.BALANCE + " / " + row.TOTAL;
                    }},
                    { field: "COST", display: _("Cost"), formatter: tableform.format_currency },
                    { field: "UNITPRICE", display: _("Unit Price"), formatter: tableform.format_currency },
                    { field: "BATCHNUMBER", display: _("Batch") },
                    { field: "EXPIRY", display: _("Expiry"), formatter: tableform.format_date, initialsort: controller.sortexp == 1 },
                    { field: "DESCRIPTION", display: _("Description") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Stock"), icon: "new", enabled: "always", perm: "asl", 
                    click: function() { stocklevel.new_level(); }},
                { id: "clone", text: _("Clone"), icon: "copy", enabled: "one", perm: "asl",
                    click: function() { stocklevel.clone_level(); }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dsl", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("stocklevel", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "viewlocation", type: "dropdownfilter", 
                    options: '<option value="0">' + _("(all)") + '</option>' + 
                        '<option value="-1">' + _("(depleted)") + '</option>' + 
                        html.list_to_options(controller.stocklocations, "ID", "LOCATIONNAME"),
                    click: function(selval) {
                        common.route("stocklevel?viewlocation=" + selval);
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
            s += html.content_header(_("Stock"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        new_level: function() { 
            let dialog = stocklevel.dialog, table = stocklevel.table;
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", "stocklevel")
                        .then(function(response) {
                            // If more than one record was created, reload the screen
                            if ($("#quantity").val() != "1") {
                                tableform.dialog_close();
                                common.route_reload();
                            }
                            else {
                                let row = {};
                                row.ID = response;
                                tableform.fields_update_row(dialog.fields, row);
                                stocklevel.set_extra_fields(row);
                                controller.rows.push(row);
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();   
                        });
                },
                onload: function() {
                    stocklevel.show_usage_fields();
                    $("#usagetype").select("firstvalue");
                }
            });
        },

        clone_level: function() { 
            let dialog = stocklevel.dialog, table = stocklevel.table;
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", "stocklevel")
                        .then(function(response) {
                            // If more than one record was created, reload the screen
                            if ($("#quantity").val() != "1") {
                                tableform.dialog_close();
                                common.route_reload();
                            }
                            else {
                                let row = {};
                                row.ID = response;
                                tableform.fields_update_row(dialog.fields, row);
                                stocklevel.set_extra_fields(row);
                                controller.rows.push(row);
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();
                        });
                },
                onload: function() {
                    let row = tableform.table_selected_row(table);
                    tableform.fields_populate_from_json(dialog.fields, row);
                    $("#name").val(_("Copy of {0}").replace("{0}", $("#name").val()));
                    stocklevel.show_usage_fields();
                    $("#usagetype").select("firstvalue");
                    $("#usagedate").datepicker("setDate", new Date());
                    $("#quantity").val("1"); 
                }
            });
        },

        hide_usage_fields: function() {
            $("#usagetype").closest("tr").prev().hide();
            $("#usagetype").closest("tr").hide();
            $("#usagedate").closest("tr").hide();
            $("#comments").closest("tr").hide();
        },

        show_usage_fields: function() {
            $("#usagetype").closest("tr").prev().fadeIn();
            $("#usagetype").closest("tr").fadeIn();
            $("#usagedate").closest("tr").fadeIn();
            $("#comments").closest("tr").fadeIn();
        },
        
        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            // If the user edits the balance, prompt for usage info
            $("#balance").change(stocklevel.show_usage_fields);

            // If the user edits the total and balance is blank, default it to total
            $("#total").change(function() {
                if (!$("#balance").val()) {
                    $("#balance").val($("#total").val());
                }
            });

            // If the user changes the name and we don't have a description or unit,
            // look up the last stock we saw with that name to autocomplete
            $("#name").change(function() {
                if (!$("#description").val() && !$("#unitname").val()) {
                    common.ajax_post("stocklevel", "mode=lastname&name=" + $("#name").val())
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

            if (controller.newlevel == 1) {
                this.new_level();
            }

        },

        sync: function() {
            // If a viewlocation is given in the querystring, update the select
            if (common.querystring_param("viewlocation")) {
                $("#viewlocation").select("value", common.querystring_param("viewlocation"));
            }

            $("#name").autocomplete({ source: html.decode(controller.stocknames.split("|")) });
            $("#name").autocomplete("option", "appendTo", "#dialog-tableform");
            $("#unitname").autocomplete({ source: html.decode(controller.stockunits.split("|")) });
            $("#unitname").autocomplete("option", "appendTo", "#dialog-tableform");

        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        set_extra_fields: function(row) {
            row.STOCKLOCATIONNAME = common.get_field(controller.stocklocations, row.STOCKLOCATIONID, "LOCATIONNAME");
        },

        name: "stocklevel",
        animation: "book",
        title: function() { return _("Stock"); },
        routes: {
            "stocklevel": function() { common.module_loadandstart("stocklevel", "stocklevel?" + this.rawqs); }
        }

    };
    
    common.module_register(stocklevel);

});
