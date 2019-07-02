/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var report_images = {

        model: function() {
            var dialog = {
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

            var table = {
                rows: controller.rows,
                idcolumn: "NAME",
                edit: function(row) {
                    common.route("image?db=" + asm.useraccount + "&mode=dbfs&id=/reports/" + row.NAME);
                },
                columns: [
                    { field: "NAME", display: _("Image file"), initialsort: true },
                    { field: "NAME", display: _("URL"), 
                        formatter: function(row) {
                            return "image?db=" + asm.useraccount + "&mode=dbfs&id=/reports/" + row.NAME;
                        }
                    }
                ]
            };

            var buttons = [
                 { id: "new", text: _("New"), icon: "new", enabled: "always", 
                     click: function() { 
                         tableform.dialog_show_add(dialog)
                             .then(function() {
                                 var fn = $("#filechooser").val().toLowerCase();
                                 validate.reset();
                                 if (fn.indexOf(".jpg") == -1 && fn.indexOf(".png") == -1 && fn.indexOf(".gif") == -1) {
                                     header.show_error(_("The selected file is not an image."));
                                     validate.highlight("filechooser");
                                     return;
                                 }
                                 $("#form-tableform").submit();
                            });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                     click: function() { 
                         tableform.delete_dialog()
                             .then(function() {
                                 tableform.buttons_default_state(buttons);
                                 var ids = tableform.table_ids(table);
                                 return common.ajax_post("report_images", "mode=delete&ids=" + ids);
                             })
                             .then(function() {
                                 common.route_reload();
                             });
                     } 
                 },
                 { id: "rename", text: _("Rename"), icon: "link", enabled: "one", 
                     click: function() { 
                         $("#newname").val(tableform.table_ids(table).split(",")[0]);
                         $("#dialog-rename").dialog("open");
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
            var renamebuttons = { }, table = report_images.table;
            renamebuttons[_("Rename")] = function() {
                validate.reset("dialog-rename");
                if (!validate.notblank([ "newname" ])) { return; }
                $("#dialog-rename").disable_dialog_buttons();
                var oldname = tableform.table_ids(table).split(",")[0];
                var newname = encodeURIComponent($("#newname").val());
                common.ajax_post("report_images", "mode=rename&newname=" + newname + "&oldname=" + oldname)
                    .then(function() {
                        common.route_reload();
                    });
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


        render: function() {
            var s = "";
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
            this.bind_rename_dialog();
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
