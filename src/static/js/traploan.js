/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var traploan = {

        model: function() {
            var dialog = {
                add_title: _("Add trap loan"),
                edit_title: _("Edit trap loan"),
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
                    { json_field: "TRAPNUMBER", post_field: "trapnumber", label: _("Trap Number"), type: "text" },
                    { json_field: "RETURNDUEDATE", post_field: "returnduedate", label: _("Due"), type: "date" },
                    { json_field: "RETURNDATE", post_field: "returndate", label: _("Returned"), type: "date" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row)
                        .then(function() {
                            tableform.fields_update_row(dialog.fields, row);
                            row.TRAPTYPENAME = common.get_field(controller.traptypes, row.TRAPTYPEID, "TRAPTYPENAME");
                            row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                            return tableform.fields_post(dialog.fields, "mode=update&traploanid=" + row.ID, controller.name);
                        })
                        .then(function(response) {
                            tableform.table_update(table);
                            tableform.dialog_close();
                        });
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
                                return edit_header.person_link(row, row.OWNERID);
                            }
                            return "";
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("person_") != -1;
                        }
                    },
                    { field: "LOANDATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
                    { field: "TRAPNUMBER", display: _("Trap Number") },
                    { field: "DEPOSITAMOUNT", display: _("Deposit"), formatter: tableform.format_currency },
                    { field: "RETURNDUEDATE", display: _("Due"), formatter: tableform.format_date },
                    { field: "RETURNDATE", display: _("Returned"), formatter: tableform.format_date },
                    { field: "COMMENTS", display: _("Comments") }
                ]
            };

            var buttons = [
                 { id: "new", text: _("New Trap Loan"), icon: "new", enabled: "always", perm: "aatl",
                     click: function() { 
                         $("#person").personchooser("clear");
                         if (controller.person) {
                             $("#person").personchooser("loadbyid", controller.person.ID);
                         }
                         tableform.dialog_show_add(dialog, null, traploan.type_change)
                             .then(function() {
                                 return tableform.fields_post(dialog.fields, "mode=create", controller.name);
                             })
                             .then(function(response) {
                                 var row = {};
                                 row.ID = response;
                                 tableform.fields_update_row(dialog.fields, row);
                                 row.TRAPTYPENAME = common.get_field(controller.traptypes, row.TRAPTYPEID, "TRAPTYPENAME");
                                 row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                                 controller.rows.push(row);
                                 tableform.table_update(table);
                                 tableform.dialog_close();
                             });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "datl",
                     click: function() { 
                         tableform.delete_dialog()
                             .then(function() {
                                 tableform.buttons_default_state(buttons);
                                 var ids = tableform.table_ids(table);
                                 return common.ajax_post(controller.name, "mode=delete&ids=" + ids);
                             }) 
                             .then(function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                             });
                     } 
                 }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            var s = "";
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
            var dc = common.get_field(controller.traptypes, $("#type").select("value"), "DEFAULTCOST");
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
            return _("Active Trap Loans");
        },
        routes: {
            "person_traploan": function() { common.module_loadandstart("traploan", "person_traploan?id=" + this.qs.id); },
            "traploan": function() { common.module_loadandstart("traploan", "traploan?" + this.rawqs); }
        }

    };

    common.module_register(traploan);

});
