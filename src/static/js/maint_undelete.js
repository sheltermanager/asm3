/*global $, jQuery, FileReader, Modernizr, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const maint_undelete = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "KEY",
                edit: function(row) {
                    //common.route("document_repository_file?ajax=false&dbfsid=" + row.ID);
                },
                columns: [
                    { field: "KEY", display: _("ID") },
                    { field: "DATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_datetime },
                    { field: "DELETEDBY", display: _("By") }
                ]
            };

            const buttons = [
                { id: "restore", text: _("Restore"), icon: "new", enabled: "multi", perm: "", 
                    click: async function() { 
                        await common.ajax_post("maint_undelete", "mode=undelete&ids=" + tableform.table_ids(table));
                        header.show_info("Restored.");
                     } 
                },
                { id: "selectall", type: "dropdownfilter", 
                    options: [ "(select)", "animal", "customreport", "onlineformincoming" ],
                    click: function(selval) {
                        $("#tableform input[type='checkbox']").each(function() {
                            if (String($(this).attr("data-id")).indexOf(selval) == 0) { 
                                $(this).prop("checked", true); 
                                $(this).closest("tr").find("td").addClass("ui-state-highlight");
                            }
                        });
                        tableform.table_update_buttons(table, buttons);
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
