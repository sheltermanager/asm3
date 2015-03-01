/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var citations = {};

    var dialog = {
        add_title: _("Add citation"),
        edit_title: _("Edit citation"),
        close_on_ok: true,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
            { json_field: "CITATIONTYPEID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "CITATIONNAME", valuefield: "ID", rows: controller.citationtypes }},
            { json_field: "CITATIONDATE", post_field: "citationdate", label: _("Date"), type: "date", validation: "notblank", defaultval: new Date() },
            { json_field: "FINEAMOUNT", post_field: "fineamount", label: _("Fine Amount"), type: "currency" },
            { json_field: "FINEDUEDATE", post_field: "finedue", label: _("Due"), type: "date" },
            { json_field: "FINEPAIDDATE", post_field: "finepaid", label: _("Paid"), type: "date" },
            { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                row.CITATIONNAME = common.get_field(controller.citationtypes, row.CITATIONTYPEID, "CITATIONNAME");
                row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                tableform.fields_post(dialog.fields, "mode=update&citationid=" + row.ID, controller.name, function(response) {
                    tableform.table_update(table);
                });
            });
        },
        complete: function(row) {
            if (row.FINEPAIDDATE) { return true; }
        },
        overdue: function(row) {
            return row.FINEDUEDATE && !row.FINEPAIDDATE && format.date_js(row.FINEDUEDATE) < common.today_no_time();
        },
        columns: [
            { field: "CITATIONNAME", display: _("Type") },
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
            { field: "ANIMALCONTROLID", display: _("Incident"), 
                formatter: function(row) { 
                    if (row.ANIMALCONTROLID) {
                        return '<a href="incident?id=' + row.ANIMALCONTROLID + '">' +
                            format.padleft(row.ID, 6) + ' - ' + row.INCIDENTNAME + '</a>';
                    }
                }, 
                hideif: function(row) {
                    return controller.name.indexOf("incident_") != -1;
                }
            },
            { field: "CITATIONDATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
            { field: "FINEAMOUNT", display: _("Fine Amount"), formatter: tableform.format_currency },
            { field: "FINEDUEDATE", display: _("Due"), formatter: tableform.format_date },
            { field: "FINEPAIDDATE", display: _("Paid"), formatter: tableform.format_date },
            { field: "COMMENTS", display: _("Comments") }
        ]
    };

    var buttons = [
         { id: "new", text: _("New Citation"), icon: "new", enabled: "always", perm: "aacc", 
             click: function() { 
                 $("#person").personchooser("clear");
                 if (controller.person) {
                     $("#person").personchooser("loadbyid", controller.person.ID);
                 }
                 if (controller.incident && controller.incident.OWNERID) {
                     $("#person").personchooser("loadbyid", controller.incident.OWNERID);
                 }
                 tableform.dialog_show_add(dialog, function() {
                     var incid = "";
                     if (controller.incident) { incid = controller.incident.ACID; }
                     tableform.fields_post(dialog.fields, "mode=create&incident=" + incid, controller.name, function(response) {
                         var row = {};
                         row.ID = response;
                         tableform.fields_update_row(dialog.fields, row);
                         row.CITATIONNAME = common.get_field(controller.citationtypes, row.CITATIONTYPEID, "CITATIONNAME");
                         row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                         controller.rows.push(row);
                         tableform.table_update(table);
                     });
                 }, function() { citations.type_change(); });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dacc", 
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

    citations = {

        render: function() {
            var s = "";
            s += tableform.dialog_render(dialog);
            if (controller.name.indexOf("incident_") == 0) {
                s += edit_header.incident_edit_header(controller.incident, "citation", controller.tabcounts);
            }
            else if (controller.name.indexOf("person_") == 0) {
                s += edit_header.person_edit_header(controller.person, "citation", controller.tabcounts);
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
            $("#type").change(citations.type_change);
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
        },

        type_change: function() {
            var dc = common.get_field(controller.citationtypes, $("#type").select("value"), "DEFAULTCOST");
            $("#fineamount").currency("value", dc);
        }

    };

    common.module(citations, "citations", "formtab");

});
