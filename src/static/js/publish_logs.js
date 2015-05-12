/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */
$(function() {

    var publish_logs = {

        model: function() {
            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    common.route("publish_logs?ajax=false&view=" + row.PATH + "/" + row.NAME);
                },
                columns: [
                    { field: "NAME", display: _("File"), initialsort: true },
                    { field: "SUCCESS", display: _("Success") },
                    { field: "ALERTS", display: _("Alerts") }
                ]
            };
            this.table = table;
        },

        render: function() {
            var s = "";
            this.model();
            s += html.content_header(_("Publishing Logs"));
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.table_bind(this.table);
        },

        name: "publish_logs",
        animation: "options",
        title: function() { return _("Publisher Logs"); },
        routes: {
            "publish_logs": function() { common.module_loadandstart("publish_logs", "publish_logs?" + this.rawqs); }
        }

    };

    common.module_register(publish_logs);

});
