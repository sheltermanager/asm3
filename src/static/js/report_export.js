/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const report_export = {

        model: function() {
            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    common.route("report_export_csv?id=" + row.ID);
                },
                hideif: function(row) {
                    // Superusers see everything
                    if (asm.superuser) { return false; }

                    // If the row has no view roles, we're good
                    if (!row.VIEWROLEIDS) { return false; }

                    // Is the user in one of the view roles?
                    if (common.array_overlap(row.VIEWROLEIDS.split("|"), asm.roleids.split("|"))) { return false; }
                    return true;
                },
                columns: [
                    { field: "TITLE", display: _("Report Title"), initialsort: true },
                    { field: "CATEGORY", display: _("Category") },
                    { field: "DESCRIPTION", display: _("Description") }
                ]
            };
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            if (controller.rows) {
                s += html.content_header(_("Export Reports as CSV"));
                s += tableform.table_render(this.table);
                s += html.content_footer();
            }
            return s;
        },

        bind: function() {
            if (controller.rows) {
                tableform.table_bind(this.table, []);
                $("input[type='checkbox']").hide();
            }
        },

        sync: function() {
        },

        destroy: function() {
        },

        name: "report_export",
        animation: "options",
        title: function() { return _("Export Reports as CSV"); }

    };
    
    common.module_register(report_export);

});
