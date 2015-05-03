/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var rota = {};

    var dialog = {
        add_title: _("Add rota item"),
        edit_title: _("Edit rota item"),
        edit_perm: 'coro',
        close_on_ok: true,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "OWNERID", post_field: "person", personmode: "brief", personfilter: "volunteerandstaff", 
                label: _("Person"), type: "person", validation: "notzero" },
            { json_field: "ROTATYPEID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "ROTATYPE", valuefield: "ID", rows: controller.rotatypes }},
            { json_field: "STARTDATETIME", post_field: "startdate", label: _("Starts"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "STARTDATETIME", post_field: "starttime", label: _("at"), type: "time", validation: "notblank", defaultval: config.str("DefaultShiftStart") },
            { json_field: "ENDDATETIME", post_field: "enddate", label: _("Ends"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "ENDDATETIME", post_field: "endtime", label: _("at"), type: "time", validation: "notblank", defaultval: config.str("DefaultShiftEnd") },
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
                row.ROTATYPENAME = common.get_field(controller.rotatypes, row.ROTATYPEID, "ROTATYPE");
                tableform.fields_post(dialog.fields, "mode=update&rotaid=" + row.ID, controller.name, function(response) {
                    tableform.table_update(table);
                });
            });
        },
        columns: [
            { field: "ROTATYPENAME", display: _("Type") },
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
            { field: "STARTDATETIME", display: _("Start Time"), formatter: tableform.format_datetime, initialsort: true, initialsortdirection: "desc" },
            { field: "ENDDATETIME", display: _("End Time"), formatter: tableform.format_datetime },
            { field: "COMMENTS", display: _("Comments") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New"), icon: "new", enabled: "always", perm: "aoro",
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
                         row.ROTATYPENAME = common.get_field(controller.rotatypes, row.ROTATYPEID, "ROTATYPE");
                         controller.rows.push(row);
                         tableform.table_update(table);
                     });
                 });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "doro",
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

    rota = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            if (controller.name.indexOf("person_rota") == 0) {
                s += edit_header.person_edit_header(controller.person, "rota", controller.tabcounts);
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
            $("#startdate").change(function() {
                $("#enddate").val($("#startdate").val());
            });
        },

        name: "rota",
        animation: "formtab"

    };

    common.module_register(rota);

});
