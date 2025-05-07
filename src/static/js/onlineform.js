/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const fieldtypes = [
        { "ID": 0, "NAME": _("Yes/No") },
        { "ID": 11, "NAME": _("Checkbox") },
        { "ID": 1, "NAME": _("Text") },
        { "ID": 19, "NAME": _("Email") },
        { "ID": 10, "NAME": _("Date") },
        { "ID": 16, "NAME": _("Time") },
        { "ID": 20, "NAME": _("Number") },
        { "ID": 2, "NAME": _("Notes") },
        { "ID": 3, "NAME": _("Lookup") },
        { "ID": 14, "NAME": _("Lookup (Multiple Select)") },
        { "ID": 12, "NAME": _("Radio Buttons") },
        { "ID": 18, "NAME": _("Checkbox Group") },
        { "ID": 4, "NAME": _("Shelter Animal") },
        { "ID": 5, "NAME": _("Adoptable Animal") },
        { "ID": 21, "NAME": _("Foster Animal") },
        { "ID": 6, "NAME": _("Color") },
        { "ID": 7, "NAME": _("Breed") },
        { "ID": 8, "NAME": _("Species") },
        { "ID": 9, "NAME": _("Raw Markup") },
        { "ID": 17, "NAME": _("Image") },
        { "ID": 13, "NAME": _("Signature") },
        { "ID": 15, "NAME": _("GDPR Contact Opt-In") }
    ];

    const onlineform = {

        model: function() {
            
            let species = controller.species;
            species.unshift( { "ID": -1, "SPECIESNAME": _("(all)") });

            $.each(controller.rows, function(i, v) {
                v.RAWMARKUP = v.TOOLTIP;
            });

            const dialog = {
                add_title: _("Add form field"),
                edit_title: _("Edit form field"),
                edit_perm: 'eof',
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "FIELDNAME", post_field: "fieldname", label: _("Name"), type: "autotext", validation: "notblank",
                        options: controller.formfields },
                    { json_field: "FIELDTYPE", post_field: "fieldtype", label: _("Type"), type: "select", options: {
                        valuefield: "ID", displayfield: "NAME", rows: fieldtypes }},
                    { json_field: "VALIDATIONRULE", post_field: "validationrule", label: _("Validation Rule"), type: "select", 
                        options: '<option value=0>' + _("None") + '</option>' + 
                            '<option value=1>' + _("No past dates") + '</option>' + 
                            '<option value=2>' + _("No future dates") + '</option>',
                        xattr: 'style="display: none;"'
                    },
                    { json_field: "LABEL", post_field: "label", label: _("Label"), type: "text", maxlength: 1000, validation: "notblank" }, 
                    { json_field: "DISPLAYINDEX", post_field: "displayindex", label: _("Display Index"), type: "number" }, 
                    { json_field: "MANDATORY", post_field: "mandatory", label: _("Mandatory"), type: "check" },
                    { json_field: "VISIBLEIF", post_field: "visibleif", label: _("Show If"), type: "text", maxlength: 1000,
                        callout: _("Only show this field based on a conditional expression, eg: field1=dog") },
                    { json_field: "LOOKUPS", post_field: "lookups", label: _("Lookups"), type: "textarea" }, 
                    { json_field: "SPECIESID", post_field: "species", label: _("Species"), type: "select", options: {
                        valuefield: "ID", displayfield: "SPECIESNAME", rows: species } }, 
                    { json_field: "TOOLTIP", post_field: "tooltip", label: _("Additional"), type: "textarea",
                        callout: _("Additional text to be shown with the label to help the user complete this form field") },
                    { json_field: "RAWMARKUP", post_field: "rawmarkup", label: _("Markup"), type: "htmleditor", width: 400,
                        validation: function(v) {
                            if (v.indexOf("<!DOCTYPE") != -1 || v.indexOf("<html") != -1 || v.indexOf("<body") != -1) {
                                tableform.dialog_error(_("Markup should be HTML fragments, not a full document."));
                                return false;
                            }
                            return true;
                        }
                    }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    try {
                        if ( row.FIELDTYPE == 10 ) {
                            $("#validationrulerow").show();
                        } else {
                            $("#validationrulerow").hide();
                        }
                        await tableform.dialog_show_edit(dialog, row, { onload: onlineform.check_controls });
                        tableform.fields_update_row(dialog.fields, row);
                        await tableform.fields_post(dialog.fields, "mode=update&formid=" + controller.formid + "&formfieldid=" + row.ID, "onlineform");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err);
                        tableform.dialog_enable_buttons();
                    }
                },
                columns: [
                    { field: "FIELDNAME", display: _("Name") },
                    { field: "DISPLAYINDEX", display: _("Display Index"), initialsort: true },
                    { field: "FIELDTYPE", display: _("Type"), formatter: function(row) {
                        return common.get_field(fieldtypes, row.FIELDTYPE, "NAME");
                    }},
                    { field: "LABEL", display: _("Label"), formatter: function(row) {
                        return row.LABEL + " " + (row.MANDATORY == 1 ? '<span style="color: #f00">*</span>' : '');
                    }},
                    { field: "VISIBLEIF", display: _("Show If") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New form field"), icon: "new", enabled: "always", perm: "eof", 
                    click: async function() { 
                        try {
                            await tableform.dialog_show_add(dialog, { onload: onlineform.check_controls });
                            let response = await tableform.fields_post(dialog.fields, "mode=create&formid=" + controller.formid, "onlineform");
                            let row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
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
                { id: "reindex", text: _("Re-Index"), icon: "refresh", enabled: "always", perm: "eof",
                    click: async function() {
                        await tableform.show_okcancel_dialog("#dialog-reindex", _("Re-Index"), { width: 500 });
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("onlineform", "mode=reindex&formid=" + controller.formid);
                        common.route_reload();
                    }
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "eof", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("onlineform", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        /** Check which dialog controls should be shown
          */
        check_controls: function() {
            let ft = $("#fieldtype").select("value");
            if (ft == 3 || ft == 12 || ft == 14 || ft == 18) {
                $("#lookupsrow").fadeIn();
            }
            else {
                $("#lookupsrow").fadeOut();
            }
            if (ft == 4 || ft == 5 || ft == 21) {
                $("#speciesrow").fadeIn();
            }
            else {
                $("#speciesrow").fadeOut();
            }
            if (ft == 9) {
                $("#tooltiprow").fadeOut();
                $("#rawmarkuprow").fadeIn();
            }
            else if (ft == 11) {
                $("#tooltiprow").find("label").html(_("Flags"));
                $("#tooltiprow").fadeIn();
                $("#rawmarkuprow").fadeOut();
            }
            else {
                $("#tooltiprow").find("label").html(_("Additional"));
                $("#tooltiprow").fadeIn();
                $("#rawmarkuprow").fadeOut();
            }
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Online Form: {0}").replace("{0}", controller.formname));
            s += '<div id="dialog-reindex" style="display: none" title="' + html.title(_("Re-Index")) + '">' +
                '<p><span class="ui-icon ui-icon-alert"></span> ' + 
                _("This will recalculate display indexes in increments of 10 for every field in the form.") +
                '</p></div>';
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            // Stop users entering a space in the fieldname box
            $("#fieldname").keydown(function (e) {
                if (e.keyCode == 32) { return false; }
            });

            // Show/hide the lookup values box if type changes
            $("#fieldtype").change(function() {
                onlineform.check_controls();
                if ($("#fieldtype").val() == "10") {
                    $("#validationrulerow").show();
                } else {
                    $("#validationrulerow").hide();
                }
            });

        },

        destroy: function() {
            common.widget_destroy("#dialog-reindex");
            tableform.dialog_destroy();
        },

        name: "onlineform",
        animation: "formtab",
        title: function() { return controller.title; },
        routes: {
            "onlineform": function() { common.module_loadandstart("onlineform", "onlineform?formid=" + this.qs.formid); }
        }

    };

    common.module_register(onlineform);

});
