/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const report_images = {

        model: function() {
            const dialog = {
                add_title: _("Extra images"),
                close_on_ok: true,
                html_form_action: "report_images",
                html_form_enctype: "multipart/form-data",
                columns: 1,
                width: 550,
                fields: [
                    { post_field: "filechooser", label: _("Image file"), type: "file", validation: "notblank" },
                    { type: "raw", label: "", markup: '<input type="hidden" name="mode" value="create" />' }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "NAME",
                edit: function(row) {
                    common.route("image?db=" + asm.useraccount + "&mode=dbfs&id=/reports/" + encodeURIComponent(row.NAME));
                },
                button_click: function() {
                    common.copy_to_clipboard($(this).attr("data"));
                    header.show_info(_("Successfully copied to the clipboard."));
                    return false;
                },
                columns: [
                    { field: "NAME", display: _("Image file"), initialsort: true },
                    { field: "NAME", display: _("URL"), 
                        formatter: function(row) {
                            let relurl = "image?db=" + asm.useraccount + "&mode=dbfs&id=/reports/" + row.NAME,
                                absurl = asm.serviceurl + "?";
                            if (asm.useraccountalias) { absurl += "account=" + asm.useraccountalias + "&"; }
                            absurl += "method=extra_image&title=" + row.NAME;
                            return relurl + ' <button type="button" data-icon="link" data="' + relurl + '">' + 
                                _("Copy relative URL to the clipboard (for use with documents and reports)") + '</button>' +
                                ' <button type="button" data-icon="extlink" data="' + absurl + '">' + 
                                _("Copy absolute service URL to the clipboard (for external use in web pages and emails)") + '</button>';
                        }
                    }
                ]
            };

            const buttons = [
                { id: "new", text: _("New"), icon: "new", enabled: "always", 
                    click: async function() { 
                        await tableform.dialog_show_add(dialog);
                        let fn = $("#filechooser").val().toLowerCase();
                        validate.reset();
                        if (fn.indexOf(".jpg") == -1 && fn.indexOf(".png") == -1 && fn.indexOf(".gif") == -1) {
                            header.show_error(_("The selected file is not an image."));
                            validate.highlight("filechooser");
                            return;
                        }
                        $("#form-tableform").submit();
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("report_images", "mode=delete&ids=" + encodeURIComponent(ids));
                        common.route_reload();
                    } 
                },
                { id: "rename", text: _("Rename"), icon: "link", enabled: "one", 
                    click: async function() { 
                        let oldname = tableform.table_ids(table).split(",")[0];
                        $("#newname").val(oldname);
                        await tableform.show_okcancel_dialog("#dialog-rename", _("Rename"), { width: 550, notblank: [ "newname" ] });
                        let newname = $("#newname").val();
                        await common.ajax_post("report_images", "mode=rename&newname=" + encodeURIComponent(newname) + "&oldname=" + encodeURIComponent(oldname));
                        common.route_reload();
                    } 
                }

            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
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

        render: function() {
            let s = "";
            this.model();
            s += this.render_rename_dialog();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Extra images"));
            s += html.info(_("This screen allows you to add extra images to your database, for use in reports and documents.") + "<br />" +
                _("Upload splash.jpg and logo.jpg to override the login screen image and logo at the top left of ASM."));
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
            common.widget_destroy("#dialog-rename");
            tableform.dialog_destroy();
        },


        name: "report_images",
        animation: "options",
        title: function() { return _("Extra images"); },
        routes: {
            "report_images": function() { common.module_loadandstart("report_images", "report_images"); }
        }

    };

    common.module_register(report_images);

});
