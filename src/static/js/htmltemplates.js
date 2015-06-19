/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var htmltemplates = {

        model: function() {
            var dialog = {
                add_title: _("Add template"),
                edit_title: _("Edit template"),
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "NAME", post_field: "templatename", readonly: true, label: _("Name"), type: "text", validation: "notblank" },
                    { json_field: "HEADER", post_field: "header", label: _("Header"), type: "textarea", validation: "notblank" },
                    { json_field: "BODY", post_field: "body", label: _("Body"), type: "textarea", validation: "notblank" },
                    { json_field: "FOOTER", post_field: "footer", label: _("Footer"), type: "textarea", validation: "notblank" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "NAME",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row)
                        .then(function() {
                            tableform.fields_update_row(dialog.fields, row);
                            tableform.fields_post(dialog.fields, "mode=update&name=" + row.NAME, "htmltemplates");
                        })
                        .then(function(response) {
                            tableform.dialog_close();
                            tableform.table_update(table);
                        });
                },
                columns: [
                    { field: "NAME", display: _("Name"), initialsort: true }
                ]
            };

            var buttons = [
                 { id: "new", text: _("New Template"), icon: "new", enabled: "always", 
                     click: function() { 
                         tableform.dialog_show_add(dialog)
                             .then(function() {
                                 return tableform.fields_post(dialog.fields, "mode=create", "htmltemplates");
                             })
                             .then(function(response) {
                                 var row = {};
                                 tableform.fields_update_row(dialog.fields, row);
                                 controller.rows.push(row);
                                 tableform.table_update(table);
                             });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                     click: function() { 
                         tableform.delete_dialog()
                             .then(function() {
                                 tableform.buttons_default_state(buttons);
                                 var names = tableform.table_ids(table);
                                 return common.ajax_post("htmltemplates", "mode=delete&names=" + names);
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
            s += html.content_header(_("HTML Publishing Templates"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {

            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            // Only allow letters and numbers in the template names, no spaces
            /*jslint regexp: true */
            $("#templatename").keyup(function(e) {
                if (this.value.match(/[^a-zA-Z0-9]/g)) {
                    this.value = this.value.replace(/[^a-zA-Z0-9]/g, '');
                }
            });
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "htmltemplates",
        animation: "options",
        title: function() { return _("HTML Publishing Templates"); },
        routes: {
            "htmltemplates": function() { common.module_loadandstart("htmltemplates", "htmltemplates"); }
        }

    };

    common.module_register(htmltemplates);

});
