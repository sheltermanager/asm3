/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            window.location = "report_export?id=" + row.ID;
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

    var report_export = {

        render: function() {
            var s = "";
            if (controller.rows) {
                s += html.content_header(_("Export Reports as CSV"));
                s += tableform.table_render(table);
                s += html.content_footer();
            }
            return s;
        },

        bind: function() {
            if (controller.rows) {
                tableform.table_bind(table, []);
                $("input[type='checkbox']").hide();
            }
            $("#submitcriteria").button().click(function() {
                window.location = "report_export?" + $("#criteriaform input, #criteriaform select").toPOST(true);
            });
        },

        sync: function() {
        }

    };
    
    common.module(report_export, "report_export", "options");

});
