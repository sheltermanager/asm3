/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var rotahours = {};

    var dialog = {
        add_title: _("Add hours"),
        edit_title: _("Edit hours"),
        close_on_ok: true,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
            { json_field: "STARTDATETIME", post_field: "startdate", label: _("Start Date"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "STARTDATETIME", post_field: "starttime", label: _("Start Time"), type: "time", validation: "notblank", defaultval: "09:00" },
            { json_field: "ENDDATETIME", post_field: "enddate", label: _("End Date"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "ENDDATETIME", post_field: "endtime", label: _("End Time"), type: "time", validation: "notblank", defaultval: "17:00" },

            { json_field: "STATUS", post_field: "status", label: _("Type"), type: "select", options: { displayfield: "STATUS", valuefield: "ID", rows: controller.rotahoursstatuses }},
            { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                row.STATUSNAME = common.get_field(controller.rotahoursstatuses, row.STATUS, "STATUS");
                tableform.fields_post(dialog.fields, "mode=update&hoursid=" + row.ID, controller.name, function(response) {
                    tableform.table_update(table);
                });
            });
        },
        columns: [
            { field: "STATUSNAME", display: _("Type") },
            { field: "PERSON", display: _("Person"),
                formatter: function(row) {
                    if (row.OWNERID) {
                        return edit_header.person_link(row, row.OWNERID);
                    }
                    return "";
                },
                hideif: function(row) {
                    return controller.name.indexOf("person_") != -1;
                }
            },
            { field: "STARTDATETIME", display: _("Start Time"), formatter: tableform.format_datetime },
            { field: "ENDDATETIME", display: _("End Time"), formatter: tableform.format_datetime },
            { field: "COMMENTS", display: _("Comments") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New Hours"), icon: "new", enabled: "always", perm: "aorh",
             click: function() { 
                 $("#person").personchooser("clear");
                 if (controller.person) {
                     $("#person").personchooser("loadbyid", controller.person.ID);
                 }
                 tableform.dialog_show_add(dialog, function() {
                     tableform.fields_post(dialog.fields, "mode=create", controller.name, function(response) {
                         var row = {};
                         row.ID = response;
                         tableform.fields_update_row(dialog.fields, row);
                         row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                         row.STATUSNAME = common.get_field(controller.rotahoursstatuses, row.STATUS, "STATUS");
                         controller.rows.push(row);
                         tableform.table_update(table);
                     });
                 });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dorh",
             click: function() { 
                 tableform.delete_dialog(function() {
                     tableform.buttons_default_state(buttons);
                     var ids = tableform.table_ids(table);
                     common.ajax_post(controller.name, "mode=delete&ids=" + ids , function() {
                         tableform.table_remove_selected_from_json(table, controller.rows);
                         tableform.table_update(table);
                     });
                 });
             } 
         }
    ];

    rotahours = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            if (controller.name.indexOf("person_") == 0) {
                s += edit_header.person_edit_header(controller.person, "rotahours", controller.tabcounts);
            }
            else {
                s += html.content_header(controller.title);
            }
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

    common.module(rotahours, "rotahours", "formtab");

});
