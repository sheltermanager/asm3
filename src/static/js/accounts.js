/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */
$(function() {

    var dialog = {
        add_title: _("Add account"),
        edit_title: _("Edit account"),
        helper_text: _("Accounts need a code.") + "<br /><br />" + 
            _("If you assign view or edit roles, only users within those roles will be able to view and edit this account."),
        close_on_ok: true,
        columns: 1,
        width: 550,
        fields: [
            { json_field: "CODE", post_field: "code", label: _("Code"), type: "text", validation: "notblank" },
            { json_field: "ACCOUNTTYPE", post_field: "type", label: _("Type"), type: "select", 
                options: { displayfield: "ACCOUNTTYPE", valuefield: "ID", rows: controller.accounttypes }},
            { json_field: "ARCHIVED", post_field: "archived", label: _("Active"), type: "select",
                options: '<option value="0">' + _("Yes") + '</option><option value="1">' + _("No") + '</option>' },
            { json_field: "DONATIONTYPEID", post_field: "donationtype", label: _("Payment Type"), type: "select", 
                tooltip: _("This income account is the source for payments received of this type"),
                options: { displayfield: "DONATIONNAME", valuefield: "ID", rows: controller.donationtypes }},
            { json_field: "VIEWROLEIDS", post_field: "viewroles", label: _("View Roles"), type: "selectmulti", 
                options: { rows: controller.roles, valuefield: "ID", displayfield: "ROLENAME" }},
            { json_field: "EDITROLEIDS", post_field: "editroles", label: _("Edit Roles"), type: "selectmulti", 
                options: { rows: controller.roles, valuefield: "ID", displayfield: "ROLENAME" }},
            { json_field: "DESCRIPTION", post_field: "description", label: _("Comments"), type: "textarea" }
        ]
    };

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        hideif: function(row) {

            // Superusers see everything
            if (asm.superuser) { return false; }

            // If the row has no view roles, we're good
            if (!row.VIEWROLEIDS) { return false; }

            // Is the user in one of the view roles?
            if (common.array_overlap(row.VIEWROLEIDS.split("|"), asm.roleids.split("|"))) { return false; }

            return true;
        },
        complete: function(row) {
            return row.ARCHIVED == 1 || row.ARCHIVED == "1";
        },
        edit: function(row) {
            // Only show donation type links for income accounts
            if (row.ACCOUNTTYPE != 5) { 
                $("#donationtype").closest("tr").hide(); 
            }
            else {
                $("#donationtype").closest("tr").show(); 
            }
            tableform.dialog_show_edit(dialog, row, function() {
                tableform.fields_update_row(dialog.fields, row);
                row.ACCOUNTTYPENAME = common.get_field(controller.accounttypes, row.ACCOUNTTYPE, "ACCOUNTTYPE");
                tableform.fields_post(dialog.fields, "mode=update&accountid=" + row.ID, "accounts", function(response) {
                    tableform.table_update(table);
                });
            });
        },
        columns: [
            { field: "CODE", display: _("Code"), formatter: function(row) {
                    var editlink = "<a href=\"#\" class=\"link-edit\" data-id=\"" + row.ID + "\">" + 
                        html.icon("accounts", _("Edit account")) + '</a>';
                    // If the user is not a superuser or in a role that has permission to
                    // edit the account, remove the edit link
                    if (!asm.superuser && !common.array_overlap(row.EDITROLEIDS.split("|"), asm.roleids.split("|"))) {
                        editlink = "";
                    }
                    return '<span style="white-space: nowrap">' +
                        '<input type="checkbox" data-id="' + row.ID + '" title="' + html.title(_("Select")) + '" />' +
                        '<a href="accounts_trx?accountid=' + row.ID + '">' + row.CODE + '</a> ' + 
                        editlink + '</span>';
                }},
            { field: "ACCOUNTTYPENAME", initialsort: true, display: _("Type") },
            { field: "DESCRIPTION", display: _("Description") },
            { field: "RECONCILED", display: _("Reconciled"), formatter: tableform.format_currency },
            { field: "BALANCE", display: _("Balance"), formatter: tableform.format_currency }

        ]
    };

    var buttons = [
         { id: "new", text: _("New Account"), icon: "new", enabled: "always", perm: "aac",
             click: function() { 
                 $("#accounttype").select("value", "0");
                 $("#donationtype").select("value", "0");
                 $("#donationtype").closest("tr").hide(); 
                 tableform.dialog_show_add(dialog, function() {
                     tableform.fields_post(dialog.fields, "mode=create", "accounts", function(response) {
                         var row = {};
                         row.ID = response;
                         tableform.fields_update_row(dialog.fields, row);
                         row.ACCOUNTTYPENAME = common.get_field(controller.accounttypes, row.ACCOUNTTYPE, "ACCOUNTTYPE");
                         controller.rows.push(row);
                         tableform.table_update(table);
                     });
                 });
             } 
         },
         { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dac",
             click: function() { 
                 tableform.delete_dialog(function() {
                     tableform.buttons_default_state(buttons);
                     var ids = tableform.table_ids(table);
                     common.ajax_post("accounts", "mode=delete&ids=" + ids , function() {
                         tableform.table_remove_selected_from_json(table, controller.rows);
                         tableform.table_update(table);
                     });
                 },
                 _("This will permanently remove this account and ALL TRANSACTIONS HELD AGAINST IT. This action is irreversible, are you sure you want to do this?")
                 );
             } 
         },
         { id: "offset", type: "dropdownfilter", 
             options: [ "active|" + _("Only active accounts"), "all|" + _("All accounts") ],
             click: function(selval) {
                window.location = "accounts?offset=" + selval;
             }
         }

    ];

    var accounts = {

        render: function() {
            var s = "";
            s += html.content_header(_("Accounts"));
            s += tableform.dialog_render(dialog);
            s += tableform.buttons_render(buttons);
            s += tableform.table_render(table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(dialog);
            tableform.buttons_bind(buttons);
            tableform.table_bind(table, buttons);
            // Add an unmapped donation type selection
            $("#donationtype").prepend('<option value="0"> </option>');
        },

        sync: function() {
            // If an offset is given in the querystring, update the select
            if (common.querystring_param("offset")) {
                $("#offset").select("value", common.querystring_param("offset"));
            }
        }

    };

    common.module(accounts, "accounts", "formtab");

});
