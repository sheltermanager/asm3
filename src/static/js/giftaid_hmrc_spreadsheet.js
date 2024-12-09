/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const giftaid_hmrc_spreadsheet = {

        render: function() {
            return [
                html.content_header("HMRC Gift Aid Spreadsheet"),
                html.warn("WARNING: Generating gift aid spreadsheets can take a few minutes if you have many donations."),
                '<form id="hmrcform" action="giftaid_hmrc_spreadsheet" method="post">',
                tableform.fields_render([
                    { name: "fromdate", type: "date", label: _("From") },
                    { name: "todate", type: "date", label: _("To") }
                ], { full_width: false }),
                tableform.buttons_render([
                    { id: "gen", icon: "report", text: _("Generate") }
                ], { centered: true }),
                '</form>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#button-gen").button().click(function() {
                if (validate.notblank([ "fromdate", "todate" ])) {
                    $("#hmrcform").submit();
                }
            });
        },

        sync: function() {
            validate.indicator([ "fromdate", "todate" ]);
        },

        name: "giftaid_hmrc_spreadsheet",
        animation: "report",
        autofocus: "#fromdate",
        title: function() { return _("HMRC Gift Aid Spreadsheet"); },
        routes: {
            "giftaid_hmrc_spreadsheet": function() { common.module_start("giftaid_hmrc_spreadsheet"); }
        }

    };

    common.module_register(giftaid_hmrc_spreadsheet);

});
