/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const document_templates = {

        doctypes: [
            { VALUE: "everywhere", DISPLAY: _("(everywhere)") },
            { VALUE: "nowhere", DISPLAY: _("(nowhere)") },
            { VALUE: "animal", DISPLAY: _("Animals") },
            { VALUE: "clinic", DISPLAY: _("Clinic") },
            { VALUE: "email", DISPLAY: _("Emails") },
            { VALUE: "foundanimal", DISPLAY: _("Found Animals") },
            { VALUE: "incident", DISPLAY: _("Incidents") },
            { VALUE: "licence", DISPLAY: _("Licenses") },
            { VALUE: "lostanimal", DISPLAY: _("Lost Animals") },
            { VALUE: "mailmerge", DISPLAY: _("Mail") },
            { VALUE: "movement", DISPLAY: _("Movements") },
            { VALUE: "payment", DISPLAY: _("Payments") },
            { VALUE: "person", DISPLAY: _("People") },
            { VALUE: "voucher", DISPLAY: _("Vouchers") },
            { VALUE: "waitinglist", DISPLAY: _("Waiting List") }
        ],

        model: function() {
            const dialog = {
                add_title: _("New template"),
                helper_text: _("Template names can include a path portion with /, eg: Vets/Rabies Certificate"),
                close_on_ok: true,
                columns: 1,
                width: 550,
                fields: [
                    { post_field: "template", label: _("Template Name"), validation: "notblank", type: "text" },
                    { post_field: "show", label: _("Show"), type: "selectmulti", 
                        options: { rows: document_templates.doctypes, valuefield: "VALUE", displayfield: "DISPLAY" }}
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    common.route("document_template_edit?dtid=" + row.ID);
                },
                columns: [
                    { field: "NAME", display: _("Template") },
                    { field: "SHOW", display: _("Show"), formatter: function(row) {
                        let l = [];
                        $.each(String(row.SHOW).split(","), function(i, v) {
                            $.each(document_templates.doctypes, function (id, vd) {
                                if (vd.VALUE == v) { l.push(vd.DISPLAY); return false; }
                            });
                        });
                        return l.join(", ");
                    }},
                    { field: "PATH", display: _("Path"), initialsort: true }
                ]
            };

            const buttons = [
                { id: "new", text: _("New"), icon: "document", tooltip: _("Create a new template"), enabled: "always", 
                    click: async function() { 
                        $("#show").closest("tr").show();
                        await tableform.dialog_show_add(dialog);
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "document_templates");
                        common.route("document_template_edit?dtid=" + response);
                    } 
                },
                { id: "newodt", text: _("Upload ODT"), icon: "media-add", tooltip: _("Upload a new OpenOffice template"), enabled: "always", 
                    hideif: function() { 
                        return !config.bool("AllowODTDocumentTemplates");
                    },
                    click: function() { 
                        $("#dialog-newodt").dialog("open");
                    } 
                },
                { id: "clone", text: _("Clone"), icon: "copy", tooltip: _("Create a new template by copying the selected template"), enabled: "one", 
                    click: async function() { 
                        let ids = tableform.table_ids(table);
                        $("#show").closest("tr").hide();
                        await tableform.dialog_show_add(dialog);
                        let response = await tableform.fields_post(dialog.fields, "mode=clone&ids=" + ids , "document_templates");
                        common.route("document_template_edit?dtid=" + response);
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("document_templates", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "rename", text: _("Rename"), icon: "link", enabled: "one", 
                    click: function() { 
                        $("#newname").val(tableform.table_selected_row(table).NAME);
                        $("#dialog-rename").dialog("open");
                    } 
                },
                { id: "show", text: _("Show"), icon: "document", enabled: "multi", 
                    click: function() { 
                        $("#newshow").val(tableform.table_selected_row(table).SHOW);
                        $("#newshow").change();
                        $("#dialog-show").dialog("open");
                    } 
                },

                { id: "images", text: _("Extra Images"), icon: "image", enabled: "always", tooltip: _("Add extra images for use in reports and documents"),
                    click: function() {
                       common.route("report_images");
                    }
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render_rename_dialog: function() {
            return [
                '<div id="dialog-rename" style="display: none" title="' + html.title(_("Rename")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="newname">' + _("New name") + '</label></td>',
                '<td><input id="newname" data="newname" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        bind_rename_dialog: function() {
            let renamebuttons = { };
            renamebuttons[_("Rename")] = async function() {
                validate.reset();
                if (!validate.notblank([ "newname" ])) { return; }
                $("#dialog-rename").disable_dialog_buttons();
                let dtid = tableform.table_ids(document_templates.table).split(",")[0];
                let newname = $("#newname").val();
                await common.ajax_post("document_templates", "mode=rename&newname=" + encodeURIComponent(newname) + "&dtid=" + dtid);
                $("#dialog-rename").enable_dialog_buttons();
                $("#dialog-rename").dialog("close");
                tableform.table_selected_row(document_templates.table).NAME = newname;
                tableform.table_update(document_templates.table);
            };
            renamebuttons[_("Cancel")] = function() {
                $("#dialog-rename").dialog("close");
            };
            $("#dialog-rename").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: renamebuttons
            });
        },

        render_newodt_dialog: function() {
            return [
                '<div id="dialog-newodt" style="display: none" title="' + html.title(_("Upload a new OpenOffice template")) + '">',
                '<form id="form-newodt" action="document_templates" method="post" enctype="multipart/form-data">',
                '<input type="hidden" name="mode" value="createodt" />',
                '<table width="100%">',
                '<tr>',
                '<td><label for="filechooser">' + _("Document file") + '</label></td>',
                '<td><input id="filechooser" name="filechooser" type="file" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="odtpath">' + _("Path") + '</label></td>',
                '<td><input id="odtpath" name="path" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="odtshow">' + _("Show") + '</label></td>',
                '<td><select id="odtshow" data="odtshow" multiple="multiple" class="asm-bsmselect">',
                html.list_to_options(document_templates.doctypes, "VALUE", "DISPLAY"),
                '</select></td>',
                '</tr>',
                '</table>',
                '</form>',
                '</div>'
            ].join("\n");
        },

        bind_newodt_dialog: function() {
            let odtbuttons = { };
            odtbuttons[_("Upload")] = function() {
                validate.reset();
                if (!validate.notblank([ "filechooser" ])) { return; }
                $("#dialog-newodt").disable_dialog_buttons();
                $("#form-newodt").submit();
            };
            odtbuttons[_("Cancel")] = function() {
                $("#dialog-newodt").dialog("close");
            };
            $("#dialog-newodt").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: odtbuttons
            });
        },

        render_show_dialog: function() {
            return [
                '<div id="dialog-show" style="display: none" title="' + html.title(_("Show")) + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="newshow">' + _("Show") + '</label></td>',
                '<td><select id="newshow" data="newshow" multiple="multiple" class="asm-bsmselect">',
                html.list_to_options(document_templates.doctypes, "VALUE", "DISPLAY"),
                '</select></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        bind_show_dialog: function() {
            let showbuttons = { };
            showbuttons[_("Change")] = async function() {
                $("#dialog-show").disable_dialog_buttons();
                let dtid = tableform.table_ids(document_templates.table);
                let newshow = $("#newshow").val();
                await common.ajax_post("document_templates", "mode=show&newshow=" + newshow + "&ids=" + dtid);
                $("#dialog-show").enable_dialog_buttons();
                $("#dialog-show").dialog("close");
                $.each(tableform.table_selected_rows(document_templates.table), function(i, v) {
                    v.SHOW = newshow;
                });
                tableform.table_update(document_templates.table);
            };
            showbuttons[_("Cancel")] = function() {
                $("#dialog-show").dialog("close");
            };
            $("#dialog-show").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: showbuttons
            });
        },



        render: function() {
            let s = "";
            this.model();
            s += this.render_rename_dialog();
            s += this.render_show_dialog();
            s += this.render_newodt_dialog();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Document Templates"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            this.bind_rename_dialog();
            this.bind_show_dialog();
            this.bind_newodt_dialog();
        },

        destroy: function() {
            common.widget_destroy("#dialog-newodt");
            common.widget_destroy("#dialog-rename");
            common.widget_destroy("#dialog-show");
            tableform.dialog_destroy();
        },

        name: "document_templates",
        animation: "options",
        title: function() { return _("Document Templates"); },
        routes: {
            "document_templates": function() {
                common.module_loadandstart("document_templates", "document_templates");
            }
        }


    };

    common.module_register(document_templates);

});
