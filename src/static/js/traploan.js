/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const traploan = {

        model: function() {
            const dialog = {
                add_title: _("Add equipment loan"),
                edit_title: _("Edit equipment loan"),
                edit_perm: 'catl',
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
                    { json_field: "TRAPTYPEID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "TRAPTYPENAME", valuefield: "ID", rows: controller.traptypes }},
                    { json_field: "LOANDATE", post_field: "loandate", label: _("Date"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "DEPOSITAMOUNT", post_field: "depositamount", label: _("Deposit"), type: "currency" },
                    { json_field: "DEPOSITRETURNDATE", post_field: "depositreturndate", label: _("Deposit Returned"), type: "date" },
                    { json_field: "TRAPNUMBER", post_field: "trapnumber", label: _("Number"), type: "text", 
                      callout: _("A unique number to identify this piece of equipment") },
                    { json_field: "RETURNDUEDATE", post_field: "returnduedate", label: _("Due"), type: "date" },
                    { json_field: "RETURNDATE", post_field: "returndate", label: _("Returned"), type: "date" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    row.TRAPTYPENAME = common.get_field(controller.traptypes, row.TRAPTYPEID, "TRAPTYPENAME");
                    row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                    await tableform.fields_post(dialog.fields, "mode=update&traploanid=" + row.ID, "traploan");
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                complete: function(row) {
                    if (row.RETURNDATE) { return true; }
                },
                overdue: function(row) {
                    return row.RETURNDUEDATE && !row.RETURNDATE && format.date_js(row.RETURNDUEDATE) < common.today_no_time();
                },
                columns: [
                    { field: "TRAPTYPENAME", display: _("Type") },
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
                    { field: "LOANDATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
                    { field: "TRAPNUMBER", display: _("Number") },
                    { field: "DEPOSITAMOUNT", display: _("Deposit"), formatter: tableform.format_currency },
                    { field: "RETURNDUEDATE", display: _("Due"), formatter: tableform.format_date },
                    { field: "RETURNDATE", display: _("Returned"), formatter: tableform.format_date },
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Loan"), icon: "new", enabled: "always", perm: "aatl",
                    click: async function() { 
                        $("#person").personchooser("clear");
                        if (controller.person) {
                            $("#person").personchooser("loadbyid", controller.person.ID);
                        }
                        await tableform.dialog_show_add(dialog, { onload: traploan.type_change });
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "traploan");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        row.TRAPTYPENAME = common.get_field(controller.traptypes, row.TRAPTYPEID, "TRAPTYPENAME");
                        row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "datl",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("traploan", "mode=delete&ids=" + ids);
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
            if (controller.name.indexOf("person_") == 0) {
                s += edit_header.person_edit_header(controller.person, "traploan", controller.tabcounts);
            }
            else {
                s += html.content_header(this.title());
            }
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            $("#type").change(traploan.type_change);
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        type_change: function() {
            let dc = common.get_field(controller.traptypes, $("#type").select("value"), "DEFAULTCOST");
            $("#depositamount").currency("value", dc);
        },

        destroy: function() {
            common.widget_destroy("#person");
            tableform.dialog_destroy();
        },

        name: "traploan",
        animation: function() { return controller.name == "traploan" ? "book" : "formtab"; },
        title: function() {
            if (controller.name == "person_traploan") {
                return controller.person.OWNERNAME;
            }
            return _("Active Equipment Loans");
        },
        routes: {
            "person_traploan": function() { common.module_loadandstart("traploan", "person_traploan?id=" + this.qs.id); },
            "traploan": function() { common.module_loadandstart("traploan", "traploan?" + this.rawqs); }
        }

    };

    common.module_register(traploan);

});
