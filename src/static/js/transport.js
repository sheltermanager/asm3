/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var transport = {};
    var statusmap = {
        1: _("New"),
        2: _("Confirmed"),
        3: _("Hold"),
        4: _("Scheduled"),
        10: _("Cancelled"),
        11: _("Completed")
    };
    var statuses = [
        { ID: 1, NAME: _("New") },
        { ID: 2, NAME: _("Confirmed") },
        { ID: 3, NAME: _("Hold") },
        { ID: 4, NAME: _("Scheduled") },
        { ID: 10, NAME: _("Cancelled") },
        { ID: 11, NAME: _("Completed") }
    ];
    var COMPLETED_STATUSES = 10;

    var dialog = {
        add_title: _("Add transport"),
        edit_title: _("Edit transport"),
        edit_perm: 'ctr',
        close_on_ok: false,
        columns: 2,
        fields: [
            { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal" },
            { json_field: "ANIMALS", post_field: "animals", label: _("Animals"), type: "animalmulti" },
            { json_field: "DRIVEROWNERID", post_field: "driver", label: _("Driver"), type: "person", personfilter: "driver" },
            { json_field: "STATUS", post_field: "status", label: _("Status"), type: "select", options: { rows: statuses, displayfield: "NAME", valuefield: "ID" }},
            { json_field: "MILES", post_field: "miles", label: _("Miles"), type: "number", defaultval: 0 },
            { json_field: "COST", post_field: "cost", label: _("Cost"), type: "currency", hideif: function() { return !config.bool("ShowCostAmount"); } },
            { json_field: "COSTPAIDDATE", post_field: "costpaid", label: _("Paid"), type: "date", hideif: function() { return !config.bool("ShowCostPaid"); } },
            { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" },
            { type: "nextcol" },
            { json_field: "PICKUPOWNERID", post_field: "pickup", label: _("Pickup"), personmode: "brief", type: "person" },
            { json_field: "PICKUPADDRESS", post_field: "pickupaddress", label: _("Address"), type: "text", validation: "notblank" },
            { json_field: "PICKUPTOWN", post_field: "pickuptown", label: _("City"), type: "text" },
            { json_field: "PICKUPCOUNTY", post_field: "pickupcounty", label: _("State"), type: "text" },
            { json_field: "PICKUPPOSTCODE", post_field: "pickuppostcode", label: _("Zipcode"), type: "text" },
            { json_field: "PICKUPDATETIME", post_field: "pickupdate", label: _("on"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "PICKUPDATETIME", post_field: "pickuptime", label: _("at"), type: "time", validation: "notblank", defaultval: format.time(new Date()) },
            { json_field: "DROPOFFOWNERID", post_field: "dropoff", label: _("Dropoff"), personmode: "brief", type: "person" },
            { json_field: "DROPOFFADDRESS", post_field: "dropoffaddress", label: _("Address"), type: "text", validation: "notblank" },
            { json_field: "DROPOFFTOWN", post_field: "dropofftown", label: _("City"), type: "text" },
            { json_field: "DROPOFFCOUNTY", post_field: "dropoffcounty", label: _("State"), type: "text" },
            { json_field: "DROPOFFPOSTCODE", post_field: "dropoffpostcode", label: _("Zipcode"), type: "text" },

            { json_field: "DROPOFFDATETIME", post_field: "dropoffdate", label: _("on"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "DROPOFFDATETIME", post_field: "dropofftime", label: _("at"), type: "time", validation: "notblank", defaultval: format.time(new Date()) }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                row.ANIMALNAME = $("#animal").animalchooser("get_selected").ANIMALNAME;
                row.SHELTERCODE = $("#animal").animalchooser("get_selected").SHELTERCODE;
                if (row.DRIVEROWNERID && row.DRIVEROWNERID != "0") { 
                    row.DRIVEROWNERNAME = $("#driver").personchooser("get_selected").OWNERNAME; 
                    row.DRIVEROWNERADDRESS = $("#driver").personchooser("get_selected").OWNERADDRESS; 
                    row.DRIVEROWNERTOWN = $("#driver").personchooser("get_selected").OWNERTOWN; 
                    row.DRIVEROWNERCOUNTY = $("#driver").personchooser("get_selected").OWNERCOUNTY; 
                    row.DRIVEROWNERPOSTCODE = $("#driver").personchooser("get_selected").OWNERPOSTCODE; 
                }
                if (row.PICKUPOWNERID && row.PICKUPOWNERID != "0") { 
                    row.PICKUPOWNERNAME = $("#pickup").personchooser("get_selected").OWNERNAME; 
                    row.PICKUPOWNERADDRESS = $("#pickup").personchooser("get_selected").OWNERADDRESS; 
                    row.PICKUPOWNERTOWN = $("#pickup").personchooser("get_selected").OWNERTOWN; 
                    row.PICKUPOWNERCOUNTY = $("#pickup").personchooser("get_selected").OWNERCOUNTY; 
                    row.PICKUPOWNERPOSTCODE = $("#pickup").personchooser("get_selected").OWNERPOSTCODE; 
                }
                if (row.DROPOFFOWNERID && row.DROPOFFOWNERID != "0") { 
                    row.DROPOFFOWNERNAME = $("#dropoff").personchooser("get_selected").OWNERNAME; 
                    row.DROPOFFOWNERADDRESS = $("#dropoff").personchooser("get_selected").OWNERADDRESS; 
                    row.DROPOFFOWNERTOWN = $("#dropoff").personchooser("get_selected").OWNERTOWN; 
                    row.DROPOFFOWNERCOUNTY = $("#dropoff").personchooser("get_selected").OWNERCOUNTY; 
                    row.DROPOFFOWNERPOSTCODE = $("#dropoff").personchooser("get_selected").OWNERPOSTCODE; 
                }
                tableform.fields_post(dialog.fields, "mode=update&transportid=" + row.ID, controller.name, function(response) {
                    tableform.table_update(table);
                    tableform.dialog_close();
                }, function() { 
                    tableform.dialog_enable_buttons();
                });
            }, function() {
                $("#animal").closest("tr").show();
                $("#animals").closest("tr").hide();
            });
        },
        complete: function(row) {
            return row.STATUS >= COMPLETED_STATUSES && row.DROPOFFDATETIME && format.date_js(row.DROPOFFDATETIME) < new Date();
        },
        overdue: function(row) {
            return row.STATUS < COMPLETED_STATUSES && row.PICKUPDATETIME && format.date_js(row.PICKUPDATETIME) < new Date() && !row.DROPOFFDATETIME;
        },
        columns: [
            { field: "STATUS", display: _("Status"),
                formatter: function(row) {
                    return "<span style=\"white-space: nowrap\">" +
                        "<input type=\"checkbox\" data-id=\"" + row.ID + "\" title=\"" + html.title(_("Select")) + "\" />" +
                        "<a href=\"#\" class=\"link-edit\" data-id=\"" + row.ID + "\">" + statusmap[row.STATUS] + "</a>" +
                        "</span>";
                }
            },
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
                    var s = "";
                    if (controller.name != "animal_transport") { s = html.animal_emblems(row) + " "; }
                    return s + '<a href="animal?id=' + row.ANIMALID + '">' + row.ANIMALNAME + ' - ' + row.SHELTERCODE + '</a>';
                },
                hideif: function(row) {
                    return controller.name.indexOf("animal_") != -1;
                }
            },
            { field: "DRIVER", display: _("Driver"), formatter: function(row) {
                    if (row.DRIVEROWNERID) {
                        return '<a href=person?id="' + row.DRIVEROWNERID + '">' + row.DRIVEROWNERNAME + '</a><br />' +
                            row.DRIVEROWNERADDRESS + "<br/>" + row.DRIVEROWNERTOWN + "<br />" + row.DRIVEROWNERCOUNTY + " " + row.DRIVEROWNERPOSTCODE;
                    }
                    return "";
                }
            },
            { field: "PICKUP", display: _("Pickup"), formatter: function(row) {
                    if (row.PICKUPOWNERID && row.PICKUPOWNERID != "0") {
                        return '<a href=person?id="' + row.PICKUPOWNERID + '">' + row.PICKUPOWNERNAME + '</a><br />' +
                            row.PICKUPADDRESS + "<br/>" + row.PICKUPTOWN + "<br />" + row.PICKUPCOUNTY + " " + row.PICKUPPOSTCODE;
                    }
                    return row.PICKUPADDRESS + "<br/>" + row.PICKUPTOWN + "<br/>" + row.PICKUPCOUNTY + "<br/>" + row.PICKUPPOSTCODE;
                }
            },
            { field: "PICKUPDATETIME", display: _("at"), initialsort: true, initialsortdirection: "desc",
                formatter: function(row) {
                    return format.date(row.PICKUPDATETIME) + " " + format.time(row.PICKUPDATETIME);
                }
            },
            { field: "DROPOFF", display: _("Dropoff"), formatter: function(row) {
                    if (row.DROPOFFOWNERID && row.DROPOFFOWNERID != "0") {
                        return '<a href=person?id="' + row.DROPOFFOWNERID + '">' + row.DROPOFFOWNERNAME + '</a><br />' +
                            row.DROPOFFADDRESS + "<br/>" + row.DROPOFFTOWN + "<br/>" + row.DROPOFFCOUNTY + "<br/>" + row.DROPOFFPOSTCODE;
                    }
                    return row.DROPOFFADDRESS + "<br/>" + row.DROPOFFTOWN + "<br/>" + row.DROPOFFCOUNTY + "<br/>" + row.DROPOFFPOSTCODE;
                }
            },
            { field: "DROPOFFDATETIME", display: _("at"), 
                formatter: function(row) {
                    return format.date(row.DROPOFFDATETIME) + " " + format.time(row.DROPOFFDATETIME);
                }
            },
            { field: "MILES", display: _("Miles") },
            { field: "COST", display: _("Cost"), formatter: tableform.format_currency,
                hideif: function() { return !config.bool("ShowCostAmount"); }
            },
            { field: "COSTPAIDDATE", display: _("Paid"), formatter: tableform.format_date,
                hideif: function() { return !config.bool("ShowCostPaid"); }
            },
            { field: "COMMENTS", display: _("Comments") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New Transport"), icon: "transport", enabled: "always", perm: "atr",
             click: function() { 
                 $("#driver").personchooser("clear");
                 $("#pickup").personchooser("clear");
                 $("#dropoff").personchooser("clear");
                 $("#animal").animalchooser("clear");
                 if (controller.animal) {
                    $("#animal").animalchooser("loadbyid", controller.animal.ID);
                 }
                 $("#animal").closest("tr").show();
                 $("#animals").closest("tr").hide();
                 tableform.dialog_show_add(dialog, function() {
                     tableform.fields_post(dialog.fields, "mode=create", controller.name, function(response) {
                         var row = {};
                         row.ID = response;
                         tableform.fields_update_row(dialog.fields, row);
                         row.ANIMALNAME = $("#animal").animalchooser("get_selected").ANIMALNAME;
                         row.SHELTERCODE = $("#animal").animalchooser("get_selected").SHELTERCODE;
                         if (row.DRIVEROWNERID && row.DRIVEROWNERID != "0") { 
                             row.DRIVEROWNERNAME = $("#driver").personchooser("get_selected").OWNERNAME; 
                             row.DRIVEROWNERADDRESS = $("#driver").personchooser("get_selected").OWNERADDRESS; 
                             row.DRIVEROWNERTOWN = $("#driver").personchooser("get_selected").OWNERTOWN; 
                             row.DRIVEROWNERCOUNTY = $("#driver").personchooser("get_selected").OWNERCOUNTY; 
                             row.DRIVEROWNERPOSTCODE = $("#driver").personchooser("get_selected").OWNERPOSTCODE; 
                         }
                         if (row.PICKUPOWNERID && row.PICKUPOWNERID != "0") { 
                             row.PICKUPOWNERNAME = $("#pickup").personchooser("get_selected").OWNERNAME; 
                             row.PICKUPOWNERADDRESS = $("#pickup").personchooser("get_selected").OWNERADDRESS; 
                             row.PICKUPOWNERTOWN = $("#pickup").personchooser("get_selected").OWNERTOWN; 
                             row.PICKUPOWNERCOUNTY = $("#pickup").personchooser("get_selected").OWNERCOUNTY; 
                             row.PICKUPOWNERPOSTCODE = $("#pickup").personchooser("get_selected").OWNERPOSTCODE; 
                         }
                         if (row.DROPOFFOWNERID && row.DROPOFFOWNERID != "0") { 
                             row.DROPOFFOWNERNAME = $("#dropoff").personchooser("get_selected").OWNERNAME; 
                             row.DROPOFFOWNERADDRESS = $("#dropoff").personchooser("get_selected").OWNERADDRESS; 
                             row.DROPOFFOWNERTOWN = $("#dropoff").personchooser("get_selected").OWNERTOWN; 
                             row.DROPOFFOWNERCOUNTY = $("#dropoff").personchooser("get_selected").OWNERCOUNTY; 
                             row.DROPOFFOWNERPOSTCODE = $("#dropoff").personchooser("get_selected").OWNERPOSTCODE; 
                         }
                         controller.rows.push(row);
                         tableform.table_update(table);
                         tableform.dialog_close();
                     }, function() {
                         tableform.dialog_enable_buttons();
                     });
                 }, function() { });
             } 
         },
         { id: "bulk", text: _("Bulk Transport"), icon: "transport", enabled: "always", perm: "atr", 
             hideif: function() { return controller.animal; }, 
             click: function() { 
                $("#animal").closest("tr").hide();
                $("#animals").closest("tr").show();
                $("#animals").animalchoosermulti("clear");
                $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
                tableform.dialog_show_add(dialog, function() {
                    tableform.fields_post(dialog.fields, "mode=createbulk", controller.name, function(response) {
                        window.location.reload();
                    }, function() {
                        tableform.dialog_enable_buttons();   
                    });
                });
            }
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dtr",
             click: function() { 
                 tableform.delete_dialog(function() {
                     tableform.buttons_default_state(buttons);
                     var ids = tableform.table_ids(table);
                     common.ajax_post(controller.name, "mode=delete&ids=" + ids , function() {
                         tableform.table_remove_selected_from_json(table, controller.rows);
                         tableform.table_update(table);
                     });
                 });
             } 
         },
         { id: "offset", type: "dropdownfilter", 
             options: [ "item|" + _("Due today"), "item2|" + _("Due in next week") ],
             click: function(selval) {
                window.location = controller.name + "?offset=" + selval;
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

    transport = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            if (controller.name.indexOf("animal_") == 0) {
                s += edit_header.animal_edit_header(controller.animal, "transport", controller.tabcounts);
            }
            else {
                s += html.content_header(controller.title);
            }
            s += tableform.buttons_render(buttons);
            s += tableform.table_render(table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
            
            // When we pickup and dropoff people, autofill the addresses
            $("#pickup").personchooser().bind("personchooserchange", function(event, rec) { 
                $("#pickupaddress").val(rec.OWNERADDRESS.replace("\n", ", "));
                $("#pickuptown").val(rec.OWNERTOWN);
                $("#pickupcounty").val(rec.OWNERCOUNTY);
                $("#pickuppostcode").val(rec.OWNERPOSTCODE);
            });
            $("#dropoff").personchooser().bind("personchooserchange", function(event, rec) { 
                $("#dropoffaddress").val(rec.OWNERADDRESS.replace("\n", ", "));
                $("#dropofftown").val(rec.OWNERTOWN);
                $("#dropoffcounty").val(rec.OWNERCOUNTY);
                $("#dropoffpostcode").val(rec.OWNERPOSTCODE);
            });

        },

        sync: function() {
            // If an offset is given in the querystring, update the select
            if (common.querystring_param("offset")) {
                $("#offset").select("value", common.querystring_param("offset"));
            }
        }

    };

    common.module(transport, "transport", "formtab");

});
