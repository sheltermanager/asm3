/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

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
