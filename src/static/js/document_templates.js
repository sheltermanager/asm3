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
            { VALUE: "medical", DISPLAY: _("Medical") },
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
                complete: function(row) {
                   return !row.SHOWAT || row.SHOWAT == "" || row.SHOWAT == "nowhere";
                },
                columns: [
                    { field: "NAME", display: _("Template") },
                    { field: "SHOWAT", display: _("Show"), formatter: function(row) {
                        let l = [];
                        $.each(String(row.SHOWAT).split(","), function(i, v) {
                            $.each(document_templates.doctypes, function (id, vd) {
                                if (vd.VALUE == v) { l.push(vd.DISPLAY); return false; }
                            });
                        });
                        return l.join(", ");
                    }},
                    { field: "SIZE", display: _("Size"), formatter: function(row) {
                        if (!row.SIZE) { return ""; }
                        return Math.round(row.SIZE / 1024.0) + " Kb";
                    }},
                    { field: "PATH", display: _("Path"), initialsort: true }
                ]
            };

            const buttons = [
                { id: "new", text: _("New"), icon: "document", tooltip: _("Create a new template"), enabled: "always", 
                    click: async function() { 
                        $("#showrow").show();
                        await tableform.dialog_show_add(dialog);
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "document_templates");
                        common.route("document_template_edit?dtid=" + response);
                    } 
                },
                { id: "upload", text: _("Upload"), icon: "media-add", tooltip: _("Upload a new document template"), enabled: "always", 
                    click: async function() { 
                        await tableform.show_okcancel_dialog("#dialog-upload", _("Upload"), { width: 550, notblank: [ "filechooser" ] });
                        let filename = $("#filechooser").val();
                        if (filename.endsWith(".odt") && !config.bool("AllowODTDocumentTemplates")) {
                            header.show_error(_(".odt templates are not permitted by the system options."));
                            return;
                        }
                        if (!filename.endsWith(".odt") && !filename.endsWith(".html")) {
                            header.show_error(_("File types accepted: {0}").replace("{0}", ".odt, .html"));
                            return;
                        }
                        $("#form-upload").submit();
                    } 
                },
                { id: "clone", text: _("Clone"), icon: "copy", tooltip: _("Create a new template by copying the selected template"), enabled: "one", 
                    click: async function() { 
                        let ids = tableform.table_ids(table);
                        $("#showrow").hide();
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
                    click: async function() { 
                        $("#newname").val(tableform.table_selected_row(table).NAME);
                        await tableform.show_okcancel_dialog("#dialog-rename", _("Rename"), { width: 550, notblank: [ "newname" ] });
                        let dtid = tableform.table_ids(document_templates.table).split(",")[0];
                        let newname = $("#newname").val();
                        await common.ajax_post("document_templates", "mode=rename&newname=" + encodeURIComponent(newname) + "&dtid=" + dtid);
                        tableform.table_selected_row(document_templates.table).NAME = newname;
                        tableform.table_update(table);
                        tableform.buttons_default_state(buttons);
                    } 
                },
                { id: "show", text: _("Show"), icon: "document", enabled: "multi", 
                    click: async function() { 
                        $("#newshow").val(tableform.table_selected_row(table).SHOWAT);
                        $("#newshow").change();
                        await tableform.show_okcancel_dialog("#dialog-show", _("Change"), { width: 550 });
                        let dtid = tableform.table_ids(document_templates.table);
                        let newshow = $("#newshow").val();
                        await common.ajax_post("document_templates", "mode=show&newshow=" + newshow + "&ids=" + dtid);
                        $.each(tableform.table_selected_rows(document_templates.table), function(i, v) {
                            v.SHOWAT = newshow;
                        });
                        tableform.table_update(document_templates.table);
                        tableform.buttons_default_state(buttons);
                    } 
                },
                { id: "images", text: _("Extra Images"), icon: "image", enabled: "always", tooltip: _("Add extra images for use in reports and documents"),
                    click: function() {
                       common.route("report_images");
                    }
                },
                { id: "reload", text: _("Reload Defaults"), icon: "refresh", enabled: "always", 
                    click: async function() {
                        await tableform.show_okcancel_dialog("#dialog-reload", _("Reload"), { width: 600 });
                        await common.ajax_post("document_templates", "mode=reload&names=" + encodeURIComponent($("#reloadtemplates").val()));
                        common.route_reload();
                    }
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render_reload_dialog: function() {
            return [
                '<div id="dialog-reload" style="display: none" title="' + html.title(_("Reload Defaults")) + '">',
                html.info(_("Use this dialog to reload default document templates that have been deleted")),
                tableform.fields_render([
                    { post_field: "reloadtemplates", type: "selectmulti", label: _("Templates"), options: controller.defaults }
                ]),
                '</div>'
            ].join("\n");
        },

        render_rename_dialog: function() {
            return [
                '<div id="dialog-rename" style="display: none" title="' + html.title(_("Rename")) + '">',
                tableform.fields_render([
                    { post_field: "newname", type: "text", label: _("New name"), doublesize: true }
                ]),
                '</div>'
            ].join("\n");
        },

        render_upload_dialog: function() {
            return [
                '<div id="dialog-upload" style="display: none" title="' + html.title(_("Upload a new document template")) + '">',
                html.info(_("File types accepted: {0}").replace("{0}", ".odt, .html")),
                '<form id="form-upload" action="document_templates" method="post" enctype="multipart/form-data">',
                '<input type="hidden" name="mode" value="upload" />',
                tableform.fields_render([
                    { name: "filechooser", type: "file", label: _("Document file") },
                    { name: "uploadpath", type: "text", label: _("Path") },
                    { name: "uploadshow", type: "selectmulti", label: _("Show"), 
                        options: { displayfield: "DISPLAY", valuefield: "VALUE", rows: document_templates.doctypes }}
                ]),
                '</form>',
                '</div>'
            ].join("\n");
        },

        render_show_dialog: function() {
            return [
                '<div id="dialog-show" style="display: none" title="' + html.title(_("Show")) + '">',
                tableform.fields_render([
                    { post_field: "newshow", type: "selectmulti", label: _("Show"), 
                        options: { displayfield: "DISPLAY", valuefield: "VALUE", rows: document_templates.doctypes }}
                ]),
                '</div>'
            ].join("\n");
        },

        render: function() {
            let s = "";
            this.model();
            s += this.render_rename_dialog();
            s += this.render_reload_dialog();
            s += this.render_show_dialog();
            s += this.render_upload_dialog();
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
        },

        destroy: function() {
            common.widget_destroy("#dialog-upload");
            common.widget_destroy("#dialog-reload");
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
