/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const SCHEDULED = 0,
        INVOICE_ONLY = 1,
        NOT_ARRIVED = 2,
        WAITING = 3,
        WITH_VET = 4,
        COMPLETE = 5,
        CANCELLED = 6,

        TIMEFORMAT = "%H:%M";

    const clinic_appointment = {

        lastperson: null,
        animals: null,
        dialog_row: null,
        is_book: false,

        model: function() {
            const dialog = {
                add_title: _("Add Appointment"),
                edit_title: _("Edit Appointment"),
                edit_perm: 'ccl',
                close_on_ok: false,
                columns: 2,
                width: 800,
                fields: [
                    { json_field: "APPTFOR", post_field: "for", label: _("For"), type: "select", 
                        options: { rows: controller.forlist, displayfield: "USERNAME", valuefield: "USERNAME" }},
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person" },
                    { json_field: "ANIMALID", post_field: "personanimal", label: _("Animal"), type: "select" },
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal", animalfilter: "shelter" },
                    { json_field: "STATUS", post_field: "status", label: _("Status"), type: "select", 
                        options: { displayfield: "STATUS", valuefield: "ID", rows: controller.clinicstatuses }},
                    { json_field: "DATETIME", post_field: "appt", label: _("Appointment"), type: "datetime", validation: "notblank" },
                    { json_field: "ARRIVEDDATETIME", post_field: "arrived", label: _("Arrived"), type: "datetime" },
                    { json_field: "WITHVETDATETIME", post_field: "withvet", label: _("With Vet"), type: "datetime" },
                    { json_field: "COMPLETEDDATETIME", post_field: "complete", label: _("Complete"), type: "datetime" },
                    { type: "nextcol" },
                    { json_field: "ISVAT", post_field: "vat", label: _("Sales Tax"), type: "check", 
                        hideif: function() { return !config.bool("VATEnabled"); } },
                    { json_field: "VATRATE", post_field: "vatrate", label: _("Tax Rate %"), type: "number", 
                        hideif: function() { return !config.bool("VATEnabled"); } },
                    { json_field: "REASONFORAPPOINTMENT", post_field: "reason", label: _("Reason For Appointment"), type: "textarea" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    clinic_appointment.dialog_row = row;
                    clinic_appointment.show_person_animals(false);
                    try {
                        await tableform.dialog_show_edit(dialog, row);
                        if (!clinic_appointment.validation()) { tableform.dialog_enable_buttons(); return; }
                        tableform.fields_update_row(dialog.fields, row);
                        clinic_appointment.set_extra_fields(row);
                        await tableform.fields_post(dialog.fields, "mode=update&appointmentid=" + row.ID, "clinic_appointment");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    finally {
                        tableform.dialog_enable_buttons();
                    }
                },
                button_click: function() {
                    if ($(this).attr("data-uri")) {
                        common.route($(this).attr("data-uri"));
                    }
                },
                complete: function(row) {
                    if (row.STATUS == COMPLETE || row.STATUS == CANCELLED) { return true; }
                    return false;
                },
                overdue: function(row) {
                    if (!row.ARRIVEDDATETIME && format.date_js(row.DATETIME) < new Date() && 
                        clinic_appointment.is_book && (row.STATUS == SCHEDULED || row.STATUS == NOT_ARRIVED)) { return true; }
                    return false;
                },
                columns: [
                    { field: "CLINICSTATUSNAME", display: _("Status"), formatter: function(row) {
                        let invlink = "<button data-icon=\"cart\" " + 
                            "data-uri=\"clinic_invoice?appointmentid=" + row.ID + "\">" + 
                            _("Edit invoice") + '</button>';
                        return '<span style="white-space: nowrap">' +
                            '<input type="checkbox" data-id="' + row.ID + '" title="' + html.title(_("Select")) + '" />' +
                            '<a href="#" data-id="' + row.ID + '" class="link-edit">' + row.CLINICSTATUSNAME + '</a> ' + 
                            invlink + '</span>';
                    }},
                    { field: "APPTFOR", display: _("For") },
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
                            let s = "";
                            if (controller.name.indexOf("animal_") == -1) { s = html.animal_emblems(row) + " "; }
                            return s + '<a href="animal?id=' + row.ANIMALID + '">' + row.ANIMALNAME + ' - ' + row.SHELTERCODE + '</a>';
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("animal_") != -1;
                        }
                    },
                    { field: "DATETIME", display: _("Appointment"), initialsort: true, initialsortdirection: "asc", 
                        formatter: function(row) {
                            let d = format.date(row.DATETIME), t = format.time(row.DATETIME, TIMEFORMAT);
                            if (clinic_appointment.is_book) { return t; }
                            return d + " " + t;
                        }},
                    { field: "ARRIVEDDATETIME", display: _("Arrived"), formatter: function(row) {
                        if (!row.ARRIVEDDATETIME) { return ""; }
                        let cutoff = format.date_js(row.WITHVETDATETIME) || new Date(),
                            diffmins = Math.round((cutoff - format.date_js(row.ARRIVEDDATETIME)) / 60000),
                            d = format.date(row.ARRIVEDDATETIME), t = format.time(row.ARRIVEDDATETIME, TIMEFORMAT),
                            dv = clinic_appointment.is_book ? t : d + " " + t;
                        if (clinic_appointment.is_book) { dv += " (" + diffmins + " " + _("mins") + ")"; }
                        return dv;
                    }},
                    { field: "WITHVETDATETIME", display: _("With Vet"), 
                        formatter: function(row) {
                            let d = format.date(row.WITHVETDATETIME), t = format.time(row.WITHVETDATETIME, TIMEFORMAT);
                            if (clinic_appointment.is_book) { return t; }
                            return d + " " + t;
                        }},
                    { field: "COMPLETEDDATETIME", display: _("Complete"), 
                        formatter: function(row) {
                            let d = format.date(row.COMPLETEDDATETIME), t = format.time(row.COMPLETEDDATETIME, TIMEFORMAT);
                            if (clinic_appointment.is_book) { return t; }
                            return d + " " + t;
                        }},
                    { field: "AMOUNT", display: _("Amount"), formatter: tableform.format_currency },
                    { field: "VATAMOUNT", display: _("Tax"), formatter: tableform.format_currency, 
                        hideif: function() { return !config.bool("VATEnabled"); } },
                    { field: "REASONFORAPPOINTMENT", display: _("Reason") },
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]

            };

            const buttons = [
                { id: "new", text: _("New Appointment"), icon: "new", enabled: "always", perm: "acl", click: async function() { 
                    await tableform.dialog_show_add(dialog, {
                        onvalidate: function() {
                            return clinic_appointment.validation();
                        },
                        onload: function() {
                            $("#status").select("value", "0");
                            if (config.bool("VATEnabled")) {
                                $("#vat").prop("checked", true);
                                $("#vatrate").val(config.number("VATRate"));
                            }
                            $("#person").personchooser("clear");
                            $("#animal").animalchooser("clear");
                            if (controller.person) {
                                $("#person").personchooser("loadbyid", controller.person.ID);
                                clinic_appointment.update_person_animals(controller.person.ID);
                                clinic_appointment.show_person_animals(true);
                            }
                            else {
                                clinic_appointment.show_person_animals(false);
                            }
                            if (controller.animal) {
                                $("#animal").animalchooser("loadbyid", controller.animal.ID);
                                clinic_appointment.show_person_animals(false);
                            }
                        }
                    });
                    try {
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "clinic_appointment");
                        var row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        clinic_appointment.set_extra_fields(row);
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    finally {
                        tableform.dialog_enable_buttons();   
                    }
                }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dcl",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        var ids = tableform.table_ids(table);
                        await common.ajax_post("clinic_appointment", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "refresh", text: _("Refresh"), icon: "refresh", enabled: "always", 
                    click: function() { 
                        common.route_reload();
                    } 
                },
                { id: "towaiting", text: _("Waiting"), icon: "diary", enabled: "multi", perm: "ccl",
                    click: async function() {
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table),
                            pdata = "mode=towaiting&ids=" + ids + "&date=" + format.date(new Date()) + "&time=" + format.time(new Date());
                        await common.ajax_post("clinic_appointment", pdata);
                        $.each(tableform.table_selected_rows(table), function(i, v) {
                            v.ARRIVEDDATETIME = format.date_now_iso();
                            v.STATUS = WAITING;
                            v.CLINICSTATUSNAME = common.get_field(controller.clinicstatuses, v.STATUS, "STATUS");
                        });
                        tableform.table_update(table);
                    }
                },
                { id: "towithvet", text: _("With Vet"), icon: "health", enabled: "multi", perm: "ccl",
                    click: async function() {
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table),
                            pdata = "mode=towithvet&ids=" + ids + "&date=" + format.date(new Date()) + "&time=" + format.time(new Date());
                        await common.ajax_post("clinic_appointment", pdata);
                        $.each(tableform.table_selected_rows(table), function(i, v) {
                            v.WITHVETDATETIME = format.date_now_iso();
                            v.STATUS = WITH_VET;
                            v.CLINICSTATUSNAME = common.get_field(controller.clinicstatuses, v.STATUS, "STATUS");
                        });
                        tableform.table_update(table);
                    }
                },
                { id: "tocomplete", text: _("Complete"), icon: "complete", enabled: "multi", perm: "ccl",
                    click: async function() {
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table),
                            pdata = "mode=tocomplete&ids=" + ids + "&date=" + format.date(new Date()) + "&time=" + format.time(new Date());
                        await common.ajax_post("clinic_appointment", pdata);
                        $.each(tableform.table_selected_rows(table), function(i, v) {
                            v.COMPLETEDDATETIME = format.date_now_iso();
                            v.STATUS = COMPLETE;
                            v.CLINICSTATUSNAME = common.get_field(controller.clinicstatuses, v.STATUS, "STATUS");
                        });
                        tableform.table_update(table);
                    }
                },
                { id: "document", text: _("Document"), icon: "document", enabled: "one", perm: "gaf", 
                    tooltip: _("Generate document from this appointment"), type: "buttonmenu" },
                 { id: "payment", text: _("Create Payment"), icon: "donation", enabled: "multi", perm: "oaod", 
                     tooltip: _("Create a due or received payment record from this appointment"),
                     click: function() {
                        $("#paymenttype").select("value", config.integer("AFDefaultDonationType"));
                        $("#paymentmethod").select("value", config.integer("AFDefaultPaymentMethod"));
                        $("#dialog-payment").dialog("open");
                     }
                 },
                { id: "filter", type: "dropdownfilter", 
                    options: '<option value="-1">' + _("(all)") + '</option>' + html.list_to_options(controller.clinicstatuses, "ID", "STATUS"),
                    hideif: function() {
                        return !clinic_appointment.is_book;
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

        set_extra_fields: function(row) {
            if (!$("#animal").animalchooser("is_empty")) {
                row.ANIMALNAME = $("#animal").animalchooser("get_selected").ANIMALNAME;
                row.SHELTERCODE = $("#animal").animalchooser("get_selected").SHELTERCODE;
            }
            else {
                row.ANIMALID = $("#personanimal").val();
                row.ANIMALNAME = common.get_field(clinic_appointment.personanimals, $("#personanimal").val(), "ANIMALNAME");
                row.SHELTERCODE = common.get_field(clinic_appointment.personanimals, $("#personanimal").val(), "SHELTERCODE");
            }
            if (controller.person) {
                row.OWNERNAME = controller.person.OWNERNAME;
                row.OWNERADDRESS = controller.person.OWNERADDRESS;
                row.HOMETELEPHONE = controller.person.HOMETELEPHONE;
                row.WORKTELEPHONE = controller.person.WORKTELEPHONE;
                row.MOBILETELEPHONE = controller.person.MOBILETELEPHONE;
            }
            else if (clinic_appointment.lastperson) {
                row.OWNERNAME = clinic_appointment.lastperson.OWNERNAME;
                row.OWNERADDRESS = clinic_appointment.lastperson.OWNERADDRESS;
                row.HOMETELEPHONE = clinic_appointment.lastperson.HOMETELEPHONE;
                row.WORKTELEPHONE = clinic_appointment.lastperson.WORKTELEPHONE;
                row.MOBILETELEPHONE = clinic_appointment.lastperson.MOBILETELEPHONE;
            }
            row.CLINICSTATUSNAME = common.get_field(controller.clinicstatuses, row.STATUS, "STATUS");
            row.LASTCHANGEDBY = asm.user;
        },

        show_person_animals: function(b) {
            if (b) {
                $("#personanimal").closest("tr").show();
                $("#animal").closest("tr").hide();
            }
            else {
                $("#personanimal").closest("tr").hide();
                $("#animal").closest("tr").show();
            }
        },

        update_person_animals: async function(personid) {
            let response = await common.ajax_post("clinic_appointment", "mode=personanimals&personid=" + personid);
            let h = "<option value=\"0\"></option>";
            clinic_appointment.personanimals = jQuery.parseJSON(response);
            $.each(clinic_appointment.personanimals, function(i,v) {
                h += "<option value=\"" + v.ID + "\">";
                h += v.ANIMALNAME + " - " + v.SHELTERCODE + " (" + v.SEXNAME + " " + v.BREEDNAME + " " + v.SPECIESNAME + ")";
                h += "</option>";
            });
            $("#personanimal").html(h);
            if (clinic_appointment.dialog_row && clinic_appointment.dialog_row.ANIMALID) {
                $("#personanimal").select("value", clinic_appointment.dialog_row.ANIMALID);
            }
            $("#movement").closest("tr").fadeIn();
        },

        render_paymentdialog: function() {
            return [
                '<div id="dialog-payment" style="display: none" title="' + html.title(_("Create Payment")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="paymenttype">' + _("Type") + '</label></td>',
                '<td><select id="paymenttype" data="paymenttype" class="asm-selectbox asm-field">',
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="paymentmethod">' + _("Method") + '</label></td>',
                '<td><select id="paymentmethod" data="paymentmethod" class="asm-selectbox asm-field">',
                html.list_to_options(controller.paymentmethods, "ID", "PAYMENTNAME"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="due">' + _("Due") + '</label></td>',
                '<td><input id="due" data="due" type="textbox" class="asm-textbox asm-datebox asm-field" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="received">' + _("Received") + '</label></td>',
                '<td><input id="received" data="received" type="textbox" class="asm-textbox asm-datebox asm-field" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        bind_paymentdialog: function() {

            let paymentbuttons = { };
            paymentbuttons[_("Create")] = async function() {
                validate.reset();
                if (!$("#due").val() && !$("#received").val()) { validate.notblank([ "received" ]); return; }
                try {
                    $("#dialog-payment").disable_dialog_buttons();
                    let ids = tableform.table_ids(clinic_appointment.table);
                    await common.ajax_post("clinic_appointment", $("#dialog-payment .asm-field").toPOST() + "&mode=payment&ids=" + ids);
                    header.show_info(_("{0} payment records created.").replace("{0}", ids.split(",").length-1));
                }
                finally {
                    $("#dialog-payment").dialog("close");
                    $("#dialog-payment").enable_dialog_buttons();
                }
            };
            paymentbuttons[_("Cancel")] = function() {
                $("#dialog-payment").dialog("close");
            };
            $("#dialog-payment").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: paymentbuttons
            });
            // Get rid of any inactive items on the create payment dialog
            $("#dialog-payment .asm-selectbox").select("removeRetiredOptions", "all");
        },

        render: function() {
            this.is_book = controller.name.indexOf("clinic") == 0;
            this.model();
            let h = [
                tableform.dialog_render(this.dialog),
                clinic_appointment.render_paymentdialog(),
                '<div id="button-document-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                edit_header.template_list(controller.templates, "CLINIC", 0),
                '</ul></div>'
            ];
            if (controller.name == "animal_clinic") {
                h.push(edit_header.animal_edit_header(controller.animal, "clinic", controller.tabcounts));
            }
            else if (controller.name == "person_clinic") {
                h.push(edit_header.person_edit_header(controller.person, "clinic", controller.tabcounts));
            }
            else {
                h.push(html.content_header(this.title()));
            }
            h.push(tableform.buttons_render(this.buttons));
            h.push(tableform.table_render(this.table));
            h.push(html.content_footer());
            return h.join("\n");
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            clinic_appointment.bind_paymentdialog();

            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
                clinic_appointment.lastperson = rec;
                clinic_appointment.update_person_animals(rec.ID);
                clinic_appointment.show_person_animals(true);
            });

            $("#person").personchooser().bind("personchoosercleared", function(event) {
                $("#personanimal").val("0");
                clinic_appointment.show_person_animals(false);
            });

            $("#person").personchooser().bind("personchooserloaded", function(event, rec) {
                clinic_appointment.lastperson = rec;
            });

            // Add click handlers to templates
            $(".templatelink").click(function() {
                // Update the href as it is clicked so default browser behaviour
                // continues on to open the link in a new window
                let template_name = $(this).attr("data");
                let id = tableform.table_selected_id(clinic_appointment.table);
                $(this).prop("href", "document_gen?linktype=CLINIC&id=" + id + "&dtid=" + template_name);
            });

        },

        sync: function() {
            $("#filter").select("value", controller.filter);
        },

        validation: function() {
            if ($("#person").personchooser("is_empty") && $("#animal").animalchooser("is_empty")) {
                validate.notzero(["animal"]);
                return false;
            }
            if (!$("#person").personchooser("is_empty") && $("#personanimal").val() == "0") {
                validate.notzero(["personanimal"]);
                return false;
            }
            if (!validate.notblank([ "apptdate", "appttime" ])) { return false; }
            return true;
        },

        destroy: function() {
            tableform.dialog_destroy();
            common.widget_destroy("#dialog-payment");
            clinic_appointment.dialog_row = null;
        },

        name: "clinic_appointment",
        animation: function() { return controller.name.indexOf("clinic_") == 0 ? "book" : "formtab"; },
        title:  function() { 
            let t = "";
            if (controller.name == "animal_clinic") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "person_clinic") { t = controller.person.OWNERNAME; }
            else if (controller.name == "clinic_waitingroom") { t = _("Waiting Room"); }
            else if (controller.name == "clinic_consultingroom") { t = _("Consulting Room - {0}").replace("{0}", asm.user); }
            return t;
        },

        routes: {
            "animal_clinic": function() { common.module_loadandstart("clinic_appointment", "animal_clinic?" + this.rawqs); },
            "person_clinic": function() { common.module_loadandstart("clinic_appointment", "person_clinic?" + this.rawqs); },
            "clinic_waitingroom": function() { common.module_loadandstart("clinic_appointment", "clinic_waitingroom?" + this.rawqs); },
            "clinic_consultingroom": function() { common.module_loadandstart("clinic_appointment", "clinic_consultingroom?" + this.rawqs); }
        }

    };
    
    common.module_register(clinic_appointment);

});
