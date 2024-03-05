/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const publish_logs = {

        PUBLISHER_NAMES:  {
            "adoptapet":        "adoptapet.com",
            "akcreunite":       "AKC Reunite",
            "anibaseuk":        "Anibase UK",
            "buddyid":          "Buddy ID",
            "foundanimals":     "Found/24Pet",
            "helpinglostpets":  "helpinglostpets.com",
            "homeagain":        "HomeAgain",
            "maddiesfund":      "Maddies Pet Assistant",
            "petcademy":        "Petcademy",
            "petfinder":        "petfinder.com",
            "petlink":          "petlink.net",
            "petrescue":        "petrescue.com.au",
            "petslocateduk":    "petslocated.co.uk",
            "pettracuk":        "AVID PETtrac",
            "rescuegroups":     "rescuegroups.org",
            "sacmetrics":       "shelteranimalscount.org",
            "savourlife":       "savour-life.com.au",
            "smarttag":         "Smart Tag"
        },

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    common.route("publish_log_view?ajax=false&view=" + row.ID);
                },
                columns: [
                    { field: "NAME", display: _("Publisher"), formatter: function(row) {
                        return PUBLISHER_NAMES[row.NAME] || row.NAME;
                    }},
                    { field: "PUBLISHDATETIME", display: _("Date"), formatter: tableform.format_datetime, initialsort: true, initialsortdirection: "desc" },
                    { field: "SUCCESS", display: _("Success") },
                    { field: "ALERTS", display: _("Alerts") }
                ]
            };
            this.table = table;
        },

        render: function() {
            let s = "";
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
