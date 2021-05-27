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
                    { field: "DATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_datetime },
                    { field: "DELETEDBY", display: _("By") }
                ]
            };

            const buttons = [
                { id: "restore", text: _("Restore"), icon: "new", enabled: "multi", perm: "", 
                    click: async function() { 
                        let rows = tableform.table_selected_rows(table), tablename = "", ids = [], multitable = false;
                        $.each(rows, function(i, row) {
                            ids.push(String(row.ID));
                            if (tablename != "" && tablename != row.TABLENAME) { multitable = true; }
                            tablename = row.TABLENAME;
                        });
                        if (multitable) { alert("Cannot restore from multiple tables at the same time."); return; }
                        await common.ajax_post("maint_undelete", "mode=undelete&ids=" + ids.join(",") + "&table=" + tablename);
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
