/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const citations = {
        
        model: function() {
            const dialog = {
                add_title: _("Add citation"),
                edit_title: _("Edit citation"),
                edit_perm: 'cacc',
                close_on_ok: false,
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

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    row.CITATIONNAME = common.get_field(controller.citationtypes, row.CITATIONTYPEID, "CITATIONNAME");
                    row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                    await tableform.fields_post(dialog.fields, "mode=update&citationid=" + row.ID, "citations");
                    tableform.table_update(table);
                    tableform.dialog_close();
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
                                return html.person_link(row.OWNERID, row.OWNERNAME);
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
                                    format.padleft(row.ANIMALCONTROLID, 6) + ' - ' + row.INCIDENTNAME + '</a>';
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
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            var buttons = [
                { id: "new", text: _("New Citation"), icon: "new", enabled: "always", perm: "aacc", 
                    click: async function() { 
                        $("#person").personchooser("clear");
                        if (controller.person) {
                            $("#person").personchooser("loadbyid", controller.person.ID);
                        }
                        if (controller.incident && controller.incident.OWNERID) {
                            $("#person").personchooser("loadbyid", controller.incident.OWNERID);
                        }
                        await tableform.dialog_show_add(dialog, { onload: citations.type_change });
                        var incid = "";
                        if (controller.incident) { incid = controller.incident.ACID; }
                        let response = await tableform.fields_post(dialog.fields, "mode=create&incident=" + incid, "citations");
                        var row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        row.CITATIONNAME = common.get_field(controller.citationtypes, row.CITATIONTYPEID, "CITATIONNAME");
                        row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dacc", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        var ids = tableform.table_ids(table);
                        await common.ajax_post("citations", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            if (controller.name.indexOf("incident_") == 0) {
                s += edit_header.incident_edit_header(controller.incident, "citation", controller.tabcounts);
            }
            else if (controller.name.indexOf("person_") == 0) {
                s += edit_header.person_edit_header(controller.person, "citation", controller.tabcounts);
            }
            else {
                s += html.content_header(controller.title);
            }
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            $("#type").change(citations.type_change);
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        type_change: function() {
            let dc = common.get_field(controller.citationtypes, $("#type").select("value"), "DEFAULTCOST");
            $("#fineamount").currency("value", dc);
        },

        destroy: function() {
            common.widget_destroy("#person");
            tableform.dialog_destroy();
        },

        name: "citations",
        animation: function() { return controller.name == "citations" ? "book" : "formtab"; },
        title:  function() { 
            let t = "";
            if (controller.name == "person_citations") { t = controller.person.OWNERNAME; }
            else if (controller.name == "incident_citations") { t = common.substitute(_("Incident {0}, {1}: {2}"), {
                0: controller.incident.ACID, 1: controller.incident.INCIDENTNAME, 2: format.date(controller.incident.INCIDENTDATETIME)});
            }
            else if (controller.name == "citations") { t = _("Unpaid Fines"); }
            return t;
        },

        routes: {
            "incident_citations": function() { common.module_loadandstart("citations", "incident_citations?id=" + this.qs.id); },
            "person_citations": function() { common.module_loadandstart("citations", "person_citations?id=" + this.qs.id); },
            "citations": function() { common.module_loadandstart("citations", "citations?" + this.rawqs); }
        }

    };

    common.module_register(citations);

});
