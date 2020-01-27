/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var fieldtypes = [
        { "ID": 0, "NAME": _("Yes/No") },
        { "ID": 11, "NAME": _("Checkbox") },
        { "ID": 1, "NAME": _("Text") },
        { "ID": 10, "NAME": _("Date") },
        { "ID": 16, "NAME": _("Time") },
        { "ID": 2, "NAME": _("Notes") },
        { "ID": 3, "NAME": _("Lookup") },
        { "ID": 14, "NAME": _("Lookup (Multiple Select)") },
        { "ID": 12, "NAME": _("Radio Buttons") },
        { "ID": 4, "NAME": _("Shelter Animal") },
        { "ID": 5, "NAME": _("Adoptable Animal") },
        { "ID": 6, "NAME": _("Color") },
        { "ID": 7, "NAME": _("Breed") },
        { "ID": 8, "NAME": _("Species") },
        { "ID": 9, "NAME": _("Raw Markup") },
        { "ID": 17, "NAME": _("Image") },
        { "ID": 13, "NAME": _("Signature") },
        { "ID": 15, "NAME": _("GDPR Contact Opt-In") }
    ];


    var onlineform = {

        model: function() {
            
            var species = controller.species;
            species.unshift( { "ID": -1, "SPECIESNAME": _("(all)") });

            var dialog = {
                add_title: _("Add form field"),
                edit_title: _("Edit form field"),
                edit_perm: 'eof',
                helper_text: _("Online form fields need a name and label."),
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "FIELDNAME", post_field: "fieldname", label: _("Name"), type: "text", validation: "notblank" }, 
                    { json_field: "FIELDTYPE", post_field: "fieldtype", label: _("Type"), type: "select", options: {
                        valuefield: "ID", displayfield: "NAME", rows: fieldtypes }},
                    { json_field: "LABEL", post_field: "label", label: _("Label"), type: "text", validation: "notblank" }, 
                    { json_field: "DISPLAYINDEX", post_field: "displayindex", label: _("Display Index"), type: "number" }, 
                    { json_field: "MANDATORY", post_field: "mandatory", label: _("Mandatory"), type: "check" },
                    { json_field: "LOOKUPS", post_field: "lookups", label: _("Lookups"), type: "textarea" }, 
                    { json_field: "SPECIESID", post_field: "species", label: _("Species"), type: "select", options: {
                        valuefield: "ID", displayfield: "SPECIESNAME", rows: species } }, 
                    { json_field: "TOOLTIP", post_field: "tooltip", label: _("Tooltip"), type: "textarea" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row, { onload: onlineform.check_controls })
                        .then(function() {
                            tableform.fields_update_row(dialog.fields, row);
                            return tableform.fields_post(dialog.fields, "mode=update&formfieldid=" + row.ID, "onlineform");
                        })
                        .then(function(response) {
                            tableform.table_update(table);
                            tableform.dialog_close();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();
                        });
                },
                columns: [
                    { field: "FIELDNAME", display: _("Name") },
                    { field: "DISPLAYINDEX", display: _("Display Index"), initialsort: true },
                    { field: "FIELDTYPE", display: _("Type"), formatter: function(row) {
                        return common.get_field(fieldtypes, row.FIELDTYPE, "NAME");
                    }},
                    { field: "LABEL", display: _("Label") }
                ]
            };

            var buttons = [
                 { id: "new", text: _("New form field"), icon: "new", enabled: "always", 
                     click: function() { 
                         tableform.dialog_show_add(dialog, { onload: onlineform.check_controls })
                             .then(function() {
                                return tableform.fields_post(dialog.fields, "mode=create&formid=" + controller.formid, "onlineform");
                             })
                             .then(function(response) {
                                 var row = {};
                                 row.ID = response;
                                 tableform.fields_update_row(dialog.fields, row);
                                 controller.rows.push(row);
                                 tableform.table_update(table);
                                 tableform.dialog_close();
                             })
                             .fail(function() {
                                 tableform.dialog_enable_buttons();
                             });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                     click: function() { 
                         tableform.delete_dialog()
                             .then(function() {
                                 tableform.buttons_default_state(buttons);
                                 var ids = tableform.table_ids(table);
                                 return common.ajax_post("onlineform", "mode=delete&ids=" + ids);
                             })
                             .then(function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                             });
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
            var ft = $("#fieldtype").select("value");
            if (ft == 3 || ft == 12 || ft == 14) {
                $("#lookups").closest("tr").fadeIn();
            }
            else {
                $("#lookups").closest("tr").fadeOut();
            }
            if (ft == 4 || ft == 5) {
                $("#species").closest("tr").fadeIn();
            }
            else {
                $("#species").closest("tr").fadeOut();
            }
            if (ft == 9) {
                $("#tooltip").closest("tr").find("label").html(_("Markup"));
            }
            else if (ft == 11) {
                $("#tooltip").closest("tr").find("label").html(_("Flags"));
            }
            else {
                $("#tooltip").closest("tr").find("label").html(_("Tooltip"));
            }
        },

        render: function() {
            var s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Online Form: {0}").replace("{0}", controller.formname));
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
            $("#fieldtype").change(this.check_controls);

            // Prompt with our recognised fields in the autocomplete
            $("#fieldname").autocomplete({ source: controller.formfields }); 
            // Fix for JQuery UI 10.3, autocomplete has to be created after the dialog is
            // shown or the stacking order is wrong. This fixes it now.
            $("#fieldname").autocomplete("widget").css("z-index", 1000);

        },

        destroy: function() {
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
