/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var report = {
        bind: function() {
            $("#submitcriteria").button().click(function() {
                common.route("report?" + $("#criteriaform input, #criteriaform select").toPOST(true));
            });
        },

        destroy: function() {
            // Criteria are manually inserted by the server side page loader
            $("#asm-content").remove();
        },

        name: "report",
        animation: "report",
        title: function() { return controller.title; }


    };

    common.module_register(report);

});
