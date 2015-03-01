/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */
$(function() {

    var table = {
        rows: controller.rows,
        idcolumn: "ID",
        edit: function(row) {
            window.location = "publish_logs?view=" + row.PATH + "/" + row.NAME;
        },
        columns: [
            { field: "NAME", display: _("File"), initialsort: true },
            { field: "SUCCESS", display: _("Success") },
            { field: "ALERTS", display: _("Alerts") }
        ]
    };


    var publish_logs = {

        render: function() {
            var s = "";
            s += html.content_header(_("Publishing Logs"));
            s += tableform.table_render(table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.table_bind(table);
        }

    };

    common.module(publish_logs, "publish_logs", "options");

});
