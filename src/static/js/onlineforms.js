/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const onlineforms = {

        email_submitter_options: [
            { ID: 0, NAME: _("Do not send email") },
            { ID: 1, NAME: _("Send and include a copy of the form submission") },
            { ID: 2, NAME: _("Send confirmation message only") }
        ],

        auto_process_options: [
            { ID: 0, NAME: _("Do not auto process") },
            { ID: 1, NAME: _("Attach animal via animalname field") },
            { ID: 9, NAME: _("Attach animal then create person") },
            { ID: 2, NAME: _("Create animal") },
            { ID: 3, NAME: _("Create person") },
            { ID: 4, NAME: _("Create lost animal") },
            { ID: 5, NAME: _("Create found animal") },
            { ID: 6, NAME: _("Create incident") },
            { ID: 7, NAME: _("Create transport") },
            { ID: 8, NAME: _("Create waiting list") }
        ],

        model: function() {
            const dialog = {
                add_title: _("Add online form"),
                edit_title: _("Edit online form"),
                edit_perm: 'eof',
                close_on_ok: false,
                columns: 1,
                width: 850,
                fields: [
                    { json_field: "NAME", post_field: "name", label: _("Name"), type: "text", classes: "asm-doubletextbox", validation: "notblank" },
                    { json_field: "REDIRECTURLAFTERPOST", post_field: "redirect", label: _("Redirect to URL after POST"), 
                        type: "text", classes: "asm-doubletextbox", 
                        tooltip: _("After the user presses submit and ASM has accepted the form, redirect the user to this URL"),
                        callout: _("After the user presses submit and ASM has accepted the form, redirect the user to this URL") },
                    { json_field: "SETOWNERFLAGS", post_field: "flags", label: _("Person Flags"), type: "selectmulti" },
                    { json_field: "AUTOPROCESS", post_field: "autoprocess", label: _("Auto Process"), 
                        type: "select", classes: "asm-doubleselectbox",
                        callout: _("Process submissions of this form automatically and bypass the incoming forms queue"),
                        options: { displayfield: "NAME", valuefield: "ID", rows: onlineforms.auto_process_options } },
                    { json_field: "EMAILADDRESS", post_field: "email", label: _("Email submissions to"), 
                        type: "textarea", rows: "2", 
                        validation: "validemail", 
                        tooltip: _("Email incoming form submissions to this comma separated list of email addresses"), 
                        callout: _("Email incoming form submissions to this comma separated list of email addresses") }, 
                    { json_field: "EMAILCOORDINATOR", post_field: "emailcoordinator", 
                        label: _("Email adoption coordinator"), 
                        type: "check",
                        callout: _("If this form has an animalname field, email this submission to the adoption coordinator for the selected animal")
                    },
                    { json_field: "EMAILSUBMITTER", post_field: "emailsubmitter", label: _("Send confirmation email to form submitter"), 
                        type: "select", classes: "asm-doubleselectbox",
                        callout: _("If this form has a populated emailaddress field during submission, send a confirmation email to it"),
                        options: { displayfield: "NAME", valuefield: "ID", rows: onlineforms.email_submitter_options } },
                    { json_field: "EMAILMESSAGE", post_field: "emailmessage", label: _("Confirmation message"), type: "richtextarea", 
                        margintop: "0px", height: "100px", width: "600px",
                        tooltip: _("The confirmation email message to send to the form submitter."),
                        callout: _("The confirmation email message to send to the form submitter.") }, 
                    { json_field: "DESCRIPTION", post_field: "description", label: _("Description"), type: "htmleditor", height: "100px", width: "600px" },
                    { json_field: "HEADER", post_field: "header", label: _("Header"), type: "htmleditor", height: "100px", width: "600px" },
                    { json_field: "FOOTER", post_field: "footer", label: _("Footer"), type: "htmleditor", height: "100px", width: "600px" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    try {
                        await tableform.dialog_show_edit(dialog, row);
                        onlineforms.check_redirect_url();
                        tableform.fields_update_row(dialog.fields, row);
                        await tableform.fields_post(dialog.fields, "mode=update&formid=" + row.ID, "onlineforms");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err);
                        tableform.dialog_enable_buttons();
                    }
                },
                button_click: function() {
                    if ($(this).attr("data-url")) {
                        common.copy_to_clipboard($(this).attr("data-url"));
                        header.show_info(_("Successfully copied to the clipboard."));
                        return false;
                    }
                    else if ($(this).attr("data-link")) {
                        common.route($(this).attr("data-link"), true);
                    }
                },
                columns: [
                    { field: "NAME", display: _("Name"), initialsort: true, formatter: function(row) {
                        return "<span style=\"white-space: nowrap\">" + 
                            "<input type=\"checkbox\" data-id=\"" + row.ID + "\" title=\"" + html.title(_("Select")) + "\" />" +
                            "<a href=\"onlineform?formid=" + row.ID + "\">" + row.NAME + "</a> " +
                            "<button class=\"link-edit\" data-icon=\"pencil\" data-id=\"" + row.ID + "\">" + _("Edit online form") + "</button>" +
                            "</span>";
                    }},
                    { field: "", display: _("Form URL"), formatter: function(row) {
                            let u = asm.serviceurl + "?";
                            if (asm.useraccountalias) { u += "account=" + asm.useraccountalias + "&"; }
                            u += "method=online_form_html&formid=" + row.ID;
                            return '<span style="white-space: nowrap">' + 
                                '<a target="_blank" href="' + u + '">' + _("View Form") + '</a>' +
                                ' <button data-icon="clipboard" data-text="false" data-url="' + u + '">' + 
                                _("Copy form URL to the clipboard") + '</button>' +
                                '<button data-icon="wrench" data-text="false" data-link="onlineform_view?formid=' + row.ID +
                                '">' + _("View the form in development mode without caching") + '</button>' +
                                '</span>';
                        }},
                    { field: "REDIRECTURLAFTERPOST", display: _("Redirect to URL after POST") },
                    { field: "EMAILADDRESS", display: _("Email submissions to"), formatter: function(row) {
                        return common.replace_all(row.EMAILADDRESS, ",", "<br/>");
                    }},
                    { field: "SETOWNERFLAGS", display: _("Person Flags"), formatter: function(row) { return row.SETOWNERFLAGS.split("|").join(", "); }},
                    { field: "NUMBEROFFIELDS", display: _("Number of fields") },
                    { field: "DESCRIPTION", display: _("Description"), formatter: function(row) { return html.truncate(row.DESCRIPTION); } }
                ]
            };

            const buttons = [
                { id: "new", text: _("New online form"), icon: "new", enabled: "always", perm: "aof", 
                    click: async function() { 
                        try {
                            await tableform.dialog_show_add(dialog);
                            onlineforms.check_redirect_url();
                            let response = await tableform.fields_post(dialog.fields, "mode=create", "onlineforms");
                            let row = {};
                            row.ID = response;
                            tableform.fields_update_row(dialog.fields, row);
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
                { id: "clone", text: _("Clone"), icon: "copy", enabled: "multi", perm: "aof",
                    click: async function() { 
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("onlineforms", "mode=clone&ids=" + ids);
                        common.route_reload();
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dof", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("onlineforms", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "headfoot", text: _("Edit Header/Footer"), icon: "forms", enabled: "always", 
                    tooltip: _("Edit online form HTML header/footer"), perm: "eof", 
                    click: function() {
                        $("#dialog-headfoot").dialog("open");
                    }
                },
                { id: "import", text: _("Import"), icon: "database", enabled: "always", 
                    tooltip: _("Import from file"), perm: "aof", 
                    click: async function() {
                        await tableform.show_okcancel_dialog("#dialog-import", _("Import"), { notblank: ["filechooser"] });
                        $("#importform").submit();
                    }
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        load_person_flags: function() {
            html.person_flag_options(null, controller.flags, $("#flags"));
        },

        render_headfoot: function() {
            return [
                '<div id="dialog-headfoot" style="display: none" title="' + html.title(_("Edit Header/Footer")) + '">',
                '<div class="ui-state-highlight ui-corner-all">',
                    '<p>',
                        '<span class="ui-icon ui-icon-info"></span>',
                        _("These are the HTML headers and footers used when displaying online forms."),
                    '</p>',
                '</div>',
                '<table width="100%">',
                '<tr>',
                '<td valign="top">',
                '<label for="rhead">' + _("Header") + '</label><br />',
                '<textarea id="rhead" data="header" class="asm-htmleditor headfoot" data-height="250px" data-width="750px">',
                controller.header,
                '</textarea>',
                '<label for="rfoot">' + _("Footer") + '</label><br />',
                '<textarea id="rfoot" data="footer" class="asm-htmleditor headfoot" data-height="250px" data-width="750px">',
                controller.footer,
                '</textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_import: function() {
            return [
                '<div id="dialog-import" style="display: none" title="' + html.title(_("Import from file")) + '">',
                '<form id="importform" action="onlineforms" method="post" enctype="multipart/form-data">',
                '<input name="mode" value="import" type="hidden" />',
                '<input id="filechooser" name="filechooser" type="file" />',
                '</form>',
                '</div>'
            ].join("\n");
        },

        bind_headfoot: function() {
            let headfootbuttons = {};
            headfootbuttons[_("Save")] = async function() {
                try {
                    let formdata = "mode=headfoot&" + $(".headfoot").toPOST();
                    await common.ajax_post("onlineforms", formdata);
                    header.show_info(_("Updated."));
                }
                finally {
                    $("#dialog-headfoot").dialog("close");
                }
            };
            headfootbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
            $("#dialog-headfoot").dialog({
                autoOpen: false,
                resizable: true,
                height: "auto",
                width: 800,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: headfootbuttons,
                open: function() {
                    $("#rhead, #rfoot").htmleditor("refresh");
                }
            });
        },

        check_redirect_url: function() {
            let u = $("#redirect").val();
            if (u && u.indexOf("http") != 0) { $("#redirect").val( "https://" + u ); }
        },

        render: function() {
            let s = "";
            this.model();
            s += this.render_headfoot();
            s += this.render_import();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Online Forms"));
            s += html.info(_("Online forms can be linked to from your website and used to take information from visitors for applications, etc."));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            this.bind_headfoot();
            this.load_person_flags();
        },

        destroy: function() {
            common.widget_destroy("#dialog-headfoot");
            common.widget_destroy("#dialog-import");
            common.widget_destroy("#rhead");
            common.widget_destroy("#rfoot");
            tableform.dialog_destroy();
        },

        name: "onlineforms",
        animation: "formtab",
        title: function() { return _("Online Forms"); },
        routes: { 
            "onlineforms": function() { common.module_loadandstart("onlineforms", "onlineforms"); }
        }

    };
    
    common.module_register(onlineforms);

});
