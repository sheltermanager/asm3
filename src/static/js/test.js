/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const test = {

        lastanimal: null,
        lastvet: null,

        model: function() {
            const dialog = {
                add_title: _("Add test"),
                edit_title: _("Edit test"),
                edit_perm: 'cat',
                close_on_ok: false,
                use_default_values: false,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal" },
                    { json_field: "ANIMALS", post_field: "animals", label: _("Animals"), type: "animalmulti" },
                    { json_field: "TESTTYPEID", post_field: "type", label: _("Type"), type: "select", 
                        options: { displayfield: "TESTNAME", valuefield: "ID", rows: controller.testtypes }},
                    { json_field: "DATEREQUIRED", post_field: "required", label: _("Required"), type: "date", validation: "notblank" },
                    { json_field: "DATEOFTEST", post_field: "given", label: _("Performed"), type: "date" },
                    { json_field: "TESTRESULTID", post_field: "result", label: _("Result"), type: "select", 
                        options: { displayfield: "RESULTNAME", valuefield: "ID", rows: controller.testresults }},
                    { json_field: "ADMINISTERINGVETID", post_field: "administeringvet", label: _("Administering Vet"), type: "person", personfilter: "vet" },
                    { json_field: "COST", post_field: "cost", label: _("Cost"), type: "currency", hideif: function() { return !config.bool("ShowCostAmount"); } },
                    { json_field: "COSTPAIDDATE", post_field: "costpaid", label: _("Paid"), type: "date", hideif: function() { return !config.bool("ShowCostPaid"); } },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    if (controller.animal) {
                        $("#animalrow").hide();
                    }
                    else {
                        $("#animalrow").show();
                    }
                    $("#animalsrow").hide();
                    $("#administeringvet").personchooser("clear");
                    test.enable_default_cost = false;
                    tableform.fields_populate_from_json(dialog.fields, row);
                    test.enable_default_cost = true;
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    test.set_extra_fields(row);
                    try {
                        await tableform.fields_post(dialog.fields, "mode=update&testid=" + row.ID, "test");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err); 
                        tableform.dialog_enable_buttons();
                    }
                },
                complete: function(row) {
                    if (row.DATEOFTEST) { return true; }
                    return false;
                },
                overdue: function(row) {
                    return !row.DATEOFTEST && format.date_js(row.DATEREQUIRED) < common.today_no_time();
                },
                columns: [
                    { field: "TESTNAME", display: _("Type") },
                    { field: "IMAGE", display: "", 
                        formatter: function(row) {
                            return html.animal_link_thumb_bare(row);
                        },
                        hideif: function(row) {
                            // Don't show this column if we're in an animal record, or the option is turned off
                            if (controller.animal || !config.bool("PicturesInBooks")) {
                                return true;
                            }
                        }
                    },
                    { field: "ANIMAL", display: _("Animal"), 
                        formatter: function(row) {
                            return html.animal_link(row, { noemblems: controller.name == "animal_test" });
                        },
                        hideif: function(row) {
                            // Don't show for animal records
                            if (controller.animal) { return true; }
                        }
                    },
                    { field: "ACCEPTANCENUMBER", display: _("Litter"),
                        hideif: function(row) {
                            if (controller.animal) { return true; }
                            return config.bool("DontShowLitterID");
                        }
                    },
                    { field: "SPECIESNAME", display: _("Species"),
                        hideif: function(row) {
                            // Don't show for animal records
                            if (controller.animal) { return true; }
                        }
                    },
                    { field: "LOCATIONNAME", display: _("Location"),
                        formatter: function(row) {
                            let s = row.LOCATIONNAME;
                            if (row.LOCATIONUNIT) {
                                s += ' <span class="asm-search-locationunit">' + row.LOCATIONUNIT + '</span>';
                            }
                            if (row.ACTIVEMOVEMENTID && row.CURRENTOWNERID && row.CURRENTOWNERNAME) {
                                s += '<br/>' + html.person_link(row.CURRENTOWNERID, row.CURRENTOWNERNAME);
                            }
                            return s;
                        },
                        hideif: function(row) {
                             // Don't show for animal records
                            if (controller.animal) { return true; }
                        }
                    },
                    { field: "DATEREQUIRED", display: _("Required"), formatter: tableform.format_date, initialsort: true, 
                        initialsortdirection: controller.name == "test" ? "asc" : "desc" },
                    { field: "DATEOFTEST", display: _("Performed"), formatter: tableform.format_date },
                    { field: "RESULTNAME", display: _("Result"), formatter: function(row) {
                            if (row.DATEOFTEST) {
                                return row.RESULTNAME;
                            }
                            return "";
                        }},
                    { field: "ADMINISTERINGVET", display: _("Vet"), 
                        formatter: function(row) {
                            if (!row.ADMINISTERINGVETID) { return ""; }
                            return html.person_link(row.ADMINISTERINGVETID, row.ADMINISTERINGVETNAME);
                        }
                    },
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
                { id: "new", text: _("New Test"), icon: "new", enabled: "always", perm: "aat", 
                    click: function() { test.new_test(); }},
                { id: "bulk", text: _("Bulk Test"), icon: "new", enabled: "always", perm: "cat", 
                    hideif: function() { return controller.animal; }, click: function() { test.new_bulk_test(); }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dat", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("test", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "perform", text: _("Perform"), icon: "complete", enabled: "multi", perm: "cat",
                    click: function() {
                        let comments = "", testtype = 0;
                        $.each(controller.rows, function(i, v) {
                            if (tableform.table_id_selected(v.ID)) {
                                comments += "[" + v.SHELTERCODE + " - " + v.ANIMALNAME + "] ";
                                testtype = v.TESTTYPEID;
                            }
                        });
                        $("#usagecomments").html(comments);
                        $("#newdate").date("today");
                        $("#restestdate").val("");
                        let rd = test.calc_reschedule_date(new Date(), testtype);
                        if (rd) { $("#retestdate").date("setDate", rd); }
                        $("#givencost").currency("value", tableform.table_selected_row(table).COST);
                        $("#testresult").select("firstvalue");
                        $("#usagetype").select("firstvalue");
                        $("#usagedate").date("today");
                        $("#usagedaterow").hide();
                        $("#quantity").val("0");
                        // Default animal's current vet if set and this is an animal test tab
                        if (controller.animal && controller.animal.CURRENTVETID) { 
                            $("#givenvet").personchooser("loadbyid", controller.animal.CURRENTVETID); 
                        }
                        $("#dialog-given").dialog("open");
                    }
                },
                { id: "offset", type: "dropdownfilter", 
                    options: [ "m365|" + _("Due today"), "p7|" + _("Due in next week"), 
                        "p31|" + _("Due in next month"), "p365|" + _("Due in next year"), 
                        "g1|" + _("Given today"), "g7|" + _("Given in last week"),
                        "g31|" + _("Given in last month") ],
                    click: function(selval) {
                        common.route(controller.name + "?offset=" + selval);
                    },
                    hideif: function(row) {
                        // Don't show for animal records
                        if (controller.animal) {
                            return true;
                        }
                    }
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += test.render_givendialog();
            if (controller.animal) {
                s += edit_header.animal_edit_header(controller.animal, "test", controller.tabcounts);
            }
            else {
                s += html.content_header(_("Test Book"));
            }
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        new_test: function() { 
            let dialog = test.dialog, table = test.table;
            tableform.dialog_show_add(dialog, {
                onvalidate: function() {
                    return validate.notzero([ "animal" ]);
                },
                onadd: async function() {
                    try {
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "test");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        test.set_extra_fields(row);
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err);
                        tableform.dialog_enable_buttons();   
                    }
                },
                onload: function() {
                    if (controller.animal) {
                        $("#animal").animalchooser("loadbyid", controller.animal.ID);
                        $("#animalrow").hide();
                    }
                    else {
                        $("#animalrow").show();
                        $("#animal").animalchooser("clear");
                    }
                    $("#animalsrow").hide();
                    $("#administeringvet").personchooser("clear");
                    $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
                    $("#type").select("value", config.str("AFDefaultTestType"));
                    test.enable_default_cost = true;
                    test.set_default_cost();
                }
            });
        },

        new_bulk_test: function() { 
            let dialog = test.dialog, table = test.table;
            tableform.dialog_show_add(dialog, {
                onvalidate: function() {
                    return validate.notblank([ "animals" ]);
                },
                onadd: async function() {
                    try {
                        await tableform.fields_post(dialog.fields, "mode=createbulk", "test");
                        tableform.dialog_close();
                        common.route_reload();
                    }
                    catch(err) {
                        log.error(err, err);
                        tableform.dialog_enable_buttons();   
                    }
                },
                onload: function() {
                    $("#animalrow").hide();
                    $("#animalsrow").show();
                    $("#animals").animalchoosermulti("clear");
                    $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
                    $("#type").select("value", config.str("AFDefaultTestType"));
                    test.enable_default_cost = true;
                    test.set_default_cost();
                }
            });
        },

        render_givendialog: function() {
            return [
                '<div id="dialog-given" style="display: none" title="' + html.title(_("Perform Test")) + '">',
                tableform.fields_render([
                    { post_field: "newdate", type: "date", label: _("Performed") },
                    { post_field: "testresult", type: "select", label: _("Result"), 
                        options: { displayfield: "RESULTNAME", rows: controller.testresults }},
                    { post_field: "retestdate", type: "date", label: _("Retest"), nopast: true },
                    { post_field: "givencost", type: "currency", label: _("Cost") },
                    { post_field: "givenvet", type: "person", label: _("Administering Vet"), personfilter: "vet" },
                    { type: "raw", fullrow: true, rowclasses: "tagstock", 
                        markup: '<p class="asm-header">' + _("Stock") + 
                            ' <span id="callout-stock" class="asm-callout">' + 
                            _("These fields allow you to deduct stock for the test(s) given. This single deduction should cover the selected tests being performed.") + 
                            '</span></p>' },
                    { post_field: "item", type: "select", label: _("Item"), rowclasses: "tagstock", 
                        options: { displayfield: "ITEMNAME", rows: controller.stockitems, prepend: '<option value="-1">' + _("(no deduction)") + '</option>'} },
                    { post_field: "quantity", type: "number", label: _("Quantity"), rowclasses: "tagstock" },
                    { post_field: "usagetype", type: "select", label: _("Usage Type"), rowclasses: "tagstock", 
                        options: { displayfield: "USAGETYPENAME", rows: controller.stockusagetypes}},
                    { post_field: "usagedate", type: "date", label: _("Usage Date"), rowclasses: "tagstock" },
                    { post_field: "usagecomments", type: "textarea", label: _("Comments"), rowclasses: "tagstock" }
                ]),
                '</div>'
            ].join("\n");
        },

        bind_givendialog: function() {
            let givenbuttons = { };
            let dialog = test.dialog, table = test.table;
            $("#item").change(function() {
                let si = common.get_row(controller.stockitems, $("#item").val(), "ID");
                $("#givencost").currency("value", si.UNITPRICE);
            });
            givenbuttons[_("Perform")] = {
                text: _("Perform"),
                "class": "asm-dialog-actionbutton",
                click: async function() {
                    validate.reset("dialog-given");
                    if (!validate.notblank([ "newdate" ])) { return; }
                    $("#usagedate").val($("#newdate").val()); // copy given to usage
                    $("#dialog-given").disable_dialog_buttons();
                    let ids = tableform.table_ids(table);
                    try {
                        await common.ajax_post("test", $("#dialog-given .asm-field").toPOST() + "&mode=perform&ids=" + ids);
                        $.each(controller.rows, function(i, t) {
                            if (tableform.table_id_selected(t.ID)) {
                                t.DATEOFTEST = format.date_iso($("#newdate").val());
                                t.TESTRESULTID = $("#testresult").val();
                                t.RESULTNAME = common.get_field(controller.testresults, t.TESTRESULTID, "RESULTNAME");
                            }
                        });
                        tableform.table_update(table);
                    }
                    finally {
                        $("#dialog-given").dialog("close");
                        $("#dialog-given").enable_dialog_buttons();
                        if (controller.name == "animal_test") {
                            common.route_reload();
                        }
                    }
                }
            };
            givenbuttons[_("Cancel")] = function() {
                $("#dialog-given").dialog("close");
            };

            $("#dialog-given").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: givenbuttons
            });

        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            this.bind_givendialog();

            validate.indicator([ "animal", "animals" ]);

            // When the test type is changed, use the default cost from the test type
            $("#type").change(test.set_default_cost);

            // Remember the currently selected animal when it changes so we can add
            // its name and code to the local set
            $("#animal").bind("animalchooserchange", function(event, rec) { test.lastanimal = rec; });
            $("#animal").bind("animalchooserloaded", function(event, rec) { test.lastanimal = rec; });

            // Same for the vet
            $("#administeringvet").bind("personchooserchange", function(event, rec) { test.lastvet = rec; });
            $("#administeringvet").bind("personchooserloaded", function(event, rec) { test.lastvet = rec; });
            $("#givenvet").bind("personchooserchange", function(event, rec) { test.lastvet = rec; });
            $("#givenvet").bind("personchooserloaded", function(event, rec) { test.lastvet = rec; });

            if (controller.newtest == 1) {
                this.new_test();
            }
        },

        sync: function() {
            // If an offset is given in the querystring, update the select
            if (common.querystring_param("offset")) {
                $("#offset").select("value", common.querystring_param("offset"));
            }
            // Hide stock deductions if stock control is disabled
            if (config.bool("DisableStockControl")) {
                $(".tagstock").hide();
            }
        },

        /** Whether or not we should allow overwriting of the cost */
        enable_default_cost: true,

        /** Sets the default cost based on the selected test type */
        set_default_cost: function() {
            if (!test.enable_default_cost) { return; }
            let seltype = $("#type").val();
            $.each(controller.testtypes, function(i, v) {
                if (seltype == v.ID) {
                    if (v.DEFAULTCOST) {
                        $("#cost").currency("value", v.DEFAULTCOST);
                    }
                    else {
                        $("#cost").currency("value", 0);
                    }
                    return true;
                }
            });
        },

        set_extra_fields: function(row) {
            if (controller.animal) {
                row.LOCATIONUNIT = controller.animal.SHELTERLOCATIONUNIT;
                row.LOCATIONNAME = controller.animal.SHELTERLOCATIONNAME;
                row.ANIMALNAME = controller.animal.ANIMALNAME;
                row.SHELTERCODE = controller.animal.SHELTERCODE;
                row.WEBSITEMEDIANAME = controller.animal.WEBSITEMEDIANAME;
            }
            else if (test.lastanimal) {
                // Only switch the location for new records to prevent
                // movementtypes being changed to internal locations on existing records
                if (!row.LOCATIONNAME) {
                    row.LOCATIONUNIT = test.lastanimal.SHELTERLOCATIONUNIT;
                    row.LOCATIONNAME = test.lastanimal.SHELTERLOCATIONNAME;
                }
                row.ANIMALNAME = test.lastanimal.ANIMALNAME;
                row.SHELTERCODE = test.lastanimal.SHELTERCODE;
                row.WEBSITEMEDIANAME = test.lastanimal.WEBSITEMEDIANAME;
            }
            row.TESTNAME = common.get_field(controller.testtypes, row.TESTTYPEID, "TESTNAME");
            row.RESULTNAME = common.get_field(controller.testresults, row.TESTRESULTID, "RESULTNAME");
            row.ADMINISTERINGVETNAME = "";
            if (row.ADMINISTERINGVETID && test.lastvet) { row.ADMINISTERINGVETNAME = test.lastvet.OWNERNAME; }
        },

        /** Fetch the appropriate reschedule period for test type and add it to passed date. Return null if rescheduling isn't availble. */
        calc_reschedule_date: function(date, testtype) {
            let reschedule = format.to_int(common.get_field(controller.testtypes, testtype, "RESCHEDULEDAYS"));
            if (!reschedule) { return null; }
            return common.add_days(date, reschedule);
        },

        destroy: function() {
            common.widget_destroy("#dialog-given");
            common.widget_destroy("#animal");
            common.widget_destroy("#animals");
            common.widget_destroy("#administeringvet", "personchooser");
            tableform.dialog_destroy();
            this.lastanimal = null;
            this.lastvet = null;
        },

        name: "test",
        animation: function() { return controller.name == "test" ? "book" : "formtab"; },
        title:  function() { 
            let t = "";
            if (controller.name == "animal_test") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "test") { t = _("Test Book"); }
            return t;
        },

        routes: {
            "animal_test": function() { common.module_loadandstart("test", "animal_test?id=" + this.qs.id); },
            "test": function() { common.module_loadandstart("test", "test?" + this.rawqs); }
        }


    };
    
    common.module_register(test);

});
