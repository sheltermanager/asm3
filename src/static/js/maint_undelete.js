/*global $, jQuery, FileReader, Modernizr, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const maint_undelete = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    //common.route("document_repository_file?ajax=false&dbfsid=" + row.ID);
                },
                columns: [
                    { field: "ID", display: _("ID") },
                    { field: "TABLENAME", display: _("Table") },
                    { field: "DATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
                    { field: "DELETEDBY", display: _("By") }
                ]
            };

            const buttons = [
                { id: "restore", text: _("Restore"), icon: "new", enabled: "one", perm: "", 
                    click: async function() { 
                        let row = tableform.table_selected_row(table);
                        await common.ajax_post("maint_undelete", "mode=undelete&id=" + row.ID + "&table=" + row.TABLENAME);
                        header.show_info("Restored.");
                     } 
                }
            ];
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += html.content_header(_("Undelete"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        destroy: function() {
        },

        name: "maint_undelete",
        animation: "options",
        title: function() { return _("Undelete"); },
        routes: {
            "maint_undelete": function() { common.module_start("maint_undelete"); }
        }

    };

    common.module_register(maint_undelete);

});
