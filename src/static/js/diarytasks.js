/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var dialog = {
        add_title: _("Add diary task"),
        edit_title: _("Edit diary task"),
        edit_perm: 'edt',
        helper_text: _("Diary tasks need a name."),
        close_on_ok: true,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "NAME", post_field: "name", label: _("Name"), type: "text", validation: "notblank" },
            { json_field: "RECORDTYPE", post_field: "type", label: _("Type"), type: "select", options: 
                '<option value="0">' + _("Animal") + '</option>' +
                '<option value="1">' + _("Person") + '</option>' }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                tableform.fields_post(dialog.fields, "mode=update&diarytaskid=" + row.ID, "diarytasks", function(response) {
                    tableform.table_update(table);
                });
            });
        },
        columns: [
            { field: "NAME", display: _("Name"), initialsort: true, formatter: function(row) {
                return "<span style=\"white-space: nowrap\">" + 
                    "<input type=\"checkbox\" data-id=\"" + row.ID + "\" title=\"" + html.title(_("Select")) + "\" />" +
                    "<a href=\"diarytask?taskid=" + row.ID + "\">" + row.NAME + "</a>" +
                    "<a href=\"#\" class=\"link-edit\" data-id=\"" + row.ID + "\">" + html.icon("edit", _("Edit diary task")) + "</a>" +
                    "</span>";
            }},
            { field: "RECORDTYPE", display: _("Type"), formatter: function(row) { return row.RECORDTYPE == 0 ? _("Animal") : _("Person"); }},
            { field: "NUMBEROFTASKS", display: _("Number of Tasks") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New diary task"), icon: "new", enabled: "always", 
             click: function() { 
                 tableform.dialog_show_add(dialog, function() {
                     tableform.fields_post(dialog.fields, "mode=create", "diarytasks", function(response) {
                         var row = {};
                         row.ID = response;
                         tableform.fields_update_row(dialog.fields, row);
                         controller.rows.push(row);
                         tableform.table_update(table);
                     });
                 });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
             click: function() { 
                 tableform.delete_dialog(function() {
                     tableform.buttons_default_state(buttons);
                     var ids = tableform.table_ids(table);
                     common.ajax_post("diarytasks", "mode=delete&ids=" + ids , function() {
                         tableform.table_remove_selected_from_json(table, controller.rows);
                         tableform.table_update(table);
                     });
                 });
             } 
         }
    ];

    var diarytasks = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            s += html.content_header(_("Diary Tasks"));
            s += tableform.buttons_render(buttons);
            s += tableform.table_render(table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
        }

    };
    
    common.module(diarytasks, "diarytasks", "formtab");

});
