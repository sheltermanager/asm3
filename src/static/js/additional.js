/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var additional = {

        model: function() {
            var dialog = {
                add_title: _("Add additional field"),
                edit_title: _("Edit additional field"),
                helper_text: _("Additional fields need a name, label and type.") + '<br />' + _("Field names should not contain spaces."),
                close_on_ok: true,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "FIELDNAME", post_field: "name", label: _("Name"), type: "text", validation: "notblank" },
                    { json_field: "FIELDLABEL", post_field: "label", label: _("Label"), type: "text", validation: "notblank" },
                    { json_field: "TOOLTIP", post_field: "tooltip", label: _("Tooltip"), type: "text" },
                    { json_field: "FIELDTYPE", post_field: "type", label: _("Type"), type: "select", 
                        options: { displayfield: "FIELDTYPE", valuefield: "ID", rows: controller.fieldtypes }},
                    { json_field: "LINKTYPE", post_field: "link", label: _("Link"), type: "select", 
                        options: { displayfield: "LINKTYPE", valuefield: "ID", rows: controller.linktypes }},
                    { json_field: "MANDATORY", post_field: "mandatory", label: _("Mandatory"), type: "check" },
                    { json_field: "SEARCHABLE", post_field: "searchable", label: _("Searchable"), type: "check" },
                    { json_field: "DISPLAYINDEX", post_field: "displayindex", label: _("Display Index"), type: "number", defaultval: "0" },
                    { json_field: "DEFAULTVALUE", post_field: "defaultvalue", label: _("Default Value"), type: "text" },
                    { json_field: "LOOKUPVALUES", post_field: "lookupvalues", label: _("Lookup Values"), type: "textarea" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row, function() {
                        tableform.fields_update_row(dialog.fields, row);
                        row.FIELDTYPENAME = common.get_field(controller.fieldtypes, row.FIELDTYPE, "FIELDTYPE");
                        row.LINKTYPENAME = common.get_field(controller.linktypes, row.LINKTYPE, "LINKTYPE");
                        tableform.fields_post(dialog.fields, "mode=update&id=" + row.ID, "additional", function(response) {
                            tableform.table_update(table);
                        });
                    }, function() {
                        additional.check_lookup_values();
                    });
                },
                columns: [
                    { field: "FIELDNAME", display: _("Name"), initialsort: true },
                    { field: "FIELDLABEL", display: _("Label") },
                    { field: "FIELDTYPENAME", display: _("Type") },
                    { field: "LINKTYPENAME", display: _("Link") },
                    { field: "MANDATORY", display: _("Mandatory"), formatter: function(row) { if (row.MANDATORY == 1) { return _("Yes"); } return _("No"); }},
                    { field: "SEARCHABLE", display: _("Searchable"), formatter: function(row) { if (row.SEARCHABLE == 1) { return _("Yes"); } return _("No"); }},
                    { field: "DISPLAYINDEX", display: _("Index") }
                ]
            };

            var buttons = [
                 { id: "new", text: _("New Field"), icon: "new", enabled: "always", 
                     click: function() { 
                         tableform.dialog_show_add(dialog, function() {
                             additional.check_lookup_values();
                             tableform.fields_post(dialog.fields, "mode=create", "additional", function(response) {
                                 var row = {};
                                 row.ID = response;
                                 tableform.fields_update_row(dialog.fields, row);
                                 row.FIELDTYPENAME = common.get_field(controller.fieldtypes, row.FIELDTYPE, "FIELDTYPE");
                                 row.LINKTYPENAME = common.get_field(controller.linktypes, row.LINKTYPE, "LINKTYPE");
                                 controller.rows.push(row);
                                 tableform.table_update(table);
                             });
                         }, function() { additional.check_lookup_values(); });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                     click: function() { 
                         tableform.delete_dialog(function() {
                             tableform.buttons_default_state(buttons);
                             var ids = tableform.table_ids(table);
                             common.ajax_post("additional", "mode=delete&ids=" + ids , function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                             });
                         },
                         _("This will permanently remove this additional field and ALL DATA CURRENTLY HELD AGAINST IT. This action is irreversible, are you sure you want to do this?"));
                     } 
                 }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render: function() {
            this.model();
            var s = "";
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Additional Fields"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        /** Check if we should show the lookup values row (only
          * valid if the field type is yes/no, lookup or multi-lookup
          */
        check_lookup_values: function() {
            var ft = $("#type").select("value");
            if (ft == 0 || ft == 6 || ft == 7) {
                $("#lookupvalues").closest("tr").fadeIn();
            }
            else {
                $("#lookupvalues").closest("tr").fadeOut();
            }
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            // Stop users entering a space or question mark in the fieldname box
            $("#name").keydown(function (e) {
                if (e.keyCode == 32 || e.keyCode == 191) { return false; }
            });

            // Show/hide the lookup values box if type changes
            $("#type").change(additional.check_lookup_values);

        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "additional",
        animation: "options",
        title: function() { return _("Additional Fields"); },

        routes: {
            "additional": function() {
                common.module_loadandstart("additional", "additional");
            }
        }


    };

    common.module_register(additional);

});
