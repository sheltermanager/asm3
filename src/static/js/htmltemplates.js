/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const htmltemplates = {

        model: function() {
            const dialog = {
                add_title: _("Add template"),
                edit_title: _("Edit template"),
                edit_button_text: _("Update"), 
                close_on_ok: false,
                columns: 1,
                width: 800,
                delete_button: true,
                delete_perm: "cpo",
                delete_button_text: _("Revert to default"),
                fields: [
                    { json_field: "NAME", post_field: "templatename", readonly: false, label: _("Name"), type: "text", validation: "notblank" },
                    { json_field: "HEADER", post_field: "header", label: _("Header"), type: "htmleditor", validation: "notblank", height: "150px", width: "720px" },
                    { json_field: "BODY", post_field: "body", label: _("Body"), type: "htmleditor", validation: "notblank", height: "150px", width: "720px" },
                    { json_field: "FOOTER", post_field: "footer", label: _("Footer"), type: "htmleditor", validation: "notblank", height: "150px", width: "720px" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "NAME",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row, {
                        
                        onload: function() {
                            if ( !controller.templates.hasOwnProperty(row.NAME) ) {
                                $(".asm-dialog-deletebutton").hide();
                            }
                        },
                        onchange: async function() {
                            tableform.fields_update_row(dialog.fields, row);
                            await tableform.fields_post(dialog.fields, "mode=update&name=" + row.NAME, "htmltemplates");
                            tableform.table_update(table);
                            tableform.dialog_enable_buttons();
                            tableform.dialog_info(_("Updated"));
                        },
                        ondelete: function() {
                            //Revert to default
                            $("#header").htmleditor("value", controller.templates[row.NAME].head);
                            $("#body").htmleditor("value", controller.templates[row.NAME].body);
                            $("#footer").htmleditor("value", controller.templates[row.NAME].foot);
                            tableform.dialog_enable_buttons();
                        },
                        onvalidate: function() {
                            var valid = true;
                            $.each(controller.rows, function(i, v) {
                                if (v.NAME == $("#templatename").val() && v.ID != row.ID) {
                                    tableform.dialog_error(_("A template with this name already exists"));
                                    valid = false;
                                    return false;
                                }
                            });
                            return valid;
                        }
                    });
                },
                columns: [
                    { field: "NAME", display: _("Name"), initialsort: true }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Template"), icon: "new", enabled: "always", 
                    click: function() { 
                        tableform.dialog_show_add(dialog, {
                            onadd: async function() {
                                await tableform.fields_post(dialog.fields, "mode=create", "htmltemplates");
                                let row = {};
                                tableform.fields_update_row(dialog.fields, row);
                                controller.rows.push(row);
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }
                        });
                    } 
                },
                { id: "clone", text: _("Clone"), icon: "copy", enabled: "one", 
                    click: function() { 
                        tableform.dialog_show_add(dialog, {
                            onadd: async function() {
                                await tableform.fields_post(dialog.fields, "mode=create", "htmltemplates");
                                let row = {};
                                tableform.fields_update_row(dialog.fields, row);
                                controller.rows.push(row);
                                tableform.table_update(table);
                                tableform.dialog_close();
                            },
                            onload: function() {
                                let row = tableform.table_selected_row(table);
                                tableform.fields_populate_from_json(dialog.fields, row);
                                $("#templatename").val($("#templatename").val() + "_copy");
                            }
                        });
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let names = tableform.table_ids(table);
                        await common.ajax_post("htmltemplates", "mode=delete&names=" + names);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "preview", text: _("Preview"), icon: "web", enabled: "one",
                    click: async function() {
                        await tableform.show_okcancel_dialog("#dialog-preview", _("Preview"), { width: 550, notblank: [ "animals" ] });
                        let ids = tableform.table_ids(table);
                        window.open("htmltemplates_preview?template=" + ids + "&animals=" + $("#animals").val(), true);
                    }
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += this.render_previewdialog();
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

        render_previewdialog: function() {
            return [
                '<div id="dialog-preview" style="display: none" title="' + html.title(_("Preview")) + '">',
                html.info(_("Preview allows you to test your HTML templates while bypassing server side caching and without making your animals adoptable")),
                tableform.fields_render([
                    { post_field: "animals", type: "animalmulti", label: _("Animals") }
                ]),
                '</div>'
            ].join("\n");
        },

        destroy: function() {
            tableform.dialog_destroy();
            common.widget_destroy("#dialog-preview");
            common.widget_destroy("#animals");
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
