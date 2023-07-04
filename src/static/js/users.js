/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const users = {

        model: function() {
            // Add extra location filter options
            controller.internallocations.push(
                { ID: -1, LOCATIONNAME: _("Adopted Animals")},
                { ID: -21, LOCATIONNAME: _("Died (On Shelter)")},
                { ID: -22, LOCATIONNAME: _("Died (DOA)")},
                { ID: -23, LOCATIONNAME: _("Died (Euthanized)")},
                { ID: -24, LOCATIONNAME: _("Died (Off Shelter)")},
                { ID: -4, LOCATIONNAME: _("Escaped Animals")},
                { ID: -2, LOCATIONNAME: _("Fostered Animals")},
                { ID: -5, LOCATIONNAME: _("Reclaimed Animals")},
                { ID: -12, LOCATIONNAME: _("My Fosters")},
                { ID: -9, LOCATIONNAME: _("Non-shelter Animals")},
                { ID: -8, LOCATIONNAME: _("Retailer Animals")},
                { ID: -6, LOCATIONNAME: _("Stolen Animals")},
                { ID: -3, LOCATIONNAME: _("Transferred Animals")},
                { ID: -7, LOCATIONNAME: _("TNR/Released Animals")}
            );

            const dialog = {
                add_title: _("Add user"),
                edit_title: _("Edit user"),
                helper_text: _("Users need a username, password and at least one role or the superuser flag setting."),
                close_on_ok: false,
                hide_read_only: true,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "USERNAME", post_field: "username", label: _("Username"), type: "text", validation: "notblank", readonly: true },
                    { json_field: "PASSWORD", post_field: "password", label: _("Password"), type: "text", validation: "notblank", readonly: true },
                    { json_field: "REALNAME", post_field: "realname", label: _("Real name"), type: "text" },
                    { json_field: "", post_field: "emailcred", label: _("Email these credentials to the user"), type: "check", readonly: true },
                    { json_field: "EMAILADDRESS", post_field: "email", label: _("Email"), type: "text" },
                    { json_field: "DISABLELOGIN", post_field: "disablelogin", label: _("Can Login"),  type: "select", defaultval: "0", 
                        callout: _("Set wether or not this user account can log in to the user interface.") + " " +
                                 _("User accounts that will only ever call the Service API should set this to No."),
                        options: '<option value="0">' + _("Yes") + '</option>' +
                        '<option value="1">' + _("No") + '</option>'},
                    { json_field: "SUPERUSER", post_field: "superuser", label: _("Type"),  type: "select", defaultval: "0", 
                        callout: _("'Super' users automatically have all permissions granted, where 'Normal' users need one or more roles to grant them permissions"),
                        options: '<option value="0">' + _("Normal user") + '</option>' +
                        '<option value="1">' + _("Super user") + '</option>'},
                    { json_field: "ROLEIDS", post_field: "roles", label: _("Roles"), type: "selectmulti", 
                        options: { rows: controller.roles, valuefield: "ID", displayfield: "ROLENAME" }},
                    { json_field: "SITEID", post_field: "site", label: _("Site"), type: "select", 
                        options: '<option value="0">' + _("(all)") + '</option>' +  
                            html.list_to_options(controller.sites, "ID", "SITENAME") },
                    { json_field: "OWNERID", post_field: "person", label: _("Staff record"), type: "person", personfilter: "staff",
                        callout: _("Link this user account to a staff person record.") + " " +
                                 _("Once linked, a user account cannot access and edit its linked person record.")
                    },
                    { json_field: "LOCATIONFILTER", post_field: "locationfilter", label: _("Location Filter"), type: "selectmulti", 
                        options: { rows: controller.internallocations, valuefield: "ID", displayfield: "LOCATIONNAME" },
                        hideif: function() { return !config.bool("LocationFiltersEnabled"); },
                        callout: _("Setting a location filter will prevent this user seeing animals who are not in these locations on shelterview, find animal and search.")
                    },
                    { json_field: "IPRESTRICTION", post_field: "iprestriction", label: _("IP Restriction"), type: "text", classes: "asm-ipbox",
                        callout: _("IP restriction is a space-separated list of IPv4 addresses or IPv6 prefixes that this user is ONLY permitted to login from.") + " " + 
                            _("If left blank, the user can login from any IP address.") + 
                            "\nex: 192.168.0.0/24 172.16.38.21 2001:db8:abcd:0012"
                    }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                showfilter: false, 
                edit: async function(row) {
                    if (row.USERNAME == asm.useraccount) { return false; }
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    users.set_extra_fields(row);
                    await tableform.fields_post(dialog.fields, "mode=update&userid=" + row.ID, "systemusers");
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                complete: function(row) {
                    if (row.DISABLELOGIN && row.DISABLELOGIN == 1) { return true; }
                    return false;
                },
                columns: [
                    { field: "USERNAME", display: _("Username"), initialsort: true, 
                        formatter: function(row) {
                            if (row.USERNAME == asm.useraccount) {
                                return row.USERNAME;
                            }
                            return "<span style=\"white-space: nowrap\">" +
                                "<input type=\"checkbox\" data-id=\"" + row.ID + "\" title=\"" + html.title(_("Select")) + "\" />" +
                                "<a href=\"#\" class=\"link-edit\" data-id=\"" + row.ID + "\">" + row.USERNAME + "</a>" +
                                "</span>";
                        }},
                    { field: "REALNAME", display: _("Real name"), formatter: function(row) {
                            if (row.USERNAME == asm.useraccount) { 
                                return _("(master user, not editable)");
                            }
                            if (row.REALNAME) {                        
                                return row.REALNAME;
                            }
                            return "";
                        }},
                    { field: "EMAILADDRESS", display: _("Email") },
                    { field: "ROLES", display: _("Roles"), formatter: function(row) {
                            return common.nulltostr(row.ROLES).replace(/[|]+/g, ", ");
                        }},
                    { field: "SUPERUSER", display: _("Type"), formatter: function(row) {
                        let tags = [];
                        if (row.DISABLELOGIN == 1) { tags.push(_("Cannot Login")); }
                        if (row.SUPERUSER == 1) { tags.push(_("Superuser")); }
                        if (row.ENABLETOTP == 1) { tags.push(_("2FA Enabled")); }
                        if (row.LOCALEOVERRIDE && row.LOCALEOVERRIDE != config.str("Locale")) { tags.push(row.LOCALEOVERRIDE); }
                        return tags.join(", ");
                        }},
                    { field: "SITEID", display: _("Site"), 
                        formatter: function(row) {
                            return common.nulltostr(common.get_field(controller.sites, row.SITEID, "SITENAME"));
                        }, hideif: function(row) { 
                            return !config.bool("MultiSiteEnabled"); 
                        }},
                    { field: "LOCATIONFILTER", display: _("Location Filter"), 
                        hideif: function() { return !config.bool("LocationFiltersEnabled"); },
                        formatter: function(row) {
                            let of = [], lf = common.nulltostr(row.LOCATIONFILTER);
                            if (!row.LOCATIONFILTER) { return ""; }
                            $.each(lf.split(/[\|,]+/), function(i, f) {
                                $.each(controller.internallocations, function(x, v) {
                                    if (parseInt(f, 10) == v.ID) {
                                        of.push(v.LOCATIONNAME);
                                        return false;
                                    }
                                });
                            });
                            return of.join(", ");
                        }
                    },
                    { field: "IPRESTRICTION", display: _("IP Restriction") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New User"), icon: "new", enabled: "always", 
                    click: async function() { 
                        await tableform.dialog_show_add(dialog);
                        try {
                            let response = await tableform.fields_post(dialog.fields, "mode=create", "systemusers");
                            let row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
                            users.set_extra_fields(row);
                            controller.rows.push(row);
                            tableform.table_update(table);
                            tableform.dialog_close();
                        }
                        catch(err) {
                            log.error(err, err);
                            tableform.dialog_enable_buttons();   
                        }
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                    click: async function() { 
                        await tableform.delete_dialog(null, _("This will permanently remove the selected user accounts. Are you sure?"));
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("systemusers", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "reset", text: _("Reset Password"), icon: "auth", enabled: "multi", 
                    click: function() { 
                        $("#dialog-reset").dialog("open");
                    } 
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render_resetdialog: function() {
            return [
                '<div id="dialog-reset" style="display: none" title="' + html.title(_("Reset Password")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="newpassword">' + _("New Password") + '</label></td>',
                '<td><input id="newpassword" data="newpassword" type="password" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="confirmpassword">' + _("Confirm Password") + '</label></td>',
                '<td><input id="confirmpassword" data="confirmpassword" type="password" class="asm-textbox" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        bind_resetdialog: function() {
            let resetbuttons = { }, table = users.table;
            resetbuttons[_("Change Password")] = async function() {
                validate.reset("dialog-reset");
                if (!validate.notblank([ "newpassword" ])) { return; }
                if (!validate.notblank([ "confirmpassword" ])) { return; }
                if (common.trim($("#newpassword").val()) != common.trim($("#confirmpassword").val())) {
                    header.show_error(_("New password and confirmation password don't match."));
                    return;
                }
                $("#dialog-reset").disable_dialog_buttons();
                let ids = tableform.table_ids(table);
                try {
                    await common.ajax_post("systemusers", "mode=reset&ids=" + ids + "&password=" + encodeURIComponent($("#newpassword").val()));
                    let h = "";
                    $("#tableform input:checked").each(function() {
                        let username = $(this).next().text();
                        $(this).prop("checked", false);
                        h += _("Password for '{0}' has been reset.").replace("{0}", username) + "<br />";
                    });
                    header.show_info(h);
                }
                finally {
                    $("#dialog-reset").dialog("close");
                    $("#dialog-reset").enable_dialog_buttons();
                }
            };
            resetbuttons[_("Cancel")] = function() {
                $("#dialog-reset").dialog("close");
            };

            $("#dialog-reset").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: resetbuttons
            });
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += this.render_resetdialog();
            s += html.content_header(_("User Accounts"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            this.bind_resetdialog();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            $("#site").closest("tr").toggle( config.bool("MultiSiteEnabled") );
            validate.indicator([ "newpassword", "confirmpassword" ]);
        },

        set_extra_fields: function(row) {
            // Build list of ROLES from ROLEIDS
            let roles = [];
            let roleids = row.ROLEIDS;
            if ($.isArray(roleids)) { roleids = roleids.join(","); }
            $.each(roleids.split(/[|,]+/), function(i, v) {
                roles.push(common.get_field(controller.roles, v, "ROLENAME"));
            });
            row.ROLES = roles.join("|");
        },

        destroy: function() {
            common.widget_destroy("#dialog-reset");
            common.widget_destroy("#person");
            tableform.dialog_destroy();
        },

        name: "users",
        animation: "options",
        title: function() { return _("Edit system users"); },
        routes: {
            "systemusers": function() { common.module_loadandstart("users", "systemusers"); }
        }

    };
    
    common.module_register(users);

});
