/*global $, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const additional = {

        model: function() {
            const dialog = {
                add_title: _("Add additional field"),
                edit_title: _("Edit additional field"),
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "FIELDNAME", post_field: "name", label: _("Name"), type: "text", validation: "notblank",
                        callout:_("Field names should not contain spaces.") },
                    { json_field: "FIELDLABEL", post_field: "label", label: _("Label"), type: "text", validation: "notblank" },
                    { json_field: "TOOLTIP", post_field: "tooltip", label: _("Tooltip"), type: "text" },
                    { json_field: "FIELDTYPE", post_field: "type", label: _("Type"), type: "select", 
                        options: { displayfield: "FIELDTYPE", valuefield: "ID", rows: controller.fieldtypes }},
                    { json_field: "LINKTYPE", post_field: "link", label: _("Link"), type: "select", 
                        options: { displayfield: "LINKTYPE", valuefield: "ID", rows: controller.linktypes }},
                    { json_field: "NEWRECORD", post_field: "newrecord", label: _("Show on new record screens"), type: "check" },
                    { json_field: "MANDATORY", post_field: "mandatory", label: _("Mandatory"), type: "check" },
                    { json_field: "SEARCHABLE", post_field: "searchable", label: _("Searchable"), type: "check" },
                    { json_field: "DISPLAYINDEX", post_field: "displayindex", label: _("Display Index"), type: "number", defaultval: "0" },
                    { json_field: "DEFAULTVALUE", post_field: "defaultvalue", label: _("Default Value"), type: "text" },
                    { json_field: "LOOKUPVALUES", post_field: "lookupvalues", label: _("Lookup Values"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row, { onload: additional.check_type });
                    tableform.fields_update_row(dialog.fields, row);
                    row.FIELDTYPENAME = common.get_field(controller.fieldtypes, row.FIELDTYPE, "FIELDTYPE");
                    row.LINKTYPENAME = common.get_field(controller.linktypes, row.LINKTYPE, "LINKTYPE");
                    await tableform.fields_post(dialog.fields, "mode=update&id=" + row.ID, "additional");
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                columns: [
                    { field: "FIELDNAME", display: _("Name"), initialsort: true },
                    { field: "FIELDLABEL", display: _("Label") },
                    { field: "ID", display: _("ID"), hideif: function(row) {
                        return !config.bool("ShowLookupDataID");
                    }},
                    { field: "FIELDTYPENAME", display: _("Type") },
                    { field: "LINKTYPENAME", display: _("Link") },
                    { field: "NEWRECORD", display: _("New Record"), formatter: function(row) { if (row.NEWRECORD == 1) { return _("Yes"); } return _("No"); }},
                    { field: "MANDATORY", display: _("Mandatory"), formatter: function(row) { if (row.MANDATORY == 1) { return _("Yes"); } return _("No"); }},
                    { field: "SEARCHABLE", display: _("Searchable"), formatter: function(row) { if (row.SEARCHABLE == 1) { return _("Yes"); } return _("No"); }},
                    { field: "DISPLAYINDEX", display: _("Index") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Field"), icon: "new", enabled: "always", 
                    click: async function() { 
                        await tableform.dialog_show_add(dialog, { onload: additional.check_type });
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "additional");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        row.FIELDTYPENAME = common.get_field(controller.fieldtypes, row.FIELDTYPE, "FIELDTYPE");
                        row.LINKTYPENAME = common.get_field(controller.linktypes, row.LINKTYPE, "LINKTYPE");
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();  
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                    click: async function() { 
                        await tableform.delete_dialog(null, _("This will permanently remove this additional field and ALL DATA CURRENTLY HELD AGAINST IT. This action is irreversible, are you sure you want to do this?"));
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("additional", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render: function() {
            this.model();
            let s = "";
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Additional Fields"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        /** 
         * Depending on type selected, show or hide the lookups
         * and searchable fields.
          */
        check_type: function() {
            let ft = $("#type").select("value");
            // Show lookups if field type is yes/no, lookup or multi-lookup
            if (ft == 0 || ft == 6 || ft == 7) {
                $("#lookupvalues").closest("tr").fadeIn();
            }
            else {
                $("#lookupvalues").closest("tr").fadeOut();
            }
            // Show searchable for correct field types
            // of text, notes, number, lookup or multi-lookup
            if (ft == 1 || ft == 2 || ft == 3 || ft == 6 || ft == 7) {
                $("#searchable").closest("tr").fadeIn();
            }
            else {
                $("#searchable").prop("checked", false);
                $("#searchable").closest("tr").fadeOut();
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

            // Show/hide fields if type changes
            $("#type").change(additional.check_type);

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
