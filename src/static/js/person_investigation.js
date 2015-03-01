/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, _, asm, common, config, controller, dlgfx, format, edit_header, html, tableform, validate */

$(function() {

    var dialog = {
        add_title: _("Add investigation"),
        edit_title: _("Edit investigation"),
        helper_text: _("Date and notes are mandatory."),
        close_on_ok: true,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "DATE", post_field: "date", label: _("Date"), type: "date", validation: "notblank" },
            { json_field: "NOTES", post_field: "notes", label: _("Notes"), type: "textarea", validation: "notblank" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                tableform.fields_post(dialog.fields, "mode=update&investigationid=" + row.ID, "person_investigation", function(response) {
                    tableform.table_update(table);
                });
            });
            $("#date").datepicker("hide");
            $("#notes").focus();
        },
        columns: [
            { field: "CREATEDBY", display: _("By") },
            { field: "DATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date }, 
            { field: "NOTES", display: _("Notes") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New"), icon: "new", enabled: "always", perm: "aoi",
             click: function() { 
                 tableform.dialog_show_add(dialog, function() {
                     tableform.fields_post(dialog.fields, "mode=create&personid="  + controller.person.ID, "person_investigation", function(response) {
                         var row = {};
                         row.ID = response;
                         tableform.fields_update_row(dialog.fields, row);
                         controller.rows.push(row);
                         tableform.table_update(table);
                     });
                 });
                 $("#date").datepicker("setDate", new Date());
                 $("#date").datepicker("hide");
                 $("#notes").focus();
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "doi",
             click: function() { 
                 tableform.delete_dialog(function() {
                     tableform.buttons_default_state(buttons);
                     var ids = tableform.table_ids(table);
                     common.ajax_post("person_investigation", "mode=delete&ids=" + ids , function() {
                         tableform.table_remove_selected_from_json(table, controller.rows);
                         tableform.table_update(table);
                     });
                 });
             } 
         }
    ];

    var person_investigation = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            s += edit_header.person_edit_header(controller.person, "investigation", controller.tabcounts);
            s += tableform.buttons_render(buttons);
            s += tableform.table_render(table);
            s += '</div> <!-- asmcontent -->';
            s += '</div> <!-- tabs -->';
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
        }

    };

    common.module(person_investigation, "person_investigation", "formtab");

});
