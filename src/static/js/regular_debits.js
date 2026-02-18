/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const regular_debits = {

        model: function() {
            let daysofmonth = [];
            for (let a = 1; a < 29; a++ ) {
                daysofmonth.push(a + "|" + a);
            }
            const dialog = {
                add_title: _("Add regular debit"),
                edit_title: _("Edit regular debit"),
                edit_perm: 'cac',
                close_on_ok: false,
                hide_read_only: true,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", personfilter: "all", personmode: "brief" },
                    { json_field: "STARTDATE", post_field: "startdate", label: _("Active from"), type: "date", validation: "notblank" },
                    { json_field: "ENDDATE", post_field: "enddate", label: _("Active to"), type: "date" },
                    { json_field: "AMOUNT", post_field: "amount", label: _("Amount"), type: "currency", validation: "notzero" },
                    { json_field: "FROMACCOUNT", post_field: "fromaccount", label: _("From account"), type: "select", options: { rows: controller.accounts, displayfield: "CODE" } },
                    { json_field: "TOACCOUNT", post_field: "toaccount", label: _("To account"), type: "select", options: { rows: controller.accounts, displayfield: "CODE" } },
                    { json_field: "PERIOD", post_field: "period", label: _("Period"), type: "select",
                        options: [
                            "1|" + _("Daily"),
                            "7|" + _("Weekly"),
                            "30|" + _("Monthly"),
                            "365|" + _("Yearly")
                        ]
                    },
                    { json_field: "WEEKDAY", post_field: "weekday", label: _("Day of week"), type: "select",
                        options: [
                            "0|" + _("Sunday"),
                            "1|" + _("Monday"),
                            "2|" + _("Tuesday"),
                            "3|" + _("Wednesday"),
                            "4|" + _("Thursday"),
                            "5|" + _("Friday"),
                            "6|" + _("Saturday")
                            
                        ]
                    },
                    { json_field: "DAYOFMONTH", post_field: "dayofmonth", label: _("Day of month"), type: "select", options: daysofmonth },
                    { json_field: "MONTH", post_field: "month", label: _("Month"), type: "select",
                        options: [
                            "1|" + _("January"),
                            "2|" + _("February"),
                            "3|" + _("March"),
                            "4|" + _("April"),
                            "5|" + _("May"),
                            "6|" + _("June"),
                            "7|" + _("July"),
                            "8|" + _("August"),
                            "9|" + _("September"),
                            "10|" + _("October"),
                            "11|" + _("November"),
                            "12|" + _("December")
                        ]
                    },
                    { json_field: "DESCRIPTION", post_field: "description", label: _("Description"), type: "textarea" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" },
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    tableform.dialog_show_edit(dialog, row, {
                        onvalidate: function() {
                            return regular_debits.validation();
                        },
                        onchange: async function() {
                            tableform.fields_post(dialog.fields, "mode=update&id=" + row.ID, "regular_debits")
                                .then(function() {
                                    row.OWNERNAME = $("#personrow .asm-embed-name").text();
                                    tableform.fields_update_row(dialog.fields, row);
                                    tableform.table_update(table);
                                    tableform.dialog_close();
                                })
                                .fail(function(response) {
                                    tableform.dialog_error(response);
                                    tableform.dialog_enable_buttons();
                                });
                        },
                        onload: function() {
                            regular_debits.period_changed();
                        }
                    });
                },
                columns: [
                    { field: "STARTDATE", display: _("Active from"),
                        formatter: function(row) {
                            return tableform.table_render_edit_link(row.ID, tableform.format_date(row, row.STARTDATE));
                        }
                    },
                    { field: "ENDDATE", display: _("Active to"), formatter: tableform.format_date },
                    { field: "OWNERID", display: _("Person"),
                        formatter: function(row) {
                            if (row.OWNERID == 0) {
                                return "";
                            } else {
                                return '<a href="person?id=' + row.OWNERID + '">' + row.OWNERNAME + '</a>';
                            }
                        }
                    },
                    { field: "AMOUNT", display: _("Amount"), formatter: tableform.format_currency },
                    { field: "PERIOD", display: _("Period"),
                        formatter: function(row) {
                            if (row.PERIOD == 1) {
                                return _("Daily");
                            } else if (row.PERIOD == 7) {
                                return _("Weekly");
                            } else if (row.PERIOD == 30) {
                                return _("Monthly");
                            } else {
                                return _("Yearly");
                            }
                        }
                    },
                    { field: "FROMACCOUNT", display: _("From Account"),
                        formatter: function(row) {
                            let accountcode = "";
                            $.each(controller.accounts, function(i, v) {
                                if (v.ID == row.FROMACCOUNT) { accountcode = v.CODE; }
                            });
                            return accountcode;
                        }
                    },
                    { field: "TOACCOUNT", display: _("To Account"),
                        formatter: function(row) {
                            let accountcode = "";
                            $.each(controller.accounts, function(i, v) {
                                if (v.ID == row.TOACCOUNT) { accountcode = v.CODE; }
                            });
                            return accountcode;
                        }
                    },
                    { field: "DESCRIPTION", display: _("Description") }
                ]
            };

            const buttons = [
               { id: "new", text: _("New Regular Debit"), icon: "new", enabled: "always", perm: "aac",
                    click: async function() { 
                        await tableform.dialog_show_add(dialog, {
                            onvalidate: function() {
                                return regular_debits.validation();
                            }
                        });
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "regular_debits");
                        let row = {};
                        row.ID = response;
                        row.OWNERNAME = $("#personrow .asm-embed-name").text();
                        tableform.fields_update_row(dialog.fields, row);
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }  
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dac",
                    click: async function() { 
                        await tableform.delete_dialog(null, _("This will permanently remove this regular debit, are you sure you want to do this?"));
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("regular_debits", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "filter", type: "dropdownfilter", 
                    options: [
                        "active|" + _("Active"),
                        "inactive|" + _("Inactive"),
                        "all|" + _("All")
                    ],
                    click: function(selval) {
                        controller.filter = selval;
                        common.route("regular_debits?filter=" + selval);
                    }
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        period_changed: function() {
            let period = $("#period").val();
            $("#weekdayrow").toggle( period == 7 );
            $("#dayofmonthrow").toggle( period == 30 || period == 365 );
            $("#monthrow").toggle( period == 365 );
        },

        validation: function() {
            let startdate = $("#startdate").val();
            let enddate = $("#enddate").val();
            if (enddate != "" && enddate < startdate) {
                tableform.dialog_error(_("End date cannot be before start date."));
                return false;
            }
            let fromaccount = $("#fromaccount").val();
            let toaccount = $("#toaccount").val();
            if (fromaccount == toaccount) {
                tableform.dialog_error(_("From account and to account must be different."));
                return false;
            }
            let amount = $("#amount").currency("value");
            if (amount <= 0) {
                tableform.dialog_error(_("Invalid amount."));
                return false;
            }
            return true;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Regular debits"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },
        
        bind: function() {
            $("#period").change(regular_debits.period_changed);
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        sync: function() {
            if (controller.filter == "") {
                $("#filter").val("active");
            } else {
                $("#filter").val(controller.filter);
            }
            regular_debits.period_changed();
        },

        destroy: function() {},

        name: "regular_debits",
        animation: "book",
        title: function() { return _("Regular debits"); },
        routes: {
            "regular_debits": function() { common.module_loadandstart("regular_debits", "regular_debits?filter=" + controller.filter); }
        }

    };
    
    common.module_register(regular_debits);

});
