/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, _, asm, common, config, controller, dlgfx, format, edit_header, html, tableform, validate */

$(function() {

    var dialog = {
        add_title: _("Add diet"),
        edit_title: _("Edit diet"),
        edit_perm: 'dcad',
        helper_text: _("Diets need a start date."),
        close_on_ok: true,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "DIETID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "DIETNAME", valuefield: "ID", rows: controller.diettypes }},
            { json_field: "DATESTARTED", post_field: "startdate", label: _("Start Date"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                row.DIETNAME = common.get_field(controller.diettypes, row.DIETID, "DIETNAME");
                row.DIETDESCRIPTION = common.get_field(controller.diettypes, row.DIETID, "DIETDESCRIPTION");
                tableform.fields_post(dialog.fields, "mode=update&dietid=" + row.ID, "animal_diet", function(response) {
                    tableform.table_update(table);
                });
            });
        },
        complete: function(row) {
            // Do we have a diet newer than this one? If so, mark it complete
            var iscomplete = false;
            $.each(controller.rows, function(i, v) {
                if (format.date_js(v.DATESTARTED) > format.date_js(row.DATESTARTED)) {
                    iscomplete = true;
                }
            });
            return iscomplete;
        },
        columns: [
            { field: "DIETNAME", display: _("Type") },
            { field: "DIETDESCRIPTION", display: _("Description") },
            { field: "DATESTARTED", display: _("Start Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
            { field: "COMMENTS", display: _("Comments") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New Diet"), icon: "new", enabled: "always", perm: "daad",
             click: function() { 
                 tableform.dialog_show_add(dialog, function() {
                     tableform.fields_post(dialog.fields, "mode=create&animalid="  + controller.animal.ID, "animal_diet", function(response) {
                         var row = {};
                         row.ID = response;
                         tableform.fields_update_row(dialog.fields, row);
                         row.DIETNAME = common.get_field(controller.diettypes, row.DIETID, "DIETNAME");
                         row.DIETDESCRIPTION = common.get_field(controller.diettypes, row.DIETID, "DIETDESCRIPTION");
                         controller.rows.push(row);
                         tableform.table_update(table);
                     });
                 });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "ddad",
             click: function() { 
                 tableform.delete_dialog(function() {
                     tableform.buttons_default_state(buttons);
                     var ids = tableform.table_ids(table);
                     common.ajax_post("animal_diet", "mode=delete&ids=" + ids , function() {
                         tableform.table_remove_selected_from_json(table, controller.rows);
                         tableform.table_update(table);
                     });
                 });
             } 
         }
    ];

    var animal_diet = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            s += edit_header.animal_edit_header(controller.animal, "diet", controller.tabcounts);
            s += tableform.buttons_render(buttons);
            s += tableform.table_render(table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
        }

    };

    common.module(animal_diet, "animal_diet", "formtab");

});
