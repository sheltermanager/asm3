/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const boarding = {

        lastanimal: null,
        lastperson: null,

        model: function() {
            const dialog = {
                add_title: _("Add Boarding"),
                edit_title: _("Edit Boarding"),
                helper_text: "",
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal", validation: "notzero" },
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
                    { json_field: "BOARDINGTYPEID", post_field: "type", label: _("Type"), type: "select", 
                        options: { displayfield: "BOARDINGNAME", valuefield: "ID", rows: controller.boardingtypes }},
                    { json_field: "INDATETIME", post_field: "in", label: _("In Date"), type: "datetime", validation: "notblank", defaultval: new Date() },
                    { json_field: "OUTDATETIME", post_field: "out", label: _("Out Date"), type: "datetime", validation: "notblank", defaultval: new Date() },
                    { json_field: "DAILYFEE", post_field: "dailyfee", label: _("Daily Fee"), type: "currency" },
                    { json_field: "SHELTERLOCATION", post_field: "location", label: _("Location"), type: "select", 
                        options: { displayfield: "LOCATIONNAME", valuefield: "ID", rows: controller.internallocations }},
                    { json_field: "SHELTERLOCATIONUNIT", post_field: "unit", label: _("Unit"), type: "select" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    tableform.dialog_show_edit(dialog, row, {
                        onchange: async function() {
                            try {
                                tableform.fields_update_row(dialog.fields, row);
                                boarding.set_extra_fields(row);
                                await tableform.fields_post(dialog.fields, "mode=update&boardingid=" + row.ID, "boarding");
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }
                            catch(err) {
                                log.error(err, err);
                                tableform.dialog_enable_buttons();
                            }
                        },
                        onload: function(row) {
                            boarding.location_change(); // load units for the selected location
                            $("#unit").val( row.SHELTERLOCATIONUNIT );
                        }
                    });
                },
                complete: function(row) {
                    if (format.date_js(row.OUTDATETIME) < common.today_no_time()) { return true; }
                    return false;
                },
                overdue: function(row) {
                    //return !row.DATECOMPLETED && format.date_js(row.DIARYDATETIME) < common.today_no_time();
                },
                columns: [
                    /*
                    { field: "ID", display: _("Number"), formatter: function (row) { 
                        return "<span style=\"white-space: nowrap\">" +
                            "<input type=\"checkbox\" data-id=\"" + row.ID + "\" title=\"" + html.title(_("Select")) + "\" />" +
                            "<a href=\"#\" class=\"link-edit\" data-id=\"" + row.ID + "\">" + format.padleft(row.ID, 6) + "</a>" +
                            "</span>";
                    }},
                    */
                    { field: "BOARDINGTYPENAME", display: _("Type") },
                    { field: "INDATETIME", display: _("Check In"), formatter: tableform.format_datetime, initialsort: true, initialsortdirection: "desc" },
                    { field: "OUTDATETIME", display: _("Check Out"), formatter: tableform.format_datetime },
                    { field: "PERSON", display: _("Person"),
                        formatter: function(row) {
                            if (row.OWNERID) {
                                return html.person_link(row.OWNERID, row.OWNERNAME);
                            }
                            return "";
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("person_") != -1;
                        }
                    },
                    { field: "ANIMAL", display: _("Animal"), 
                        formatter: function(row) {
                            if (!row.ANIMALID || row.ANIMALID == 0) { return ""; }
                            let s = html.animal_link(row);
                            return s;
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("animal_") != -1;
                        }
                    },
                    { field: "SHELTERLOCATION", display: _("Location"), 
                        formatter: function(row) {
                            return row.SHELTERLOCATIONNAME + (row.SHELTERLOCATIONUNIT ? ' <span class="asm-search-locationunit">' + row.SHELTERLOCATIONUNIT + '</span>' : '');
                        }},
                    { field: "DAILYFEE", display: _("Fee"),
                        formatter: function(row) {
                            return _("{2} ({0} days at {1})").replace("{0}", row.DAYS)
                                .replace("{1}", format.currency(row.DAILYFEE))
                                .replace("{2}", format.currency(row.DAILYFEE * row.DAYS));
                        }},
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Boarding"), icon: "new", enabled: "always", perm: "abi", click: function() { 
                    boarding.new_boarding();
                }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dbi", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("boarding", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "payment", text: _("Create Payment"), icon: "donation", enabled: "one", perm: "oaod", 
                    click: async function() {
                        let row = tableform.table_selected_row(table);
                        $("#createpayment").createpayment("show", {
                            animalid: row.ANIMALID,
                            personid: row.OWNERID,
                            personname: row.OWNERNAME,
                            donationtypes: controller.donationtypes,
                            paymentmethods: controller.paymentmethods,
                            chosentype: config.integer("BoardingPaymentType"),
                            amount: row.DAILYFEE * row.DAYS,
                            comments: common.sub_arr(_("{0} - {1} ({2} days at {3})"), [ row.BOARDINGTYPENAME, row.ANIMALNAME, row.DAYS, format.currency(row.DAILYFEE) ])
                        });
                    }
                },
                { id: "filter", type: "dropdownfilter", 
                    options: [ "active|" + _("Active"),
                        "st|" + _("Starting today"),
                        "p90|" + _("Starts in next 3 months"),
                        "et|" + _("Ending today"),
                        "m90|" + _("Ended in last 3 months")
                        ],
                    hideif: function() {
                        return controller.name == "animal_boarding" || controller.name == "person_boarding";
                    },
                    click: function(selval) {
                        common.route(controller.name + "?filter=" + selval);
                    }
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        type_change: function() {
            let dc = common.get_field(controller.boardingtypes, $("#type").select("value"), "DEFAULTCOST");
            $("#dailyfee").currency("value", dc);
        },

        location_change: function() {
            let units = common.get_field(controller.internallocations, $("#location").val(), "UNITS");
            if (units && units.indexOf(",") != -1) {
                $("#unit").html( html.list_to_options(units.split(",")) );
            }
            else {
                $("#unit").html("");
            }
        },

        set_extra_fields: function(row) {
            if (controller.animal) {
                row.ANIMALNAME = controller.animal.ANIMALNAME;
                row.SHELTERCODE = controller.animal.SHELTERCODE;
                row.SHORTCODE = controller.animal.SHORTCODE;
                row.WEBSITEMEDIANAME = controller.animal.WEBSITEMEDIANAME;
            }
            else if (boarding.lastanimal) {
                row.ANIMALNAME = boarding.lastanimal.ANIMALNAME;
                row.SHELTERCODE = boarding.lastanimal.SHELTERCODE;
                row.SHORTCODE = boarding.lastanimal.SHORTCODE;
                row.WEBSITEMEDIANAME = boarding.lastanimal.WEBSITEMEDIANAME;
            }
            if (controller.person) {
                row.OWNERCODE = controller.person.OWNERCODE;
                row.OWNERNAME = controller.person.OWNERNAME;
                row.OWNERADDRESS = controller.person.OWNERADDRESS;
                row.EMAILADDRESS = controller.person.EMAILADDRESS;
                row.HOMETELEPHONE = controller.person.HOMETELEPHONE;
                row.WORKTELEPHONE = controller.person.WORKTELEPHONE;
                row.MOBILETELEPHONE = controller.person.MOBILETELEPHONE;
            }
            else if (boarding.lastperson) {
                row.OWNERCODE = boarding.lastperson.OWNERCODE;
                row.OWNERNAME = boarding.lastperson.OWNERNAME;
                row.OWNERADDRESS = boarding.lastperson.OWNERADDRESS;
                row.EMAILADDRESS = boarding.lastperson.EMAILADDRESS;
                row.HOMETELEPHONE = boarding.lastperson.HOMETELEPHONE;
                row.WORKTELEPHONE = boarding.lastperson.WORKTELEPHONE;
                row.MOBILETELEPHONE = boarding.lastperson.MOBILETELEPHONE;
            }
            row.BOARDINGTYPENAME = common.get_field(controller.boardingtypes, row.BOARDINGTYPEID, "BOARDINGNAME");
            row.SHELTERLOCATIONNAME = common.get_field(controller.internallocations, row.SHELTERLOCATION, "LOCATIONNAME");
            row.DAYS = format.date_diff_days( $("#indate").datepicker("getDate"), $("#outdate").datepicker("getDate") ); 
        },

        render: function() {
            let h = [];
            this.model();
            h.push(tableform.dialog_render(this.dialog));
            h.push('<div id="createpayment"></div>');
            if (controller.name == "animal_boarding") {
                h.push(edit_header.animal_edit_header(controller.animal, "boarding", controller.tabcounts));
            }
            else if (controller.name == "person_boarding") {
                h.push(edit_header.person_edit_header(controller.person, "boarding", controller.tabcounts));
            }
            else if (controller.name == "boarding") {
                h.push(html.content_header(_("Boarding Book")));
            }
            h.push(tableform.buttons_render(this.buttons));
            h.push(tableform.table_render(this.table));
            h.push(html.content_footer());
            return h.join("\n");
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            $("#createpayment").createpayment();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            $("#location").change(this.location_change);
            $("#type").change(this.type_change);

            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
                boarding.lastanimal = rec;
                // if person is not set, load from the current owner if animal has one
                if ($("#person").val() == "0" && rec.OWNERID) {
                    $("#person").val(rec.OWNERID);
                    $("#person").personchooser("loadbyid", rec.OWNERID);
                }
            });

            $("#animal").animalchooser().bind("animalchooserloaded", function(event, rec) {
                boarding.lastanimal = rec;
                // if person is not set, load from the current owner if animal has one
                if ($("#person").val() == "0" && rec.OWNERID) {
                    $("#person").val(rec.OWNERID);
                    $("#person").personchooser("loadbyid", rec.OWNERID);
                }
            });

            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
                boarding.lastperson = rec;
            });

            $("#person").personchooser().bind("personchooserloaded", function(event, rec) {
                boarding.lastperson = rec;
            });

        },

        sync: function() {
            // If a filter is given in the querystring, update the select
            if (common.current_url().indexOf("filter=") != -1) {
                let filterurl = common.current_url().substring(common.current_url().indexOf("filter=")+7);
                $("#filter").select("value", filterurl);
            }

            if (controller.newboarding) {
                boarding.new_boarding();
            }
        },

        new_boarding: function() {
            tableform.dialog_show_add(boarding.dialog, {
                onadd: async function() {
                    try {
                        let response = await tableform.fields_post(boarding.dialog.fields, "mode=create", "boarding");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(boarding.dialog.fields, row);
                        boarding.set_extra_fields(row);
                        controller.rows.push(row);
                        tableform.table_update(boarding.table);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err);
                        tableform.dialog_enable_buttons();
                    }
                },
                onload: function() {
                    tableform.dialog_enable_buttons();
                    $("#animal").animalchooser("clear");
                    $("#person").personchooser("clear");
                    if (controller.animal) {
                        $("#animal").animalchooser("loadbyid", controller.animal.ID);
                    }
                    if (controller.person) {
                        $("#person").personchooser("loadbyid", controller.person.ID);
                    }
                    $("#indate").date("today");
                    $("#outdate").date("today");
                    $("#intime").val("00:00");
                    $("#outtime").val("00:00");
                    boarding.location_change();
                    boarding.type_change();
                }
            });
        },

        destroy: function() {
            tableform.dialog_destroy();
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
            common.widget_destroy("#createpayment");
            boarding.lastanimal = null;
            boarding.lastperson = null;
        },

        name: "boarding",
        animation: function() { return controller.name.indexOf("boarding") == 0 ? "book" : "formtab"; },
        title:  function() { 
            let t = "";
            if (controller.name == "animal_boarding") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "person_boarding") { t = controller.person.OWNERNAME; }
            else { t = _("Boarding Book"); }
            return t;
        },

        routes: {
            "animal_boarding": function() { common.module_loadandstart("boarding", "animal_boarding?id=" + this.qs.id); },
            "person_boarding": function() { common.module_loadandstart("boarding", "person_boarding?id=" + this.qs.id); },
            "boarding": function() { common.module_loadandstart("boarding", "boarding?" + this.rawqs); }
        }

    };

    common.module_register(boarding);

});
