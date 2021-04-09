/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const statusmap = {
        1: _("New"),
        2: _("Confirmed"),
        3: _("Hold"),
        4: _("Scheduled"),
        10: _("Cancelled"),
        11: _("Completed")
    };
    const statusmenu = [
        "1|" + _("New"),
        "2|" + _("Confirmed"),
        "3|" + _("Hold"),
        "4|" + _("Scheduled"),
        "10|" + _("Cancelled"),
        "11|" + _("Completed")
    ];

    const COMPLETED_STATUSES = 10;

    const transport = {

        model: function() {
            const dialog = {
                add_title: _("Add transport"),
                edit_title: _("Edit transport"),
                edit_perm: 'ctr',
                close_on_ok: false,
                resizable: true,
                columns: 2,
                fields: [
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal" },
                    { json_field: "ANIMALS", post_field: "animals", label: _("Animals"), type: "animalmulti" },
                    { json_field: "DRIVEROWNERID", post_field: "driver", label: _("Driver"), type: "person", personfilter: "driver" },
                    { json_field: "TRANSPORTREFERENCE", post_field: "reference", label: _("Reference"), type: "text" },
                    { json_field: "TRANSPORTTYPEID", post_field: "type", label: _("Type"), type: "select", options: { rows: controller.transporttypes, displayfield: "TRANSPORTTYPENAME", valuefield: "ID" }},
                    { json_field: "STATUS", post_field: "status", label: _("Status"), type: "select", options: { rows: controller.statuses, displayfield: "NAME", valuefield: "ID" }},
                    { json_field: "MILES", post_field: "miles", label: transport.miles_label(), type: "number", defaultval: 0 },
                    { json_field: "COST", post_field: "cost", label: _("Cost"), type: "currency", hideif: function() { return !config.bool("ShowCostAmount"); } },
                    { json_field: "COSTPAIDDATE", post_field: "costpaid", label: _("Paid"), type: "date", hideif: function() { return !config.bool("ShowCostPaid"); } },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" },
                    { type: "nextcol" },
                    { json_field: "PICKUPOWNERID", post_field: "pickup", label: _("Pickup"), personmode: "brief", type: "person" },
                    { json_field: "PICKUPADDRESS", post_field: "pickupaddress", label: _("Address"), type: "text", validation: "notblank" },
                    { json_field: "PICKUPTOWN", post_field: "pickuptown", label: _("City"), type: "text" },
                    { json_field: "PICKUPCOUNTY", post_field: "pickupcounty", label: _("State"), type: "text" },
                    { json_field: "PICKUPPOSTCODE", post_field: "pickuppostcode", label: _("Zipcode"), type: "text" },
                    { json_field: "PICKUPCOUNTRY", post_field: "pickupcountry", label: _("Country"), type: "text", 
                        hideif: function() { return config.bool("HideCountry"); }},
                    { json_field: "PICKUPDATETIME", post_field: "pickupdate", label: _("on"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "PICKUPDATETIME", post_field: "pickuptime", label: _("at"), type: "time", validation: "notblank", defaultval: format.time(new Date()) },
                    { json_field: "DROPOFFOWNERID", post_field: "dropoff", label: _("Dropoff"), personmode: "brief", type: "person" },
                    { json_field: "DROPOFFADDRESS", post_field: "dropoffaddress", label: _("Address"), type: "text", validation: "notblank" },
                    { json_field: "DROPOFFTOWN", post_field: "dropofftown", label: _("City"), type: "text" },
                    { json_field: "DROPOFFCOUNTY", post_field: "dropoffcounty", label: _("State"), type: "text" },
                    { json_field: "DROPOFFPOSTCODE", post_field: "dropoffpostcode", label: _("Zipcode"), type: "text" },
                    { json_field: "DROPOFFCOUNTRY", post_field: "dropoffcountry", label: _("Country"), type: "text", 
                        hideif: function() { return config.bool("HideCountry"); }},
                    { json_field: "DROPOFFDATETIME", post_field: "dropoffdate", label: _("on"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "DROPOFFDATETIME", post_field: "dropofftime", label: _("at"), type: "time", validation: "notblank", defaultval: format.time(new Date()) }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row, {
                        onchange: function() {
                            tableform.fields_update_row(dialog.fields, row);
                            transport.set_extra_fields(row);
                            tableform.fields_post(dialog.fields, "mode=update&transportid=" + row.ID, "transport", function(response) {
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }, function() { 
                                tableform.dialog_enable_buttons();
                            });
                        },
                        onload: function() {
                            $("#animal").closest("tr").show();
                            $("#animals").closest("tr").hide();
                        }
                    });
                },
                complete: function(row) {
                    return row.STATUS >= COMPLETED_STATUSES && row.DROPOFFDATETIME && format.date_js(row.DROPOFFDATETIME) < new Date();
                },
                overdue: function(row) {
                    return row.STATUS < COMPLETED_STATUSES && row.PICKUPDATETIME && format.date_js(row.PICKUPDATETIME) < new Date() && !row.DROPOFFDATETIME;
                },
                columns: [
                    { field: "TRANSPORTTYPENAME", display: _("Type") },
                    { field: "STATUS", display: _("Status"), formatter: function(row) { return statusmap[row.STATUS]; }},
                    { field: "TRANSPORTREFERENCE", display: _("Reference")},
                    { field: "IMAGE", display: "", 
                        formatter: function(row) {
                            if (!row.ANIMALID) { return ""; }
                            return '<a href="animal?id=' + row.ANIMALID + '"><img src=' + html.thumbnail_src(row, "animalthumb") + ' style="margin-right: 8px" class="asm-thumbnail thumbnailshadow" /></a>';
                        },
                        hideif: function(row) {
                            // Don't show this column if we're in the animal's record or the option is turned off
                            if (controller.name.indexOf("animal_") == 0 || !config.bool("PicturesInBooks")) {
                                return true;
                            }
                        }
                    },
                    { field: "ANIMAL", display: _("Animal"), 
                        formatter: function(row) {
                            if (!row.ANIMALID) { return ""; }
                            return html.animal_link(row, { noemblems: controller.name == "animal_transport" });
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("animal_") != -1;
                        }
                    },
                    { field: "DRIVER", display: _("Driver"), formatter: function(row) {
                            if (row.DRIVEROWNERID && common.has_permission("vo")) {
                                return html.person_link(row.DRIVEROWNERID, row.DRIVEROWNERNAME) + '<br />' +
                                    row.DRIVEROWNERADDRESS + "<br/>" + row.DRIVEROWNERTOWN + "<br />" + row.DRIVEROWNERCOUNTY + " " + row.DRIVEROWNERPOSTCODE +
                                    (!config.bool("HideCountry") ? "<br/>" + row.DRIVEROWNERCOUNTRY : "");
                            }
                            return "";
                        }
                    },
                    { field: "PICKUP", display: _("Pickup"), formatter: function(row) {
                            if (row.PICKUPOWNERID && common.has_permission("vo")) {
                                return html.person_link(row.PICKUPOWNERID, row.PICKUPOWNERNAME) + '<br />' +
                                    row.PICKUPADDRESS + "<br/>" + row.PICKUPTOWN + "<br />" + row.PICKUPCOUNTY + " " + 
                                    row.PICKUPPOSTCODE + 
                                    (!config.bool("HideCountry") ? "<br/>" + row.PICKUPCOUNTRY : "");
                            }
                            else {
                                return row.PICKUPADDRESS + "<br/>" + row.PICKUPTOWN + "<br/>" + row.PICKUPCOUNTY + 
                                    "<br/>" + row.PICKUPPOSTCODE + 
                                    (!config.bool("HideCountry") ? "<br/>" + row.PICKUPCOUNTRY : "");
                            }
                        }
                    },
                    { field: "PICKUPDATETIME", display: _("at"), initialsort: true, initialsortdirection: "desc",
                        formatter: function(row) {
                            return format.date(row.PICKUPDATETIME) + " " + format.time(row.PICKUPDATETIME);
                        }
                    },
                    { field: "DROPOFF", display: _("Dropoff"), formatter: function(row) {
                            if (row.DROPOFFOWNERID && common.has_permission("vo")) {
                                return html.person_link(row.DROPOFFOWNERID, row.DROPOFFOWNERNAME) + '<br />' +
                                    row.DROPOFFADDRESS + "<br/>" + row.DROPOFFTOWN + "<br/>" + row.DROPOFFCOUNTY + 
                                    "<br/>" + row.DROPOFFPOSTCODE + 
                                    (!config.bool("HideCountry") ? "<br/>" + row.DROPOFFCOUNTRY : "");
                            }
                            else {
                                return row.DROPOFFADDRESS + "<br/>" + row.DROPOFFTOWN + "<br/>" + row.DROPOFFCOUNTY + 
                                    "<br/>" + row.DROPOFFPOSTCODE + 
                                    (!config.bool("HideCountry") ? "<br/>" + row.DROPOFFCOUNTRY : "");
                            }
                        }
                    },
                    { field: "DROPOFFDATETIME", display: _("at"), 
                        formatter: function(row) {
                            return format.date(row.DROPOFFDATETIME) + " " + format.time(row.DROPOFFDATETIME);
                        }
                    },
                    { field: "MILES", display: transport.miles_label() },
                    { field: "COST", display: _("Cost"), formatter: tableform.format_currency,
                        hideif: function() { return !config.bool("ShowCostAmount"); }
                    },
                    { field: "COSTPAIDDATE", display: _("Paid"), formatter: tableform.format_date,
                        hideif: function() { return !config.bool("ShowCostPaid"); }
                    },
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Transport"), icon: "transport", enabled: "always", perm: "atr",
                    click: async function() { 
                        $("#driver").personchooser("clear");
                        $("#pickup").personchooser("clear");
                        $("#dropoff").personchooser("clear");
                        $("#animal").animalchooser("clear");
                        if (controller.animal) {
                            $("#animal").animalchooser("loadbyid", controller.animal.ID);
                        }
                        $("#animal").closest("tr").show();
                        $("#animals").closest("tr").hide();
                        await tableform.dialog_show_add(dialog);
                        try {
                            let response = await tableform.fields_post(dialog.fields, "mode=create", "transport");
                            let row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
                            transport.set_extra_fields(row);
                            controller.rows.push(row);
                            tableform.table_update(table);
                            tableform.dialog_close();
                        }
                        catch(err) {
                            log.error(err, err);
                            tableform.dialog_enable_buttons();
                        }
                    } 
                },
                { id: "bulk", text: _("Bulk Transport"), icon: "transport", enabled: "always", perm: "atr", 
                    hideif: function() { return controller.animal; }, 
                    click: async function() { 
                        $("#animal").closest("tr").hide();
                        $("#animals").closest("tr").show();
                        $("#animals").animalchoosermulti("clear");
                        $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
                        await tableform.dialog_show_add(dialog);
                        try {
                            await tableform.fields_post(dialog.fields, "mode=createbulk", "transport");
                            common.route_reload();
                        }
                        catch(err) {
                            log.error(err, err);
                            tableform.dialog_enable_buttons();   
                        }
                    }
                },
                { id: "clone", text: _("Clone"), icon: "copy", enabled: "one", perm: "atr",
                    hideif: function() { return controller.animal; }, 
                    click: async function() { 
                        $("#animal").closest("tr").hide();
                        $("#animals").closest("tr").show();
                        $("#animals").animalchoosermulti("clear");
                        $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
                        await tableform.dialog_show_add(dialog, {
                                onload: function() {
                                     let row = tableform.table_selected_row(table);
                                     tableform.fields_populate_from_json(dialog.fields, row);
                                }
                            });
                        try {
                            await tableform.fields_post(dialog.fields, "mode=createbulk", "transport");
                            common.route_reload();
                        }
                        catch(err) {
                            log.error(err, err);
                            tableform.dialog_enable_buttons();   
                        }
                    }
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dtr",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("transport", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "setstatus", text: _("Status"), icon: "complete", type: "buttonmenu", options: statusmenu, enabled: "multi", perm: "ctr", 
                    click: async function(newstatus) {
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("transport", "mode=setstatus&ids=" + ids + "&newstatus=" + newstatus);
                        $.each(tableform.table_selected_rows(table), function(i, v) {
                            v.STATUS = newstatus;
                        });
                        tableform.table_update(table);
                    }
                },
                { id: "document", text: _("Document"), icon: "document", enabled: "multi", perm: "gaf", 
                    tooltip: _("Generate document from this transport"), type: "buttonmenu" },
                { id: "offset", type: "dropdownfilter", 
                    options: [ "item|" + _("Due today"), "item2|" + _("Due in next week") ],
                    click: function(selval) {
                        common.route(controller.name + "?offset=" + selval);
                    },
                    hideif: function(row) {
                        // TODO: Don't show at all for now, not sure what this will be
                        return true;
                        // Don't show for animal records
                        //if (controller.animal) {
                        //    return true;
                        //}
                    }
                }

            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        /**
         * Sets extra json fields according to what the user has picked. Call
         * this after updating a json row for entered fields to get the
         * extra lookup fields.
         */
        set_extra_fields: function(row) {
            row.ANIMALNAME = $("#animal").animalchooser("get_selected").ANIMALNAME;
            row.SHELTERCODE = $("#animal").animalchooser("get_selected").SHELTERCODE;
            row.TRANSPORTTYPENAME = common.get_field(controller.transporttypes, row.TRANSPORTTYPEID, "TRANSPORTTYPENAME");
            if (row.DRIVEROWNERID && row.DRIVEROWNERID != "0") { 
                row.DRIVEROWNERNAME = $("#driver").personchooser("get_selected").OWNERNAME; 
                row.DRIVEROWNERADDRESS = $("#driver").personchooser("get_selected").OWNERADDRESS; 
                row.DRIVEROWNERTOWN = $("#driver").personchooser("get_selected").OWNERTOWN; 
                row.DRIVEROWNERCOUNTY = $("#driver").personchooser("get_selected").OWNERCOUNTY; 
                row.DRIVEROWNERPOSTCODE = $("#driver").personchooser("get_selected").OWNERPOSTCODE; 
                row.DRIVEROWNERCOUNTRY = $("#driver").personchooser("get_selected").OWNERCOUNTRY; 
            }
            if (row.PICKUPOWNERID && row.PICKUPOWNERID != "0") { 
                row.PICKUPOWNERNAME = $("#pickup").personchooser("get_selected").OWNERNAME; 
                row.PICKUPOWNERADDRESS = $("#pickup").personchooser("get_selected").OWNERADDRESS; 
                row.PICKUPOWNERTOWN = $("#pickup").personchooser("get_selected").OWNERTOWN; 
                row.PICKUPOWNERCOUNTY = $("#pickup").personchooser("get_selected").OWNERCOUNTY; 
                row.PICKUPOWNERPOSTCODE = $("#pickup").personchooser("get_selected").OWNERPOSTCODE; 
                row.PICKUPOWNERCOUNTRY = $("#pickup").personchooser("get_selected").OWNERCOUNTRY; 
            }
            if (row.DROPOFFOWNERID && row.DROPOFFOWNERID != "0") { 
                row.DROPOFFOWNERNAME = $("#dropoff").personchooser("get_selected").OWNERNAME; 
                row.DROPOFFOWNERADDRESS = $("#dropoff").personchooser("get_selected").OWNERADDRESS; 
                row.DROPOFFOWNERTOWN = $("#dropoff").personchooser("get_selected").OWNERTOWN; 
                row.DROPOFFOWNERCOUNTY = $("#dropoff").personchooser("get_selected").OWNERCOUNTY; 
                row.DROPOFFOWNERPOSTCODE = $("#dropoff").personchooser("get_selected").OWNERPOSTCODE; 
                row.DROPOFFOWNERCOUNTRY = $("#dropoff").personchooser("get_selected").OWNERCOUNTRY; 
            }
        }, 

        /**
         * Returns the label as miles or km based on locale
         */
        miles_label: function() {
            if (asm.locale == "en" || asm.locale == "en_GB") {
                return _("Miles");
            }
            return _("Km");
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += '<div id="button-document-body" class="asm-menu-body">' +
                '<ul class="asm-menu-list">' +
                edit_header.template_list(controller.templates, "TRANSPORT", 0) +
                '</ul></div>';
            if (controller.name.indexOf("animal_") == 0) {
                s += edit_header.animal_edit_header(controller.animal, "transport", controller.tabcounts);
            }
            else {
                s += html.content_header(this.title());
            }
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            
            // When we pickup and dropoff people, autofill the addresses
            $("#pickup").personchooser().bind("personchooserchange", function(event, rec) { 
                $("#pickupaddress").val(html.decode(rec.OWNERADDRESS.replace("\n", ", ")));
                $("#pickuptown").val(html.decode(rec.OWNERTOWN));
                $("#pickupcounty").val(html.decode(rec.OWNERCOUNTY));
                $("#pickuppostcode").val(html.decode(rec.OWNERPOSTCODE));
                $("#pickupcountry").val(html.decode(rec.OWNERCOUNTRY));
            });
            $("#dropoff").personchooser().bind("personchooserchange", function(event, rec) { 
                $("#dropoffaddress").val(html.decode(rec.OWNERADDRESS.replace("\n", ", ")));
                $("#dropofftown").val(html.decode(rec.OWNERTOWN));
                $("#dropoffcounty").val(html.decode(rec.OWNERCOUNTY));
                $("#dropoffpostcode").val(html.decode(rec.OWNERPOSTCODE));
                $("#dropoffcountry").val(html.decode(rec.OWNERCOUNTRY));
            });

            // Add click handlers to templates
            $(".templatelink").click(function() {
                // Update the href as it is clicked so default browser behaviour
                // continues on to open the link in a new window
                let template_name = $(this).attr("data");
                let ids = tableform.table_ids(transport.table);
                $(this).prop("href", "document_gen?linktype=TRANSPORT&id=" + ids + "&dtid=" + template_name);
            });

        },

        sync: function() {
            // If an offset is given in the querystring, update the select
            if (common.querystring_param("offset")) {
                $("#offset").select("value", common.querystring_param("offset"));
            }
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#driver", "personchooser");
            common.widget_destroy("#pickup", "personchooser");
            common.widget_destroy("#dropoff", "personchooser");
            tableform.dialog_destroy();
        },


        name: "transport",
        animation: function() { return controller.name == "transport" ? "book" : "formtab"; },
        title:  function() { 
            let t = "";
            if (controller.name == "animal_transport") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "transport") { t = _("Transport Book"); }
            return t;
        },

        routes: {
            "animal_transport": function() { common.module_loadandstart("transport", "animal_transport?id=" + this.qs.id); },
            "transport": function() { common.module_loadandstart("transport", "transport?" + this.rawqs); }
        }


    };

    common.module_register(transport);

});
