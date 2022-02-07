/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const medicalprofile = {

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
                    { json_field: "DOSAGE", post_field: "dosage", label: _("Dosage"), type: "text", classes: "asm-doubletextbox", validation: "notblank" },
                    { json_field: "COST", post_field: "cost", label: _("Cost"), type: "currency" },
                    { post_field: "singlemulti", label: _("Frequency"), type: "select",  
                        options: '<option value="0">' + _("Single Treatment") + '</option>' +
                        '<option value="1" selected="selected">' + _("Multiple Treatments") + '</option>' },
                    { type: "raw", justwidget: true, markup: "<tr><td></td><td>" },
                    { json_field: "TIMINGRULE", post_field: "timingrule", type: "number", justwidget: true, halfsize: true, defaultval: "1" },
                    { type: "raw", justwidget: true, markup: " " + _("treatments, every") + " " },
                    { json_field: "TIMINGRULENOFREQUENCIES", post_field: "timingrulenofrequencies", type: "number", justwidget: true, halfsize: true, defaultval: "1" },
                    { type: "raw", justwidget: true, markup: " " },
                    { json_field: "TIMINGRULEFREQUENCY", post_field: "timingrulefrequency", type: "select", justwidget: true, halfsize: true, options: 
                            '<option value="0">' + _("days") + '</option>' + 
                            '<option value="1">' + _("weeks") + '</option>' +
                            '<option value="2">' + _("months") + '</option>' + 
                            '<option value="3">' + _("years") + '</option>' },
                    { type: "raw", justwidget: true, markup: "</td></tr>" },
                    { type: "raw", justwidget: true, markup: "<tr><td>" + _("Duration") + "</td><td>" },
                    { json_field: "TREATMENTRULE", post_field: "treatmentrule", justwidget: true, type: "select", halfsize: true, options:
                            '<option value="0">' + _("Ends after") + '</option>' +
                            '<option value="1">' + _("Unspecified") + '</option>' },
                    { type: "raw", justwidget: true, markup: " <span id='treatmentrulecalc'>" },
                    { json_field: "TOTALNUMBEROFTREATMENTS", post_field: "totalnumberoftreatments", justwidget: true, halfsize: true, type: "number", 
                            defaultval: "1" },
                    { type: "raw", justwidget: true, markup:
                        ' <span id="timingrulefrequencyagain">' + _("days") + '</span> ' +
                        '(<span id="displaytotalnumberoftreatments">0</span> ' + _("treatments") + ')' +
                        '</span></span>' +
                        '</td></tr>'},
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    $("#singlemulti").select("value", (row.TOTALNUMBEROFTREATMENTS == 1 ? 0 : 1));
                    $("#treatmentrule").select("value", row.TREATMENTRULE);
                    medicalprofile.change_singlemulti();
                    medicalprofile.change_values();
                    try {
                        await tableform.dialog_show_edit(dialog, row);
                        tableform.fields_update_row(dialog.fields, row);
                        medicalprofile.set_extra_fields(row);
                        await tableform.fields_post(dialog.fields, "mode=update&profileid=" + row.ID, "medicalprofile");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err);
                        tableform.dialog_enable_buttons();
                    }
                },
                columns: [
                    { field: "PROFILENAME", display: _("Name"), initialsort: true },
                    { field: "TREATMENTNAME", display: _("Treatment") },
                    { field: "DOSAGE", display: _("Dosage") },
                    { field: "COST", display: _("Cost"), formatter: tableform.format_currency },
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
            $("#dialog-tableform .asm-textbox, #dialog-tableform .asm-textarea").val("");
            try {
                await tableform.dialog_show_add(medicalprofile.dialog);
                await tableform.fields_post(medicalprofile.dialog.fields, "mode=create", "medicalprofile");
                common.route_reload();
            }
            catch(err) {
                log.error(err, err);
                tableform.dialog_enable_buttons();   
            }
        },

        /* What to do when we switch between single/multiple treatments */
        change_singlemulti: function() {
            if ($("#singlemulti").val() == 0) {
                $("#timingrule").val("1");
                $("#timingrulenofrequencies").val("1");
                $("#timingrulefrequency").select("value", "0");
                $("#timingrulefrequency").select("disable");
                $("#treatmentrule").select("value", "0");
                $("#treatmentrule").select("disable");
                $("#totalnumberoftreatments").val("1");
                $("#timingrule").closest("tr").fadeOut();
                $("#treatmentrule").closest("tr").fadeOut();
            }
            else {
                $("#timingrule").val("1");
                $("#timingrulenofrequencies").val("1");
                $("#timingrulefrequency").select("value", "0");
                $("#timingrulefrequency").select("enable");
                $("#treatmentrule").select("value", "0");
                $("#treatmentrule").select("enable");
                $("#totalnumberoftreatments").val("1");
                $("#timingrule").closest("tr").fadeIn();
                $("#treatmentrule").closest("tr").fadeIn();
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

        name: "medicalprofile",
        animation: "book",
        title: function() { return _("Medical Profiles"); },
        routes: {
            "medicalprofile": function() { return common.module_loadandstart("medicalprofile", "medicalprofile"); }
        }

    };

    common.module_register(medicalprofile);

});
