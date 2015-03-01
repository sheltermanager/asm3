/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var log = {};

    var dialog = {
        add_title: _("Add log"),
        edit_title: _("Edit log"),
        helper_text: _("Log entries need a date and text."),
        close_on_ok: true,
        columns: 1,
        width: 500,
        fields: [
            { json_field: "LOGTYPEID", post_field: "type", label: _("Type"), type: "select", 
                options: { displayfield: "LOGTYPENAME", valuefield: "ID", rows: controller.logtypes }},
            { json_field: "DATE", post_field: "logdate", label: _("Date"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "COMMENTS", post_field: "entry", label: _("Comments"), type: "textarea" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.fields_populate_from_json(dialog.fields, row);
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                log.set_extra_fields(row);
                tableform.fields_post(dialog.fields, "mode=update&logid=" + row.ID, controller.name, function(response) {
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                function(response) {
                    tableform.dialog_error(response);
                    tableform.dialog_enable_buttons();
                });
            });
        },
        columns: [
            { field: "LOGTYPENAME", display: _("Type") },
            { field: "LASTCHANGEDBY", display: _("By") },
            { field: "DATE", display: _("Date"), formatter: tableform.format_date, initialsort: true, initialsortdirection: "desc" },
            { field: "COMMENTS", display: _("Note"), formatter: function(row, v) { return v.replace(/\n/g, "<br />");  }}
        ]
    };

    var buttons = [
        { id: "new", text: _("New Log"), icon: "new", enabled: "always", perm: "ale", click: function() { 
            tableform.dialog_show_add(dialog, function() {
                tableform.fields_post(dialog.fields, "mode=create&linkid=" + controller.linkid, controller.name, function(response) {
                    var row = {};
                    row.ID = response;
                    tableform.fields_update_row(dialog.fields, row);
                    log.set_extra_fields(row);
                    controller.rows.push(row);
                    tableform.table_update(table);
                    tableform.dialog_close();
                }, function() {
                    tableform.dialog_enable_buttons();   
                });
            });
         }},
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dle",
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
         },
         { id: "filter", type: "dropdownfilter", 
             options: '<option value="-1">' + _("(all)") + '</option>' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
             click: function(selval) {
                window.location = controller.name + "?id=" + controller.linkid + "&filter=" + selval;
             }
         }
    ];

    log = {

        set_extra_fields: function(row) {
            row.LOGTYPENAME = common.get_field(controller.logtypes, row.LOGTYPEID, "LOGTYPENAME");
            row.LASTCHANGEDBY = asm.user;
        },

        render: function() {
            var h = [];
            h.push(tableform.dialog_render(dialog));
            if (controller.name == "animal_log") {
                h.push(edit_header.animal_edit_header(controller.animal, "logs", controller.tabcounts));
            }
            else if (controller.name == "person_log") {
                h.push(edit_header.person_edit_header(controller.person, "logs", controller.tabcounts));
            }
            else if (controller.name == "waitinglist_log") {
                h.push(edit_header.waitinglist_edit_header(controller.animal, "logs", controller.tabcounts));
            }
            else if (controller.name == "lostanimal_log") {
                h.push(edit_header.lostfound_edit_header("lost", controller.animal, "logs", controller.tabcounts));
            }
            else if (controller.name == "foundanimal_log") {
                h.push(edit_header.lostfound_edit_header("found", controller.animal, "logs", controller.tabcounts));
            }
            else if (controller.name == "incident_log") {
                h.push(edit_header.incident_edit_header(controller.incident, "logs", controller.tabcounts));
            }
            h.push(tableform.buttons_render(buttons));
            h.push(tableform.table_render(table));
            h.push(html.content_footer());
            return h.join("\n");
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
        },

        sync: function() {
            // If we have a filter, update the select
            if (controller.filter) {
                $("#filter").select("value", controller.filter);
            }
        }
    };
    
    common.module(log, "log", "formtab");

});
