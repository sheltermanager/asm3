/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var report = {

        bind: function() {
        },

        destroy: function() {
        },

        name: "report",
        animation: "report",
        title: function() { return controller.title; }


    };

    common.module_register(report);

});
