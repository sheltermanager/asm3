/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const medicalprofile = {

        TREATMENT_SINGLE: 0,
        TREATMENT_MULTI: 1,
        TREATMENT_CUSTOM: 2,
        MEDICAL_TYPES_WITHOUT_DOSAGE: [ 11,12,13,14,15,16,18,19,26,27,29 ],

        model: function() {
            const dialog = {
                add_title: _("Add medical profile"),
                edit_title: _("Edit medical profile"),
                edit_perm: 'mcam',
                close_on_ok: true,
                columns: 1,
                width: 800,
                fields: [
                    { json_field: "PROFILENAME", post_field: "profilename", label: _("Profile"), type: "text", classes: "asm-doubletextbox", validation: "notblank" },
                    { json_field: "TREATMENTNAME", post_field: "treatmentname", label: _("Name"), type: "text", classes: "asm-doubletextbox", validation: "notblank" }, 
                    { json_field: "MEDICALTYPEID", post_field: "medicaltype", label: _("Type"), type: "select", doublesize: true, 
                        options: "<option></option>" + html.list_to_options(controller.medicaltypes, "ID", "MEDICALTYPENAME") },
                    { json_field: "DOSAGE", post_field: "dosage", label: _("Dosage"), type: "text", classes: "asm-doubletextbox" },
                    { json_field: "COST", post_field: "cost", label: _("Cost"), type: "currency",
                        callout: _("The total cost of all treatments.") },
                    { json_field: "COSTPERTREATMENT", post_field: "costpertreatment", label: _("Cost per Treatment"), type: "currency",
                        callout: _("If this field has a value, the cost field above will be automatically calculated after each treatment is given.") },
                    { post_field: "singlemulti", label: _("Frequency"), type: "select",  
                        options: '<option value="0">' + _("Single Treatment") + '</option>' +
                        '<option value="1" selected="selected">' + _("Multiple Treatments") + '</option>' + 
                        '<option value="2">' + _("Custom Frequency") + '</option>' },
                    { json_field: "TIMINGRULE", post_field: "timingrule", type: "number", label: "", halfsize: true, defaultval: "1", 
                        xmarkup: ' ' + _("treatments, every") + ' ',
                        rowclose: false },
                    { json_field: "TIMINGRULENOFREQUENCIES", post_field: "timingrulenofrequencies", type: "intnumber", justwidget: true, halfsize: true, defaultval: "1" },
                    { json_field: "TIMINGRULEFREQUENCY", post_field: "timingrulefrequency", type: "select", justwidget: true, halfsize: true, options: 
                                '<option value="0">' + _("days") + '</option>' + 
                                '<option value="4">' + _("weekdays") + '</option>' +
                                '<option value="1">' + _("weeks") + '</option>' +
                                '<option value="2">' + _("months") + '</option>' + 
                                '<option value="3">' + _("years") + '</option>' },
                    { type: "rowclose" },
                    { json_field: "TREATMENTRULE", post_field: "treatmentrule", label: _("Duration"), type: "select", halfsize: true,  
                        options: '<option value="0">' + _("Ends after") + '</option>' +
                            '<option value="1">' + _("Unspecified") + '</option>',
                        xmarkup: ' <span id="treatmentrulecalc">',
                        rowclose: false },
                    { json_field: "TOTALNUMBEROFTREATMENTS", post_field: "totalnumberoftreatments", 
                            type: "intnumber", justwidget: true, halfsize: true, defaultval: "1" },
                    { type: "raw", justwidget: true, markup: ' <span id="timingrulefrequencyagain">' + _("days") + '</span> ' +
                            '(<span id="displaytotalnumberoftreatments">0</span> ' + _("treatments") + ')' +
                            '</span>'},
                    { type: "rowclose" },
                    { json_field: "CUSTOMTIMINGRULE", post_field: "customtiming", label: _("Treatments"), type: "text", classes: "asm-doubletextbox", 
                        callout: _("A comma separated list of treatment timings.") + "<br>" + 
                            _("An optional label may be applied to each treatment using '{title}={no of days since start of course}'") + "<br>" + 
                            _("Examples") + "<br>" + "'1,3,5,7,9'<br>" + 
                            "'first=1,second=3,third=5,fourth=7,final=9'"
                    },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    $("#singlemulti").prop("disabled", false);
                    if (row.CUSTOMTIMINGRULE) {
                        $("#singlemulti").val(medicalprofile.TREATMENT_CUSTOM);
                    } else if (row.TOTALNUMBEROFTREATMENTS == 1) {
                        $("#singlemulti").val(medicalprofile.TREATMENT_SINGLE);
                    } else {
                        $("#singlemulti").val(medicalprofile.TREATMENT_MULTI);
                    }
                    $("#treatmentrule").select("value", row.TREATMENTRULE);
                    medicalprofile.change_singlemulti();
                    medicalprofile.change_values();
                    medicalprofile.change_medicaltype();
                    try {
                        tableform.dialog_show_edit(dialog, row, {
                            onvalidate: function() {
                                if ($("#singlemulti").val() == medicalprofile.TREATMENT_CUSTOM) {
                                    let valoutput = medicalprofile.validate_custom_timing_rule();
                                    if (valoutput == "") {
                                        return true;
                                    } else {
                                        tableform.dialog_error(valoutput);
                                        tableform.dialog_enable_buttons();
                                        return false;
                                    }
                                } else {
                                    return true;
                                }
                            },
                            onload: function() {
                                medicalprofile.change_values();
                            },
                            onchange: async function() {
                                medicalprofile.set_extra_fields(row);
                                await tableform.fields_post(dialog.fields, "mode=update&profileid=" + row.ID, "medicalprofile");
                                tableform.fields_update_row(dialog.fields, row);
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }
                        });
                        
                        
                    }
                    catch(err) {
                        log.error(err, err);
                        console.log(err);
                        tableform.dialog_enable_buttons();
                    }
                },
                columns: [
                    { field: "PROFILENAME", display: _("Profile"), initialsort: true },
                    { field: "TREATMENTNAME", display: _("Name") },
                    { field: "MEDICALTYPENAME", display: _("Type") },
                    { field: "DOSAGE", display: _("Dosage") },
                    { field: "COST", display: _("Cost"), 
                        formatter: function(row) {
                            if (row.COSTPERTREATMENT) { return format.currency(row.COSTPERTREATMENT); }
                            return format.currency(row.COST);
                        },
                        hideif: function() { return !config.bool("ShowCostAmount"); }
                    },
                    { field: "NAMEDFREQUENCY", display: _("Frequency") },
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Profile"), icon: "new", enabled: "always", perm: "maam",
                     click: function() { medicalprofile.new_medicalprofile(); }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "mdam", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        var ids = tableform.table_ids(table);
                        await common.ajax_post("medicalprofile", "mode=delete&ids=" + ids);
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
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Medical Profiles"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        new_medicalprofile: async function() { 
            $("#singlemulti").prop("disabled", false);
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            $("#medicaltype").val(config.integer("AFDefaultMedicalType"));
            medicalprofile.change_singlemulti();
            try {
                await tableform.dialog_show_add(medicalprofile.dialog, {
                    onvalidate: function() {
                        if ($("#singlemulti").val() == medicalprofile.TREATMENT_CUSTOM) {
                            let valoutput = medicalprofile.validate_custom_timing_rule();
                            if (valoutput == "") {
                                return true;
                            } else {
                                tableform.dialog_error(valoutput);
                                tableform.dialog_enable_buttons();
                                return false;
                            }
                        } else {
                            return true;
                        }
                    },
                    onadd: async function() {
                        await tableform.fields_post(medicalprofile.dialog.fields, "mode=create", "medicalprofile");
                        common.route_reload();
                    }
                });
            }
            catch(err) {
                log.error(err, err);
                tableform.dialog_enable_buttons();   
            }
        },

        change_medicaltype: function() {
            let mtid = $("#medicaltype").val();
            let forcesingletx = common.get_field(controller.medicaltypes, mtid, "FORCESINGLEUSE");
            if (forcesingletx) {
                $("#singlemulti").val(medicalprofile.TREATMENT_SINGLE);
                $("#singlemulti").prop("disabled", true);
                medicalprofile.change_singlemulti();
            }
            else {
                $("#singlemulti").prop("disabled", false);
            }
            $("#dosagerow").toggle( !medicalprofile.MEDICAL_TYPES_WITHOUT_DOSAGE.includes(format.to_int(mtid)) );
        },
        
        /* What to do when we switch between single/multiple treatments */
        change_singlemulti: function() {
            if ($("#singlemulti").val() == medicalprofile.TREATMENT_SINGLE) {
                $("#timingrule").val("1");
                $("#timingrulenofrequencies").val("1");
                $("#timingrulefrequency").select("value", "0");
                $("#timingrulefrequency").select("disable");
                $("#treatmentrule").select("value", "0");
                $("#treatmentrule").select("disable");
                $("#totalnumberoftreatments").val("1");
                $("#timingrulerow").fadeOut();
                $("#treatmentrulerow").fadeOut();
                $("#customtimingrow").fadeOut();
            } else if ($("#singlemulti").val() == medicalprofile.TREATMENT_MULTI) {
                $("#timingrule").val("1");
                $("#timingrulenofrequencies").val("1");
                $("#timingrulefrequency").select("value", "0");
                $("#timingrulefrequency").select("enable");
                $("#treatmentrule").select("value", "0");
                $("#treatmentrule").select("enable");
                $("#totalnumberoftreatments").val("1");
                $("#timingrulerow").fadeIn();
                $("#treatmentrulerow").fadeIn();
                $("#customtimingrow").fadeOut();
            } else {
                $("#timingrule").val("1");
                $("#timingrulenofrequencies").val("1");
                $("#timingrulefrequency").select("value", "0");
                $("#timingrulefrequency").select("disable");
                $("#treatmentrule").select("value", "0");
                $("#treatmentrule").select("disable");
                $("#totalnumberoftreatments").val("1");
                $("#timingrulerow").fadeOut();
                $("#treatmentrulerow").fadeOut();
                $("#customtimingrow").fadeIn();
            }
        },

        /* Recalculate ends after period and update screen*/
        change_values: function() {
            $.each([ "#timingrule", "#timingrulenofrequencies", "#totalnumberoftreatments" ], function(i, v) {
                if ($(v).val() == "0" || $(v).val().indexOf("-") != -1) { $(v).val("1"); }
            });
            if ($("#treatmentrule").val() == "0") {
                $("#treatmentrulecalc").fadeIn();
                $("#displaytotalnumberoftreatments").text( parseInt($("#timingrule").val(), 10) * parseInt($("#totalnumberoftreatments").val(), 10));
                $("#timingrulefrequencyagain").text($("#timingrulefrequency option[value=\"" + $("#timingrulefrequency").val() + "\"]").text());
            }
            else if ($("#treatmentrule").val() == "1") {
                $("#treatmentrulecalc").fadeOut();
                $("#totalnumberoftreatments").val("1");
            }
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            $("#medicaltype").change(medicalprofile.change_medicaltype);
            $("#singlemulti").change(medicalprofile.change_singlemulti);
            $("#treatmentrule").change(medicalprofile.change_values);
            $("#timingrule").change(medicalprofile.change_values);
            $("#timingrulefrequency").change(medicalprofile.change_values);
            $("#timingrulenofrequencies").change(medicalprofile.change_values);
            $("#treatmentrule").change(medicalprofile.change_values);
            $("#totalnumberoftreatments").change(medicalprofile.change_values);

        },

        sync: function() {
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        set_extra_fields: function(row) {
        },

        validate_custom_timing_rule: function() {
            let problem = "";
            let customtiming = $("#customtiming").val().trim();
            while (customtiming.slice(-1) == ",") {
                customtiming = customtiming.slice(0, -1); //Remove trailing commas
            }
            $("#customtiming").val(customtiming);
            if (customtiming.length == 0) {
                problem = _("No custom rules found");
            } else {
                $.each(customtiming.split(","), function(i, v) {
                    if (v.includes("=")) {
                        let [label, value] = v.split("=");
                        label = label.trim();
                        value = value.trim();
                        if (label == "") {
                            problem = _("Missing label");
                            return false;
                        }
                        if (value == "") {
                            problem = _("Missing value");
                            return false;
                        } else if (!common.is_integer(value)) {
                            problem = _("Value '{0}' is not an integer").replace("{0}", value);
                            return false;
                        }
                    } else {
                        let value = v.trim();
                        if (!common.is_integer(value)) {
                            problem = _("Value '{0}' is not an integer").replace("{0}", value);
                            return false;
                        }

                    }
                });
            }
            return problem;
        },

        name: "medicalprofile",
        animation: "book",
        title: function() { return _("Medical Profiles"); },
        routes: {
            "medicalprofile": function() { return common.module_loadandstart("medicalprofile", "medicalprofile"); }
        }

    };

    common.module_register(medicalprofile);

});
