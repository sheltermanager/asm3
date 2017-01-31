/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var vaccination = {

        lastanimal: null, 
        lastvet: null, 

        model: function() {
            var dialog = {
                add_title: _("Add vaccination"),
                edit_title: _("Edit vaccination"),
                edit_perm: 'cav',
                helper_text: _("Vaccinations need an animal and at least a required date."),
                close_on_ok: false,
                use_default_values: false,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal" },
                    { json_field: "ANIMALS", post_field: "animals", label: _("Animals"), type: "animalmulti" },
                    { json_field: "VACCINATIONID", post_field: "type", label: _("Type"), type: "select", 
                        options: { displayfield: "VACCINATIONTYPE", valuefield: "ID", rows: controller.vaccinationtypes }},
                    { json_field: "DATEREQUIRED", post_field: "required", label: _("Required"), type: "date", validation: "notblank" },
                    { json_field: "DATEOFVACCINATION", post_field: "given", label: _("Given"), type: "date" },
                    { json_field: "ADMINISTERINGVETID", post_field: "administeringvet", label: _("Administering Vet"), type: "person", personfilter: "vet" },
                    { json_field: "DATEEXPIRES", post_field: "expires", label: _("Expires"), type: "date" },
                    { json_field: "BATCHNUMBER", post_field: "batchnumber", label: _("Batch Number"), type: "text" },
                    { json_field: "MANUFACTURER", post_field: "manufacturer", label: _("Manufacturer"), type: "text" },
                    { json_field: "COST", post_field: "cost", label: _("Cost"), type: "currency", hideif: function() { return !config.bool("ShowCostAmount"); } },
                    { json_field: "COSTPAIDDATE", post_field: "costpaid", label: _("Paid"), type: "date", hideif: function() { return !config.bool("ShowCostPaid"); } },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    if (controller.animal) {
                        $("#animal").closest("tr").hide();
                    }
                    else {
                        $("#animal").closest("tr").show();
                    }
                    $("#animals").closest("tr").hide();
                    $("#administeringvet").personchooser("clear");
                    vaccination.enable_default_cost = false;
                    tableform.fields_populate_from_json(dialog.fields, row);
                    vaccination.enable_default_cost = true;
                    tableform.dialog_show_edit(dialog, row)
                        .then(function() {
                            tableform.fields_update_row(dialog.fields, row);
                            vaccination.set_extra_fields(row);
                            return tableform.fields_post(dialog.fields, "mode=update&vaccid=" + row.ID, controller.name);
                        })
                        .then(function(response) {
                            tableform.table_update(table);
                            tableform.dialog_close();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();
                        });
                },
                complete: function(row) {
                    if (row.DATEOFVACCINATION) { return true; }
                    return false;
                },
                overdue: function(row) {
                    if (!row.DATEOFVACCINATION && format.date_js(row.DATEREQUIRED) < common.today_no_time()) { return true; }
                    //if (row.DATEOFVACCINATION && format.date_js(row.DATEEXPIRES) < common.today_no_time()) { return true; } // Too aggressive
                    return false;
                },
                columns: [
                    { field: "VACCINATIONTYPE", display: _("Type") },
                    { field: "IMAGE", display: "", 
                        formatter: function(row) {
                            return '<a href="animal?id=' + row.ANIMALID + '"><img src=' + html.thumbnail_src(row, "animalthumb") + ' style="margin-right: 8px" class="asm-thumbnail thumbnailshadow" /></a>';
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
                            return html.animal_link(row, { noemblems: controller.name == "animal_vaccination" });
                        },
                        hideif: function(row) {
                            // Don't show for animal records
                            if (controller.animal) { return true; }
                        }
                    },
                    { field: "ACCEPTANCENUMBER", display: _("Litter"),
                        hideif: function(row) {
                            return config.bool("DontShowLitterID");
                        }
                    },
                    { field: "LOCATIONNAME", display: _("Location"),
                        formatter: function(row) {
                            var s = row.LOCATIONNAME;
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
                    { field: "DATEREQUIRED", display: _("Required"), formatter: tableform.format_date, initialsort: true, initialsortdirection: "desc" },
                    { field: "DATEOFVACCINATION", display: _("Given"), formatter: tableform.format_date },
                    { field: "ADMINISTERINGVET", display: _("Vet"), 
                        formatter: function(row) {
                            if (!row.ADMINISTERINGVETID) { return ""; }
                            return html.person_link(row.ADMINISTERINGVETID, row.ADMINISTERINGVETNAME);
                        }
                    },
                    { field: "DATEEXPIRES", display: _("Expires"), formatter: tableform.format_date },
                    { field: "MANUFACTURER", display: _("Manufacturer") },
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
                { id: "new", text: _("New Vaccination"), icon: "new", enabled: "always", perm: "aav", 
                    click: function() { vaccination.new_vacc(); }},
                { id: "bulk", text: _("Bulk Vaccination"), icon: "new", enabled: "always", perm: "cav", 
                    hideif: function() { return controller.animal; }, click: function() { vaccination.new_bulk_vacc(); }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dav", 
                     click: function() { 
                         tableform.delete_dialog()
                             .then(function() {
                                 tableform.buttons_default_state(buttons);
                                 var ids = tableform.table_ids(table);
                                 return common.ajax_post(controller.name, "mode=delete&ids=" + ids);
                             })
                             .then(function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                             });
                     } 
                 },
                 { id: "given", text: _("Give"), icon: "complete", enabled: "multi", perm: "cav",
                     click: function() {
                        var comments = "";
                        $.each(controller.rows, function(i, v) {
                            if (tableform.table_id_selected(v.ID)) {
                                comments += "[" + v.SHELTERCODE + " - " + v.ANIMALNAME + "] ";
                            }
                        });
                        $("#usagecomments").val(comments);
                        $("#newdateg").datepicker("setDate", new Date());
                        $("#usagetype").select("firstvalue");
                        $("#usagedate").datepicker("setDate", new Date());
                        $("#usagedate").closest("tr").hide();
                        $("#quantity").val("0");
                        // Default animal's current vet if set and this is an animal vacc tab
                        if (controller.animal && controller.animal.CURRENTVETID) { 
                            $("#givenvet").personchooser("loadbyid", controller.animal.CURRENTVETID); 
                        }
                        $("#dialog-given").dialog("open");
                     }
                 },
                 { id: "required", text: _("Change Date Required"), icon: "calendar", enabled: "multi", perm: "cav", 
                     click: function() {
                        $("#dialog-required").dialog("open");
                     }
                 },
                 { id: "offset", type: "dropdownfilter", 
                     options: [ "m365|" + _("Due today"), "p7|" + _("Due in next week"), "p31|" + _("Due in next month"), "p365|" + _("Due in next year"), 
                        "xm365|" + _("Expired"), "xp31|" + _("Expire in next month") ],
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
            var s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += vaccination.render_givendialog();
            s += vaccination.render_requireddialog();
            if (controller.animal) {
                s += edit_header.animal_edit_header(controller.animal, "vaccination", controller.tabcounts);
            }
            else {
                s += html.content_header(_("Vaccination Book"));
            }
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        render_requireddialog: function() {
            return [
                '<div id="dialog-required" style="display: none" title="' + html.title(_("Change Date Required")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="newdate">' + _("Required") + '</label></td>',
                '<td><input id="newdate" data="newdate" type="text" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        bind_requireddialog: function() {

            var requiredbuttons = { }, table = vaccination.table;
            requiredbuttons[_("Save")] = function() {
                validate.reset("dialog-required");
                if (!validate.notblank([ "newdate" ])) { return; }
                $("#dialog-required").disable_dialog_buttons();
                var ids = tableform.table_ids(table);
                var newdate = encodeURIComponent($("#newdate").val());
                common.ajax_post(controller.name, "mode=required&newdate=" + newdate + "&ids=" + ids)
                    .then(function() {
                        $.each(controller.rows, function(i, v) {
                            if (tableform.table_id_selected(v.ID)) {
                                v.DATEREQUIRED = format.date_iso($("#newdate").val());
                            }
                        });
                        tableform.table_update(table);
                    })
                    .always(function() {
                        $("#dialog-required").dialog("close");
                        $("#dialog-required").enable_dialog_buttons();
                    });
            };
            requiredbuttons[_("Cancel")] = function() {
                $("#dialog-required").dialog("close");
            };

            $("#dialog-required").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: requiredbuttons
            });

        },

        new_vacc: function() { 
            var table = vaccination.table, dialog = vaccination.dialog;
            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=create", controller.name)
                        .then(function(response) {
                            var row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
                            vaccination.set_extra_fields(row);
                            controller.rows.push(row);
                            tableform.table_update(table);
                            tableform.dialog_close();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();
                        });
                },
                onload: function() {
                    if (controller.animal) {
                        $("#animal").animalchooser("loadbyid", controller.animal.ID);
                        $("#animal").closest("tr").hide();
                    }
                    else {
                        $("#animal").closest("tr").show();
                        $("#animal").animalchooser("clear");
                    }
                    $("#animals").closest("tr").hide();
                    $("#administeringvet").personchooser("clear");
                    $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
                    $("#type").select("value", config.str("AFDefaultVaccinationType"));
                    vaccination.enable_default_cost = true;
                    vaccination.set_default_cost();
                }
            });
        },

        new_bulk_vacc: function() {
            var dialog = vaccination.dialog;
            tableform.dialog_show_add(dialog, {
                onadd: function() {
                    tableform.fields_post(dialog.fields, "mode=createbulk", controller.name)
                        .then(function(response) {
                            tableform.dialog_close();
                            common.route_reload();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();   
                        });
                },
                onload: function() {
                    $("#animal").closest("tr").hide();
                    $("#animals").closest("tr").show();
                    $("#animals").animalchoosermulti("clear");
                    $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
                    $("#type").select("value", config.str("AFDefaultVaccinationType"));
                    vaccination.enable_default_cost = true;
                    vaccination.set_default_cost();
                }
            });
        },

        render_givendialog: function() {
            return [
                '<div id="dialog-given" style="display: none" title="' + html.title(_("Give Vaccination")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="newdateg">' + _("Given") + '</label></td>',
                '<td><input id="newdateg" data="newdate" type="text" class="asm-textbox asm-datebox asm-field" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="givenvet">' + _("Administering Vet") + '</label></td>',
                '<td><input id="givenvet" data="givenvet" type="hidden" class="asm-personchooser asm-field" data-filter="vet" /></td>',
                '</tr>',
                '<tr><td></td><td>' + html.info(_("Specifying a reschedule date will make copies of the selected vaccinations and mark them to be given on the reschedule date. Example: If this vaccination needs to be given every year, set the reschedule date to be 1 year from today.")) + '</td></tr>',
                '<tr>',
                '<td><label for="rescheduledate">' + _("Reschedule") + '</label></td>',
                '<td><input id="rescheduledate" data="rescheduledate" type="text" class="asm-textbox asm-datebox asm-field" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="reschedulecomments">' + _("Comments") + '</label></td>',
                '<td><textarea id="reschedulecomments" data="reschedulecomments" class="asm-textarea asm-field"></textarea>',
                '</td>',
                '</tr>',
                '<tr class="tagstock"><td></td><td>' + html.info(_("These fields allow you to deduct stock for the vaccination(s) given. This single deduction should cover the selected vaccinations being administered.")) + '</td></tr>',
                '<tr class="tagstock">',
                '<td><label for="item">' + _("Item") + '</label></td>',
                '<td><select id="item" data="item" class="asm-selectbox asm-field">',
                '<option value="-1">' + _("(no deduction)") + '</option>',
                html.list_to_options(controller.stockitems, "ID", "ITEMNAME"),
                '</select></td>',
                '</tr>',
                '<tr class="tagstock">',
                '<td><label for="quantity">' + _("Quantity") + '</label></td>',
                '<td><input id="quantity" data="quantity" type="text" class="asm-textbox asm-numberbox asm-field" /></td>',
                '</tr>',
                '<tr class="tagstock">',
                '<td><label for="usagetype">' + _("Usage Type") + '</label></td>',
                '<td><select id="usagetype" data="usagetype" class="asm-selectbox asm-field">',
                html.list_to_options(controller.stockusagetypes, "ID", "USAGETYPENAME"),
                '</select></td>',
                '</tr>',
                '<tr class="tagstock">',
                '<td><label for="usagedate">' + _("Usage Date") + '</label></td>',
                '<td><input id="usagedate" data="usagedate" class="asm-textbox asm-datebox asm-field" />',
                '</select></td>',
                '</tr>',
                '<tr class="tagstock">',
                '<td><label for="usagecomments">' + _("Comments") + '</label></td>',
                '<td><textarea id="usagecomments" data="usagecomments" class="asm-textarea asm-field"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        bind_givendialog: function() {
            var givenbuttons = { }, table = vaccination.table;
            givenbuttons[_("Save")] = function() {
                validate.reset("dialog-given");
                if (!validate.notblank([ "newdateg" ])) { return; }
                $("#usagedate").val($("#newdateg").val()); // copy given to usage
                $("#dialog-given").disable_dialog_buttons();
                var ids = tableform.table_ids(table);
                common.ajax_post(controller.name, $("#dialog-given .asm-field").toPOST() + "&mode=given&ids=" + ids)
                    .then(function() {
                        $.each(controller.rows, function(i, v) {
                            if (tableform.table_id_selected(v.ID)) {
                                v.DATEOFVACCINATION = format.date_iso($("#newdateg").val());
                            }
                        });
                        tableform.table_update(table);
                    })
                    .always(function() {
                        $("#dialog-given").dialog("close");
                        $("#dialog-given").enable_dialog_buttons();
                        if (controller.name == "animal_vaccination") {
                            common.route_reload();
                        }
                    });
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
            this.bind_requireddialog();

            // When the vacc type is changed, use the default cost from the vaccination type
            $("#type").change(vaccination.set_default_cost);

            // Remember the currently selected animal when it changes so we can add
            // its name and code to the local set
            $("#animal").bind("animalchooserchange", function(event, rec) { vaccination.lastanimal = rec; });
            $("#animal").bind("animalchooserloaded", function(event, rec) { vaccination.lastanimal = rec; });

            // Same for the vet
            $("#administeringvet").bind("personchooserchange", function(event, rec) { vaccination.lastvet = rec; });
            $("#administeringvet").bind("personchooserloaded", function(event, rec) { vaccination.lastvet = rec; });
            $("#givenvet").bind("personchooserchange", function(event, rec) { vaccination.lastvet = rec; });
            $("#givenvet").bind("personchooserloaded", function(event, rec) { vaccination.lastvet = rec; });

            if (controller.newvacc == 1) {
                this.new_vacc();
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
            // Autocomplete manufacturers
            $("#manufacturer").autocomplete({ source: html.decode(controller.manufacturers.split("|")) });
            $("#manufacturer").autocomplete("option", "appendTo", "#dialog-tableform");

        },

        /** Whether or not we should allow overwriting of the cost */
        enable_default_cost: true,

        /** Sets the default cost based on the selected vaccination type */
        set_default_cost: function() {
            if (!vaccination.enable_default_cost) { return; }
            var seltype = $("#type").val();
            $.each(controller.vaccinationtypes, function(i, v) {
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
            else if (vaccination.lastanimal) {
                // Only switch the location for new records to prevent
                // movementtypes being changed to internal locations on existing records
                if (!row.LOCATIONNAME) {
                    row.LOCATIONUNIT = vaccination.lastanimal.SHELTERLOCATIONUNIT;
                    row.LOCATIONNAME = vaccination.lastanimal.SHELTERLOCATIONNAME;
                }
                row.ANIMALNAME = vaccination.lastanimal.ANIMALNAME;
                row.SHELTERCODE = vaccination.lastanimal.SHELTERCODE;
                row.WEBSITEMEDIANAME = vaccination.lastanimal.WEBSITEMEDIANAME;
            }
            row.ADMINISTERINGVETNAME = "";
            if (row.ADMINISTERINGVETID && vaccination.lastvet) { row.ADMINISTERINGVETNAME = vaccination.lastvet.OWNERNAME; }
            row.VACCINATIONTYPE = common.get_field(controller.vaccinationtypes, row.VACCINATIONID, "VACCINATIONTYPE");
        },

        destroy: function() {
            common.widget_destroy("#dialog-required");
            common.widget_destroy("#dialog-given");
            common.widget_destroy("#animal");
            common.widget_destroy("#animals");
            common.widget_destroy("#administeringvet");
            common.widget_destroy("#givenvet");
            tableform.dialog_destroy();
            this.lastanimal = null;
            this.lastvet = null;
        },

        name: "vaccination",
        animation: function() { return controller.name == "vaccination" ? "book" : "formtab"; },
        title:  function() { 
            var t = "";
            if (controller.name == "animal_vaccination") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "vaccination") { t = _("Vaccination Book"); }
            return t;
        },

        routes: {
            "animal_vaccination": function() { common.module_loadandstart("vaccination", "animal_vaccination?id=" + this.qs.id); },
            "vaccination": function() { common.module_loadandstart("vaccination", "vaccination?" + this.rawqs); }
        }


    };
    
    common.module_register(vaccination);

});
