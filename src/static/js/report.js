/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var report = {
        bind: function() {
            $("#submitcriteria").button().click(function() {
                window.location = "report?" + $("#criteriaform input, #criteriaform select").toPOST(true);
            });
        },

        name: "report",
        animation: "report"

    };

    common.module_register(report);

});
